from premedy.remediation_base import RemediationBase, remediation
import logging
from premedy import config

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


class RemediateFeatureDemo(RemediationBase):
    category = "FEATURE_DEMO"

    @remediation
    def remediate01(self):
        logger.info(f" FEATURE_DEMO: [01] {self.finding_result.finding.name}")
        return "ok"

    @remediation(notify_success=True)
    def remediate02(self):
        logger.info(f" FEATURE_DEMO: [02] {self.finding_result.finding.name}")
        return "ok"
