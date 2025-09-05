#!/usr/bin/env python3
"""
Session 4 Validation Gate: Media Provider System

Tests the contract for image/audio generation abstraction.
These tests define how media providers should abstract
external APIs for image and audio generation.

CONTRACT BEING TESTED:
- Media providers abstract external API calls
- Multiple providers can be registered and prioritized
- Failover between providers works correctly
- Cost tracking and limits are enforced
- Media file management is consistent
"""

import pytest
from typing import Dict, Any, List, Optional
from tests.e2e.conftest import MockProvider, MockOpenAI, MockForvo


class TestMediaProviderContract:
    """Test media provider basic contracts"""
    
    def test_image_provider_interface(self):
        """Contract: Image providers implement required interface"""
        provider = MockImageProvider("openai")
        
        # Should generate images
        request = {
            "prompt": "Boy eating tacos at table",
            "style": "Studio Ghibli animation style",
            "size": {"width": 1024, "height": 1024}
        }
        
        result = provider.generate_image(request)
        
        assert result["status"] == "success"
        assert "image_url" in result
        assert "cost" in result
        assert result["provider"] == "openai"
    
    def test_audio_provider_interface(self):
        """Contract: Audio providers implement required interface"""
        provider = MockAudioProvider("forvo")
        
        # Should generate/fetch audio
        request = {
            "word": "casa",
            "language": "es",
            "country_preference": ["MX", "CO"]
        }
        
        result = provider.get_pronunciation(request)
        
        assert result["status"] == "success"
        assert "audio_url" in result
        assert "metadata" in result
        assert result["provider"] == "forvo"
    
    def test_media_provider_registration(self):
        """Contract: Media providers can be registered and discovered"""
        registry = MockMediaProviderRegistry()
        
        # Register providers
        openai_provider = MockImageProvider("openai")
        runware_provider = MockImageProvider("runware")
        
        registry.register_image_provider("openai", openai_provider)
        registry.register_image_provider("runware", runware_provider)
        
        # Should be discoverable
        providers = registry.list_image_providers()
        assert "openai" in providers
        assert "runware" in providers
        
        # Should be retrievable
        assert registry.get_image_provider("openai") == openai_provider
    
    def test_provider_prioritization(self):
        """Contract: Providers can be prioritized and ordered"""
        registry = MockMediaProviderRegistry()
        
        # Register with different priorities
        registry.register_image_provider("openai", MockImageProvider("openai"), priority=1)
        registry.register_image_provider("runware", MockImageProvider("runware"), priority=2)
        
        # Should return providers in priority order
        ordered_providers = registry.get_ordered_image_providers()
        assert ordered_providers[0].name == "runware"  # Higher priority first
        assert ordered_providers[1].name == "openai"
    
    def test_provider_failover(self):
        """Contract: Failover works when providers fail"""
        registry = MockMediaProviderRegistry()
        
        # Primary provider that fails
        failing_provider = MockImageProvider("primary", should_fail=True)
        backup_provider = MockImageProvider("backup")
        
        registry.register_image_provider("primary", failing_provider, priority=2)
        registry.register_image_provider("backup", backup_provider, priority=1)
        
        # Should failover to backup
        request = {"prompt": "test image"}
        result = registry.generate_image_with_failover(request)
        
        assert result["status"] == "success"
        assert result["provider"] == "backup"


class TestMediaProviderCosts:
    """Test cost tracking and limits"""
    
    def test_cost_tracking(self):
        """Contract: Media generation costs are tracked"""
        provider = MockImageProvider("openai")
        cost_tracker = MockCostTracker()
        
        provider.set_cost_tracker(cost_tracker)
        
        # Generate images and track costs
        for i in range(3):
            request = {"prompt": f"test image {i}"}
            result = provider.generate_image(request)
            assert result["cost"] > 0
        
        # Costs should be accumulated
        total_cost = cost_tracker.get_total_cost("openai")
        assert total_cost == 0.12  # 3 * 0.04 per image
    
    def test_cost_limits(self):
        """Contract: Cost limits are enforced"""
        provider = MockImageProvider("openai")
        cost_tracker = MockCostTracker(limit=0.08)  # Limit to 2 images
        
        provider.set_cost_tracker(cost_tracker)
        
        # Should allow within limit
        provider.generate_image({"prompt": "test 1"})  # $0.04
        provider.generate_image({"prompt": "test 2"})  # $0.08
        
        # Should reject over limit
        with pytest.raises(CostLimitExceededError):
            provider.generate_image({"prompt": "test 3"})  # Would be $0.12
    
    def test_cost_estimation(self):
        """Contract: Providers can estimate costs before execution"""
        provider = MockImageProvider("openai")
        
        # Should estimate cost
        request = {"prompt": "test image", "count": 3}
        estimated_cost = provider.estimate_cost(request)
        
        assert estimated_cost == 0.12  # 3 * 0.04
    
    def test_daily_cost_limits(self):
        """Contract: Daily cost limits are enforced"""
        cost_tracker = MockCostTracker(daily_limit=0.20)
        
        # Track costs over multiple days
        cost_tracker.record_cost("openai", 0.16, "2024-01-01")  # Day 1
        cost_tracker.record_cost("openai", 0.08, "2024-01-02")  # Day 2
        
        # Should allow within daily limit
        assert cost_tracker.can_spend("openai", 0.04, "2024-01-02") is True
        
        # Should reject over daily limit
        assert cost_tracker.can_spend("openai", 0.16, "2024-01-02") is False


class TestMediaFileManagement:
    """Test media file management contracts"""
    
    def test_media_file_storage(self):
        """Contract: Media files are stored consistently"""
        manager = MockMediaFileManager()
        
        # Should store image files
        image_data = b"fake_image_data"
        image_path = manager.store_image_file("casa_house.png", image_data)
        
        assert image_path.endswith("casa_house.png")
        assert manager.file_exists(image_path)
        
        # Should store audio files
        audio_data = b"fake_audio_data"
        audio_path = manager.store_audio_file("casa.mp3", audio_data)
        
        assert audio_path.endswith("casa.mp3")
        assert manager.file_exists(audio_path)
    
    def test_media_file_deduplication(self):
        """Contract: Duplicate media files are avoided"""
        manager = MockMediaFileManager()
        
        # Store same file twice
        data = b"test_data"
        path1 = manager.store_image_file("test.png", data)
        path2 = manager.store_image_file("test.png", data)
        
        # Should return same path (deduplicated)
        assert path1 == path2
        assert manager.get_file_count() == 1
    
    def test_media_file_cleanup(self):
        """Contract: Unused media files can be cleaned up"""
        manager = MockMediaFileManager()
        
        # Store files
        used_path = manager.store_image_file("used.png", b"data1")
        unused_path = manager.store_image_file("unused.png", b"data2")
        
        # Mark one as used
        manager.mark_file_as_used("used.png")
        
        # Cleanup unused files
        cleaned_count = manager.cleanup_unused_files()
        
        assert cleaned_count == 1
        assert manager.file_exists(used_path)
        assert not manager.file_exists(unused_path)
    
    def test_media_metadata_tracking(self):
        """Contract: Media file metadata is tracked"""
        manager = MockMediaFileManager()
        
        # Store file with metadata
        metadata = {
            "card_id": "casa_house",
            "prompt": "House in countryside",
            "provider": "openai",
            "cost": 0.04
        }
        
        path = manager.store_image_file("casa_house.png", b"data", metadata)
        
        # Should retrieve metadata
        retrieved_metadata = manager.get_file_metadata(path)
        assert retrieved_metadata["card_id"] == "casa_house"
        assert retrieved_metadata["cost"] == 0.04


class TestMediaProviderErrorHandling:
    """Test error handling in media providers"""
    
    def test_api_rate_limiting(self):
        """Contract: API rate limits are handled gracefully"""
        provider = MockImageProvider("openai")
        provider.set_rate_limit(requests_per_minute=2)
        
        # Should handle rate limiting
        provider.generate_image({"prompt": "test 1"})
        provider.generate_image({"prompt": "test 2"})
        
        # Third request should trigger rate limit
        with pytest.raises(RateLimitError):
            provider.generate_image({"prompt": "test 3"})
    
    def test_api_authentication_errors(self):
        """Contract: Authentication errors are handled properly"""
        provider = MockImageProvider("openai", api_key="invalid_key")
        
        with pytest.raises(AuthenticationError):
            provider.generate_image({"prompt": "test"})
    
    def test_network_timeout_handling(self):
        """Contract: Network timeouts are handled gracefully"""
        provider = MockImageProvider("openai")
        provider.set_timeout(0.1)  # Very short timeout
        
        # Long-running request should timeout
        request = {"prompt": "complex image", "processing_time": 0.5}
        
        with pytest.raises(TimeoutError):
            provider.generate_image(request)
    
    def test_invalid_content_handling(self):
        """Contract: Invalid content requests are handled"""
        provider = MockImageProvider("openai")
        
        # Request with policy violation
        invalid_request = {"prompt": "violent content that violates policy"}
        
        with pytest.raises(ContentPolicyError):
            provider.generate_image(invalid_request)


# Mock Media Provider Implementations
class MockImageProvider(MockProvider):
    """Mock image generation provider"""
    
    def __init__(self, name: str, should_fail: bool = False, api_key: str = "valid_key"):
        super().__init__(name, should_fail)
        self.api_key = api_key
        self.cost_per_image = 0.04
        self.cost_tracker = None
        self.rate_limit = None
        self.request_count = 0
        self.timeout = 30.0
    
    def generate_image(self, request: Dict[str, Any]) -> Dict[str, Any]:
        self.request_count += 1
        
        # Check authentication
        if self.api_key == "invalid_key":
            raise AuthenticationError("Invalid API key")
        
        # Check rate limiting
        if self.rate_limit and self.request_count > self.rate_limit:
            raise RateLimitError("Rate limit exceeded")
        
        # Check timeout
        processing_time = request.get("processing_time", 0.1)
        if processing_time > self.timeout:
            raise TimeoutError("Request timed out")
        
        # Check content policy
        if "violent" in request.get("prompt", "").lower():
            raise ContentPolicyError("Content violates policy")
        
        if self.should_fail:
            raise RuntimeError(f"Provider {self.name} failed")
        
        # Calculate cost
        count = request.get("count", 1)
        cost = self.cost_per_image * count
        
        # Track cost
        if self.cost_tracker:
            self.cost_tracker.record_cost(self.name, cost)
        
        return {
            "status": "success",
            "provider": self.name,
            "image_url": f"https://example.com/{self.name}/image.png",
            "cost": cost,
            "metadata": {
                "prompt": request.get("prompt"),
                "size": request.get("size", {"width": 1024, "height": 1024})
            }
        }
    
    def estimate_cost(self, request: Dict[str, Any]) -> float:
        """Estimate generation cost"""
        count = request.get("count", 1)
        return self.cost_per_image * count
    
    def set_cost_tracker(self, tracker):
        """Set cost tracker"""
        self.cost_tracker = tracker
    
    def set_rate_limit(self, requests_per_minute: int):
        """Set rate limit"""
        self.rate_limit = requests_per_minute
    
    def set_timeout(self, timeout: float):
        """Set timeout"""
        self.timeout = timeout


class MockAudioProvider(MockProvider):
    """Mock audio generation/fetching provider"""
    
    def __init__(self, name: str, should_fail: bool = False):
        super().__init__(name, should_fail)
        self.pronunciations_db = {
            "casa": {
                "es": [
                    {
                        "country": "MX",
                        "url": "https://forvo.com/casa_mx.mp3",
                        "quality": "high"
                    },
                    {
                        "country": "ES", 
                        "url": "https://forvo.com/casa_es.mp3",
                        "quality": "medium"
                    }
                ]
            }
        }
    
    def get_pronunciation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if self.should_fail:
            raise RuntimeError(f"Provider {self.name} failed")
        
        word = request["word"]
        language = request["language"]
        preferences = request.get("country_preference", [])
        
        if word not in self.pronunciations_db:
            raise AudioNotFoundError(f"No pronunciation found for {word}")
        
        pronunciations = self.pronunciations_db[word].get(language, [])
        
        # Find best match based on country preference
        best_match = None
        for pref in preferences:
            for pron in pronunciations:
                if pron["country"] == pref:
                    best_match = pron
                    break
            if best_match:
                break
        
        if not best_match:
            best_match = pronunciations[0] if pronunciations else None
        
        if not best_match:
            raise AudioNotFoundError(f"No pronunciation found for {word} in {language}")
        
        return {
            "status": "success",
            "provider": self.name,
            "audio_url": best_match["url"],
            "metadata": {
                "word": word,
                "language": language,
                "country": best_match["country"],
                "quality": best_match["quality"]
            }
        }


class MockMediaProviderRegistry:
    """Mock media provider registry"""
    
    def __init__(self):
        self.image_providers = {}
        self.audio_providers = {}
        self.provider_priorities = {}
    
    def register_image_provider(self, name: str, provider: MockImageProvider, priority: int = 1):
        """Register image provider with priority"""
        self.image_providers[name] = provider
        self.provider_priorities[name] = priority
    
    def register_audio_provider(self, name: str, provider: MockAudioProvider, priority: int = 1):
        """Register audio provider with priority"""
        self.audio_providers[name] = provider
        self.provider_priorities[name] = priority
    
    def get_image_provider(self, name: str) -> Optional[MockImageProvider]:
        """Get image provider by name"""
        return self.image_providers.get(name)
    
    def list_image_providers(self) -> List[str]:
        """List registered image providers"""
        return list(self.image_providers.keys())
    
    def get_ordered_image_providers(self) -> List[MockImageProvider]:
        """Get image providers ordered by priority"""
        sorted_names = sorted(self.image_providers.keys(), 
                            key=lambda name: self.provider_priorities.get(name, 1), 
                            reverse=True)
        return [self.image_providers[name] for name in sorted_names]
    
    def generate_image_with_failover(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate image with automatic failover"""
        providers = self.get_ordered_image_providers()
        last_error = None
        
        for provider in providers:
            try:
                return provider.generate_image(request)
            except Exception as e:
                last_error = e
                continue
        
        raise last_error or RuntimeError("All providers failed")


class MockCostTracker:
    """Mock cost tracking system"""
    
    def __init__(self, limit: float = None, daily_limit: float = None):
        self.costs = {}
        self.daily_costs = {}
        self.limit = limit
        self.daily_limit = daily_limit
    
    def record_cost(self, provider: str, cost: float, date: str = "2024-01-01"):
        """Record cost for provider"""
        # Check limits before recording
        if self.limit and self.get_total_cost(provider) + cost > self.limit:
            raise CostLimitExceededError(f"Cost limit exceeded for {provider}")
        
        # Record cost
        if provider not in self.costs:
            self.costs[provider] = 0
        self.costs[provider] += cost
        
        # Record daily cost
        if provider not in self.daily_costs:
            self.daily_costs[provider] = {}
        if date not in self.daily_costs[provider]:
            self.daily_costs[provider][date] = 0
        self.daily_costs[provider][date] += cost
    
    def get_total_cost(self, provider: str) -> float:
        """Get total cost for provider"""
        return self.costs.get(provider, 0.0)
    
    def can_spend(self, provider: str, amount: float, date: str = "2024-01-01") -> bool:
        """Check if provider can spend amount on date"""
        if self.daily_limit:
            current_daily = self.daily_costs.get(provider, {}).get(date, 0)
            return current_daily + amount <= self.daily_limit
        return True


class MockMediaFileManager:
    """Mock media file manager"""
    
    def __init__(self):
        self.files = {}
        self.metadata = {}
        self.used_files = set()
    
    def store_image_file(self, filename: str, data: bytes, metadata: Dict[str, Any] = None) -> str:
        """Store image file"""
        path = f"/media/images/{filename}"
        
        # Check for deduplication
        if path in self.files:
            return path
        
        self.files[path] = data
        if metadata:
            self.metadata[path] = metadata
        
        return path
    
    def store_audio_file(self, filename: str, data: bytes, metadata: Dict[str, Any] = None) -> str:
        """Store audio file"""
        path = f"/media/audio/{filename}"
        
        if path in self.files:
            return path
        
        self.files[path] = data
        if metadata:
            self.metadata[path] = metadata
        
        return path
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        return path in self.files
    
    def get_file_count(self) -> int:
        """Get total file count"""
        return len(self.files)
    
    def mark_file_as_used(self, filename: str):
        """Mark file as used"""
        self.used_files.add(filename)
    
    def cleanup_unused_files(self) -> int:
        """Clean up unused files, return count cleaned"""
        to_remove = []
        for path in self.files:
            filename = path.split("/")[-1]
            if filename not in self.used_files:
                to_remove.append(path)
        
        for path in to_remove:
            del self.files[path]
            if path in self.metadata:
                del self.metadata[path]
        
        return len(to_remove)
    
    def get_file_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        return self.metadata.get(path)


# Custom Exceptions for Testing
class CostLimitExceededError(Exception):
    """Cost limit exceeded"""
    pass


class RateLimitError(Exception):
    """Rate limit exceeded"""
    pass


class AuthenticationError(Exception):
    """Authentication failed"""
    pass


class ContentPolicyError(Exception):
    """Content violates policy"""
    pass


class AudioNotFoundError(Exception):
    """Audio not found"""
    pass