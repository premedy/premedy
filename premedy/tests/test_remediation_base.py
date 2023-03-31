import unittest

from premedy.remediation_base import RemediationBase


class TestRemediationBase(unittest.TestCase):
    def test_ini_requires_to_be_executed_by_child_class(self):
        finding_result = None

        with self.assertRaises(Exception) as e:
            RemediationBase(finding_result)

        self.assertEqual(
            e.exception.args[0],
            "missing category: set a category in the child instance",
        )
