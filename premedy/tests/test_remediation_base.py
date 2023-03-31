import unittest

from premedy.remediation_base import RemediationBase


class TestRemediationBase(unittest.TestCase):
    def test_init_requires_to_be_executed_by_child_class(self):
        finding_result = None

        with self.assertRaises(Exception) as e:
            RemediationBase(finding_result)

        self.assertEqual(
            e.exception.args[0],
            "missing category: set a category in the child instance",
        )

    def test_init_with_child_class(self):
        finding_result = None

        class ChildRemediation(RemediationBase):
            category = "CATEGORY"

        remediation = ChildRemediation(finding_result)

        self.assertEqual(remediation.category, "CATEGORY")
