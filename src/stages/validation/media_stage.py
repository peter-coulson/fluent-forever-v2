#!/usr/bin/env python3
"""
Media Validation Stage
Validates media file data in pipeline
"""

from pathlib import Path
from typing import Dict, Any, List
from stages.base.validation_stage import ValidationStage


class MediaValidationStage(ValidationStage):
    """Validates media file data in pipeline"""
    
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate media file data
        
        Args:
            data: Media data with file information
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not isinstance(data, dict):
            return ["Data must be a dictionary"]
        
        media_files = data.get('media_files', [])
        if not isinstance(media_files, list):
            return ["'media_files' must be a list"]
        
        for i, media_file in enumerate(media_files):
            if not isinstance(media_file, dict):
                errors.append(f"Media file entry {i} must be a dictionary")
                continue
            
            file_id = media_file.get('id')
            file_type = media_file.get('type')
            file_path = media_file.get('file_path')
            
            if not file_id:
                errors.append(f"Media file entry {i} missing 'id' field")
            
            if not file_type:
                errors.append(f"Media file entry {i} missing 'type' field")
            elif file_type not in ['audio', 'image', 'video']:
                errors.append(f"Media file entry {i} has unsupported type: {file_type}")
            
            if not file_path:
                errors.append(f"Media file entry {i} missing 'file_path' field")
            else:
                # Check if file exists
                path_obj = Path(file_path)
                if not path_obj.exists():
                    errors.append(f"Media file not found: {file_path}")
                elif not path_obj.is_file():
                    errors.append(f"Media path is not a file: {file_path}")
                else:
                    # Validate file extension matches type
                    extension = path_obj.suffix.lower()
                    if file_type == 'audio' and extension not in ['.mp3', '.wav', '.ogg', '.m4a']:
                        errors.append(f"Audio file {file_path} has unsupported extension: {extension}")
                    elif file_type == 'image' and extension not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        errors.append(f"Image file {file_path} has unsupported extension: {extension}")
                    elif file_type == 'video' and extension not in ['.mp4', '.avi', '.mkv', '.webm']:
                        errors.append(f"Video file {file_path} has unsupported extension: {extension}")
        
        return errors