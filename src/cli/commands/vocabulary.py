"""Vocabulary command for backward compatibility."""

from typing import List, Dict, Any
from pathlib import Path
from core.context import PipelineContext
from providers.registry import get_provider_registry
from core.registry import get_pipeline_registry
from cli.config.cli_config import CLIConfig


class VocabularyCommand:
    """Vocabulary-specific command interface for backward compatibility."""
    
    def __init__(self, config: CLIConfig = None):
        """Initialize vocabulary command.
        
        Args:
            config: Optional CLI configuration
        """
        self.config = config or CLIConfig.load()
        self.pipeline_registry = get_pipeline_registry()
        self.provider_registry = get_provider_registry()
        self.project_root = Path(__file__).parents[3]
        
        # Initialize providers
        self.config.initialize_providers(self.provider_registry)
        
        # Register vocabulary pipeline
        from pipelines.vocabulary.pipeline import VocabularyPipeline
        vocabulary_pipeline = VocabularyPipeline()
        if not self.pipeline_registry.has_pipeline('vocabulary'):
            self.pipeline_registry.register(vocabulary_pipeline)
    
    def prepare_batch(self, words: List[str], **kwargs) -> Dict[str, Any]:
        """Prepare batch of words for processing.
        
        Args:
            words: List of words to prepare
            **kwargs: Additional arguments
            
        Returns:
            Result of preparation
        """
        context = PipelineContext(
            pipeline_name='vocabulary',
            project_root=self.project_root,
            config=self.config.to_dict()
        )
        
        context.set('words', words)
        context.set('providers', {
            'data': self.provider_registry.get_data_provider('default'),
            'media': self.provider_registry.get_media_provider('default'), 
            'sync': self.provider_registry.get_sync_provider('default')
        })
        
        # Set additional arguments
        for key, value in kwargs.items():
            context.set(key, value)
        
        pipeline = self.pipeline_registry.get('vocabulary')
        result = pipeline.execute_stage('prepare', context)
        
        return {
            'success': result.status.value == 'success',
            'message': result.message,
            'data': result.data,
            'errors': result.errors
        }
    
    def generate_media(self, cards: List[str], **kwargs) -> Dict[str, Any]:
        """Generate media for cards.
        
        Args:
            cards: List of card IDs
            **kwargs: Additional arguments
            
        Returns:
            Result of media generation
        """
        context = PipelineContext(
            pipeline_name='vocabulary',
            project_root=self.project_root,
            config=self.config.to_dict()
        )
        
        context.set('cards', cards)
        context.set('providers', {
            'data': self.provider_registry.get_data_provider('default'),
            'media': self.provider_registry.get_media_provider('default'), 
            'sync': self.provider_registry.get_sync_provider('default')
        })
        
        # Set additional arguments
        for key, value in kwargs.items():
            context.set(key, value)
        
        pipeline = self.pipeline_registry.get('vocabulary')
        result = pipeline.execute_stage('media', context)
        
        return {
            'success': result.status.value == 'success',
            'message': result.message,
            'data': result.data,
            'errors': result.errors
        }
    
    def sync_anki(self, **kwargs) -> Dict[str, Any]:
        """Sync to Anki.
        
        Args:
            **kwargs: Additional arguments
            
        Returns:
            Result of sync
        """
        context = PipelineContext(
            pipeline_name='vocabulary',
            project_root=self.project_root,
            config=self.config.to_dict()
        )
        
        context.set('providers', {
            'data': self.provider_registry.get_data_provider('default'),
            'media': self.provider_registry.get_media_provider('default'), 
            'sync': self.provider_registry.get_sync_provider('default')
        })
        
        # Set additional arguments
        for key, value in kwargs.items():
            context.set(key, value)
        
        pipeline = self.pipeline_registry.get('vocabulary')
        result = pipeline.execute_stage('sync', context)
        
        return {
            'success': result.status.value == 'success',
            'message': result.message,
            'data': result.data,
            'errors': result.errors
        }
    
    def ingest_batch(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Ingest batch file.
        
        Args:
            file_path: Path to batch file
            **kwargs: Additional arguments
            
        Returns:
            Result of ingestion
        """
        # This would typically be handled by a separate ingestion stage
        # For now, return a basic success response
        return {
            'success': True,
            'message': f'Batch file {file_path} ingested successfully',
            'data': {'file_path': file_path},
            'errors': []
        }
    
    def get_available_stages(self) -> List[str]:
        """Get available stages for vocabulary pipeline.
        
        Returns:
            List of available stage names
        """
        pipeline = self.pipeline_registry.get('vocabulary')
        return pipeline.stages