"""Spanish verb conjugation practice pipeline."""

from typing import List, Dict, Any
from pathlib import Path

from core.pipeline import Pipeline
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext
from stages import get_stage
from config.config_manager import get_config_manager


class ConjugationPipeline(Pipeline):
    """Spanish verb conjugation practice pipeline"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._stages_cache: Dict[str, Stage] = {}
        
        # Load pipeline configuration
        config_manager = get_config_manager()
        self.pipeline_config = config_manager.get_pipeline_config('conjugation')
    
    @property
    def name(self) -> str:
        return "conjugation"
    
    @property
    def display_name(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('display_name', 'Conjugation Practice')
    
    @property
    def stages(self) -> List[str]:
        """Available stages for conjugation pipeline"""
        return [
            'analyze_verbs',      # Analyze verb forms (conjugation-specific)
            'create_cards',       # Create conjugation card pairs
            'generate_media',     # Generate images (shared with vocabulary)
            'validate_data',      # Validate conjugation data
            'sync_templates',     # Sync Anki templates (shared)
            'sync_cards'         # Sync cards to Anki (shared)
        ]
    
    @property
    def data_file(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('data_file', 'conjugations.json')
    
    @property
    def anki_note_type(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('anki_note_type', 'Conjugation')
    
    def get_stage(self, stage_name: str) -> Stage:
        """Get stage instance by name"""
        if stage_name in self._stages_cache:
            return self._stages_cache[stage_name]
        
        # Create stage instance
        if stage_name == 'analyze_verbs':
            from .stages.verb_analysis import VerbAnalysisStage
            stage = VerbAnalysisStage(self.pipeline_config)
        elif stage_name == 'create_cards':
            from .stages.card_creation import ConjugationCardCreationStage
            stage = ConjugationCardCreationStage(self.pipeline_config)
        elif stage_name == 'generate_media':
            # Reuse shared media generation stage
            stage = get_stage('generate_media')
        elif stage_name == 'validate_data':
            from .validation.conjugation_validator import ConjugationDataValidationStage
            stage = ConjugationDataValidationStage(self.pipeline_config)
        elif stage_name == 'sync_templates':
            # Reuse shared template sync stage
            stage = get_stage('sync_templates')
        elif stage_name == 'sync_cards':
            # Reuse shared card sync stage  
            stage = get_stage('sync_cards')
        else:
            raise ValueError(f"Unknown stage: {stage_name}")
        
        self._stages_cache[stage_name] = stage
        return stage
    
    def execute_stage(self, stage_name: str, context) -> StageResult:
        """Execute a specific stage"""
        if stage_name not in self.stages:
            return StageResult.failure(f"Stage '{stage_name}' not available in conjugation pipeline")
        
        # Convert dictionary context to PipelineContext if needed
        if isinstance(context, dict):
            pipeline_context = PipelineContext(
                pipeline_name=self.name,
                project_root=Path.cwd(),
                data=context
            )
        else:
            pipeline_context = context
        
        stage = self.get_stage(stage_name)
        
        # Validate stage can run with current context
        validation_errors = stage.validate_context(pipeline_context)
        if validation_errors:
            return StageResult.failure(
                f"Stage validation failed: {len(validation_errors)} errors",
                validation_errors
            )
        
        # Execute stage
        try:
            return stage.execute(pipeline_context)
        except Exception as e:
            return StageResult.failure(
                f"Stage execution failed: {str(e)}",
                [str(e)]
            )
    
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
    
    def get_media_config(self) -> Dict[str, Any]:
        """Get media configuration for this pipeline."""
        return {
            "media_dir": f"media/{self.name}",
            "image_dir": f"media/{self.name}/images", 
            "audio_dir": f"media/{self.name}/audio",
            "providers": self.pipeline_config.get('stage_providers', {})
        }
    
    def get_sync_config(self) -> Dict[str, Any]:
        """Get sync configuration for this pipeline."""
        return {
            "note_type": self.anki_note_type,
            "data_file": self.data_file,
            "providers": self.pipeline_config.get('stage_providers', {})
        }
    
    def get_data_paths(self) -> Dict[str, str]:
        """Get data paths for this pipeline."""
        return {
            "data_file": self.data_file,
            "media_dir": f"media/{self.name}",
            "template_dir": f"templates/anki/{self.anki_note_type}"
        }