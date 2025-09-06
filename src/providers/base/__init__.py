"""
Base provider interfaces for all provider types.
"""

from .data_provider import DataProvider
from .media_provider import MediaProvider, MediaRequest, MediaResult
from .sync_provider import SyncProvider, SyncRequest, SyncResult

__all__ = [
    'DataProvider',
    'MediaProvider', 'MediaRequest', 'MediaResult',
    'SyncProvider', 'SyncRequest', 'SyncResult'
]