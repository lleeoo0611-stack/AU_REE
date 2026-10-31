"""Offline test for all-P2-P3-P4 Batch-04 evidence overlay."""
import unittest
from scripts.check_p234_all_sources_b04 import validate
class TestBatch04(unittest.TestCase):
    def test_full_339_join_and_no_promotion(self):
        self.assertTrue(validate())
if __name__=="__main__":
    unittest.main()
