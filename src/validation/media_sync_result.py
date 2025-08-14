#!/usr/bin/env python3
"""
MediaSyncResult - Shared data structure for media validation results
"""

from dataclasses import dataclass
from typing import List

@dataclass
class MediaSyncResult:
    """Result of media synchronization validation"""
    missing_images: List[str]
    missing_audio: List[str]
    
    def has_missing_files(self) -> bool:
        """Check if there are any missing files"""
        return len(self.missing_images) > 0 or len(self.missing_audio) > 0
    
    def total_missing(self) -> int:
        """Total count of missing files"""
        return len(self.missing_images) + len(self.missing_audio)
    
    def is_synchronized(self) -> bool:
        """Check if everything is synchronized (no missing files)"""
        return not self.has_missing_files()