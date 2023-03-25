#!/usr/bin/env python3

import base64
import requests as r
import json
import sys
import subprocess

if len(sys.argv) < 2:
    print("./post_finding.py FINDING_JSON_PATH [url|127.0.0.1:8080]")
    print("./post_finding.py ./sample_findings/FEATURE_DEMO.json")
    print(
        "./post_finding.py ./sample_findings/FEATURE_DEMO.json https://premedy------------uc.a.run.app"
    )
    sys.exit(1)

with open(sys.argv[1], "rb") as f:
    data = b"".join(f.readlines())

url = "http://127.0.0.1:8080"
headers = {"content-type": "application/json"}

if len(sys.argv) >= 3:
    url = sys.argv[2]
    token = (
        subprocess.check_output(["gcloud", "auth", "print-identity-token"])
        .decode("utf8")
        .strip()
    )
    headers["Authorization"] = f"Bearer {token}"

data = base64.b64encode(data).decode("utf-8")
json_data = {
    "message": {"data": data},
    "subscription": "projects/GOOGLE_PROJECT/topics/scc-active-findings",
}

response = r.post(url=url, headers=headers, data=json.dumps(json_data))
print(response.status_code)
