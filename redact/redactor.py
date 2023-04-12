import json
import os
import random
import string


class Redactor:
    def __init__(self, config_file):
        with open(config_file, "r") as f:
            self.config = json.load(f)

        if "substrings" not in self.config:
            raise ValueError("Missing required key 'substrings' in configuration file")

        if not isinstance(self.config["substrings"], list):
            raise TypeError(
                "Value of key 'substrings' must be a list in configuration file"
            )

    def redact_file(self, input_file, dict_location=None):
        try:
            with open(input_file, "r") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"File not found: {input_file}")
            return
        except PermissionError:
            print(f"Permission denied: {input_file}")
            return

        replacement_dict = {}
        for substring in self.config["substrings"]:
            for case_sensitive_substring in {
                substring,
                substring.lower(),
                substring.upper(),
            }:
                if case_sensitive_substring not in content:
                    continue

                random_string = self._generate_random_string(
                    len(case_sensitive_substring)
                )
                replacement_dict[case_sensitive_substring] = random_string
                content = content.replace(case_sensitive_substring, random_string)

        output_file = self._create_output_file_name(input_file)
        try:
            with open(output_file, "w") as f:
                f.write(content)
        except PermissionError:
            print(f"Permission denied: {output_file}")
            return

        if dict_location:
            try:
                with open(dict_location, "w") as f:
                    json.dump(replacement_dict, f)
            except PermissionError:
                print(f"Permission denied: {dict_location}")
                return

    def _generate_random_string(self, length):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def _create_output_file_name(self, input_file):
        name, extension = os.path.splitext(input_file)
        if not extension:
            extension = ".txt"
        return f"{name}_redacted{extension}"
