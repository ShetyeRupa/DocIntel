"""Evaluation framework for DocIntel."""
from .test_suite import TestSuite
from .metrics import MetricsCalculator

__all__ = ["TestSuite", "MetricsCalculator"]