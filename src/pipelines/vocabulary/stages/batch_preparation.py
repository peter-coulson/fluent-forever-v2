"""Batch preparation stage for vocabulary pipeline."""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import json

from core.stages import Stage, StageResult
from core.context import PipelineContext


class BatchPreparationStage(Stage):
    """
    Prepare Claude staging batch for vocabulary meanings.
    
    Integrates with the existing Claude batch system and creates staging files
    compatible with the current ingest_claude_batch.py workflow.
    """
    
    def __init__(self, pipeline_config: Dict[str, Any] = None):
        self.config = pipeline_config or {}
        self.batch_size = self.config.get('batch_settings', {}).get('cards_per_batch', 5)
    
    @property
    def name(self) -> str:
        return "prepare_batch"
    
    @property
    def display_name(self) -> str:
        return "Prepare Claude Batch"
    
    @property
    def dependencies(self) -> List[str]:
        return ["analyze_words"]
    
    def validate_context(self, context: PipelineContext) -> List[str]:
        """Validate context has required data."""
        errors = []
        
        analyzed_meanings = context.get('analyzed_meanings')
        if not analyzed_meanings:
            errors.append("No analyzed meanings available (missing 'analyzed_meanings' in context)")
        elif not isinstance(analyzed_meanings, list):
            errors.append("Analyzed meanings must be a list")
        
        return errors
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute batch preparation."""
        analyzed_meanings = context.get('analyzed_meanings', [])
        
        if not analyzed_meanings:
            return StageResult.failure("No analyzed meanings available for batch creation")
        
        # Limit to batch size if needed
        original_count = len(analyzed_meanings)
        if original_count > self.batch_size:
            analyzed_meanings = analyzed_meanings[:self.batch_size]
            # Note: Limited batch size (could add to context metadata if needed)
        
        # Create staging batch structure compatible with existing system
        batch_data = self._create_batch_structure(analyzed_meanings)
        
        # Save to staging directory
        staging_file = self._save_batch_file(batch_data, context)
        
        # Store results in context
        context.set('batch_data', batch_data)
        context.set('batch_file', staging_file)
        
        return StageResult.success(
            f"Created Claude batch with {len(analyzed_meanings)} meanings",
            {
                'batch_file': str(staging_file),
                'meaning_count': len(analyzed_meanings),
                'batch_data': batch_data
            }
        )
    
    def _create_batch_structure(self, analyzed_meanings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create batch structure compatible with existing Claude batch format.
        
        This matches the format expected by ingest_claude_batch.py
        """
        # Extract unique words from meanings
        words = list(set(meaning['SpanishWord'] for meaning in analyzed_meanings))
        
        batch_data = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "source": "pipeline-vocabulary",
                "pipeline": "vocabulary",
                "stage": "prepare_batch",
                "instructions": (
                    "Claude: enumerate distinct meanings for each word, and fill the 'meanings' "
                    "array below with entries conforming to the schema in CLAUDE.md and config.json "
                    "(meaning_entry). Add any words to skip to the 'skipped_words' array."
                )
            },
            "words": words,
            "meanings": self._create_meaning_templates(analyzed_meanings),
            "skipped_words": []
        }
        
        return batch_data
    
    def _create_meaning_templates(self, analyzed_meanings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create meaning templates for Claude to fill out.
        
        These templates provide the structure and context that Claude needs
        to generate the complete card data.
        """
        meaning_templates = []
        
        for meaning in analyzed_meanings:
            template = {
                # Pre-filled from analysis
                'SpanishWord': meaning['SpanishWord'],
                'MeaningID': meaning['MeaningID'],
                'MeaningContext': meaning['MeaningContext'],
                'CardID': meaning['CardID'],
                
                # Fields for Claude to fill
                'MonolingualDef': '',
                'ExampleSentence': '',
                'GappedSentence': '',  # Must contain '_____'
                'IPA': '',  # Must be in bracket notation [...]
                'prompt': '',  # Image generation prompt
                
                # Optional metadata from analysis
                'GrammaticalCategory': meaning.get('GrammaticalCategory', ''),
                'EstimatedDifficulty': meaning.get('EstimatedDifficulty', 'intermediate'),
                
                # Processing flags
                'RequiresPrompt': meaning.get('RequiresPrompt', True)
            }
            
            meaning_templates.append(template)
        
        return meaning_templates
    
    def _save_batch_file(self, batch_data: Dict[str, Any], context: PipelineContext) -> Path:
        """
        Save batch file to staging directory.
        
        Uses the same naming convention as the existing prepare_claude_batch.py
        """
        # Ensure staging directory exists
        staging_dir = context.project_root / 'staging'
        staging_dir.mkdir(exist_ok=True)
        
        # Generate timestamp-based filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f'claude_batch_{timestamp}.json'
        staging_file = staging_dir / filename
        
        # Write batch data
        staging_file.write_text(
            json.dumps(batch_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        return staging_file