#!/usr/bin/env python3
"""Local preview server that correctly declares UTF-8 (python -m http.server doesn't)."""

import functools
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler


class UTF8Handler(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        mimetype = super().guess_type(path)
        base = mimetype[0] if isinstance(mimetype, tuple) else mimetype
        if base == "text/html":
            return "text/html; charset=utf-8"
        return mimetype


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8422
    directory = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    handler = functools.partial(UTF8Handler, directory=directory)
    HTTPServer(("", port), handler).serve_forever()
