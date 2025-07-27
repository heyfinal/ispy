#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ispy-ios-toolkit",
    version="1.0.0",
    author="iSpy Development Team",
    author_email="contact@ispy-toolkit.com",
    description="Advanced iOS Diagnostic & Management Tool with AI Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ispy-toolkit/ispy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "openai>=1.0.0", 
        "requests>=2.25.0",
        "psutil>=5.8.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "cryptography>=3.4.0",
        "pillow>=8.0.0",
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "ispy=ispy:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)