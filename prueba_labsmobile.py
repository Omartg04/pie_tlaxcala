import requests
from requests.auth import HTTPBasicAuth

USER = "admin@alcaldia-ao.mx"
PASS = "T81xFC056bIoVhN3ZoTRyQY6dZg2QcuA"

resp = requests.post(
    "https://api.labsmobile.com/json/send",
    json={
        "message": "Prueba PIE Tlaxcala",
        "recipient": [{"msisdn": "5215528856227"}],
        "sender": "PIEDemo"
    },
    auth=HTTPBasicAuth(USER, PASS),
    headers={"Content-Type": "application/json"},
)
print(resp.status_code)
print(resp.text)