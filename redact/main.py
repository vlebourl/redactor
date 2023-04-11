import argparse
from redactor import Redactor
from unredactor import Unredactor

def main():
    parser = argparse.ArgumentParser(description="Redact and unredact files.")
    parser.add_argument("action", choices=["redact", "unredact"], help="Specify whether to redact or unredact the file.")
    parser.add_argument("input_file", help="The input file to redact or unredact.")
    parser.add_argument("-c", "--config_file", default="config.json", help="The configuration file for redaction (default: config.json).")
    parser.add_argument("-d", "--dict_location", default=None, help="The location of the encrypted dictionary (default: None).")

    args = parser.parse_args()

    if args.action == "redact":
        redactor = Redactor(args.config_file)
        redactor.redact_file(args.input_file, args.dict_location)
    elif args.action == "unredact":
        unredactor = Unredactor(args.dict_location)
        unredactor.unredact_file(args.input_file)

if __name__ == "__main__":
    main()
