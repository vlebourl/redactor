# Redact App

Redact App is a Python package that provides an executable for redacting and unredacting files based on a given configuration file. It replaces case-sensitive occurrences of substrings with random strings, preserving the original case and generating separate random strings for different capitalizations.

## Installation

To install the Redact App, simply clone the repository and install the required dependencies:

```bash
git clone https://github.com/your_username/redact_app.git
cd redact_app
pip install -r requirements.txt
```

## Usage

The general syntax for using the Redact App is:

```bash
redact [-h] [-c CONFIG_FILE] [-d DICT_LOCATION] [-f] {redact,unredact} input_file
```

## Arguments:

```
{redact,unredact}: Specify whether to redact or unredact the file.
input_file: The input file to redact or unredact.
-h, --help: Show help message and exit.
-c CONFIG_FILE, --config_file CONFIG_FILE: The configuration file for redaction (default: config.json).
-d DICT_LOCATION, --dict_location DICT_LOCATION: The location of the encrypted dictionary (default: None).
```

## Examples

To redact a file:

```
redact redact input_file.sh
```

To unredact a file:

```
redact unredact input_file_redacted.sh
```

## Contributing

If you want to contribute to this project, please submit an issue or pull request on the GitHub repository.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
