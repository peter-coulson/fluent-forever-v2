"""
Tests for base stage classes
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from core.context import PipelineContext
from core.stages import StageStatus
from stages.base.file_stage import FileLoadStage, FileSaveStage
from stages.base.validation_stage import ValidationStage
from stages.base.api_stage import APIStage


class TestFileLoadStage:
    """Test FileLoadStage functionality"""
    
    def test_load_existing_file(self):
        """Test loading an existing JSON file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / 'test.json'
            test_data = {'test': 'data', 'count': 42}
            
            # Create test file
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            
            # Create context
            context = PipelineContext('test_pipeline', temp_path)
            context.set('test_file', str(test_file))
            
            # Create and execute stage
            stage = FileLoadStage('test_file')
            result = stage.execute(context)
            
            # Check result
            assert result.status == StageStatus.SUCCESS
            assert result.data['test'] == test_data
            assert context.get('test') == test_data
    
    def test_load_missing_required_file(self):
        """Test loading a missing required file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing_file = temp_path / 'missing.json'
            
            context = PipelineContext('test_pipeline', temp_path)
            context.set('missing_file', str(missing_file))
            
            stage = FileLoadStage('missing_file', required=True)
            result = stage.execute(context)
            
            assert result.status == StageStatus.FAILURE
            assert 'not found' in result.message.lower()
    
    def test_load_missing_optional_file(self):
        """Test loading a missing optional file with default"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing_file = temp_path / 'missing.json'
            default_data = {'default': True}
            
            context = PipelineContext('test_pipeline', temp_path)
            context.set('missing_file', str(missing_file))
            
            stage = FileLoadStage('missing_file', required=False, default_value=default_data)
            result = stage.execute(context)
            
            assert result.status == StageStatus.SUCCESS
            assert context.get('missing') == default_data


class TestFileSaveStage:
    """Test FileSaveStage functionality"""
    
    def test_save_file(self):
        """Test saving data to file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_file = temp_path / 'output.json'
            test_data = {'saved': 'data', 'timestamp': '2024-01-01'}
            
            context = PipelineContext('test_pipeline', temp_path)
            context.set('output_data', test_data)
            context.set('output_file', str(output_file))
            
            stage = FileSaveStage('output_data', 'output_file')
            result = stage.execute(context)
            
            assert result.status == StageStatus.SUCCESS
            assert output_file.exists()
            
            # Verify file contents
            with open(output_file, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == test_data


class TestValidationStage:
    """Test ValidationStage base class"""
    
    def test_validation_success(self):
        """Test successful validation"""
        class TestValidator(ValidationStage):
            def __init__(self):
                super().__init__('test_data')
            
            def validate_data(self, data):
                return []  # No errors
        
        with tempfile.TemporaryDirectory() as temp_dir:
            context = PipelineContext('test_pipeline', Path(temp_dir))
            context.set('test_data', {'valid': 'data'})
            
            stage = TestValidator()
            result = stage.execute(context)
            
            assert result.status == StageStatus.SUCCESS
    
    def test_validation_failure(self):
        """Test validation failure"""
        class TestValidator(ValidationStage):
            def __init__(self):
                super().__init__('test_data')
            
            def validate_data(self, data):
                return ['Error 1', 'Error 2']  # Validation errors
        
        with tempfile.TemporaryDirectory() as temp_dir:
            context = PipelineContext('test_pipeline', Path(temp_dir))
            context.set('test_data', {'invalid': 'data'})
            
            stage = TestValidator()
            result = stage.execute(context)
            
            assert result.status == StageStatus.FAILURE
            assert len(result.errors) == 2


class TestAPIStage:
    """Test APIStage base class"""
    
    def test_api_stage_with_provider(self):
        """Test API stage with available provider"""
        class TestAPIStage(APIStage):
            def __init__(self):
                super().__init__('test_provider')
            
            def execute_api_call(self, context, provider):
                from core.stages import StageResult, StageStatus
                return StageResult(
                    status=StageStatus.SUCCESS,
                    message="API call successful",
                    data={'result': 'success'},
                    errors=[]
                )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            context = PipelineContext('test_pipeline', Path(temp_dir))
            mock_provider = Mock()
            context.set('providers.test_provider', mock_provider)
            
            stage = TestAPIStage()
            result = stage.execute(context)
            
            assert result.status == StageStatus.SUCCESS
    
    def test_api_stage_missing_provider(self):
        """Test API stage with missing required provider"""
        class TestAPIStage(APIStage):
            def __init__(self):
                super().__init__('missing_provider')
            
            def execute_api_call(self, context, provider):
                pass  # Should not be called
        
        with tempfile.TemporaryDirectory() as temp_dir:
            context = PipelineContext('test_pipeline', Path(temp_dir))
            
            stage = TestAPIStage()
            result = stage.execute(context)
            
            assert result.status == StageStatus.FAILURE
            assert 'not available' in result.message.lower()