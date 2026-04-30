import sys
sys.path.insert(0, '.')
from app.core.config import settings
print(f"DATABASE_URL: {settings.DATABASE_URL}")

import os
print(f"Current dir: {os.getcwd()}")
print(f"DB path resolved: {os.path.abspath(settings.DATABASE_URL.replace('sqlite:///./', ''))}")

from app.core.database import engine
print(f"Engine URL: {engine.url}")
