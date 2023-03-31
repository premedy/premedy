import unittest
from unittest.mock import MagicMock

from premedy.premedy import Premedy
from premedy.tests.remediations.dummy_remediation import DummyRemediation


class TestPremedy(unittest.TestCase):
    def test_init(self):
        consume = MagicMock(return_value="consume")
        app = MagicMock()
        app.topic = MagicMock(return_value=consume)

        topic = "topic"
        project = "project"
        path = "./premedy/tests/remediations"

        premedy = Premedy(app, topic, project, path)

        self.assertEqual(premedy.app, app)
        self.assertEqual(premedy.topic, "topic")
        self.assertEqual(premedy.project, "project")
        self.assertEqual(premedy.use_subscription, True)
        self.assertEqual(premedy.remediation_classes[0].__name__, "DummyRemediation")
        self.assertEqual(premedy.consume, "consume")
