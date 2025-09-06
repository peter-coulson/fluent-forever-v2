"""
Mock Media Provider

Mock provider for testing that simulates media generation without API calls.
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from providers.base.media_provider import MediaProvider, MediaRequest, MediaResult


class MockMediaProvider(MediaProvider):
    """Mock media provider for testing"""
    
    def __init__(self, supported_types: Optional[List[str]] = None, should_fail: bool = False):
        """Initialize mock media provider
        
        Args:
            supported_types: List of media types to support (default: ['image', 'audio'])
            should_fail: If True, generation will always fail (for error testing)
        """
        self._supported_types = supported_types or ['image', 'audio']
        self.should_fail = should_fail
        self.generated_requests: List[MediaRequest] = []
        self.generation_count = 0
    
    @property
    def supported_types(self) -> List[str]:
        """Return configured supported types"""
        return self._supported_types
    
    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Mock media generation
        
        Args:
            request: MediaRequest to process
            
        Returns:
            MediaResult with mock data
        """
        # Track all requests for testing verification
        self.generated_requests.append(request)
        self.generation_count += 1
        
        # Simulate failure if configured
        if self.should_fail:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={'mock': True, 'failure_mode': True},
                error="Mock provider configured to fail"
            )
        
        # Check if type is supported
        if not self.supports_type(request.type):
            return MediaResult(
                success=False,
                file_path=None,
                metadata={'mock': True},
                error=f"Mock provider doesn't support media type: {request.type}"
            )
        
        # Simulate some processing time
        time.sleep(0.1)  # Small delay to simulate API call
        
        # Create mock file path
        filename = request.params.get('filename', f'mock_{request.type}_{self.generation_count}')
        if request.type == 'image':
            if not filename.endswith(('.jpg', '.png', '.jpeg')):
                filename += '.jpg'
        elif request.type == 'audio':
            if not filename.endswith(('.mp3', '.wav')):
                filename += '.mp3'
        
        if request.output_path:
            mock_file_path = request.output_path / filename
        else:
            mock_file_path = Path(f"/mock/media/{request.type}/{filename}")
        
        return MediaResult(
            success=True,
            file_path=mock_file_path,
            metadata={
                'mock': True,
                'request_count': len(self.generated_requests),
                'generation_id': self.generation_count,
                'content': request.content,
                'type': request.type,
                'params': request.params
            },
            error=None
        )
    
    def get_cost_estimate(self, requests: List[MediaRequest]) -> Dict[str, float]:
        """Mock cost estimation
        
        Args:
            requests: List of requests to estimate
            
        Returns:
            Mock cost breakdown
        """
        supported_requests = [r for r in requests if self.supports_type(r.type)]
        num_requests = len(supported_requests)
        
        # Mock costs: $0.01 per image, $0.005 per audio
        image_requests = [r for r in supported_requests if r.type == 'image']
        audio_requests = [r for r in supported_requests if r.type == 'audio']
        
        image_cost = len(image_requests) * 0.01
        audio_cost = len(audio_requests) * 0.005
        total_cost = image_cost + audio_cost
        
        return {
            'total_cost': total_cost,
            'breakdown': {
                'provider': 'Mock',
                'total_requests': num_requests,
                'image_requests': len(image_requests),
                'audio_requests': len(audio_requests),
                'image_cost': image_cost,
                'audio_cost': audio_cost,
                'note': 'Mock costs for testing'
            }
        }
    
    # Testing utility methods
    def clear_history(self) -> None:
        """Clear request history (testing utility)"""
        self.generated_requests.clear()
        self.generation_count = 0
    
    def get_request_history(self) -> List[MediaRequest]:
        """Get history of all requests (testing utility)"""
        return self.generated_requests.copy()
    
    def get_requests_by_type(self, media_type: str) -> List[MediaRequest]:
        """Get requests filtered by media type (testing utility)"""
        return [r for r in self.generated_requests if r.type == media_type]
    
    def set_failure_mode(self, should_fail: bool) -> None:
        """Enable/disable failure mode (testing utility)"""
        self.should_fail = should_fail
    
    def add_supported_type(self, media_type: str) -> None:
        """Add supported media type (testing utility)"""
        if media_type not in self._supported_types:
            self._supported_types.append(media_type)
    
    def remove_supported_type(self, media_type: str) -> None:
        """Remove supported media type (testing utility)"""
        if media_type in self._supported_types:
            self._supported_types.remove(media_type)