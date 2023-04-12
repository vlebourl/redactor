import json
import mmap
import os
import re
from concurrent.futures import ThreadPoolExecutor

from regex import regex


class DictionaryLoadError(Exception):
    pass


class NoDictionaryLocationError(Exception):
    pass


class Unredactor:
    """
    Class to unredact a file using a dictionary of replacements.
    """

    def __init__(self, dict_location=None, chunk_size=64 * 1024, num_threads=1):
        """
        Initializes the Unredactor object.

        Args:
            dict_location (str): The location of the dictionary file.
            chunk_size (int): The size of the chunks to read the file in.
            num_threads (int): The number of threads to use for processing the file.
        """
        self.chunk_size = chunk_size
        self.num_threads = num_threads
        self.pattern = None
        self.replacement_dict = None
        if dict_location:
            self.load_dictionary(dict_location)

    def load_dictionary(self, dict_location):
        """
        Loads the replacement dictionary from the specified file.

        Args:
            dict_location (str): The location of the dictionary file.
        """
        with open(dict_location, "r") as f:
            self.replacement_dict = json.load(f)
        patterns = [re.escape(key) for key in self.replacement_dict.keys()]
        self.pattern = regex("|".join(patterns))

    def unredact_file(self, file_path):
        """
        Unredacts the specified file.

        Args:
            file_path (str): The location of the file to be unredacted.
        """
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
        """
        Splits the data into chunks of the specified size.

        Args:
            data (bytes): The data to be split.

        Returns:
            List[bytes]: The chunks of data.
        """
        return [
            data[i : i + self.chunk_size] for i in range(0, len(data), self.chunk_size)
        ]

    def _unredact_chunk(self, chunk_idx, chunk, f_out):
        """
        Unredacts a single chunk of data and writes it to the output file.

        Args:
            chunk_idx (int): The index of the chunk.
            chunk (bytes): The data to be unredacted.
            f_out (file object): The output file object.
        """
        chunk = self.pattern.sub(lambda m: self.replacement_dict[m.group(0)], chunk)
        f_out.seek(chunk_idx * self.chunk_size)
        f_out.write(chunk)

    def _create_output_file_name(self, file_path):
        """
        Creates a new output file name for the unredacted file.

        Args:
            file_path (str): The location of the file to be unredacted.

        Returns:
            str: The new file name.
        """
        filename, extension = os.path.splitext(file_path)
        if not extension:
            extension = ".txt"
        if "_unredacted" in filename:
            filename = filename.replace("_unredacted", "")
        if "_redacted" in filename:
            filename = filename.replace("_redacted", "")
        return f"{filename}_unredacted{extension}"
