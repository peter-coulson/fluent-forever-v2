"""
Media Validation Stage

Validates that required media files exist and are accessible. Checks for
missing images and audio files referenced in vocabulary.
"""

from pathlib import Path
from typing import Dict, Any, List, Set

from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext
from stages.base.validation_stage import ValidationStage
from utils.logging_config import get_logger, ICONS


class MediaValidationStage(ValidationStage):
    """Validate media files existence"""
    
    def __init__(self, data_key: str = 'vocabulary', require_all: bool = False):
        """
        Initialize media validation stage
        
        Args:
            data_key: Key in context for data containing media references
            require_all: Whether to require all media files to exist
        """
        super().__init__(data_key)
        self.require_all = require_all
        self.logger = get_logger('stages.validation.media')
    
    @property
    def name(self) -> str:
        return f"validate_media"
    
    @property  
    def display_name(self) -> str:
        return "Validate Media Files"
    
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate media files referenced in data"""
        errors = []
        
        # Get project root from context
        context = PipelineContext()  # Temporary context to access project_root
        project_root = Path(context.get('project_root', Path.cwd()))
        media_dir = project_root / 'media'
        
        # Extract media references
        referenced_images, referenced_audio = self.extract_media_references(data)
        
        if not referenced_images and not referenced_audio:
            self.logger.info(f"{ICONS['info']} No media references found to validate")
            return []
        
        self.logger.info(f"{ICONS['search']} Validating {len(referenced_images)} images and {len(referenced_audio)} audio files...")
        
        # Check image files
        missing_images = self.check_media_files(media_dir / 'images', referenced_images)
        
        # Check audio files
        missing_audio = self.check_media_files(media_dir / 'audio', referenced_audio)
        
        # Handle missing files
        if missing_images:
            message = f"Missing {len(missing_images)} image files"
            self.log_missing_files("images", missing_images)
            
            if self.require_all:
                errors.append(message)
            else:
                self.logger.warning(f"{ICONS['warning']} {message} (not required)")
        
        if missing_audio:
            message = f"Missing {len(missing_audio)} audio files"
            self.log_missing_files("audio", missing_audio)
            
            if self.require_all:
                errors.append(message)
            else:
                self.logger.warning(f"{ICONS['warning']} {message} (not required)")
        
        # Report success if no missing files
        if not missing_images and not missing_audio:
            self.logger.info(f"{ICONS['check']} All referenced media files exist")
        
        return errors
    
    def extract_media_references(self, data: Dict[str, Any]) -> tuple[Set[str], Set[str]]:
        """Extract media file references from data"""
        images = set()
        audio = set()
        
        if 'words' in data:
            # Vocabulary format
            for word_data in data['words'].values():
                if 'meanings' in word_data:
                    for meaning in word_data['meanings']:
                        self.extract_meaning_media(meaning, images, audio)
        
        elif 'meanings' in data:
            # Staging format
            for meaning in data['meanings']:
                self.extract_meaning_media(meaning, images, audio)
        
        elif isinstance(data, list):
            # List of cards/meanings
            for item in data:
                if isinstance(item, dict):
                    self.extract_meaning_media(item, images, audio)
        
        return images, audio
    
    def extract_meaning_media(self, meaning: Dict[str, Any], images: Set[str], audio: Set[str]) -> None:
        """Extract media references from a single meaning"""
        # Extract image file
        if 'ImageFile' in meaning and meaning['ImageFile']:
            images.add(meaning['ImageFile'])
        
        # Extract audio file from WordAudio field like "[sound:word.mp3]"
        word_audio = meaning.get('WordAudio', '')
        if word_audio.startswith('[sound:') and word_audio.endswith(']'):
            audio_file = word_audio[7:-1]  # Remove "[sound:" and "]"
            audio.add(audio_file)
        
        # Extract audio file from WordAudioAlt field
        word_audio_alt = meaning.get('WordAudioAlt', '')
        if word_audio_alt.startswith('[sound:') and word_audio_alt.endswith(']'):
            audio_file = word_audio_alt[7:-1]
            audio.add(audio_file)
    
    def check_media_files(self, media_dir: Path, referenced_files: Set[str]) -> Set[str]:
        """Check which referenced files are missing"""
        missing = set()
        
        if not media_dir.exists():
            # If media directory doesn't exist, all files are missing
            return referenced_files
        
        for filename in referenced_files:
            file_path = media_dir / filename
            if not file_path.exists():
                missing.add(filename)
        
        return missing
    
    def log_missing_files(self, media_type: str, missing_files: Set[str], max_show: int = 10) -> None:
        """Log missing media files"""
        files_list = sorted(missing_files)
        
        for i, filename in enumerate(files_list[:max_show]):
            self.logger.warning(f"   Missing {media_type}: {filename}")
        
        if len(files_list) > max_show:
            self.logger.warning(f"   ... and {len(files_list) - max_show} more missing {media_type}")