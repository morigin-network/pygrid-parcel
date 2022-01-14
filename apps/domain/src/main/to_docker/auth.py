# %%
# stdlib
import random
import time

# third party
from jose import jws
from jose.constants import ALGORITHMS
from jwcrypto.jwk import JWK
import requests
from requests import Session
import json


client_id = "REPLACE_ME"
app_id = "REPLACE_ME"
jwk = {
    "REPLACE": "ME",
}

private_key = (
    JWK(**jwk).export_to_pem(private_key=True, password=None).decode("utf-8")
)


token_endpoint = "https://auth.oasislabs.com/oauth/token"
audience = "https://api.oasislabs.com/parcel"
token_life_time = 1 * 60 * 60
client_assertion_life_time = 1 * 60 * 60
base_url = "https://api.oasislabs.com/parcel/v1"

def make_jws(private_key, key_id, payload, lifetime):
    headers = {
        "alg": "ES256",
        "typ": "JWT",
        "kid": key_id,
    }
    now = int(time.time())
    payload["iat"] = (
        now - 2 * 60
    )  # Take off a couple of minutes to account for clock skew.
    payload["exp"] = now + lifetime

    return jws.sign(
        payload, private_key, headers=headers, algorithm=ALGORITHMS.ES256
    )


payload = {
    "sub": client_id,
    "iss": client_id,
    "aud": token_endpoint,
    "jti": "%016x" % random.randrange(16 ** 16),
}
signature = make_jws(
    private_key, jwk["kid"], payload, client_assertion_life_time
)


body = {
    "grant_type": "client_credentials",
    "client_assertion": signature,
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "scope": "parcel.full",
    "audience": audience,
}

r = requests.post(token_endpoint, data=body)
r = json.loads(r.text)

token = r['access_token']

headers = {
    "authorization": f"Bearer {token}",
}

identity_res = requests.get(
    f"{base_url}/identities/me",
    headers=headers,
)
# print(identity_res.text)


identity_id = json.loads(identity_res.text)["id"]
print(identity_id)


class NoRebuildAuthSession(Session):
    def rebuild_auth(self, prepared_request, response):
        pass


session = NoRebuildAuthSession()


headers = {
    "authorization": f"Bearer {token}",
}

with open('avg_plan',"r") as f:
    avgplan = f.read()

with open("orgparam","r") as f:
    orgparam = f.read()

with open("diffcrazy.txt","r") as f:
    diffcrazy = f.read()


files = {
    "data": ("data", avgplan.encode(), "application/octet-stream"),
    "metadata": (
        "metadata",
        json.dumps(
            {
                "details": {
                    "title": "avergaging plan",
                    "tags": ["federated"],
                },
                "owner": app_id,
                # "owner": "IDV2kpWEC6vnB9ui9vEqJ8U",
            }
        ),
        "application/json",
    ),
}


files2 = {
    "data": ("data", orgparam.encode(), "application/octet-stream"),
    "metadata": (
        "metadata",
        json.dumps(
            {
                "details": {
                    "title": "Model parameter",
                    "tags": ["federated"],
                },
                "owner": identity_id,
                # "owner": "IDV2kpWEC6vnB9ui9vEqJ8U",
            }
        ),
        "application/json",
    ),
}

files3 = {
    "data": ("data", diffcrazy.encode(), "application/octet-stream"),
    "metadata": (
        "metadata",
        json.dumps(
            {
                "details": {
                    "title": "Difference calculation",
                    "tags": ["federated"],
                },
                "owner": identity_id,
                # "owner": "IDV2kpWEC6vnB9ui9vEqJ8U",
            }
        ),
        "application/json",
    ),
}

upload_res = session.post(
    f"{base_url}/documents",
    headers=headers,
    files=files,
)

docid_avgplan = json.loads(upload_res.text)["id"]

upload_res = session.post(
    f"{base_url}/documents",
    headers=headers,
    files=files2,
)

docid_orgparam = json.loads(upload_res.text)["id"]

upload_res = session.post(
    f"{base_url}/documents",
    headers=headers,
    files=files3,
)

docid_diff = json.loads(upload_res.text)["id"]
print("The document id is", docid_avgplan,docid_orgparam,docid_diff)

compute_data = {
    "name": "federated-averaging",
    "cmd" : ['python','avg.py'],
    "image": "topmmthomas/pygriddatax:diffavg2",
    "inputDocuments":[{ "mountPath": 'diff1.txt', "id": docid_diff}, { "mountPath": 'orgparam', "id": docid_orgparam }, { "mountPath": 'avg_plan', "id": docid_avgplan }],
    "outputDocuments": [{"mountPath":'prediction.txt',"owner":app_id}],
    "cpus": 1,
    "memory":"2G"
}

# print(json.dumps(compute_data))


queued_job = session.post(f"{base_url}/compute/jobs",data=json.dumps(compute_data),headers=headers)

print(queued_job.text)

jobid = json.loads(queued_job.text)["id"]
import time
jobdata = {
    'jobId':jobid
}
while True:
    result = session.get(f"{base_url}/compute/jobs/{jobid}/status",data=json.dumps(jobdata),headers=headers)
    result = json.loads(result.text)
    print(result['status']['phase'])
    if result['status']['phase'] == "Succeeded":
        outdoc = result['status']['outputDocuments']
        break
    time.sleep(1)
print(outdoc)

download_res = session.get(
    f"{base_url}/documents/{outdoc[0]['id']}/download",
    headers=headers,
)
print(download_res.text[:100])


