import unittest
import os
import json
from redact.redactor import Redactor
from redact.unredactor import Unredactor

class TestUnredactor(unittest.TestCase):
    def setUp(self):
        self.config_file = "test_config.json"
        self.create_test_config()

        self.redactor = Redactor(self.config_file)
        self.unredactor = Unredactor("test_dict.json")

    def create_test_config(self):
        config_data = {
            "substrings": ["SensitiveData", "private"]
        }
        with open(self.config_file, "w") as f:
            f.write(json.dumps(config_data))

    def test_unredact_file(self):
        # Create a sample input file
        with open("test_input.txt", "w") as f:
            f.write("Hello, world! SensitiveData\n")
            f.write("This is a private message.\n")
            f.write("SensitiveData should be redacted.\n")
            f.write("The word private should also be redacted.")

        # Redact the input file
        self.redactor.redact_file("test_input.txt", "test_dict.json")

        # Unredact the redacted file
        self.unredactor.unredact_file("test_input_redacted.txt")

        # Check if the output file exists
        self.assertTrue(os.path.exists("test_input_redacted_unredacted.txt"))

        # Clean up test files
        os.remove("test_input.txt")
        os.remove("test_input_redacted.txt")
        os.remove("test_input_redacted_unredacted.txt")
        os.remove("test_dict.json")
        os.remove(self.config_file)

if __name__ == "__main__":
    unittest.main()
