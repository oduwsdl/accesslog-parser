import re
import time


fields = {
    "origline": "Original log line",
    "host": "IP address of the client",
    "identity": "Identity of the client, usually '-'",
    "user": "User ID for authentication, usually '-'",
    "origtime": "Original date and time (typically in '%d/%b/%Y:%H:%M:%S %z' format)",
    "epoch": "Seconds from the Unix epoch (derived from origtime)",
    "date": "UTC date in '%Y-%m-%d' format (derived from origtime)",
    "time": "UTC time in '%H:%M:%S' format (derived from origtime)",
    "datetime": "14 digit datetime in '%Y%m%d%H%M%S' format (derived from origtime)",
    "request": "Original HTTP request line",
    "method": "HTTP method (empty for invalid request)",
    "path": "Path and query (scheme and host removed, empty for invalid request)",
    "prefix": "Memento endpoint path prefix (derived from path)",
    "mtime": "14 digit Memento datetime (derived from path)",
    "rflag": "Memento rewrite flag (derived from path)",
    "urir": "Memento URI-R (derived from path)",
    "httpv": "HTTP version (empty for invalid request)",
    "status": "Returned status code",
    "size": "Number of bytes returned",
    "referrer": "Referer header (empty, if not logged)",
    "agent": "User-agent header (empty, if not logged)",
    "extras": "Any additional logged fields"
}

matchers = {
    "clog": re.compile(r'^(?P<host>\S+)\s+(?P<identity>\S+)\s+(?P<user>\S+)\s+\[(?P<origtime>.+?)\]\s+"(?P<request>.*?)"\s+(?P<status>\S+)\s+(?P<size>\S+)(\s+"(?P<referrer>.*?)"\s+"(?P<agent>.*?)"\s*(?P<extras>.*?))?\s*$'),
    "hreq": re.compile(r'^(?P<method>[A-Z]+)\s+([hH][tT]{2}[pP][sS]?://[\w\-\.]+(:\d+)?)?(?P<path>\S+)\s+(?P<httpv>HTTP\/\d(\.\d)?)$'),
    "urim": re.compile(r'^(?P<prefix>[\w\-\/]*?\/)(?P<mtime>\d{14})((?P<rflag>[a-z]{2}_))?\/(?P<urir>\S+)$')
}

validators = {
    "host": re.compile(r'^((25[0-5]|(2[0-4]|1\d?|[2-9])?\d)(\.(25[0-5]|(2[0-4]|1\d?|[2-9])?\d)){3})|([\da-fA-F]{0,4}:){2,7}[\da-fA-F]{0,4}$'),
    "request": re.compile(r'^[A-Z]+\s+\S+\s+HTTP\/\d(\.\d)?$'),
    "status": re.compile(r'^[1-5]\d{2}$'),
    "size": re.compile(r'^\-|\d+$'),
    "referrer": re.compile(r'^(https?://[\w\-\.]+(:\d+)?(/(\S)*)?)?$', re.I)
}


def parse(line, non_empty_fields=[], validate_fields=[], field_matches=[], origtime_format="%d/%b/%Y:%H:%M:%S %z"):
    """
    Parse a single Common Log formatted line and return a dictionary with various original and derived fields.
    Raise exceptions for invalid records or when given filter conditions do not match.
    """

    m = matchers["clog"].match(line)
    if not m:
        raise ValueError("Malformed record")

    record = {fld: "" for fld in fields}
    record["origline"] = line
    record.update(m.groupdict(default=""))

    for fld in validate_fields:
        reg = validators.get(fld)
        val = record.get(fld, "")
        if reg and not reg.match(val):
            raise ValueError(f"Invalid field {fld}: {val}")

    try:
        et = time.mktime(time.strptime(record["origtime"], origtime_format))
        record["epoch"] = int(et)
        ut = time.gmtime(et)
        record["date"] = time.strftime("%Y-%m-%d", ut)
        record["time"] = time.strftime("%H:%M:%S", ut)
        record["datetime"] = time.strftime("%Y%m%d%H%M%S", ut)
    except Exception as e:
        raise ValueError(f"Invalid time: {record['origtime']}")

    m = matchers["hreq"].match(record["request"])
    if m:
        record.update(m.groupdict(default=""))

    m = matchers["urim"].match(record["path"])
    if m:
        record.update(m.groupdict(default=""))

    for fld in non_empty_fields:
        if record.get(fld, "") in ["", "-"]:
            raise ValueError(f"Empty field: {fld}")

    for (fld, reg) in field_matches:
        val = record.get(fld, "")
        m = reg.search(val)
        if not m:
            raise ValueError(f"Mismatch field {fld}: {val}")

    return record
