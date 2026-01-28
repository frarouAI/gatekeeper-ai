from setuptools import setup, find_packages
setup(
    name="gatekeeper-ai",
    version="1.0.0",
    py_modules=["claude_cli"],
    entry_points={"console_scripts": ["gatekeeper=claude_cli:main"]},
    install_requires=[],
)
