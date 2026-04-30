#!/usr/bin/env python3
"""后端启动脚本 - 解决 proxy headers 问题"""
import uvicorn
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8000,
    proxy_headers=True,
    forwarded_allow_ips="*",
)
