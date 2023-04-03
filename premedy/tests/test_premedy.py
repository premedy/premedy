import unittest
from unittest.mock import MagicMock

from premedy.premedy import Premedy


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
