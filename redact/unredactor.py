import json
import mmap
import os
import re
from concurrent.futures import ThreadPoolExecutor

import regex


class DictionaryLoadError(Exception):
    pass


class NoDictionaryLocationError(Exception):
    pass


class Unredactor:
    def __init__(self, dict_location=None, chunk_size=64 * 1024, num_threads=1):
        self.chunk_size = chunk_size
        self.num_threads = num_threads
        self.pattern = None
        self.replacement_dict = None
        if dict_location:
            self.load_dictionary(dict_location)

    def load_dictionary(self, dict_location):
        with open(dict_location, "r") as f:
            self.replacement_dict = json.load(f)
        patterns = [re.escape(key) for key in self.replacement_dict.keys()]
        self.pattern = regex.compile("|".join(patterns))

    def unredact_file(self, file_path):
        if not self.replacement_dict:
            print("Replacement dictionary is empty.")
            return

        output_file = self._create_output_file_name(file_path)
        with open(file_path, "r+b") as f_in, open(output_file, "w+b") as f_out:
            # Memory-map the input file
            with mmap.mmap(f_in.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                chunks = self._split_chunks(mm)
                with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                    for chunk_idx, chunk in enumerate(chunks):
                        executor.submit(self._unredact_chunk, chunk_idx, chunk, f_out)

    def _split_chunks(self, data):
        return [
            data[i : i + self.chunk_size] for i in range(0, len(data), self.chunk_size)
        ]

    def _unredact_chunk(self, chunk_idx, chunk, f_out):
        chunk = self.pattern.sub(lambda m: self.replacement_dict[m.group(0)], chunk)
        f_out.seek(chunk_idx * self.chunk_size)
        f_out.write(chunk)

    def _create_output_file_name(self, file_path):
        filename, extension = os.path.splitext(file_path)
        if not extension:
            extension = ".txt"
        if "_unredacted" in filename:
            filename = filename.replace("_unredacted", "")
        if "_redacted" in filename:
            filename = filename.replace("_redacted", "")
        return f"{filename}_unredacted{extension}"
