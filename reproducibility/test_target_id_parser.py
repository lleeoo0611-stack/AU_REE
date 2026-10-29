import unittest
from quality_gate_487 import split_target_ids
class TargetParserTests(unittest.TestCase):
    def test_mixed_delimiters_and_crlf(self):
        self.assertEqual(split_target_ids(" LEGACY:abc | E1:C-def; E1:C-ghi\r\nLEGACY:jkl "), ["LEGACY:abc","E1:C-def","E1:C-ghi","LEGACY:jkl"])
    def test_empty(self):
        self.assertEqual(split_target_ids(None), [])
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): split_target_ids("E1:C-a | E1:C-a")
    def test_malformed_rejected(self):
        for value in ["E1:C-a,E1:C-b", "junk", "LEGACY:"]:
            with self.assertRaises(ValueError): split_target_ids(value)
if __name__ == "__main__": unittest.main()

