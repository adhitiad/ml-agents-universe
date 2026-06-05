"""Shared library untuk ML Agents Universe.

Package ini menyediakan base classes, utilities, dan komponen yang
digunakan bersama oleh semua domain agents dalam monorepo.

Submodules:
    - data: Data loading, validation, dan transformation utilities.
    - models: Base model classes dan Pydantic schemas bersama.
    - env: Environment configuration dan settings management.
    - serving: API serving utilities dan middleware.
    - monitoring: Logging, metrics, dan health check utilities.
    - utils: Helper functions yang bersifat umum.
"""

from __future__ import annotations


__version__: str = "0.1.0"
__author__: str = "ML Agents Universe Team"

__all__: list[str] = [
    "__author__",
    "__version__",
    "data",
    "env",
    "models",
    "monitoring",
    "serving",
    "utils",
]
