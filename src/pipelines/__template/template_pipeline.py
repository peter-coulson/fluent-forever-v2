"""
Template pipeline implementation for new card types.

Instructions for creating a new pipeline:

1. Copy this entire __template/ directory to a new directory with your pipeline name
2. Rename template_pipeline.py to {your_pipeline_name}_pipeline.py  
3. Update the class name and all properties below
4. Implement your stages in the stages/ directory
5. Register your pipeline in src/pipelines/__init__.py
6. Create configuration file in config/pipelines/{your_pipeline_name}.json
7. Add CLI commands if needed

Example structure for a "conjugation" pipeline:
```
src/pipelines/conjugation/
├── __init__.py
├── conjugation_pipeline.py     # Main pipeline class
├── stages/
│   ├── __init__.py
│   ├── verb_analysis.py        # Analyze verb conjugations
│   ├── pattern_generation.py   # Generate conjugation patterns
│   └── card_creation.py        # Create Anki cards
└── data/
    ├── __init__.py
    └── conjugation_data.py     # Handle conjugation.json
```
"""

from typing import List, Dict, Any
from pathlib import Path

from core.pipeline import Pipeline
from core.stages import Stage, StageResult
from core.context import PipelineContext
from core.exceptions import StageNotFoundError
from config.config_manager import get_config_manager


class TemplatePipeline(Pipeline):
    """
    Template pipeline for creating new card types.
    
    TODO: Change class name to match your pipeline (e.g., ConjugationPipeline)
    """
    
    def __init__(self):
        """Initialize the pipeline with configuration."""
        # Load pipeline configuration
        config_manager = get_config_manager()
        self.pipeline_config = config_manager.get_pipeline_config(self.name)
        
        # Initialize stages - customize for your pipeline
        self._stages = {
            "analyze": TemplateAnalysisStage(),
            "prepare": TemplatePreparationStage(), 
            "generate": TemplateGenerationStage(),
            "validate": TemplateValidationStage(),
            "sync": TemplateSyncStage(),
        }
    
    @property
    def name(self) -> str:
        """TODO: Change to your pipeline name (e.g., 'conjugation')."""
        return "template"
    
    @property
    def display_name(self) -> str:
        """TODO: Change to your pipeline display name."""
        return "Template Pipeline"
    
    @property
    def stages(self) -> List[str]:
        """Available stages for this pipeline."""
        return list(self._stages.keys())
    
    def get_stages(self) -> List[str]:
        """Get available stages (for backward compatibility)."""
        return self.stages
    
    def get_stage(self, stage_name: str) -> Stage:
        """Get a stage instance by name."""
        if stage_name not in self._stages:
            raise StageNotFoundError(f"Stage '{stage_name}' not found in {self.name} pipeline")
        
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
        """TODO: Change to your data file (e.g., 'conjugation.json')."""
        return "template.json"
    
    @property
    def anki_note_type(self) -> str:
        """TODO: Change to your Anki note type."""
        return "Template Note Type"


# Template stage implementations
# TODO: Implement your actual stages - these are just examples

class TemplateAnalysisStage(Stage):
    """Template analysis stage - customize for your needs."""
    
    @property
    def name(self) -> str:
        return "analyze"
    
    @property
    def display_name(self) -> str:
        return "Analyze Input Data"
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute analysis stage."""
        # TODO: Implement your analysis logic
        input_data = context.get("input_data", [])
        if not input_data:
            return StageResult.failure("No input data provided")
        
        # Simulate analysis
        analyzed_data = {"analyzed": True, "items": input_data}
        context.set("analyzed_data", analyzed_data)
        
        return StageResult.success(
            f"Analyzed {len(input_data)} items",
            analyzed_data
        )
    
    def validate_context(self, context: PipelineContext) -> List[str]:
        """Validate context for this stage."""
        errors = []
        if not context.get("input_data"):
            errors.append("Context must contain 'input_data'")
        return errors


class TemplatePreparationStage(Stage):
    """Template preparation stage."""
    
    @property
    def name(self) -> str:
        return "prepare"
    
    @property
    def display_name(self) -> str:
        return "Prepare Data"
    
    @property
    def dependencies(self) -> List[str]:
        return ["analyze"]
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute preparation stage."""
        analyzed_data = context.get("analyzed_data")
        if not analyzed_data:
            return StageResult.failure("No analyzed data found")
        
        # TODO: Implement your preparation logic
        prepared_data = {"prepared": True, "ready_for_generation": True}
        context.set("prepared_data", prepared_data)
        
        return StageResult.success("Data preparation completed", prepared_data)


class TemplateGenerationStage(Stage):
    """Template generation stage."""
    
    @property
    def name(self) -> str:
        return "generate"
    
    @property
    def display_name(self) -> str:
        return "Generate Cards"
    
    @property
    def dependencies(self) -> List[str]:
        return ["prepare"]
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute generation stage."""
        prepared_data = context.get("prepared_data")
        if not prepared_data:
            return StageResult.failure("No prepared data found")
        
        # TODO: Implement your card generation logic
        generated_data = {"cards_generated": 5, "stage": "generate"}
        context.set("generated_data", generated_data)
        
        return StageResult.success("Card generation completed", generated_data)


class TemplateValidationStage(Stage):
    """Template validation stage."""
    
    @property
    def name(self) -> str:
        return "validate"
    
    @property
    def display_name(self) -> str:
        return "Validate Generated Data"
    
    @property
    def dependencies(self) -> List[str]:
        return ["generate"]
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute validation stage."""
        generated_data = context.get("generated_data")
        if not generated_data:
            return StageResult.failure("No generated data found")
        
        # TODO: Implement your validation logic
        validation_data = {"validated": True, "errors": []}
        context.set("validation_data", validation_data)
        
        return StageResult.success("Validation completed", validation_data)


class TemplateSyncStage(Stage):
    """Template sync stage."""
    
    @property
    def name(self) -> str:
        return "sync"
    
    @property
    def display_name(self) -> str:
        return "Sync to Anki"
    
    @property
    def dependencies(self) -> List[str]:
        return ["validate"]
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute sync stage."""
        validation_data = context.get("validation_data")
        if not validation_data:
            return StageResult.failure("No validation data found")
        
        # TODO: Implement your sync logic
        sync_data = {"synced": True, "cards_synced": 5}
        context.set("sync_data", sync_data)
        
        return StageResult.success("Sync to Anki completed", sync_data)