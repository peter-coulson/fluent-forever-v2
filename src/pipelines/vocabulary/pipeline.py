"""Vocabulary pipeline implementation for Fluent Forever cards."""

from typing import List, Dict, Any
from core.pipeline import Pipeline
from core.stages import Stage
from core.exceptions import StageNotFoundError
from config.config_manager import get_config_manager
# Import from stages.py file (use sys to avoid package import conflict)
import sys
from pathlib import Path
import importlib.util

# Load stages.py module explicitly 
stages_file = Path(__file__).parent / "stages.py"
spec = importlib.util.spec_from_file_location("vocab_stages_module", stages_file)
vocab_stages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vocab_stages)

# Import existing stages from stages.py
PrepareStage = vocab_stages.PrepareStage
MediaGenerationStage = vocab_stages.MediaGenerationStage  
SyncStage = vocab_stages.SyncStage
ClaudeBatchStage = vocab_stages.ClaudeBatchStage
ValidateStage = vocab_stages.ValidateStage

# Import new stages from stages/ directory
from .stages.word_analysis import WordAnalysisStage
from .stages.batch_preparation import BatchPreparationStage


class VocabularyPipeline(Pipeline):
    """Pipeline for Fluent Forever vocabulary cards."""
    
    def __init__(self):
        # Load pipeline configuration
        config_manager = get_config_manager()
        self.pipeline_config = config_manager.get_pipeline_config('vocabulary')
        
        # Initialize stages with configuration
        self._stages = {
            # New comprehensive stages
            "analyze_words": WordAnalysisStage(self.pipeline_config),
            "prepare_batch": BatchPreparationStage(self.pipeline_config),
            "ingest_batch": ClaudeBatchStage(),
            "validate_data": ValidateStage(),
            "sync_cards": SyncStage(),
            
            # Backward compatibility stages (original names)
            "prepare": PrepareStage(),
            "claude_batch": ClaudeBatchStage(),
            "validate": ValidateStage(),
            "generate_media": MediaGenerationStage(),
            "sync": SyncStage(),  # Add sync alias for backward compatibility
        }
    
    @property
    def name(self) -> str:
        return "vocabulary"
    
    @property
    def display_name(self) -> str:
        return "Fluent Forever Vocabulary"
    
    @property
    def stages(self) -> List[str]:
        return list(self._stages.keys())
    
    def get_stages(self) -> List[str]:
        """Get available stages (for backward compatibility)."""
        return self.stages
    
    def get_stage(self, stage_name: str) -> Stage:
        """Get a stage instance by name."""
        if stage_name not in self._stages:
            raise StageNotFoundError(f"Stage '{stage_name}' not found in vocabulary pipeline")
        
        return self._stages[stage_name]
    
    def get_info(self) -> Dict[str, Any]:
        """Get pipeline information."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.get_description(),
            "stages": self.stages,
            "data_file": self.data_file,
            "anki_note_type": self.anki_note_type
        }
    
    @property
    def data_file(self) -> str:
        return "vocabulary.json"
    
    @property
    def anki_note_type(self) -> str:
        return "Fluent Forever"