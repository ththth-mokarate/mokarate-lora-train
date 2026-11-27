#!/usr/bin/env python3
"""Tiny file server for the LoRA training container.

- GET /ready always returns 200 (Salad readiness probe must pass from the
  moment the container starts, long before training finishes).
- Everything else serves the ai-toolkit output directory (train.log,
  checkpoint .safetensors files, sample images) with HTTP Range support
  so large files can be fetched in chunks through the Salad gateway.
"""
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

ROOT = "/app/ai-toolkit/output"
os.makedirs(ROOT, exist_ok=True)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/ready":
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        rel = path.lstrip("/")
        full = os.path.normpath(os.path.join(ROOT, rel))
        if not full.startswith(ROOT):
            self.send_error(403)
            return
        if os.path.isdir(full):
            entries = sorted(os.listdir(full))
            items = "".join(
                f'<li><a href="{e}">{e}</a> '
                f'({os.path.getsize(os.path.join(full, e))} bytes)</li>'
                for e in entries)
            body = f"<html><body><ul>{items}</ul></body></html>".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if not os.path.isfile(full):
            self.send_error(404)
            return
        size = os.path.getsize(full)
        range_hdr = self.headers.get("Range")
        start, end = 0, size - 1
        status = 200
        if range_hdr:
            m = re.match(r"bytes=(\d*)-(\d*)", range_hdr)
            if m:
                if m.group(1):
                    start = int(m.group(1))
                if m.group(2):
                    end = min(int(m.group(2)), size - 1)
                status = 206
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(full, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 3000), Handler).serve_forever()
