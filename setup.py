"""
Gatekeeper AI - Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="gatekeeper-ai",
    version="1.0.0",
    author="Francois Roux",
    author_email="frankroux@gmail.com",
    description="Autonomous code quality enforcement with AI-powered repair",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frarouAI/gatekeeper-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.11",
    install_requires=[
        "anthropic>=0.18.0",
        "pyyaml>=6.0",
        "jsonschema>=4.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gatekeeper=gatekeeper_ai.cli:main",
            "gatekeeper-ci=gatekeeper_ai.ci_gate:main",
        ],
    },
    include_package_data=True,
    package_data={
        "gatekeeper_ai": [
            "schemas/*.json",
            "migrations/*.py",
        ],
    },
)
