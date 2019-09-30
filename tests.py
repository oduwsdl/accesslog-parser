#!/usr/bin/env python3

import sys

from commonlog import parser


valid_logs = [{
    'origline': '68.10.168.183 - - [16/Jan/2012:18:18:30 -0400] "GET /~mln/ HTTP/1.1" 200 5336',
    'host': '68.10.168.183',
    'identity': '-',
    'user': '-',
    'origtime': '16/Jan/2012:18:18:30 -0400',
    'epoch': 1326755910,
    'date': '2012-01-16',
    'time': '23:18:30',
    'datetime': '20120116231830',
    'request': 'GET /~mln/ HTTP/1.1',
    'method': 'GET',
    'path': '/~mln/',
    'prefix': '',
    'mtime': '',
    'rflag': '',
    'urir': '',
    'httpv': 'HTTP/1.1',
    'status': '200',
    'size': '5336',
    'referrer': '',
    'agent': '',
    'extras': ''
}, {
    'origline': '0.113.134.112 - - [07/Jan/2012:00:01:02 +0000] "GET http://web.archive.org/web/20100926071739im_/http://example.com/img/logo.jpg HTTP/1.1" 302 0 "http://web.archive.org/web/20100926071739/http://example.com/" "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"',
    'host': '0.113.134.112',
    'identity': '-',
    'user': '-',
    'origtime': '07/Jan/2012:00:01:02 +0000',
    'epoch': 1325912462,
    'date': '2012-01-07',
    'time': '05:01:02',
    'datetime': '20120107050102',
    'request': 'GET http://web.archive.org/web/20100926071739im_/http://example.com/img/logo.jpg HTTP/1.1',
    'method': 'GET',
    'path': '/web/20100926071739im_/http://example.com/img/logo.jpg',
    'prefix': '/web/',
    'mtime': '20100926071739',
    'rflag': 'im_',
    'urir': 'http://example.com/img/logo.jpg',
    'httpv': 'HTTP/1.1',
    'status': '302',
    'size': '0',
    'referrer': 'http://web.archive.org/web/20100926071739/http://example.com/',
    'agent': 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7',
    'extras': ''
}, {
    'origline': '127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326',
    'host': '127.0.0.1',
    'identity': 'user-identifier',
    'user': 'frank',
    'origtime': '10/Oct/2000:13:55:36 -0700',
    'epoch': 971200536,
    'date': '2000-10-10',
    'time': '17:55:36',
    'datetime': '20001010175536',
    'request': 'GET /apache_pb.gif HTTP/1.0',
    'method': 'GET',
    'path': '/apache_pb.gif',
    'prefix': '',
    'mtime': '',
    'rflag': '',
    'urir': '',
    'httpv': 'HTTP/1.0',
    'status': '200',
    'size': '2326',
    'referrer': '',
    'agent': '',
    'extras': ''
}]

invalid_logs = [
    "",
    "Hello World!",
    "The quick brown fox jumps over the lazy dog"
]


def print_diff(expected, returned):
    # TODO: Check for keys that are present in one, but not in the other
    for k in expected:
        e = expected.get(k, "")
        r = returned.get(k, "")
        if e != r:
            print(f"  Field '{k}' => Expected: '{e}', Returned: '{r}'")


if __name__ == "__main__":
    failures = 0
    for log in valid_logs:
        try:
            record = parser.parse(log['origline'])
            assert record == log
            print("[PASSED]")
        except AssertionError as e:
            failures += 1
            print(f"[FAILED]: {log['origline']}")
            print_diff(log, record)

    for log in invalid_logs:
        try:
            parser.parse(log)
            failures += 1
            print(f"[FAILED]: {log}")
            print("  Expected: ValueError")
        except ValueError as e:
            print("[PASSED]")

    if failures:
        sys.exit(f"{failures} failures!")
    print("All passed!")
