"""
Root conftest — sets up sys.path for all test directories.
"""
import sys
import os

# Add service roots to path so `from app.X import Y` works from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services/ingest"))

# API service is only added when running api tests directly (avoids psycopg2 eager load issue)
# Run API tests from: cd services/api && python -m pytest tests/
