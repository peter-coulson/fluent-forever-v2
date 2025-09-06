"""
Data Provider Interface

Abstract interface for data sources (JSON files, databases, memory, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path


class DataProvider(ABC):
    """Abstract interface for data sources"""
    
    @abstractmethod
    def load_data(self, identifier: str) -> Dict[str, Any]:
        """Load data by identifier (e.g., filename, key)
        
        Args:
            identifier: Data identifier (filename without extension, key, etc.)
            
        Returns:
            Dictionary containing the loaded data
            
        Raises:
            ValueError: If data cannot be loaded or doesn't exist
        """
        pass
    
    @abstractmethod  
    def save_data(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Save data to identifier. Return True if successful.
        
        Args:
            identifier: Data identifier to save to
            data: Dictionary data to save
            
        Returns:
            True if save was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """Check if data exists for identifier
        
        Args:
            identifier: Data identifier to check
            
        Returns:
            True if data exists, False otherwise
        """
        pass
    
    @abstractmethod
    def list_identifiers(self) -> List[str]:
        """List all available data identifiers
        
        Returns:
            List of all available identifiers
        """
        pass
    
    def backup_data(self, identifier: str) -> Optional[str]:
        """Create backup of data. Return backup identifier if successful.
        
        Args:
            identifier: Data identifier to backup
            
        Returns:
            Backup identifier if successful, None if backup failed or not supported
        """
        return None  # Optional for providers