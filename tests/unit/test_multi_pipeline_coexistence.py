#!/usr/bin/env python3
"""Unit tests for multi-pipeline coexistence."""

import pytest
from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root / 'src'))

from core.registry import get_pipeline_registry
from pipelines.vocabulary.pipeline import VocabularyPipeline
from pipelines.conjugation.conjugation_pipeline import ConjugationPipeline
from core.context import PipelineContext
from utils.resource_isolation import (
    get_pipeline_media_paths, 
    get_pipeline_template_paths,
    validate_pipeline_isolation
)


class TestMultiPipelineCoexistence:
    """Test that multiple pipelines can coexist without conflicts"""
    
    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """Setup clean registry for each test"""
        # Get fresh registry
        registry = get_pipeline_registry()
        
        # Clear any existing registrations
        registry._pipelines.clear()
        
        # Register both pipelines
        vocab_pipeline = VocabularyPipeline()
        conj_pipeline = ConjugationPipeline()
        
        registry.register(vocab_pipeline)
        registry.register(conj_pipeline)
        
        return registry
    
    def test_both_pipelines_registered(self, setup_registry):
        """Test that both pipelines are registered"""
        registry = setup_registry
        
        pipelines = registry.list_pipelines()
        assert 'vocabulary' in pipelines
        assert 'conjugation' in pipelines
        assert len(pipelines) >= 2
    
    def test_pipeline_independence(self, setup_registry):
        """Test that pipelines operate independently"""
        registry = setup_registry
        
        vocab_pipeline = registry.get('vocabulary')
        conj_pipeline = registry.get('conjugation')
        
        # Test different configurations
        vocab_info = vocab_pipeline.get_info()
        conj_info = conj_pipeline.get_info()
        
        assert vocab_info['name'] != conj_info['name']
        assert vocab_info['anki_note_type'] != conj_info['anki_note_type']
        assert vocab_info['data_file'] != conj_info['data_file']
    
    def test_simultaneous_execution(self, setup_registry):
        """Test that both pipelines can execute simultaneously"""
        registry = setup_registry
        
        vocab_pipeline = registry.get('vocabulary')
        conj_pipeline = registry.get('conjugation')
        
        # Create separate contexts
        vocab_context = PipelineContext(
            pipeline_name='vocabulary',
            project_root=Path.cwd(),
            data={'words': ['test']}
        )
        
        conj_context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': ['hablar']}
        )
        
        # Execute stages on both pipelines
        vocab_result = vocab_pipeline.execute_stage('analyze_words', vocab_context)
        conj_result = conj_pipeline.execute_stage('analyze_verbs', conj_context)
        
        # Both should succeed independently
        assert vocab_result is not None
        assert conj_result is not None
        
        # Verify contexts don't interfere
        # Vocabulary pipeline stores analyzed_meanings, not analyzed_words
        assert vocab_context.get('analyzed_meanings') is not None
        assert conj_context.get('analyzed_conjugations') is not None
        assert vocab_context.get('analyzed_conjugations') is None
        assert conj_context.get('analyzed_meanings') is None


class TestResourceIsolation:
    """Test resource isolation between pipelines"""
    
    def test_media_path_isolation(self):
        """Test that pipelines have separate media paths"""
        vocab_paths = get_pipeline_media_paths('vocabulary')
        conj_paths = get_pipeline_media_paths('conjugation')
        
        # Vocabulary should use root media directory (backward compatibility)
        assert vocab_paths['base'] == Path.cwd() / "media"
        
        # Conjugation should have its own subdirectory
        assert conj_paths['base'] == Path.cwd() / "media" / "conjugation"
        
        # Ensure they don't overlap
        assert vocab_paths['images'] != conj_paths['images']
        assert vocab_paths['audio'] != conj_paths['audio']
    
    def test_template_path_isolation(self):
        """Test that pipelines have separate template paths"""
        vocab_paths = get_pipeline_template_paths('vocabulary', 'Fluent Forever')
        conj_paths = get_pipeline_template_paths('conjugation', 'Conjugation')
        
        # Should have different template directories
        assert vocab_paths['base'] != conj_paths['base']
        assert 'Fluent Forever' in str(vocab_paths['base'])
        assert 'Conjugation' in str(conj_paths['base'])
    
    def test_pipeline_isolation_validation(self):
        """Test pipeline isolation validation"""
        # Test vocabulary pipeline isolation
        vocab_validation = validate_pipeline_isolation('vocabulary', 'Fluent Forever')
        assert vocab_validation['isolated'] == True
        assert len(vocab_validation['issues']) == 0
        
        # Test conjugation pipeline isolation
        conj_validation = validate_pipeline_isolation('conjugation', 'Conjugation')
        assert conj_validation['isolated'] == True
        assert len(conj_validation['issues']) == 0
    
    def test_no_template_conflicts(self):
        """Test that pipelines don't have template conflicts"""
        vocab_paths = get_pipeline_template_paths('vocabulary', 'Fluent Forever')
        conj_paths = get_pipeline_template_paths('conjugation', 'Conjugation')
        
        # Template directories should be completely separate
        assert vocab_paths['base'] != conj_paths['base']
        assert vocab_paths['front'] != conj_paths['front']
        assert vocab_paths['back'] != conj_paths['back']
        assert vocab_paths['styling'] != conj_paths['styling']


class TestSharedResourceManagement:
    """Test that shared resources are handled correctly"""
    
    @pytest.fixture
    def registry(self):
        """Setup registry with both pipelines"""
        registry = get_pipeline_registry()
        registry._pipelines.clear()
        
        vocab_pipeline = VocabularyPipeline()
        conj_pipeline = ConjugationPipeline()
        
        registry.register(vocab_pipeline)
        registry.register(conj_pipeline)
        
        return registry
    
    def test_shared_media_generation(self, registry):
        """Test that both pipelines can use shared media generation"""
        vocab_pipeline = registry.get('vocabulary')
        conj_pipeline = registry.get('conjugation')
        
        # Both should be able to get media generation stage
        vocab_media_stage = vocab_pipeline.get_stage('generate_media')
        conj_media_stage = conj_pipeline.get_stage('generate_media')
        
        assert vocab_media_stage.name == 'generate_media'
        assert conj_media_stage.name == 'generate_media'
    
    def test_shared_sync_stages(self, registry):
        """Test that both pipelines can use shared sync stages"""
        vocab_pipeline = registry.get('vocabulary')
        conj_pipeline = registry.get('conjugation')
        
        # Both should be able to get sync stages
        vocab_sync = vocab_pipeline.get_stage('sync_cards')
        conj_sync = conj_pipeline.get_stage('sync_cards')
        
        # Both should return valid stages (name depends on implementation)
        assert vocab_sync.name in ['sync', 'sync_cards']
        assert conj_sync.name in ['sync', 'sync_cards']
    
    def test_pipeline_specific_configurations(self, registry):
        """Test that pipelines have their own configurations"""
        vocab_pipeline = registry.get('vocabulary')
        conj_pipeline = registry.get('conjugation')
        
        vocab_config = vocab_pipeline.get_media_config()
        conj_config = conj_pipeline.get_media_config()
        
        # Should have different media directories
        assert vocab_config['media_dir'] != conj_config['media_dir']
        assert vocab_config['image_dir'] != conj_config['image_dir']
        assert vocab_config['audio_dir'] != conj_config['audio_dir']
    
    def test_anki_note_type_isolation(self, registry):
        """Test that pipelines use different Anki note types"""
        vocab_pipeline = registry.get('vocabulary')
        conj_pipeline = registry.get('conjugation')
        
        vocab_sync_config = vocab_pipeline.get_sync_config()
        conj_sync_config = conj_pipeline.get_sync_config()
        
        # Should use different note types
        assert vocab_sync_config['note_type'] != conj_sync_config['note_type']
        assert vocab_sync_config['note_type'] == 'Fluent Forever'
        assert conj_sync_config['note_type'] == 'Conjugation'


class TestPipelineRegistryBehavior:
    """Test pipeline registry behavior with multiple pipelines"""
    
    def test_registry_get_pipeline_info(self):
        """Test getting info for all registered pipelines"""
        registry = get_pipeline_registry()
        registry._pipelines.clear()
        
        # Register pipelines
        vocab_pipeline = VocabularyPipeline()
        conj_pipeline = ConjugationPipeline()
        registry.register(vocab_pipeline)
        registry.register(conj_pipeline)
        
        # Get all pipeline info
        all_info = registry.get_all_pipeline_info()
        
        assert 'vocabulary' in all_info
        assert 'conjugation' in all_info
        
        vocab_info = all_info['vocabulary']
        conj_info = all_info['conjugation']
        
        assert vocab_info['name'] == 'vocabulary'
        assert conj_info['name'] == 'conjugation'
        assert vocab_info['anki_note_type'] == 'Fluent Forever'
        assert conj_info['anki_note_type'] == 'Conjugation'
    
    def test_registry_pipeline_existence_check(self):
        """Test checking if pipelines exist in registry"""
        registry = get_pipeline_registry()
        registry._pipelines.clear()
        
        # Initially no pipelines
        assert not registry.has_pipeline('vocabulary')
        assert not registry.has_pipeline('conjugation')
        
        # Register vocabulary
        vocab_pipeline = VocabularyPipeline()
        registry.register(vocab_pipeline)
        
        assert registry.has_pipeline('vocabulary')
        assert not registry.has_pipeline('conjugation')
        
        # Register conjugation
        conj_pipeline = ConjugationPipeline()
        registry.register(conj_pipeline)
        
        assert registry.has_pipeline('vocabulary')
        assert registry.has_pipeline('conjugation')