#!/usr/bin/env python3

import argparse
import fileinput
import json
import os
import re
import sys

from commonlog import parser


origtime_format = "%d/%b/%Y:%H:%M:%S %z"
output_format = '{host} {date} {time} {method} {path} {status} {size} "{referrer}" "{agent}"'
icount = ocount = 0


def print_fields():
    lines = ["formatting fields:"]
    for fld, desc in parser.fields.items():
        fld = f"{{{fld}}}"
        lines.append(f"  {fld:21} {desc}")
    lines.append(f"Default FORMAT: '{output_format}'")
    return "\n".join(lines)


def print_summary(**kw):
    print(f"PROCESSED: {icount}, PRODUCED: {ocount}, SKIPPED: {icount - ocount}", **kw)


def string_output(record, template, **kw):
    print(template.format_map({k: v or "-" for k, v in record.items()}), **kw)


def json_output(record, template, **kw):
    print(json.dumps({fld: record[fld] for fld in template}), **kw)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage="%(prog)s [options] [FILES ...]", description="A tool to parse Common Log formatted access logs with various derived fields.", epilog=print_fields(), formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("-d", "--debug", action="store_true", help="Show debug messages on STDERR")
    ap.add_argument("-n", "--non-empty-fields", metavar="FIELDS", default=[], type=lambda flds: [f.strip() for f in flds.split(",") if f], help="Skip record if any of the provided fields is empty (comma separated list)")
    ap.add_argument("-v", "--validate-fields", metavar="FIELDS", default=[], type=lambda flds: [f.strip() for f in flds.split(",") if f], help=f"Skip record if any of the provided field values are invalid\n('all' or comma separated list from '{','.join(parser.validators.keys())}')")
    ap.add_argument("-m", "--match-field", metavar="FIELD~RegExp", default=[], action="append", help="Skip record if field does not match the RegExp (can be used multiple times)")
    ap.add_argument("-t", "--origtime-format", metavar="TFORMAT", default=origtime_format, help=f"Original datetime format of logs (default: '{origtime_format.replace('%', '%%')}')")
    ap.add_argument("-f", "--format", default=output_format, help="Output format string (see available formatting fields below)")
    ap.add_argument("-j", "--json", metavar="JFIELDS", default=[], type=lambda flds: [f.strip() for f in flds.split(",") if f], help="Output NDJSON with the provided fields (use 'all' for all fields except 'origline')")
    ap.add_argument("files", nargs="*", help="Log files (plain/gz/bz2) to parse (reads from the STDIN, if empty or '-')")
    args = ap.parse_args()

    debuglog = sys.stderr
    if not args.debug:
        debuglog = open(os.devnull, "w")

    field_matches = []
    for am in args.match_field:
        fm = am.split("~", 1)
        if len(fm) != 2 or fm[0] not in parser.fields.keys() or not fm[1]:
            sys.exit(f"'{am}' is not a valid field match option (use 'FIELD~RegEg' instead)")
        try:
            reg = re.compile(fm[1])
            field_matches.append((fm[0], reg))
        except Exception as e:
            sys.exit(f"'{fm[1]}' is not a valid Regular Expression")

    if args.validate_fields == ["all"]:
        args.validate_fields = parser.validators.keys()
    for vf in args.validate_fields:
        if vf not in parser.validators.keys():
            sys.exit(f"'{vf}' field does not have a builtin validation, only '{','.join(parser.validators.keys())}' do")

    output_formatter = lambda record, **kw: string_output(record, args.format.replace("\\t", "\t"), **kw)
    if args.json:
        if args.json == ["all"]:
            flds = list(parser.fields.keys())
            flds.remove("origline")
            args.json = flds
        output_formatter = lambda record, **kw: json_output(record, args.json, **kw)
    try:
        output_formatter({fld: "" for fld in parser.fields}, file=open(os.devnull, "w"))
    except KeyError as e:
        sys.exit(f"{e} is not a valid formatting field")
    except ValueError as e:
        sys.exit(e)

    try:
        for line in fileinput.input(files=args.files, mode="rb", openhook=fileinput.hook_compressed):
            if not icount % 1_000 and icount:
                print_summary(file=debuglog)
            try:
                icount += 1
                line = line.decode().strip()
                record = parser.parse(line, non_empty_fields=args.non_empty_fields, validate_fields=args.validate_fields, field_matches=field_matches, origtime_format=args.origtime_format)
                output_formatter(record)
                ocount += 1
            except Exception as e:
                print(f"SKIPPING [{e}]: {line}", file=debuglog)
        print_summary(file=debuglog)
    except (BrokenPipeError, KeyboardInterrupt) as e:
        print_summary(file=debuglog)
        sys.exit()
