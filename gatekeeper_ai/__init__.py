"""
Gatekeeper AI - Autonomous Code Quality Enforcement

A production-grade code quality system with AI-powered repair capabilities.
"""

__version__ = "1.0.0"
__author__ = "Francois Roux"
__license__ = "MIT"

from .judge import judge_code
from .loop_controller import run_loop
from .gatekeeper_config import GatekeeperConfig

__all__ = [
    "judge_code",
    "run_loop",
    "GatekeeperConfig",
]
