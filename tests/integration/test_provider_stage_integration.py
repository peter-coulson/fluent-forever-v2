"""
Integration tests for provider-stage system
"""

import pytest
from pathlib import Path
from core.context import PipelineContext
from providers import setup_providers_in_context, get_provider_from_context
from stages.media.provider_image_stage import ProviderImageGenerationStage
from core.stages import StageStatus


class TestProviderStageIntegration:
    """Test integration between providers and stages"""
    
    def test_provider_setup_in_context(self):
        """Test setting up providers in pipeline context"""
        # Create pipeline context
        context = PipelineContext("test_pipeline", Path.cwd())
        
        # Setup providers with minimal config
        config = {
            'apis': {},
            'image_generation': {'primary_provider': 'openai'}
        }
        
        # This should not fail even without API keys
        setup_providers_in_context(context, config)
        
        # Verify providers are available
        media_provider = get_provider_from_context(context, 'media')
        data_provider = get_provider_from_context(context, 'data')
        sync_provider = get_provider_from_context(context, 'sync')
        
        assert media_provider is not None, "Media provider should be available"
        assert data_provider is not None, "Data provider should be available"
        assert sync_provider is not None, "Sync provider should be available"
    
    def test_image_stage_with_mock_provider(self):
        """Test image generation stage with mock provider"""
        # Create pipeline context
        context = PipelineContext("test_pipeline", Path.cwd())
        
        # Setup mock provider manually
        from providers.media.mock_provider import MockMediaProvider
        mock_provider = MockMediaProvider(['image'])
        context.set('providers.image', mock_provider)
        
        # Create image requests
        image_requests = [
            {
                'prompt': 'A cat sitting on a chair',
                'filename': 'cat_chair.jpg',
                'card_id': 'test_card_1'
            },
            {
                'prompt': 'A dog running in a park',
                'filename': 'dog_park.jpg',
                'card_id': 'test_card_2'
            }
        ]
        context.set('image_requests', image_requests)
        
        # Execute image generation stage
        stage = ProviderImageGenerationStage()
        result = stage.execute(context)
        
        # Verify results
        assert result.status == StageStatus.SUCCESS
        assert result.data['success_count'] == 2
        assert result.data['total_count'] == 2
        
        # Check generated images in context
        generated_images = context.get('generated_images')
        assert len(generated_images) == 2
        assert all(img['success'] for img in generated_images)
    
    def test_image_stage_with_unsupported_provider(self):
        """Test image stage with provider that doesn't support images"""
        # Create pipeline context
        context = PipelineContext("test_pipeline", Path.cwd())
        
        # Setup mock provider that only supports audio
        from providers.media.mock_provider import MockMediaProvider
        mock_provider = MockMediaProvider(['audio'])  # No image support
        context.set('providers.image', mock_provider)
        
        # Create image requests
        context.set('image_requests', [{'prompt': 'test', 'filename': 'test.jpg'}])
        
        # Execute image generation stage
        stage = ProviderImageGenerationStage()
        result = stage.execute(context)
        
        # Should fail because provider doesn't support images
        assert result.status == StageStatus.FAILURE
        assert "does not support image generation" in result.message
    
    def test_image_stage_without_provider(self):
        """Test image stage when provider is missing"""
        # Create pipeline context without image provider
        context = PipelineContext("test_pipeline", Path.cwd())
        context.set('image_requests', [{'prompt': 'test', 'filename': 'test.jpg'}])
        
        # Execute image generation stage
        stage = ProviderImageGenerationStage(required=True)
        result = stage.execute(context)
        
        # Should fail because provider is missing
        assert result.status == StageStatus.FAILURE
        assert "Provider image not available" in result.message
    
    def test_optional_provider_stage(self):
        """Test stage with optional provider that's missing"""
        # Create pipeline context without provider
        context = PipelineContext("test_pipeline", Path.cwd())
        
        # Execute optional stage
        stage = ProviderImageGenerationStage(required=False)
        result = stage.execute(context)
        
        # Should succeed but skip processing
        assert result.status == StageStatus.SUCCESS
        assert "not available, skipped" in result.message
    
    def test_stage_with_provider_failure(self):
        """Test stage behavior when provider fails"""
        # Create pipeline context
        context = PipelineContext("test_pipeline", Path.cwd())
        
        # Setup mock provider in failure mode
        from providers.media.mock_provider import MockMediaProvider
        mock_provider = MockMediaProvider(['image'], should_fail=True)
        context.set('providers.image', mock_provider)
        
        # Create image requests
        context.set('image_requests', [
            {'prompt': 'test prompt', 'filename': 'test.jpg', 'card_id': 'test'}
        ])
        
        # Execute stage
        stage = ProviderImageGenerationStage()
        result = stage.execute(context)
        
        # Should report failure
        assert result.status == StageStatus.FAILURE
        assert result.data['success_count'] == 0
        assert len(result.errors) > 0