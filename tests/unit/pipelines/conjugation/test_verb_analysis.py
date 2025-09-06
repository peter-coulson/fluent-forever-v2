#!/usr/bin/env python3
"""Unit tests for verb analysis stage."""

import pytest
from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parents[4]
sys.path.insert(0, str(project_root / 'src'))

from pipelines.conjugation.stages.verb_analysis import VerbAnalysisStage
from core.context import PipelineContext
from core.stages import StageStatus


class TestVerbAnalysisStage:
    """Test VerbAnalysisStage class"""
    
    @pytest.fixture
    def stage(self):
        """Create verb analysis stage instance"""
        config = {
            'conjugation_settings': {
                'tenses': ['present', 'preterite'],
                'persons': ['yo', 'tú', 'él'],
                'max_forms_per_verb': 6
            }
        }
        return VerbAnalysisStage(config)
    
    @pytest.fixture
    def context_with_verbs(self):
        """Create context with verb data"""
        return PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': ['hablar', 'comer']}
        )
    
    @pytest.fixture  
    def empty_context(self):
        """Create context without verb data"""
        return PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={}
        )
    
    def test_stage_properties(self, stage):
        """Test basic stage properties"""
        assert stage.name == "analyze_verbs"
        assert stage.display_name == "Analyze Verb Conjugations"
    
    def test_validate_context_success(self, stage, context_with_verbs):
        """Test context validation with valid data"""
        errors = stage.validate_context(context_with_verbs)
        assert errors == []
    
    def test_validate_context_no_verbs(self, stage, empty_context):
        """Test context validation without verbs"""
        errors = stage.validate_context(empty_context)
        assert len(errors) == 1
        assert "No verbs provided" in errors[0]
    
    def test_validate_context_invalid_verbs(self, stage):
        """Test context validation with invalid verbs format"""
        context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': 'hablar'}  # String instead of list
        )
        
        errors = stage.validate_context(context)
        assert len(errors) == 1
        assert "must be provided as a list" in errors[0]
    
    def test_execute_success(self, stage, context_with_verbs):
        """Test successful execution"""
        result = stage.execute(context_with_verbs)
        
        assert result.status == StageStatus.SUCCESS
        assert "Analyzed" in result.message
        assert result.data['conjugation_count'] > 0
        
        # Check context was updated
        conjugations = context_with_verbs.get('analyzed_conjugations')
        assert conjugations is not None
        assert len(conjugations) > 0
    
    def test_execute_no_verbs(self, stage, empty_context):
        """Test execution without verbs"""
        result = stage.execute(empty_context)
        
        # Should still succeed but with no conjugations
        assert result.status == StageStatus.SUCCESS
        assert result.data['conjugation_count'] == 0
    
    def test_conjugate_hablar(self, stage):
        """Test conjugation of 'hablar'"""
        # Test present tense
        assert stage._conjugate('hablar', 'present', 'yo') == 'hablo'
        assert stage._conjugate('hablar', 'present', 'tú') == 'hablas'
        assert stage._conjugate('hablar', 'present', 'él') == 'habla'
        
        # Test preterite tense
        assert stage._conjugate('hablar', 'preterite', 'yo') == 'hablé'
        assert stage._conjugate('hablar', 'preterite', 'tú') == 'hablaste'
    
    def test_conjugate_comer(self, stage):
        """Test conjugation of 'comer'"""
        assert stage._conjugate('comer', 'present', 'yo') == 'como'
        assert stage._conjugate('comer', 'present', 'tú') == 'comes'
        assert stage._conjugate('comer', 'preterite', 'yo') == 'comí'
    
    def test_conjugate_unknown_verb(self, stage):
        """Test conjugation of unknown verb"""
        # Should return the infinitive for unknown verbs
        result = stage._conjugate('unknown_verb', 'present', 'yo')
        assert result == 'unknown_verb'
    
    def test_analyze_verb_conjugations(self, stage, context_with_verbs):
        """Test verb conjugation analysis"""
        conjugations = stage._analyze_verb_conjugations('hablar', context_with_verbs)
        
        assert len(conjugations) > 0
        
        # Check first conjugation
        conj = conjugations[0]
        required_fields = [
            'CardID', 'InfinitiveVerb', 'ConjugatedForm', 'Tense', 'Person',
            'Front', 'Back', 'Add Reverse', 'Sentence', 'Extra', 'RequiresMedia'
        ]
        
        for field in required_fields:
            assert field in conj
        
        # Verify structure
        assert conj['InfinitiveVerb'] == 'hablar'
        assert conj['Back'] == 'hablar'
        assert conj['Add Reverse'] == '1'
        assert conj['RequiresMedia'] == True
        assert '_____' in conj['Sentence']
    
    def test_create_example_sentence(self, stage):
        """Test example sentence creation"""
        pattern = {'tense': 'present', 'person': 'yo'}
        
        # Test known pattern
        sentence = stage._create_example_sentence('hablar', pattern)
        assert '_____' in sentence
        assert sentence == 'Yo _____ español todos los días.'
        
        # Test unknown pattern
        pattern_unknown = {'tense': 'future', 'person': 'nosotros'}
        sentence = stage._create_example_sentence('unknown_verb', pattern_unknown)
        assert '_____' in sentence
        assert 'conjugate unknown_verb' in sentence
    
    def test_get_english_translation(self, stage):
        """Test English translation of persons"""
        translations = {
            'yo': 'I',
            'tú': 'you (informal)',
            'él': 'he/she',
            'nosotros': 'we',
            'vosotros': 'you all (informal)',
            'ellos': 'they'
        }
        
        for spanish, english in translations.items():
            pattern = {'person': spanish}
            assert stage._get_english_translation(pattern) == english
        
        # Test unknown person
        pattern_unknown = {'person': 'unknown'}
        assert stage._get_english_translation(pattern_unknown) == 'unknown'
    
    def test_max_forms_per_verb_limit(self, stage):
        """Test that max_forms_per_verb setting is respected"""
        context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': ['hablar']}
        )
        
        conjugations = stage._analyze_verb_conjugations('hablar', context)
        
        # Should not exceed max_forms_per_verb (6 in test config)
        assert len(conjugations) <= 6
    
    def test_conjugation_card_ids(self, stage, context_with_verbs):
        """Test that card IDs follow expected format"""
        conjugations = stage._analyze_verb_conjugations('hablar', context_with_verbs)
        
        for conj in conjugations:
            card_id = conj['CardID']
            # Should follow format: verb_tense_person
            parts = card_id.split('_')
            assert len(parts) >= 3
            assert parts[0] == 'hablar'
            assert parts[1] in ['present', 'preterite', 'imperfect', 'future']
            assert parts[2] in ['yo', 'tú', 'él', 'nosotros', 'vosotros', 'ellos']


class TestVerbAnalysisStageIntegration:
    """Integration tests for verb analysis stage"""
    
    @pytest.fixture
    def stage(self):
        """Create verb analysis stage with full configuration"""
        config = {
            'conjugation_settings': {
                'tenses': ['present', 'preterite', 'imperfect'],
                'persons': ['yo', 'tú', 'él', 'nosotros'],
                'max_forms_per_verb': 8
            }
        }
        return VerbAnalysisStage(config)
    
    def test_multiple_verbs_analysis(self, stage):
        """Test analysis of multiple verbs"""
        context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': ['hablar', 'comer', 'vivir']}
        )
        
        result = stage.execute(context)
        assert result.status == StageStatus.SUCCESS
        
        conjugations = context.get('analyzed_conjugations')
        assert len(conjugations) > 0
        
        # Should have conjugations from all three verbs
        verbs_found = set()
        for conj in conjugations:
            verbs_found.add(conj['InfinitiveVerb'])
        
        assert 'hablar' in verbs_found
        assert 'comer' in verbs_found  
        assert 'vivir' in verbs_found
    
    def test_ser_irregular_conjugations(self, stage):
        """Test irregular verb 'ser' conjugations"""
        context = PipelineContext(
            pipeline_name='conjugation',
            project_root=Path.cwd(),
            data={'verbs': ['ser']}
        )
        
        conjugations = stage._analyze_verb_conjugations('ser', context)
        
        # Find present tense conjugations
        present_conjugations = [c for c in conjugations if c['Tense'] == 'present']
        
        # Check irregular forms
        yo_present = next((c for c in present_conjugations if c['Person'] == 'yo'), None)
        if yo_present:
            assert yo_present['ConjugatedForm'] == 'soy'
        
        tu_present = next((c for c in present_conjugations if c['Person'] == 'tú'), None)
        if tu_present:
            assert tu_present['ConjugatedForm'] == 'eres'