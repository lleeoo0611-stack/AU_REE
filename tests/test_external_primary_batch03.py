"""Offline integrity regression for source-scoped external primary Batch 03."""
import unittest
from scripts.check_external_primary_batch03 import validate

class ExternalPrimaryBatch03Test(unittest.TestCase):
    def test_frozen_source_and_no_unapproved_promotion(self):
        self.assertTrue(validate())

if __name__ == "__main__":
    unittest.main()
