import os
import json
import tempfile
from redact.redactor import Redactor
from redact.unredactor import Unredactor, DictionaryLoadError, NoDictionaryLocationError

def test_redactor_init_with_invalid_config_file():
    with pytest.raises(FileNotFoundError):
        redactor = Redactor("invalid_config_file.json")

def test_redactor_init_with_invalid_config_file_content():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, "invalid_config_file.json"), "w") as f:
            f.write("invalid content")
        with pytest.raises(ValueError):
            redactor = Redactor(os.path.join(tempdir, "invalid_config_file.json"))

def test_redactor_init_with_config_file_missing_substrings_key():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, "config_missing_substrings_key.json"), "w") as f:
            f.write(json.dumps({}))
        with pytest.raises(ValueError):
            redactor = Redactor(os.path.join(tempdir, "config_missing_substrings_key.json"))

def test_redactor_init_with_config_file_substrings_key_not_a_list():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, "config_substrings_key_not_a_list.json"), "w") as f:
            f.write(json.dumps({"substrings": "not a list"}))
        with pytest.raises(TypeError):
            redactor = Redactor(os.path.join(tempdir, "config_substrings_key_not_a_list.json"))

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

def test_redactor_redact_file_with_invalid_input_file():
    with tempfile.TemporaryDirectory() as tempdir:
        redactor = Redactor(os.path.join(tempdir, "config.json"))
        with pytest.raises(FileNotFoundError):
            redactor.redact_file(os.path.join(tempdir, "invalid_input_file.txt"))

def test_redactor_redact_file_with_permission_denied_input_file():
    with tempfile.TemporaryDirectory() as tempdir:
        redactor = Redactor(os.path.join(tempdir, "config.json"))
        with open(os.path.join(tempdir, "permission_denied_file.txt"), "w") as f:
            pass
        os.chmod(os.path.join(tempdir, "permission_denied_file.txt"), 0o222)
        with pytest.raises(PermissionError):
            redactor.redact_file(os.path.join(tempdir, "permission_denied_file.txt"))

def test_redactor_redact_file_with_invalid_dict_location():
    with tempfile.TemporaryDirectory() as tempdir:
        redactor = Redactor(os.path.join(tempdir, "config.json"))
        with open(os.path.join(tempdir, "test_file.txt"), "w") as f:
            pass
        with pytest.raises(PermissionError):
            redactor.redact_file(os.path.join(tempdir, "test_file.txt"), dict_location=os.path.join(tempdir, "invalid_dict_location/dict.json"))

def test_redactor_redact_file_with_valid_input_file_and_dict_location():
    with tempfile.TemporaryDirectory() as tempdir:
        redactor = Redactor(os.path.join(tempdir, "config.json"))
        with open(os.path.join(tempdir, "test_file.txt"), "w") as f:
            f.write("This is a test file with some test1 and test2 substrings that will be redacted.\n")
        redactor.redact_file(os.path.join(tempdir, "test_file.txt"), dict_location=os.path.join(tempdir, "dict.json"))
        with open(os.path.join(tempdir, "test_file_redacted.txt"), "r") as f:
            content = f.read()
        assert "test1" not in content
        assert "test2" not in content
        assert len(content) == len("This is a ****** file with some ***** and ***** substrings that will be redacted.\n")

def test_unredactor_init_with_invalid_dict_location():
    with pytest.raises(NoDictionaryLocationError):
        unredactor = Unredactor(dict_location="invalid_dict_location/dict.json")

def test_unredactor_init_with_invalid_dict_file_content():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, "invalid_dict.json"), "w") as f:
            f.write("invalid content")
        with pytest.raises(DictionaryLoadError):
            unredactor = Unredactor(dict_location=os.path.join(tempdir, "invalid_dict.json"))

def test_unredactor_unredact_file_with_invalid_input_file():
    with tempfile.TemporaryDirectory() as tempdir:
        unredactor = Unredactor(dict_location=os.path.join(tempdir, "dict.json"))
        with pytest.raises(FileNotFoundError):
            unredactor.unredact_file(os.path.join(tempdir, "invalid_input_file.txt"))

def test_unredactor_unredact_file_with_permission_denied_input_file():
    with tempfile.TemporaryDirectory() as tempdir:
        unredactor = Unredactor(dict_location=os.path.join(tempdir, "dict.json"))
        with open(os.path.join(tempdir, "permission_denied_file.txt"), "w") as f:
            pass
        os.chmod(os.path.join(tempdir, "permission_denied_file.txt"), 0o000)
        with pytest.raises(PermissionError):
            unredactor.unredact_file(os.path.join(tempdir, "permission_denied_file.txt"))

def test_unredactor_unredact_file_with_no_replacement_dictionary():
    with tempfile.TemporaryDirectory() as tempdir:
        unredactor = Unredactor()
        with open(os.path.join(tempdir, "test_file_redacted.txt"), "w") as f:
            f.write("This is a ****** file with some ***** and ***** substrings that will be redacted.\n")
        with pytest.raises(RuntimeError):
            unredactor.unredact_file(os.path.join(tempdir, "test_file_redacted.txt"))

def test_unredactor_unredact_file_with_valid_replacement_dictionary():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, "dict.json"), "w") as f:
            json.dump({"******": "test1", "*****": "test2"}, f)
        unredactor = Unredactor(dict_location=os.path.join(tempdir, "dict.json"))
        with open(os.path.join(tempdir, "test_file_redacted.txt"), "w") as f:
            f.write("test1 is a test 2\n")
        unredactor.unredact_file(os.path.join(tempdir, "test_file_redacted.txt"))
        with open(os.path.join(tempdir, "test_file_unredacted.txt"), "r") as f:
            content = f.read()
        assert content == "test1 is a test 2\n"


