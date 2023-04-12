import json
import os
import random

import nltk
from nltk.corpus import brown

from redact.redactor import Redactor
from redact.unredactor import Unredactor

nltk.download("brown")


def create_config_file():
    substrings = [
        "test",
        "word",
        "example",
        "item",
        "data",
        "code",
        "substring",
        "text",
        "content",
        "value",
    ]
    config = {"substrings": substrings}
    with open("config.json", "w") as f:
        json.dump(config, f)


def create_test_file():
    substrings = [
        "test",
        "word",
        "example",
        "item",
        "data",
        "code",
        "substring",
        "text",
        "content",
        "value",
    ]
    words = [w.lower() for w in brown.words() if w.isalpha() and len(w) > 3]
    random.shuffle(words)
    selected_words = []
    for substring in substrings:
        for word in words:
            if substring in word:
                # Randomize the casing of the substring
                substr_len = len(substring)
                idx = word.lower().find(substring.lower())
                if idx >= 0:
                    selected_words.append(
                        word[:idx]
                        + word[idx : idx + substr_len].swapcase()
                        + word[idx + substr_len :]
                    )
                if len(selected_words) == 10:
                    break
        if len(selected_words) < 10:
            # If there are not enough words with the substring, select random words
            selected_words.extend(words[: 10 - len(selected_words)])

    words = selected_words
    random.shuffle(words)

    with open("test.txt", "w") as f:
        for i, word in enumerate(words):
            if i % 10 == 9:
                f.write(f"{word}\n")
            else:
                f.write(f"{word} ")

    with open("test.txt", "w") as f:
        for i, word in enumerate(words):
            if i % 10 == 9:
                f.write(f"{word}\n")
            else:
                f.write(f"{word} ")


def test_redactor_and_unredactor():
    create_config_file()
    create_test_file()

    redactor = Redactor("config.json")
    redactor.redact_file("test.txt")

    with open("config.json", "r") as f:
        config = json.load(f)
        substrings = config["substrings"]

    with open("test_redacted.txt", "r") as f:
        redacted_text = f.read().lower()
        for substring in substrings:
            assert substring.lower() not in redacted_text

    unredactor = Unredactor()
    unredactor.load_dictionary("test_redacted.txt.dict")
    unredactor.unredact_file("test_redacted.txt")

    with open("test.txt", "r") as f1, open("test_unredacted.txt", "r") as f2:
        original_text = f1.read()
        unredacted_text = f2.read()
        assert original_text == unredacted_text

    os.remove("config.json")
    os.remove("test.txt")
    os.remove("test_redacted.txt")
    os.remove("test_redacted.txt.dict")
    os.remove("test_unredacted.txt")
