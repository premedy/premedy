import unittest
from unittest.mock import MagicMock, patch

from premedy.premedy import (
    Premedy,
    path_handler_action_taken,
    path_handler_error_while_taking_action,
    path_handler_no_remediation_for_finding,
)


class TestPremedy(unittest.TestCase):
    def test_init(self):
        consume = MagicMock(return_value="consume")
        app = MagicMock()
        app.topic = MagicMock(return_value=consume)

        topic = "topic"
        project = "project"
        path = "./premedy/tests/mocks/remediations"

        premedy = Premedy(app, topic, project, path)

        self.assertEqual(premedy.app, app)
        self.assertEqual(premedy.topic, "topic")
        self.assertEqual(premedy.project, "project")
        self.assertEqual(premedy.use_subscription, True)
        self.assertEqual(
            premedy.remediation_classes[0].__name__, "RemediateDummyRemediation"
        )
        self.assertEqual(premedy.consume, "consume")

    @patch("premedy.premedy.findings.save_in_gcs_bucket")
    @patch("premedy.premedy.findings.parse_finding_result")
    def test_consume_handler(self, parse_finding_result_mock, save_in_gcs_bucket_mock):
        app = MagicMock()
        topic = "topic"
        project = "project"
        path = "./premedy/tests/mocks/remediations"

        premedy = Premedy(app, topic, project, path)

        premedy.remediate = MagicMock()
        premedy.consume_handler("message")

        parse_finding_result_mock.assert_called_once_with(message="message")
        save_in_gcs_bucket_mock.assert_not_called()

    @patch("premedy.premedy.findings.save_in_gcs_bucket")
    def test_remediate_take_action(self, save_in_gcs_bucket):
        app = MagicMock()
        topic = "topic"
        project = "project"
        path = "./premedy/tests/mocks/remediations"
        premedy = Premedy(app, topic, project, path)

        instance_take_action = MagicMock()
        instance_take_action.should_take_action.return_value = True
        instance_take_action.remediate.return_value = None

        TakeAction = MagicMock(return_value=instance_take_action)

        premedy.remediation_classes = [TakeAction]

        # asserts
        self.assertEqual(instance_take_action.should_take_action(), True)
        self.assertEqual(instance_take_action.remediate(), None)

        finding_result = "finding_result"
        premedy.remediate(finding_result)
        save_in_gcs_bucket.assert_called_once_with(
            finding_result=finding_result, store_path_handler=path_handler_action_taken
        )

    @patch("premedy.premedy.findings.save_in_gcs_bucket")
    def test_remediate_dont_take_action(self, save_in_gcs_bucket):
        app = MagicMock()
        topic = "topic"
        project = "project"
        path = "./premedy/tests/mocks/remediations"
        premedy = Premedy(app, topic, project, path)

        instance_take_action = MagicMock()
        instance_take_action.should_take_action.return_value = False
        instance_take_action.remediate.return_value = None

        TakeAction = MagicMock(return_value=instance_take_action)

        premedy.remediation_classes = [TakeAction]

        # asserts
        self.assertEqual(instance_take_action.should_take_action(), False)
        self.assertEqual(instance_take_action.remediate(), None)

        finding_result = "finding_result"
        premedy.remediate(finding_result)
        save_in_gcs_bucket.assert_called_once_with(
            finding_result=finding_result,
            store_path_handler=path_handler_no_remediation_for_finding,
        )

    @patch("premedy.premedy.findings.save_in_gcs_bucket")
    def test_remediate_dont_take_action_because_of_error(self, save_in_gcs_bucket):
        app = MagicMock()
        topic = "topic"
        project = "project"
        path = "./premedy/tests/mocks/remediations"
        premedy = Premedy(app, topic, project, path)

        instance_take_action = MagicMock()
        instance_take_action.should_take_action.return_value = True
        instance_take_action.remediate = MagicMock()
        instance_take_action.remediate.side_effect = Exception("oops!")

        TakeAction = MagicMock(return_value=instance_take_action)

        premedy.remediation_classes = [TakeAction]

        # asserts
        self.assertEqual(instance_take_action.should_take_action(), True)

        with self.assertRaises(Exception):
            instance_take_action.remediate()

        premedy.remediate("finding")
        save_in_gcs_bucket.assert_called_once_with(
            finding_result="finding",
            store_path_handler=path_handler_error_while_taking_action,
        )

    @patch("premedy.premedy.findings.save_in_gcs_bucket")
    def test_remediate_saves_finding_when_no_remediation_classes(
        self, save_in_gcs_bucket
    ):
        app = MagicMock()
        topic = "topic"
        project = "project"
        path = "./premedy/tests/mocks/remediations"
        premedy = Premedy(app, topic, project, path)

        instance_take_action = MagicMock()
        instance_take_action.should_take_action.return_value = True
        instance_take_action.remediate = MagicMock()
        instance_take_action.remediate.side_effect = Exception("oops!")

        premedy.remediation_classes = []

        # asserts
        self.assertEqual(instance_take_action.should_take_action(), True)

        with self.assertRaises(Exception):
            instance_take_action.remediate()

        premedy.remediate("finding")
        save_in_gcs_bucket.assert_called_once_with(
            finding_result="finding",
            store_path_handler=path_handler_no_remediation_for_finding,
        )
