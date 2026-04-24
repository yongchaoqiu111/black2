"""
Black2 Protocol SDK - AI Transaction Trust Layer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="black2-sdk",
    version="1.0.0",
    author="Black2 Team",
    description="SDK for Black2 Protocol (B2P) - AI-to-AI transaction trust layer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "pygit2",
        "uvd-x402-sdk",
    ],
)
