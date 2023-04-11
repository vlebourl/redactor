import os
import json
import random
import string

class Redactor:
    def __init__(self, config_file):
        with open(config_file, "r") as f:
            self.config = json.load(f)

    def redact_file(self, input_file, dict_location=None):
        with open(input_file, "r") as f:
            content = f.read()

        replacement_dict = {}
        for substring in self.config["substrings"]:
            for case_sensitive_substring in {substring, substring.lower(), substring.upper()}:
                if case_sensitive_substring not in content:
                    continue

                random_string = self._generate_random_string(len(case_sensitive_substring))
                replacement_dict[case_sensitive_substring] = random_string
                content = content.replace(case_sensitive_substring, random_string)

        output_file = self._create_output_file_name(input_file)
        with open(output_file, "w") as f:
            f.write(content)

        if dict_location:
            with open(dict_location, "w") as f:
                json.dump(replacement_dict, f)

    def _generate_random_string(self, length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _create_output_file_name(self, input_file):
        name, extension = os.path.splitext(input_file)
        return f"{name}_redacted{extension}"
