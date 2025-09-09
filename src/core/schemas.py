"""
Configuration Schema Definitions

Defines data structures for different configuration types.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    """Base provider configuration"""
    type: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    name: str
    display_name: str
    data_file: str
    anki_note_type: str
    stages: List[str]
    providers: Dict[str, str] = field(default_factory=dict)  # stage -> provider mapping
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class SystemConfig:
    """System-wide configuration"""
    project_root: str
    log_level: str = "INFO"
    cache_enabled: bool = True
    max_concurrent_requests: int = 5
    timeout_seconds: int = 300


@dataclass
class CLIConfig:
    """CLI configuration"""
    output_format: str = "table"
    show_progress: bool = True
    confirm_destructive: bool = True
    default_dry_run: bool = False