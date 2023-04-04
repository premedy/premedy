import json
from google.cloud.securitycenter_v1 import ListFindingsResponse

finding_as_dict = {
    "finding": {
        "name": "organizations/659624054309/sources/14882874427929637851/findings/0f6d1815f292ff068946c40ca0d579c8",
        "parent": "organizations/659624054309/sources/14882874427929637851",
        "resourceName": "//storage.googleapis.com/premise-governance-premedy",
        "state": 1,
        "category": "BUCKET_LOGGING_DISABLED",
        "externalUri": "https://cloud.google.com/storage/docs/access-logs",
        "sourceProperties": {
            "compliance_standards": {"cis": [{"version": "1.0", "ids": ["5.3"]}]},
            "Recommendation": "To set up logging for a bucket, complete the usage logs & storage logs guide at: https://cloud.google.com/storage/docs/access-logs",
            "ResourcePath": [
                "projects/premise-governance/",
                "folders/180949481639/",
                "folders/1098094629246/",
                "organizations/659624054309/",
            ],
            "ScannerName": "LOGGING_SCANNER",
            "ReactivationCount": 1,
            "Explanation": "To help investigate security issues and monitor storage consumption, enable usage logs and storage logs for your Cloud Storage buckets. Usage logs provide information for all of the requests made on a specified bucket, and the storage logs provide information about the storage consumption of that bucket.",
            "ExceptionInstructions": 'Add the security mark "allow_bucket_logging_disabled" to the asset with a value of "true" to prevent this finding from being activated again.',
        },
        "securityMarks": {
            "name": "organizations/659624054309/sources/14882874427929637851/findings/0f6d1815f292ff068946c40ca0d579c8/securityMarks",
            "marks": {},
            "canonicalName": "",
        },
        "eventTime": "2023-03-29T10:01:13.606589Z",
        "createTime": "2023-03-28T22:14:36.208Z",
        "severity": 4,
        "canonicalName": "projects/844513899481/sources/14882874427929637851/findings/0f6d1815f292ff068946c40ca0d579c8",
        "mute": 4,
        "findingClass": 3,
        "contacts": {
            "technical": {"contacts": [{"email": "governance-platform@premise.com"}]},
            "security": {"contacts": [{"email": "governance-platform@premise.com"}]},
        },
        "compliances": [{"standard": "cis", "version": "1.0", "ids": ["5.3"]}],
        "parentDisplayName": "Security Health Analytics",
        "description": "To help investigate security issues and monitor storage consumption, enable usage logs and storage logs for your Cloud Storage buckets. Usage logs provide information for all of the requests made on a specified bucket, and the storage logs provide information about the storage consumption of that bucket.",
        "externalSystems": {},
        "connections": [],
        "muteInitiator": "",
        "processes": [],
        "iamBindings": [],
        "nextSteps": "",
        "containers": [],
    },
    "resource": {
        "name": "//storage.googleapis.com/premise-governance-premedy",
        "projectDisplayName": "premise-governance",
        "parentDisplayName": "premise-governance",
        "type": "google.cloud.storage.Bucket",
        "folders": [
            {
                "resourceFolder": "//cloudresourcemanager.googleapis.com/folders/180949481639",
                "resourceFolderDisplayName": "env-prod",
            },
            {
                "resourceFolder": "//cloudresourcemanager.googleapis.com/folders/1098094629246",
                "resourceFolderDisplayName": "active",
            },
        ],
        "displayName": "premise-governance-premedy",
        "projectName": "",
        "parentName": "",
    },
    "stateChange": 0,
}

finding_as_json = json.dumps(finding_as_dict)
finding_as_protobuf = ListFindingsResponse.ListFindingsResult.from_json(finding_as_json)
