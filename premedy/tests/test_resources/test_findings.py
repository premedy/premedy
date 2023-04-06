import unittest
from unittest.mock import MagicMock, patch

from premedy.resources.findings import get_finding_id, save_in_gcs_bucket
from premedy.tests.mocks.bucket_logging_disabled_finding import finding_as_protobuf


class TestFindings(unittest.TestCase):
    @patch.dict(
        "premedy.resources.findings.os.environ",
        {"BUCKET_NAME": "my-bucket", "BUCKET_PROJECT": "my-project"},
    )
    @patch("premedy.resources.findings.storage.Client")
    def test_save_in_gcs_bucket_default_path_with_handler(self, ClientMock=None):
        ClientMock.return_value = client_mock = MagicMock()
        client_mock.get_bucket.return_value = bucket_mock = MagicMock()

        finding_result = finding_as_protobuf

        def handler(finding_result):
            return "/".join(finding_result.finding.name.split("/")[-4:])

        save_in_gcs_bucket(finding_result, store_path_handler=handler)

        bucket_mock.blob.assert_called_once_with(
            "sources/14882874427929637851/findings/0f6d1815f292ff068946c40ca0d579c8"
        )

    @patch.dict(
        "premedy.resources.findings.os.environ",
        {"BUCKET_NAME": "my-bucket", "BUCKET_PROJECT": "my-project"},
    )
    @patch("premedy.resources.findings.storage.Client")
    def test_save_in_gcs_bucket_default_path(self, ClientMock=None):
        ClientMock.return_value = client_mock = MagicMock()
        client_mock.get_bucket.return_value = bucket_mock = MagicMock()

        finding_result = finding_as_protobuf

        save_in_gcs_bucket(finding_result)

        bucket_mock.blob.assert_called_once_with(
            "findings/categories/BUCKET_LOGGING_DISABLED/0f6d1815f292ff068946c40ca0d579c8"
        )

    @patch.dict(
        "premedy.resources.findings.os.environ",
        {"BUCKET_NAME": "my-bucket", "BUCKET_PROJECT": "my-project"},
    )
    @patch("premedy.resources.findings.storage.Client")
    def test_save_in_gcs_bucket_store_path_none(self, ClientMock=None):
        ClientMock.return_value = client_mock = MagicMock()
        client_mock.get_bucket.return_value = bucket_mock = MagicMock()

        finding_result = finding_as_protobuf

        save_in_gcs_bucket(finding_result, store_path_handler=lambda _: None)

        bucket_mock.blob.assert_not_called()
