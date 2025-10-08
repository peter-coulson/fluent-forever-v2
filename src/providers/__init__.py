"""
Provider System for Fluent Forever V2

Abstracts all external dependencies (APIs, data sources, sync targets) into
pluggable providers that can be mocked, swapped, or configured independently.
"""

from .registry import get_provider_registry

__all__ = [
    "get_provider_registry",
]
