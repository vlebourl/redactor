import concurrent.futures
import json
import mmap
import random
import string
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import regex


class RedactorError(Exception):
    pass


class RedactorFileNotFoundError(RedactorError):
    pass


class RedactorPermissionError(RedactorError):
    pass


class RedactorValueError(RedactorError):
    pass


class RedactorTypeError(RedactorError):
    pass


class RedactorConfig:
    def __init__(self, config_file_path: str):
        if not config_file_path:
            raise RedactorValueError(
                "config_file_path argument is required but not provided"
            )

        with open(config_file_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        if "substrings" not in self.config:
            raise RedactorValueError(
                "Missing required key 'substrings' in configuration file"
            )

        if not isinstance(self.config["substrings"], list):
            raise RedactorTypeError(
                "Value of key 'substrings' must be a list in configuration file"
            )

        self.case_insensitive_substrings = [
            regex.compile(regex.escape(substring), regex.IGNORECASE)
            for substring in self.config["substrings"]
        ]


class Redactor:
    def __init__(
        self, config_file_path: str, chunk_size: int = 64 * 1024, num_threads: int = 1
    ):
        self.config = RedactorConfig(config_file_path)
        self.chunk_size = chunk_size
        self.num_threads = num_threads

    def generate_random_string(
        self, length: int, replacement_dict: Dict[str, str]
    ) -> str:
        # while the generated string is already in the replacement dictionary's values, generate a new one
        # else return the generated string
        while True:
            rstring = "".join(
                random.choices(string.ascii_letters + string.digits, k=length)
            )
            if rstring not in replacement_dict.values():
                return rstring
            length *= 2

    def redact_file(self, input_file: str, dict_location: Optional[str] = None) -> None:
        output_file = self._create_output_file_name(input_file)
        with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
            content = mmap.mmap(f_in.fileno(), 0, access=mmap.ACCESS_READ)
            chunks = self._split_chunks(content)
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                replacement_dicts = [
                    executor.submit(self._redact_chunk, chunk) for chunk in chunks
                ]
            for chunk_idx, future in enumerate(replacement_dicts):
                replacement_dict, chunk = future.result()
                f_out.seek(chunk_idx * self.chunk_size)
                f_out.write(chunk)

        if dict_location:
            self._save_replacement_dict(replacement_dicts, dict_location)
        else:
            self._save_replacement_dict(replacement_dicts, f"{output_file}.dict")

    def _split_chunks(self, data: mmap.mmap) -> List[mmap.mmap]:
        num_chunks = (len(data) + self.chunk_size - 1) // self.chunk_size
        return [
            data[i * self.chunk_size : (i + 1) * self.chunk_size]
            for i in range(num_chunks)
        ]

    def _redact_chunk(self, chunk: mmap.mmap) -> Tuple[Dict[str, str], bytes]:
        replacement_dict = {}
        chunk_text = chunk.decode("utf-8")

        patterns = [
            regex.escape(substring) for substring in self.config.config["substrings"]
        ]
        joint_pattern = regex.compile("|".join(patterns), regex.IGNORECASE)

        def replace_match(match):
            old = match.group(0)
            if old not in replacement_dict:
                random_string = self.generate_random_string(len(old), replacement_dict)
                replacement_dict[old] = random_string
            return replacement_dict[old]

        chunk_text = joint_pattern.sub(replace_match, chunk_text)
        return replacement_dict, chunk_text.encode("utf-8")

    def _create_output_file_name(self, file_path: str) -> str:
        filename = Path(file_path).stem
        extension = Path(file_path).suffix
        return f"{filename}_redacted{extension}"

    def _save_replacement_dict(
        self, replacement_dicts: List[concurrent.futures.Future], dict_location: str
    ) -> None:
        combined_dict = {}
        for future in replacement_dicts:
            combined_dict.update(future.result()[0])
        with open(dict_location, "w") as f:
            json.dump(combined_dict, f)
