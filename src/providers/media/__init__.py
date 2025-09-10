"""
Media providers for different media generation services.
"""

from .forvo_provider import ForvoProvider
from .mock_provider import MockMediaProvider

__all__ = ["ForvoProvider", "MockMediaProvider"]
