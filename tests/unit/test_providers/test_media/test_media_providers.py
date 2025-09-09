#!/usr/bin/env python3
"""
Unit tests for Media Providers after migration from APIs

Tests media provider functionality in the new provider structure.
"""

import pytest
import tempfile
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from providers.media.forvo_provider import ForvoProvider
from providers.media.openai_provider import OpenAIProvider
from providers.media.runware_provider import RunwareProvider
from providers.base.media_provider import MediaRequest, MediaResult


class TestForvoProvider:
    """Test Forvo audio provider"""
    
    @patch.dict(os.environ, {'FORVO_API_KEY': 'test_key'})
    def setup_method(self, method):
        """Set up test provider"""
        self.provider = ForvoProvider()
    
    def test_supported_types(self):
        """Test supported media types"""
        assert 'audio' in self.provider.supported_types
    
    @patch('requests.get')
    def test_generate_audio(self, mock_get):
        """Test audio generation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake_audio_data'
        mock_get.return_value = mock_response
        
        request = MediaRequest(
            type='audio',
            content='hola',
            params={'language': 'es'}
        )
        
        result = self.provider.generate_media(request)
        
        # Should succeed in mock environment
        assert isinstance(result, MediaResult)
    
    def test_unsupported_type(self):
        """Test unsupported media type handling"""
        request = MediaRequest(
            type='image',
            content='test',
            params={}
        )
        
        result = self.provider.generate_media(request)
        
        assert not result.success
        assert result.error is not None


class TestOpenAIProvider:
    """Test OpenAI media provider"""
    
    def setup_method(self):
        """Set up test provider"""
        self.provider = OpenAIProvider()
    
    def test_supported_types(self):
        """Test supported media types"""
        assert 'image' in self.provider.supported_types
        assert 'audio' in self.provider.supported_types
    
    def test_generate_image(self):
        """Test image generation (placeholder implementation)"""
        request = MediaRequest(
            type='image',
            content='a red apple',
            params={'size': '512x512'}
        )
        
        result = self.provider.generate_media(request)
        
        # Since this is a placeholder implementation, it should return failure
        assert isinstance(result, MediaResult)
        assert not result.success
        assert "not yet implemented" in result.error
    
    def test_cost_estimation(self):
        """Test cost estimation functionality"""
        request = MediaRequest(
            type='image',
            content='test prompt',
            params={'size': '1024x1024'}
        )
        
        cost = self.provider.estimate_cost(request)
        
        assert isinstance(cost, (int, float))
        assert cost >= 0


class TestRunwareProvider:
    """Test Runware image provider"""
    
    def setup_method(self):
        """Set up test provider"""
        self.provider = RunwareProvider()
    
    def test_supported_types(self):
        """Test supported media types"""
        assert 'image' in self.provider.supported_types
    
    def test_generate_image(self):
        """Test image generation (placeholder implementation)"""
        request = MediaRequest(
            type='image',
            content='a blue car',
            params={'width': 512, 'height': 512}
        )
        
        result = self.provider.generate_media(request)
        
        # Since this is a placeholder implementation, it should return failure
        assert isinstance(result, MediaResult)
        assert not result.success
        assert "not yet implemented" in result.error
    
    def test_batch_processing(self):
        """Test batch image processing"""
        requests = [
            MediaRequest(type='image', content='cat', params={}),
            MediaRequest(type='image', content='dog', params={})
        ]
        
        with patch.object(self.provider, 'generate_media') as mock_generate:
            mock_generate.return_value = MediaResult(
                success=True,
                file_path=Path('/fake/path/image.jpg'),
                metadata={}
            )
            
            results = self.provider.generate_batch(requests)
            
            assert len(results) == 2
            assert all(isinstance(r, MediaResult) for r in results)


class TestMediaRequest:
    """Test MediaRequest data structure"""
    
    def test_media_request_creation(self):
        """Test MediaRequest object creation"""
        request = MediaRequest(
            type='image',
            content='test prompt',
            params={'size': '512x512'}
        )
        
        assert request.type == 'image'
        assert request.content == 'test prompt'
        assert request.params['size'] == '512x512'
        assert request.output_path is None
    
    def test_media_request_validation(self):
        """Test MediaRequest validation"""
        # Should raise ValueError for empty type
        with pytest.raises(ValueError, match="Media request type cannot be empty"):
            MediaRequest(type='', content='test', params={})
        
        # Should raise ValueError for empty content
        with pytest.raises(ValueError, match="Media request content cannot be empty"):
            MediaRequest(type='image', content='', params={})
    
    def test_media_request_defaults(self):
        """Test MediaRequest default values"""
        request = MediaRequest(
            type='image',
            content='test',
            params=None
        )
        
        assert request.params == {}


class TestMediaResult:
    """Test MediaResult data structure"""
    
    def test_media_result_creation(self):
        """Test MediaResult object creation"""
        result = MediaResult(
            success=True,
            file_path=Path('/test/path.jpg'),
            metadata={'width': 512, 'height': 512}
        )
        
        assert result.success is True
        assert result.file_path == Path('/test/path.jpg')
        assert result.metadata['width'] == 512
        assert result.error is None
    
    def test_media_result_defaults(self):
        """Test MediaResult default values"""
        result = MediaResult(
            success=False,
            file_path=None,
            metadata=None
        )
        
        assert result.metadata == {}
        assert result.error is None


if __name__ == "__main__":
    pytest.main([__file__])