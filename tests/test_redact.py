import json
import os
import tempfile

import pytest

from redact.redactor import Redactor
from redact.unredactor import DictionaryLoadError, NoDictionaryLocationError, Unredactor


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tempdir:
        yield tempdir


@pytest.fixture
def redactor(temp_dir):
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, "w") as f:
        f.write(json.dumps({"substrings": ["test1", "test2"]}))
    yield Redactor(config_path)


@pytest.fixture
def unredactor(temp_dir):
    dict_path = os.path.join(temp_dir, "dict.json")
    with open(dict_path, "w") as f:
        json.dump({"******": "test1", "*****": "test2"}, f)
    yield Unredactor(dict_location=dict_path)


def test_redactor_init_with_invalid_config_file():
    with pytest.raises(FileNotFoundError):
        Redactor("invalid_config_file.json")


def test_redactor_init_with_invalid_config_file_content(temp_dir):
    config_path = os.path.join(temp_dir, "invalid_config_file.json")
    with open(config_path, "w") as f:
        f.write("invalid content")
    with pytest.raises(ValueError):
        Redactor(config_path)


def test_redactor_init_with_config_file_missing_substrings_key(temp_dir):
    config_path = os.path.join(temp_dir, "config_missing_substrings_key.json")
    with open(config_path, "w") as f:
        f.write(json.dumps({}))
    with pytest.raises(ValueError):
        Redactor(config_path)


def test_redactor_init_with_config_file_substrings_key_not_a_list(temp_dir):
    config_path = os.path.join(temp_dir, "config_substrings_key_not_a_list.json")
    with open(config_path, "w") as f:
        f.write(json.dumps({"substrings": "not a list"}))
    with pytest.raises(TypeError):
        Redactor(config_path)


def test_redactor_generate_random_string():
    redactor = Redactor(None)
    random_string = redactor._generate_random_string(10)
    assert len(random_string) == 10


def test_redactor_create_output_file_name_without_extension():
    redactor = Redactor(None)
    output_file_name = redactor._create_output_file_name("test_file")
    assert output_file_name == "test_file_redacted.txt"


def test_redactor_create_output_file_name_with_extension():
    redactor = Redactor(None)
    output_file_name = redactor._create_output_file_name("test_file.txt")
    assert output_file_name == "test_file_redacted.txt"


def test_redactor_redact_file_with_invalid_input_file(temp_dir, redactor):
    with pytest.raises(FileNotFoundError):
        redactor.redact_file(os.path.join(temp_dir, "invalid_input_file.txt"))


def test_redactor_redact_file_with_permission_denied_input_file(temp_dir, redactor):
    with open(os.path.join(temp_dir, "permission_denied_file.txt"), "w"):
        pass
    os.chmod(os.path.join(temp_dir, "permission_denied_file.txt"), 0o222)
    with pytest.raises(PermissionError):
        redactor.redact_file(os.path.join(temp_dir, "permission_denied_file.txt"))


def test_redactor_redact_file_with_invalid_dict_location(temp_dir, redactor):
    with open(os.path.join(temp_dir, "test_file.txt"), "w"):
        pass
    with pytest.raises(PermissionError):
        redactor.redact_file(
            os.path.join(temp_dir, "test_file.txt"),
            dict_location=os.path.join(temp_dir, "invalid_dict_location/dict.json"),
        )


def test_redactor_redact_file_with_valid_input_file_and_dict_location(
    temp_dir, redactor
):
    with open(os.path.join(temp_dir, "test_file.txt"), "w") as f:
        f.write(
            "This is a test file with some test1 and test2 substrings that will be redacted.\n"
        )
    redactor.redact_file(
        os.path.join(temp_dir, "test_file.txt"),
        dict_location=os.path.join(temp_dir, "dict.json"),
    )
    with open(os.path.join(temp_dir, "test_file_redacted.txt"), "r") as f:
        content = f.read()
    assert "test1" not in content
    assert "test2" not in content
    assert len(content) == len(
        "This is a ****** file with some ***** and ***** substrings that will be redacted.\n"
    )


def test_unredactor_init_with_invalid_dict_location():
    with pytest.raises(NoDictionaryLocationError):
        Unredactor(dict_location="invalid_dict_location/dict.json")


def test_unredactor_init_with_invalid_dict_file_content(temp_dir):
    dict_path = os.path.join(temp_dir, "invalid_dict.json")
    with open(dict_path, "w") as f:
        f.write("invalid content")
    with pytest.raises(DictionaryLoadError):
        Unredactor(dict_location=dict_path)


def test_unredactor_unredact_file_with_invalid_input_file(temp_dir, unredactor):
    with pytest.raises(FileNotFoundError):
        unredactor.unredact_file(os.path.join(temp_dir, "invalid_input_file.txt"))


def test_unredactor_unredact_file_with_permission_denied_input_file(
    temp_dir, unredactor
):
    with open(os.path.join(temp_dir, "permission_denied_file.txt"), "w"):
        pass
    os.chmod(os.path.join(temp_dir, "permission_denied_file.txt"), 0o000)
    with pytest.raises(PermissionError):
        unredactor.unredact_file(os.path.join(temp_dir, "permission_denied_file.txt"))


def test_unredactor_unredact_file_with_no_replacement_dictionary(temp_dir, unredactor):
    with open(os.path.join(temp_dir, "test_file_redacted.txt"), "w") as f:
        f.write(
            "This is a ****** file with some ***** and ***** substrings that will be redacted.\n"
        )
    with pytest.raises(RuntimeError):
        unredactor.unredact_file(os.path.join(temp_dir, "test_file_redacted.txt"))


def test_unredactor_unredact_file_with_valid_replacement_dictionary(
    temp_dir, unredactor
):
    dict_path = os.path.join(temp_dir, "dict.json")
    with open(dict_path, "w") as f:
        json.dump({"******": "test1", "*****": "test2"}, f)
    with open(os.path.join(temp_dir, "test_file_redacted.txt"), "w") as f:
        f.write("test1 is a test 2\n")
    unredactor = Unredactor(dict_location=dict_path)
    unredactor.unredact_file(os.path.join(temp_dir, "test_file_redacted.txt"))
    with open(os.path.join(temp_dir, "test_file_unredacted.txt"), "r") as f:
        content = f.read()
    assert content == "test1 is a test 2\n"
