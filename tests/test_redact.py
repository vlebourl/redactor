import json
import os
import random
import string

from redact.redactor import Redactor
from redact.unredactor import Unredactor


def create_random_word(min_length=4, max_length=10):
    length = random.randint(min_length, max_length)
    return "".join(random.choices(string.ascii_lowercase, k=length))


def insert_substring_in_word(word, substring):
    index = random.randint(0, len(word))
    return word[:index] + substring + word[index:]


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

    # Generate sentences with random words and at least 5 substrings
    sentences = []
    for _ in range(10):
        random_words = [create_random_word() for _ in range(15)]
        substrings_sample = random.sample(substrings, 5)

        # Insert substrings into random words
        for substring in substrings_sample:
            word = random.choice(random_words)
            new_word = insert_substring_in_word(word, substring)
            random_words[random_words.index(word)] = new_word

        sentence = " ".join(random_words)
        sentences.append(sentence)

    # Save the test file
    with open("test.txt", "w") as f:
        for sentence in sentences:
            f.write(f"{sentence}\n")


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
        assert len(unredacted_text) > 0
        assert original_text == unredacted_text

    os.remove("config.json")
    os.remove("test.txt")
    os.remove("test_redacted.txt")
    os.remove("test_redacted.txt.dict")
    os.remove("test_unredacted.txt")
