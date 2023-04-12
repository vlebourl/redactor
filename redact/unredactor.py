import json
import mmap
import os
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
            loaded_dict = json.load(f)
        # Reverse the dictionary
        self.replacement_dict = {v: k for k, v in loaded_dict.items()}
        patterns = [regex.escape(key) for key in self.replacement_dict]
        self.pattern = regex.compile("|".join(patterns), regex.IGNORECASE)

    def unredact_file(self, file_path):
        if not self.replacement_dict:
            print("Replacement dictionary is empty.")
            return

        output_file = self._create_output_file_name(file_path)
        with open(file_path, "r+b") as f_in, open(output_file, "w+b") as f_out:
            # Memory-map the input file
            with mmap.mmap(f_in.fileno(), 0, access=mmap.ACCESS_READ) as self.mm:
                chunks = self._split_chunks(self.mm)
                with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                    for chunk_idx, chunk in enumerate(chunks):
                        executor.submit(self._unredact_chunk, chunk_idx, chunk, f_out)

    def _split_chunks(self, mm):
        chunks = []
        for i in range(0, mm.size(), self.chunk_size):
            start = i
            end = min(i + self.chunk_size, mm.size())

            # Find the nearest newline character to avoid splitting in the middle of a line
            while end < mm.size() and mm[end] != ord(b"\n"):
                end += 1

            chunks.append((start, end))

        return chunks

    def _unredact_chunk(self, chunk_idx, chunk, f_out):
        start, end = chunk
        chunk_data = self.mm[start:end].decode("utf-8")
        unredacted_chunk = self.pattern.sub(
            lambda m: self.replacement_dict[m.group(0)], chunk_data
        )

        # Ensure the output file is in binary mode
        f_out.seek(start)
        f_out.write(unredacted_chunk.encode("utf-8"))

    def _create_output_file_name(self, file_path):
        filename, extension = os.path.splitext(file_path)
        if not extension:
            extension = ".txt"
        if "_unredacted" in filename:
            filename = filename.replace("_unredacted", "")
        if "_redacted" in filename:
            filename = filename.replace("_redacted", "")
        return f"{filename}_unredacted{extension}"
