import unittest
from redact_release_outputs import clean
class RedactionTests(unittest.TestCase):
    def test_query_and_whitespace(self):
        for space in ["", " ", "\n"]:
            value="https://example.invalid/doc?"+space+"access_token=dummy_credential&x=1"
            self.assertEqual(clean(value),"https://example.invalid/doc?x=1")
    def test_nested(self):
        self.assertNotIn("dummy_credential",str(clean({"context":["https://example.invalid/?token=dummy_credential"]})))
if __name__=='__main__': unittest.main()
