"""
File Operation Stages

Base implementations for common file operations like loading and saving JSON files.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext
from utils.logging_config import get_logger, ICONS


class FileLoadStage(Stage):
    """Load data from JSON file"""
    
    def __init__(self, file_key: str, required: bool = True, default_value: Optional[Dict[str, Any]] = None):
        """
        Initialize file load stage
        
        Args:
            file_key: Key in context for file path (e.g. 'vocabulary_path')
            required: Whether the file must exist
            default_value: Default value if file doesn't exist and not required
        """
        self.file_key = file_key
        self.required = required
        self.default_value = default_value or {}
        self.logger = get_logger(f'stages.file.load_{file_key}')
    
    @property
    def name(self) -> str:
        return f"load_{self.file_key}"
    
    @property
    def display_name(self) -> str:
        return f"Load {self.file_key.replace('_', ' ').title()}"
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Load JSON file from path specified in context"""
        file_path_str = context.get(self.file_key)
        if not file_path_str:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"No file path provided for key '{self.file_key}'",
                data={},
                errors=[f"Missing '{self.file_key}' in context"]
            )
        
        file_path = Path(file_path_str)
        
        # Check if file exists
        if not file_path.exists():
            if self.required:
                return StageResult(
                    status=StageStatus.FAILURE,
                    message=f"Required file not found: {file_path}",
                    data={},
                    errors=[f"File does not exist: {file_path}"]
                )
            else:
                # Use default value
                data_key = self.file_key.replace('_path', '').replace('_file', '')
                context.set(data_key, self.default_value)
                self.logger.info(f"{ICONS['info']} File not found, using default value: {file_path}")
                return StageResult(
                    status=StageStatus.SUCCESS,
                    message=f"Used default value for missing file: {file_path}",
                    data={data_key: self.default_value},
                    errors=[]
                )
        
        # Load file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Store data in context (remove _path/_file suffix)
            data_key = self.file_key.replace('_path', '').replace('_file', '')
            context.set(data_key, data)
            
            self.logger.info(f"{ICONS['check']} Loaded {file_path}")
            return StageResult(
                status=StageStatus.SUCCESS,
                message=f"Loaded file: {file_path}",
                data={data_key: data},
                errors=[]
            )
            
        except json.JSONDecodeError as e:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Invalid JSON in file: {file_path}",
                data={},
                errors=[f"JSON decode error: {e}"]
            )
        except Exception as e:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Failed to load file: {file_path}",
                data={},
                errors=[f"File load error: {e}"]
            )


class FileSaveStage(Stage):
    """Save data to JSON file"""
    
    def __init__(self, data_key: str, file_key: str, create_dirs: bool = True):
        """
        Initialize file save stage
        
        Args:
            data_key: Key in context for data to save
            file_key: Key in context for file path
            create_dirs: Whether to create parent directories
        """
        self.data_key = data_key
        self.file_key = file_key
        self.create_dirs = create_dirs
        self.logger = get_logger(f'stages.file.save_{data_key}')
    
    @property
    def name(self) -> str:
        return f"save_{self.data_key}"
    
    @property
    def display_name(self) -> str:
        return f"Save {self.data_key.replace('_', ' ').title()}"
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Save data to JSON file"""
        # Get data to save
        data = context.get(self.data_key)
        if data is None:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"No data found for key '{self.data_key}'",
                data={},
                errors=[f"Missing '{self.data_key}' in context"]
            )
        
        # Get file path
        file_path_str = context.get(self.file_key)
        if not file_path_str:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"No file path provided for key '{self.file_key}'",
                data={},
                errors=[f"Missing '{self.file_key}' in context"]
            )
        
        file_path = Path(file_path_str)
        
        # Create directories if needed
        if self.create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"{ICONS['check']} Saved {file_path}")
            return StageResult(
                status=StageStatus.SUCCESS,
                message=f"Saved file: {file_path}",
                data={'file_path': str(file_path)},
                errors=[]
            )
            
        except Exception as e:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Failed to save file: {file_path}",
                data={},
                errors=[f"File save error: {e}"]
            )