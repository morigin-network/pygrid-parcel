# %%
# stdlib
import random
from time import time,sleep

# third party
from jose import jws
from jose.constants import ALGORITHMS
from jwcrypto.jwk import JWK
import requests
from requests import Session
import json
from ..models import model_manager
import base64

PARCEL_CLIENT_ID = "REPLACE_ME"
PARCEL_APP_ID = "REPLACE_ME"
PARCEL_JWK = {
    "REPLACE": "ME"
}
DOCKER_IMG_TAG = "REPLACE/ME"


def RunAveraging(diff_docids,orgparam,avgplan,cyclenum):
    client_id = PARCEL_CLIENT_ID
    app_id = PARCEL_APP_ID
    jwk = PARCEL_JWK

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
        now = int(time())
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

    class NoRebuildAuthSession(Session):
        def rebuild_auth(self, prepared_request, response):
            pass


    session = NoRebuildAuthSession()


    headers = {
        "authorization": f"Bearer {token}",
    }

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
                    "owner": app_id,
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

    inputdoc =  []
    for i,ff in enumerate(diff_docids):
        inputdoc.append({'mountPath':f"diff{i}.txt","id":ff})
    inputdoc.append({"mountPath": 'orgparam', "id": docid_orgparam})
    inputdoc.append({ "mountPath": 'avg_plan', "id": docid_avgplan })

    compute_data = {
        "name": f"federated-averaging-{cyclenum}",
        "cmd" : ['python','avg.py'],
        "image": DOCKER_IMG_TAG,
        "inputDocuments": inputdoc,
        "outputDocuments": [{"mountPath":'prediction.txt',"owner":app_id}],
        "cpus": 1,
        "memory":"2G"
    }

    # print(json.dumps(compute_data))


    

    # print(queued_job.text)
    jobid = None
    for i in range(5):
        try: 
            queued_job = session.post(f"{base_url}/compute/jobs",data=json.dumps(compute_data),headers=headers)
            print(queued_job.text)
            jobid = json.loads(queued_job.text)["id"]
            break
        except Exception as e:
            print(e)
            sleep(5)
    if jobid is None:
        return None   
    jobdata = {
        'jobId':jobid
    }
    outdoc = None
    while True:
        result = session.get(f"{base_url}/compute/jobs/{jobid}/status",data=json.dumps(jobdata),headers=headers)
        result = json.loads(result.text)
        if result.get('status', {}).get('phase', None) == "Succeeded": # result['status']['phase'] == "Succeeded":
            result = session.get(f"{base_url}/compute/jobs/{jobid}",data=json.dumps(jobdata),headers=headers)
            result = json.loads(result.text)
            try:
                outdoc = result['io']['outputDocuments']
                break
            except KeyError as e:
                print(e)                
        sleep(1)

    download_res = session.get(
        f"{base_url}/documents/{outdoc[0]['id']}/download",
        headers=headers,
    )
    final = base64.b64decode(download_res.text.encode())
    return model_manager.unserialize_model_params(final)
