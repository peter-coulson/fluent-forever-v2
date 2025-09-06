#!/usr/bin/env python3
"""Unit tests for conjugation pipeline."""

import pytest
from pathlib import Path
import sys
import json

# Add src to path
project_root = Path(__file__).parents[4]
sys.path.insert(0, str(project_root / 'src'))

from pipelines.conjugation.conjugation_pipeline import ConjugationPipeline
from core.context import PipelineContext
from core.stages import StageStatus


class TestConjugationPipeline:
    """Test ConjugationPipeline class"""
    
    @pytest.fixture
    def pipeline(self):
        """Create conjugation pipeline instance"""
        return ConjugationPipeline()
    
    @pytest.fixture 
    def sample_config(self):
        """Sample pipeline configuration"""
        return {
            "pipeline": {
                "name": "conjugation",
                "display_name": "Conjugation Practice Cards",
                "data_file": "conjugations.json",
                "anki_note_type": "Conjugation"
            },
            "conjugation_settings": {
                "tenses": ["present", "preterite"],
                "persons": ["yo", "tú", "él"],
                "max_forms_per_verb": 6
            }
        }
    
    def test_pipeline_properties(self, pipeline):
        """Test basic pipeline properties"""
        assert pipeline.name == "conjugation"
        assert pipeline.display_name == "Conjugation Practice Cards"
        assert pipeline.data_file == "conjugations.json"
        assert pipeline.anki_note_type == "Conjugation"
    
    def test_pipeline_stages(self, pipeline):
        """Test pipeline has expected stages"""
        expected_stages = [
            'analyze_verbs',
            'create_cards', 
            'generate_media',
            'validate_data',
            'sync_templates',
            'sync_cards'
        ]
        
        assert pipeline.stages == expected_stages
    
    def test_get_info(self, pipeline):
        """Test get_info method"""
        info = pipeline.get_info()
        
        assert info['name'] == 'conjugation'
        assert info['display_name'] == 'Conjugation Practice Cards'
        assert info['data_file'] == 'conjugations.json'
        assert info['anki_note_type'] == 'Conjugation'
        assert 'stages' in info
        assert 'description' in info
    
    def test_get_media_config(self, pipeline):
        """Test media configuration"""
        config = pipeline.get_media_config()
        
        assert config['media_dir'] == 'media/conjugation'
        assert config['image_dir'] == 'media/conjugation/images'
        assert config['audio_dir'] == 'media/conjugation/audio'
        assert 'providers' in config
    
    def test_get_sync_config(self, pipeline):
        """Test sync configuration"""
        config = pipeline.get_sync_config()
        
        assert config['note_type'] == 'Conjugation'
        assert config['data_file'] == 'conjugations.json'
        assert 'providers' in config
    
    def test_get_data_paths(self, pipeline):
        """Test data paths"""
        paths = pipeline.get_data_paths()
        
        assert paths['data_file'] == 'conjugations.json'
        assert paths['media_dir'] == 'media/conjugation'
        assert paths['template_dir'] == 'templates/anki/Conjugation'
    
    def test_stage_creation(self, pipeline):
        """Test that stages can be created"""
        # Test conjugation-specific stages
        analyze_stage = pipeline.get_stage('analyze_verbs')
        assert analyze_stage.name == 'analyze_verbs'
        
        create_stage = pipeline.get_stage('create_cards')
        assert create_stage.name == 'create_cards'
        
        validate_stage = pipeline.get_stage('validate_data')
        assert validate_stage.name == 'validate_data'
        
        # Test shared stages
        media_stage = pipeline.get_stage('generate_media')
        assert media_stage.name == 'generate_media'
    
    def test_invalid_stage(self, pipeline):
        """Test error on invalid stage"""
        with pytest.raises(ValueError, match="Unknown stage"):
            pipeline.get_stage('invalid_stage')
    
    def test_execute_stage_with_dict_context(self, pipeline):
        """Test executing stage with dictionary context"""
        context = {'verbs': ['hablar'], 'tenses': ['present']}
        
        result = pipeline.execute_stage('analyze_verbs', context)
        
        # Should succeed with proper context
        assert result.status == StageStatus.SUCCESS
        assert 'analyzed' in result.message.lower()
    
    def test_execute_stage_with_pipeline_context(self, pipeline):
        """Test executing stage with PipelineContext"""
        context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': ['hablar'], 'tenses': ['present']}
        )
        
        result = pipeline.execute_stage('analyze_verbs', context)
        
        # Should succeed with proper context
        assert result.status == StageStatus.SUCCESS
    
    def test_execute_invalid_stage(self, pipeline):
        """Test executing invalid stage"""
        context = {'verbs': ['hablar']}
        
        result = pipeline.execute_stage('invalid_stage', context)
        
        assert result.status == StageStatus.FAILURE
        assert 'not available' in result.message
    
    def test_stage_caching(self, pipeline):
        """Test that stages are cached"""
        stage1 = pipeline.get_stage('analyze_verbs')
        stage2 = pipeline.get_stage('analyze_verbs')
        
        # Should be the same instance due to caching
        assert stage1 is stage2


class TestConjugationPipelineIntegration:
    """Integration tests for conjugation pipeline"""
    
    @pytest.fixture
    def pipeline(self):
        """Create conjugation pipeline instance"""
        return ConjugationPipeline()
    
    def test_full_verb_analysis_flow(self, pipeline):
        """Test complete verb analysis flow"""
        context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': ['hablar', 'comer']}
        )
        
        # Execute analysis stage
        result = pipeline.execute_stage('analyze_verbs', context)
        assert result.status == StageStatus.SUCCESS
        assert context.get('analyzed_conjugations') is not None
        
        # Execute card creation stage
        result = pipeline.execute_stage('create_cards', context)
        assert result.status == StageStatus.SUCCESS
        assert context.get('created_cards') is not None
        
        cards = context.get('created_cards')
        assert len(cards) > 0
        
        # Verify card structure
        card = cards[0]
        required_fields = ['CardID', 'Front', 'Back', 'Sentence', 'Extra', 'InfinitiveVerb']
        for field in required_fields:
            assert field in card
    
    def test_validation_flow(self, pipeline):
        """Test validation stage flow"""
        # Create sample cards
        sample_cards = [
            {
                'CardID': 'hablar_present_yo',
                'Front': 'hablo',
                'Back': 'hablar',
                'Sentence': 'Yo _____ español.',
                'Extra': 'Present tense, yo (I)',
                'InfinitiveVerb': 'hablar',
                'ConjugatedForm': 'hablo',
                'Tense': 'present',
                'Person': 'yo'
            }
        ]
        
        context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'cards': sample_cards}
        )
        
        result = pipeline.execute_stage('validate_data', context)
        assert result.status == StageStatus.SUCCESS
        
        validated_cards = context.get('validated_cards')
        assert validated_cards is not None
        assert len(validated_cards) == 1
    
    def test_pipeline_with_invalid_verb_data(self, pipeline):
        """Test pipeline behavior with invalid data"""
        context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': []}  # Empty verb list
        )
        
        result = pipeline.execute_stage('analyze_verbs', context)
        assert result.status == StageStatus.FAILURE
        assert 'validation failed' in result.message.lower() or 'no verbs provided' in result.message.lower()