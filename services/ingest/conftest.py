"""Add services/ingest to sys.path for test discovery from repo root."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
