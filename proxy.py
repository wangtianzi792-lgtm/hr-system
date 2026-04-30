#!/usr/bin/env python3
"""简单 API 代理：将 /api/* 请求转发到后端 8000，其他路径返回 index.html（SPA fallback）"""
import http.server
import socketserver
import urllib.request
import os

PORT = 8080
BACKEND = "http://localhost:8000"
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted", "dist")
INDEX_HTML = os.path.join(DIST_DIR, "index.html")


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api"):
            self.proxy("GET")
        else:
            # SPA fallback: 非 api 路径，检查文件是否存在，不存在则返回 index.html
            # 去掉查询参数
            path = self.path.split("?")[0]
            file_path = os.path.join(DIST_DIR, path.lstrip("/"))
            if os.path.isfile(file_path):
                super().do_GET()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                with open(INDEX_HTML, "rb") as f:
                    content = f.read()
                self.send_header("Content-Length", len(content))
                self.end_headers()
                self.wfile.write(content)

    def do_POST(self):
        if self.path.startswith("/api"):
            self.proxy("POST")
        else:
            super().do_GET()

    def do_PUT(self):
        if self.path.startswith("/api"):
            self.proxy("PUT")
        else:
            super().do_GET()

    def do_DELETE(self):
        if self.path.startswith("/api"):
            self.proxy("DELETE")
        else:
            super().do_GET()

    def proxy(self, method):
        url = BACKEND + self.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None

        headers = {}
        for k, v in self.headers.items():
            if k.lower() not in ("host", "content-length"):
                headers[k] = v

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(k, v)
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.URLError as e:
            self.send_error(502, str(e))

    def log_message(self, format, *args):
        pass


os.chdir(DIST_DIR)
with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
    print(f"代理启动: http://localhost:{PORT} -> {BACKEND}")
    httpd.serve_forever()
