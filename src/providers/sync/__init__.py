"""
Sync providers for different sync targets.
"""

from .anki_provider import AnkiProvider
from .mock_provider import MockSyncProvider

__all__ = ["AnkiProvider", "MockSyncProvider"]
