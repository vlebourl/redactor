import argparse

from unredactor import Unredactor

from redactor import Redactor


def main():
    """Redacts or unredacts files based on command-line arguments."""
    parser = argparse.ArgumentParser(description="Redact and unredact files.")
    parser.add_argument(
        "action",
        choices=["redact", "unredact"],
        type=str,
        help="Specify whether to redact or unredact the file.",
    )
    parser.add_argument(
        "input_file", type=str, help="The input file to redact or unredact."
    )
    parser.add_argument(
        "-c",
        "--config_file",
        type=str,
        default="config.json",
        help="The configuration file for redaction (default: config.json).",
    )
    parser.add_argument(
        "-d",
        "--dict_location",
        type=str,
        default=None,
        help="The location of the encrypted dictionary (default: None).",
    )

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            if args.action == "redact":
                redactor = Redactor(args.config_file)
                redactor.redact_file(f, args.dict_location)
            elif args.action == "unredact":
                unredactor = Unredactor(args.dict_location)
                unredactor.unredact_file(f)
    except FileNotFoundError:
        print(f"File not found: {args.input_file}")
    except PermissionError:
        print(f"Permission denied: {args.input_file}")


if __name__ == "__main__":
    main()
