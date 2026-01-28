from setuptools import setup
setup(
    name="gatekeeper-ai",
    version="1.0.1",
    py_modules=["gatekeeper", "claude_cli"],
    entry_points={"console_scripts": ["gatekeeper=gatekeeper:main"]},
    package_data={"": ["multi_judge.py", "bot_server.py", "*.py"]},
)
