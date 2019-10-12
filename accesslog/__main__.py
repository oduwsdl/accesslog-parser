#!/usr/bin/env python3

import argparse
import fileinput
import json
import os
import re
import sys

if not __package__:
    sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from accesslog import __VERSION__
from accesslog.clparser import CLParser


origtime_format = "%d/%b/%Y:%H:%M:%S %z"
output_format = '{host} {date} {time} {method} {path} {status} {size} "{referrer}" "{agent}"'
counts = {"input": 0, "output": 0}


def argument_parser():
    ap = argparse.ArgumentParser(usage="accesslog [options] [FILES ...]", description="A tool to parse Common Log formatted access logs with various derived fields.", epilog=print_fields(), add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    ap.add_argument("-v", "--version", action="version", version=f"accesslog {__VERSION__}", help="Show version number and exit")
    ap.add_argument("-d", "--debug", action="store_true", help="Show debug messages on STDERR")
    ap.add_argument("-e", "--nonempty", metavar="FIELDS", default=[], type=lambda flds: [f.strip() for f in flds.split(",") if f], help="Skip record if any of the provided fields is empty (comma separated list)")
    ap.add_argument("-i", "--valid", metavar="FIELDS", default=[], type=lambda flds: [f.strip() for f in flds.split(",") if f], help=f"Skip record if any of the provided field values are invalid\n('all' or comma separated list from '{','.join(CLParser.validators.keys())}')")
    ap.add_argument("-m", "--match", metavar="FIELD~RegExp", default=[], action="append", help="Skip record if field does not match the RegExp (can be used multiple times)")
    ap.add_argument("-t", "--origtime", metavar="TFORMAT", default=origtime_format, help=f"Original datetime format of logs (default: '{origtime_format.replace('%', '%%')}')")
    ap.add_argument("-f", "--format", default=output_format, help="Output format string (see available formatting fields below)")
    ap.add_argument("-j", "--json", metavar="FIELDS", default=[], type=lambda flds: [f.strip() for f in flds.split(",") if f], help="Output NDJSON with the provided fields (use 'all' for all fields except 'origline')")
    ap.add_argument("files", nargs="*", help="Log files (plain/gz/bz2) to parse (reads from the STDIN, if empty or '-')")
    return ap


def print_fields():
    lines = ["formatting fields:"]
    for fld, desc in CLParser.fields.items():
        fld = f"{{{fld}}}"
        lines.append(f"  {fld:21} {desc}")
    lines.append(f"Default FORMAT: '{output_format}'")
    return "\n".join(lines)


def print_summary(**kw):
    print(f"PROCESSED: {counts['input']}, PRODUCED: {counts['output']}, SKIPPED: {counts['input'] - counts['output']}", **kw)


def string_output(record, template, **kw):
    print(template.format_map({k: v or "-" for k, v in record.items()}), **kw)


def json_output(record, template, **kw):
    print(json.dumps({fld: record[fld] for fld in template}), **kw)


def main():
    args = argument_parser().parse_args()

    debuglog = sys.stderr
    if not args.debug:
        debuglog = open(os.devnull, "w")

    output_formatter = lambda record, **kw: string_output(record, args.format.replace("\\t", "\t"), **kw)
    if args.json:
        if args.json == ["all"]:
            flds = list(CLParser.fields.keys())
            flds.remove("origline")
            args.json = flds
        output_formatter = lambda record, **kw: json_output(record, args.json, **kw)
    try:
        output_formatter({fld: "" for fld in CLParser.fields}, file=open(os.devnull, "w"))
    except KeyError as e:
        sys.exit(f"{e} is not a valid formatting field")
    except ValueError as e:
        sys.exit(e)

    if args.valid == ["all"]:
        args.valid = CLParser.validators.keys()

    try:
        clp = CLParser(origtime_format=args.origtime, non_empty_fields=args.nonempty, validate_fields=args.valid, field_matchers=args.match)
    except ValueError as e:
        sys.exit(e)

    try:
        for line in fileinput.input(files=args.files, mode="rb", openhook=fileinput.hook_compressed):
            if not counts["input"] % 1_000 and counts["input"]:
                print_summary(file=debuglog)
            try:
                counts["input"] += 1
                line = line.decode().strip()
                record = clp.parse(line)
                output_formatter(record)
                counts["output"] += 1
            except ValueError as e:
                print(f"SKIPPING [{e}]: {line}", file=debuglog)
        print_summary(file=debuglog)
    except (BrokenPipeError, KeyboardInterrupt) as e:
        print_summary(file=debuglog)
        sys.exit()


if __name__ == "__main__":
    main()
