"""Pipeline implementations for different card types."""

from .vocabulary import VocabularyPipeline
from .conjugation import ConjugationPipeline

# Auto-register pipelines with the global registry
from core.registry import get_pipeline_registry

def register_all_pipelines():
    """Register all available pipelines with the global registry."""
    registry = get_pipeline_registry()
    
    # Register vocabulary pipeline
    vocab_pipeline = VocabularyPipeline()
    if not registry.has_pipeline(vocab_pipeline.name):
        registry.register(vocab_pipeline)
    
    # Register conjugation pipeline
    conj_pipeline = ConjugationPipeline()
    if not registry.has_pipeline(conj_pipeline.name):
        registry.register(conj_pipeline)

# Auto-register when module is imported
register_all_pipelines()

__all__ = [
    'VocabularyPipeline',
    'ConjugationPipeline',
    'register_all_pipelines'
]