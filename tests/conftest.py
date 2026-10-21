"""Pytest configuration for roman-pipeline tests."""
import os

# Enable test mode to disable ProjectEnvSource
os.environ["ROMAN_PIPELINE_TEST_MODE"] = "1"