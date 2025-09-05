"""Vocabulary pipeline implementation for Fluent Forever cards."""

from typing import List
from core.pipeline import Pipeline
from core.stages import Stage
from core.exceptions import StageNotFoundError
from .stages import PrepareStage, MediaGenerationStage, SyncStage


class VocabularyPipeline(Pipeline):
    """Pipeline for Fluent Forever vocabulary cards."""
    
    def __init__(self):
        self._stages = {
            "prepare": PrepareStage(),
            "media": MediaGenerationStage(),
            "sync": SyncStage(),
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
    
    def get_stage(self, stage_name: str) -> Stage:
        """Get a stage instance by name."""
        if stage_name not in self._stages:
            raise StageNotFoundError(f"Stage '{stage_name}' not found in vocabulary pipeline")
        
        return self._stages[stage_name]
    
    @property
    def data_file(self) -> str:
        return "vocabulary.json"
    
    @property
    def anki_note_type(self) -> str:
        return "Fluent Forever"