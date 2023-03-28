from google.cloud.securitycenter_v1 import ListFindingsResponse
import traceback
import os
import logging
from premedy import config

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


class PremedyFinding:
    def __init__(self, message):
        self.message = message
        self.finding_result = PremedyFinding.parse_finding_result(message)

    @staticmethod
    def parse_finding_result(message: str) -> ListFindingsResponse.ListFindingsResult:
        try:
            finding_result = ListFindingsResponse.ListFindingsResult.from_json(
                message, ignore_unknown_fields=True
            )
            return finding_result
        except:
            logger.error("parsing finding result from json")
            logger.debug(traceback.format_exc())

    @property
    def finding_result_id(self) -> str:
        return self.finding_result.finding.name.split("/")[-1]

    def save_in_gcs_bucket(self):
        try:
            bucket_name = os.environ.get("BUCKET_NAME", None)
            bucket_project = os.environ.get("BUCKET_PROJECT", None)
            if not bucket_name or not bucket_project:
                return

            from google.cloud import storage

            client = storage.Client(project=bucket_project)
            bucket = client.get_bucket(bucket_name)
            store_path = "/".join(self.finding_result.finding.name.split("/")[-4:])
            blob = bucket.blob(store_path)
            finding_result_json = ListFindingsResponse.ListFindingsResult.to_json(
                instance=self.finding_result, indent=2
            )

            premedy_finding = f"""{{
                "finding": {self.message},
                "finding_result": {finding_result_json}
            }}"""

            blob.upload_from_string(premedy_finding)
            logger.info(
                f"stored finding [{self.finding_result_id}] in GCS Bucket [{bucket_name}]"
            )
        except:
            logger.error("saving finding in GCS Bucket")
            logger.debug(traceback.format_exc())
