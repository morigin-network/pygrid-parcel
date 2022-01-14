import Parcel, { JobPhase } from "@oasislabs/parcel";
import * as fs from "fs";

const parcel = new Parcel({
  //This should actuallyy be in bob's mobile so generate bob's private key.
  // Replace with your service client ID, e.g. "C92EAFfH67w4bGkVMjihvkQ"
  clientId: "REPLACE_ME",
  // Replace with the private key of your service client.
  privateKey: {
    REPLACE: "ME",
  },
});

const bobId = "REPLACE_ME";
const appId = "REPLACE_ME";

const data = fs.readFileSync("diffcrazy.txt", "utf8");
const documentDetails = { title: "difference_report", tags: ["federated"] };

const bobDocument = await parcel.uploadDocument(data, {
  details: documentDetails,
  owner: bobId,
  toApp: appId,
}).finished;

console.log(
  `Created document ${bobDocument.id} with owner ${bobDocument.owner}`
);

const data2 = fs.readFileSync("orgparam");
const documentDetails2 = { title: "model_params", tags: ["federated"] };

const paramDocument = await parcel.uploadDocument(data2, {
  details: documentDetails2,
  toApp: appId,
}).finished;

console.log(
  `Created document ${paramDocument.id} with owner ${paramDocument.owner}`
);

const data3 = fs.readFileSync("avg_plan", "utf-8");
const documentDetails3 = { title: "avg_plan", tags: ["federated"] };

const avgDocument = await parcel.uploadDocument(data3, {
  details: documentDetails3,
  toApp: appId,
}).finished;

console.log(
  `Created document ${avgDocument.id} with owner ${avgDocument.owner}`
);

const jobSpec = {
  name: "federated-averaging",
  image: "topmmthomas/pygriddatax:diffavg",
  inputDocuments: [
    { mountPath: "diff1.txt", id: bobDocument.id },
    { mountPath: "orgparam", id: paramDocument.id },
    { mountPath: "avg_plan", id: avgDocument.id },
  ],
  outputDocuments: [{ mountPath: "prediction.txt", owner: appId }],
  cmd: ["python", "avg.py"],
  memory: "2G",
};

console.log("Running the job as myself.");
const jobId = (await parcel.submitJob(jobSpec)).id;

// Wait for job to finish.
let job = 0;
do {
  await new Promise((resolve) => setTimeout(resolve, 5000)); // eslint-disable-line no-promise-executor-return
  job = await parcel.getJobStatus(jobId);
  console.log(`Job status is ${JSON.stringify(job.status)}`);
} while (
  job.status.phase === JobPhase.PENDING ||
  job.status.phase === JobPhase.RUNNING
);

console.log(
  `Job ${jobId} completed with status ${job.status.phase} and ${job.status.outputDocuments.length} output document(s).`
);

console.log("Downloading output document as Bob.");
const outputDownload = parcel.downloadDocument(
  job.status.outputDocuments[0].id
);
const outputSaver = fs.createWriteStream(`output_document`);
await outputDownload.pipeTo(outputSaver);
const output = fs.readFileSync("output_document", "utf-8");
console.log(`Here's the computed result: "${output}"`);
