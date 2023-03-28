from operator import methodcaller
from google.cloud import securitycenter_v1
import logging
from premedy import config

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


def get_project_finding_results(
    project: str,
    query_filters: list = [],
    result_filters: list = (),
    exclude_muted=True,
) -> list:
    securitycenter_client = securitycenter_v1.SecurityCenterClient()

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
    securitycenter_client = securitycenter_v1.SecurityCenterClient()

    request = securitycenter_v1.SetMuteRequest()
    request.name = finding_path
    request.mute = securitycenter_v1.Finding.Mute.MUTED

    finding = securitycenter_client.set_mute(request)
    logger.info(f"Mute value for the finding: {finding.mute.name}")
