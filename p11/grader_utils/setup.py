"""
Lets the grader_utils package be installed in
editable mode through pip.
"""

from setuptools import setup, find_packages

setup(
    name="grader_utils",
    version="0.0",
    description="Shared utilities for CS220 grader packages",
    packages=find_packages(),
)
