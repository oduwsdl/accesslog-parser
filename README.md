# AccessLog Parser and CLI

Web server access log parser and CLI tool with added features for web archive replay logs.

## Input Parsing

TODO

## Record Filtering

TODO

## Output Formatting

TODO

## CLI Reference

```
$ accesslog -h
usage: accesslog [options] [FILES ...]

A tool to parse Common Log formatted access logs with various derived fields.

positional arguments:
  files                 Log files (plain/gz/bz2) to parse (reads from the STDIN, if empty or '-')

optional arguments:
  -h, --help            Show this help message and exit
  -v, --version         Show version number and exit
  -d, --debug           Show debug messages on STDERR
  -e FIELDS, --nonempty FIELDS
                        Skip record if any of the provided fields is empty (comma separated list)
  -i FIELDS, --valid FIELDS
                        Skip record if any of the provided field values are invalid
                        ('all' or comma separated list from 'host,request,status,size,referrer')
  -m FIELD~RegExp, --match FIELD~RegExp
                        Skip record if field does not match the RegExp (can be used multiple times)
  -t TFORMAT, --origtime TFORMAT
                        Original datetime format of logs (default: '%d/%b/%Y:%H:%M:%S %z')
  -f FORMAT, --format FORMAT
                        Output format string (see available formatting fields below)
  -j FIELDS, --json FIELDS
                        Output NDJSON with the provided fields (use 'all' for all fields except 'origline')

formatting fields:
  {origline}            Original log line
  {host}                IP address of the client
  {identity}            Identity of the client, usually '-'
  {user}                User ID for authentication, usually '-'
  {origtime}            Original date and time (typically in '%d/%b/%Y:%H:%M:%S %z' format)
  {epoch}               Seconds from the Unix epoch (derived from origtime)
  {date}                UTC date in '%Y-%m-%d' format (derived from origtime)
  {time}                UTC time in '%H:%M:%S' format (derived from origtime)
  {datetime}            14 digit datetime in '%Y%m%d%H%M%S' format (derived from origtime)
  {request}             Original HTTP request line
  {method}              HTTP method (empty for invalid request)
  {path}                Path and query (scheme and host removed, empty for invalid request)
  {prefix}              Memento endpoint path prefix (derived from path)
  {mtime}               14 digit Memento datetime (derived from path)
  {rflag}               Memento rewrite flag (derived from path)
  {urir}                Memento URI-R (derived from path)
  {httpv}               HTTP version (empty for invalid request)
  {status}              Returned status code
  {size}                Number of bytes returned
  {referrer}            Referer header (empty, if not logged)
  {agent}               User-agent header (empty, if not logged)
  {extras}              Any additional logged fields
Default FORMAT: '{host} {date} {time} {method} {path} {status} {size} "{referrer}" "{agent}"'
```
