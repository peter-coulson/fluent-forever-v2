"""
Provider System for Fluent Forever V2

Abstracts all external dependencies (APIs, data sources, sync targets) into
pluggable providers that can be mocked, swapped, or configured independently.
"""

from .context_helper import (
    get_provider_from_context,
    register_provider_in_context,
    setup_providers_in_context,
)
from .registry import get_provider_registry

__all__ = [
    "get_provider_registry",
    "setup_providers_in_context",
    "get_provider_from_context",
    "register_provider_in_context",
]
