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
print(identity_res.text)


identity_id = json.loads(identity_res.text)["id"]
# identity_id


class NoRebuildAuthSession(Session):
    def rebuild_auth(self, prepared_request, response):
        pass


session = NoRebuildAuthSession()


headers = {
    "authorization": f"Bearer {token}",
}

files = {
    "data": ("data", b"Hellodosiljfdkslfj", "application/octet-stream"),
    "metadata": (
        "metadata",
        json.dumps(
            {
                "details": {
                    "title": "Difference 123testing",
                    "tags": ["diff_report"],
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

print(upload_res.text)
docid = json.loads(upload_res.text)["id"]
print("The document id is", docid)

data = {
    "documentId":docid
}
dl = session.get(f"{base_url}/documents/{docid}/download",headers=headers)
print(dl.text)


