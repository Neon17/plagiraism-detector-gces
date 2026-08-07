"""Tests for the detector services.

Run them from the backend folder with:

    python -m unittest discover -s tests -t .

The services are pure Python, so they are tested directly without starting Django.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
