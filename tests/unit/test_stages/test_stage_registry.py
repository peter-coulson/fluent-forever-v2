"""
Tests for stage registry functionality
"""

import pytest
from stages import get_stage, list_stages, get_stage_info, STAGE_REGISTRY


def test_stage_registry_contains_expected_stages():
    """Test that the stage registry contains expected stages"""
    expected_stages = [
        'analyze_words',
        'prepare_batch',
        'ingest_batch', 
        'generate_images',
        'generate_audio',
        'generate_media',
        'sync_templates',
        'sync_cards',
        'sync_media',
        'validate_data',
        'validate_ipa',
        'validate_media',
        'load_file',
        'save_file'
    ]
    
    available_stages = list_stages()
    
    for stage_name in expected_stages:
        assert stage_name in available_stages, f"Expected stage '{stage_name}' not found in registry"


def test_get_stage_creates_valid_instances():
    """Test that get_stage creates valid stage instances"""
    # Test a few key stages
    test_stages = ['analyze_words', 'validate_data', 'generate_media']
    
    for stage_name in test_stages:
        stage = get_stage(stage_name)
        
        # Should have required stage interface
        assert hasattr(stage, 'name'), f"Stage {stage_name} missing 'name' property"
        assert hasattr(stage, 'display_name'), f"Stage {stage_name} missing 'display_name' property"
        assert hasattr(stage, 'execute'), f"Stage {stage_name} missing 'execute' method"
        
        # Name should match
        assert stage.name == stage_name, f"Stage name mismatch: expected {stage_name}, got {stage.name}"


def test_get_stage_with_invalid_name():
    """Test that get_stage raises error for invalid stage name"""
    with pytest.raises(ValueError) as exc_info:
        get_stage('nonexistent_stage')
    
    assert 'Unknown stage: nonexistent_stage' in str(exc_info.value)


def test_get_stage_info():
    """Test stage info retrieval"""
    info = get_stage_info('analyze_words')
    
    assert 'name' in info
    assert 'class' in info
    assert 'module' in info
    assert 'docstring' in info
    
    assert info['name'] == 'analyze_words'
    assert 'WordAnalysisStage' in info['class']


def test_get_stage_info_invalid_name():
    """Test stage info for invalid name"""
    with pytest.raises(ValueError):
        get_stage_info('invalid_stage')


def test_registry_completeness():
    """Test that all stages in registry are accessible"""
    for stage_name in STAGE_REGISTRY.keys():
        # Should be able to create instance
        stage = get_stage(stage_name)
        assert stage is not None
        
        # Should be able to get info
        info = get_stage_info(stage_name)
        assert info is not None