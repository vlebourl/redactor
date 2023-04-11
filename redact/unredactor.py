import os
import json

class Unredactor:
    def __init__(self, dict_location):
        with open(dict_location, "r") as f:
            self.replacement_dict = json.load(f)

    def unredact_file(self, input_file):
        with open(input_file, "r") as f:
            content = f.read()

        for original, replacement in self.replacement_dict.items():
            content = content.replace(replacement, original)

        output_file = self._create_output_file_name(input_file)
        with open(output_file, "w") as f:
            f.write(content)

    def _create_output_file_name(self, input_file):
        name, extension = os.path.splitext(input_file)
        return f"{name}_unredacted{extension}"
