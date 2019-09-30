import datetime
import re


class CLParser():
    """CLParser is a generic Common Log formatted log parser that has some additional features for Web archive replay logs"""

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

    extractors = {
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


    def __init__(self, **kw):
        """Initialize a CLParser instance with various parsing and filtering configurations."""

        self.origtime_format = "%d/%b/%Y:%H:%M:%S %z"
        self.non_empty_fields = []
        self.validate_fields = []
        self.field_matchers = []
        self.__dict__.update(kw)

        self.field_matcher_tuples = []
        for fm in self.field_matchers:
            fmt = fm.split("~", 1)
            if len(fmt) != 2 or not fmt[1]:
                raise ValueError(f"'{fm}' is not a valid field match option (use 'FIELD~RegEg' instead)")
            if fmt[0] not in CLParser.fields.keys():
                raise ValueError(f"'{fm[0]}' is not a valid field in '{fm}'")
            self.field_matcher_tuples.append((fmt[0], re.compile(fmt[1])))

        for nef in self.non_empty_fields:
            if nef not in CLParser.fields.keys():
                raise ValueError(f"'{nef}' is not a valid log field")

        for vf in self.validate_fields:
            if vf not in CLParser.validators.keys():
                raise ValueError(f"'{vf}' field does not have a builtin validation, only '{','.join(CLParser.validators.keys())}' do")


    def parse(self, line):
        """
        Parse a single Common Log formatted line and return a dictionary with various original and derived fields.
        Raise exceptions for invalid records or when given filter conditions do not match.
        """

        m = CLParser.extractors["clog"].match(line)
        if not m:
            raise ValueError("Malformed record")

        record = {fld: "" for fld in CLParser.fields}
        record["origline"] = line
        record.update(m.groupdict(default=""))

        for fld in self.validate_fields:
            reg = CLParser.validators.get(fld)
            val = record.get(fld, "")
            if reg and not reg.match(val):
                raise ValueError(f"Invalid field {fld}: {val}")

        try:
            ut = datetime.datetime.strptime(record["origtime"], self.origtime_format).astimezone(tz=datetime.timezone.utc)
            record["epoch"] = int(ut.timestamp())
            record["date"] = ut.strftime("%Y-%m-%d")
            record["time"] = ut.strftime("%H:%M:%S")
            record["datetime"] = ut.strftime("%Y%m%d%H%M%S")
        except ValueError as e:
            raise ValueError(f"Invalid time: '{record['origtime']}' not in '{self.origtime_format}' format")

        m = CLParser.extractors["hreq"].match(record["request"])
        if m:
            record.update(m.groupdict(default=""))

        m = CLParser.extractors["urim"].match(record["path"])
        if m:
            record.update(m.groupdict(default=""))

        for fld in self.non_empty_fields:
            if record.get(fld, "") in ["", "-"]:
                raise ValueError(f"Empty field: {fld}")

        for (fld, reg) in self.field_matcher_tuples:
            val = record.get(fld, "")
            m = reg.search(val)
            if not m:
                raise ValueError(f"Mismatch field {fld}: {val}")

        return record
