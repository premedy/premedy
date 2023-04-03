import traceback
from operator import methodcaller
from google.cloud import securitycenter
from google.cloud.securitycenter_v1 import ListFindingsResponse
from google.cloud import storage
import logging
import os
from premedy import config

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


def parse_finding_result(message: str) -> ListFindingsResponse.ListFindingsResult:
    try:
        finding_result = ListFindingsResponse.ListFindingsResult.from_json(
            message, ignore_unknown_fields=True
        )
        return finding_result
    except Exception as e:
        logger.error("parsing finding result from json: " + str(e))


def save_in_gcs_bucket(finding_result: ListFindingsResponse.ListFindingsResult):
    try:
        bucket_name = os.environ.get("BUCKET_NAME", None)
        bucket_project = os.environ.get("BUCKET_PROJECT", None)
        if not bucket_name or not bucket_project:
            return

        finding_id = get_finding_id(finding_result)
        client = storage.Client(project=bucket_project)
        bucket = client.get_bucket(bucket_name)
        store_path = "/".join(finding_result.finding.name.split("/")[-4:])
        blob = bucket.blob(store_path)
        blob.upload_from_string(
            ListFindingsResponse.ListFindingsResult.to_json(
                instance=finding_result, indent=2
            )
        )
        logger.info(f"store finding [{finding_id}] in GCS Bucket [{bucket_name}]")
    except Exception as e:
        logger.error("saving finding in GCS Bucket: " + str(e))


def get_finding_id(finding_result: ListFindingsResponse.ListFindingsResult) -> str:
    return finding_result.finding.name.split("/")[-1]


def get_project_finding_results(
    project: str,
    query_filters: list = [],
    result_filters: list = (),
    exclude_muted=True,
) -> list:
    securitycenter_client = securitycenter.SecurityCenterClient()

    source_name = f"projects/{project}/sources/-"
    request = {"parent": source_name}

    if exclude_muted:
        query_filters.append({"lhs": "mute", "op": "!=", "rhs": "MUTED"})

    if query_filters:
        request["filter"] = " AND ".join(
            [
                f'{query_filter["lhs"]}{query_filter["op"]}"{query_filter["rhs"]}"'
                for query_filter in query_filters
            ]
        )
    finding_results = []
    finding_result_iterator = securitycenter_client.list_findings(request=request)
    for i, finding in enumerate(finding_result_iterator):
        if (
            not result_filters
            or result_filters
            and all(list(map(methodcaller("__call__", finding), result_filters)))
        ):
            finding_results.append(finding)
    return finding_results


def set_mute_finding(finding_path: str) -> None:
    """
      Mute an individual finding.
      If a finding is already muted, muting it again has no effect.
      Various mute states are: MUTE_UNSPECIFIED/MUTE/UNMUTE.
    Args:
        finding_path: The relative resource name of the finding. See:
        https://cloud.google.com/apis/design/resource_names#relative_resource_name
        Use any one of the following formats:
        - organizations/{organization_id}/sources/{source_id}/finding/{finding_id},
        - folders/{folder_id}/sources/{source_id}/finding/{finding_id},
        - projects/{project_id}/sources/{source_id}/finding/{finding_id}.
    """
    securitycenter_client = securitycenter.SecurityCenterClient()

    request = securitycenter.SetMuteRequest()
    request.name = finding_path
    request.mute = securitycenter.Finding.Mute.MUTED

    finding = securitycenter_client.set_mute(request)
    logger.info(f"Mute value for the finding: {finding.mute.name}")
