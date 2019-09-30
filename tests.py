#!/usr/bin/env python3

import sys

from commonlog.clparser import CLParser


valid_logs = [{
    'origline': '68.10.168.183 - - [16/Jan/2012:18:18:30 -0400] "GET /~mln/ HTTP/1.1" 200 5336',
    'host': '68.10.168.183',
    'identity': '-',
    'user': '-',
    'origtime': '16/Jan/2012:18:18:30 -0400',
    'epoch': 1326752310,
    'date': '2012-01-16',
    'time': '22:18:30',
    'datetime': '20120116221830',
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
    'epoch': 1325894462,
    'date': '2012-01-07',
    'time': '00:01:02',
    'datetime': '20120107000102',
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
    'epoch': 971211336,
    'date': '2000-10-10',
    'time': '20:55:36',
    'datetime': '20001010205536',
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
            print(f"  Field '{k}' => Expected: '\033[92m{e}\033[0m', Returned: '\033[91m{r}\033[0m'")


def print_result(msg=""):
    if msg:
        print(f"\033[91m[FAILED]\033[0m: {msg}")
    else:
        print("\033[92m[PASSED]\033[0m")


if __name__ == "__main__":
    failures = 0
    clp = CLParser()
    for log in valid_logs:
        try:
            record = clp.parse(log['origline'])
            assert record == log
            print_result()
        except AssertionError as e:
            failures += 1
            print_result(log['origline'])
            print_diff(log, record)

    for log in invalid_logs:
        try:
            clp.parse(log)
            failures += 1
            print_result(log)
            print("  Expected: ValueError")
        except ValueError as e:
            print_result()

    if failures:
        sys.exit(f"{failures} failures!")
    print("All passed!")
