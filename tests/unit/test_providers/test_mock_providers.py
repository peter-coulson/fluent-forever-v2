"""
Unit tests for mock providers
"""

import pytest
from pathlib import Path
from providers.base.media_provider import MediaRequest
from providers.base.sync_provider import SyncRequest
from providers.data.memory_provider import MemoryDataProvider
from providers.media.mock_provider import MockMediaProvider
from providers.sync.mock_provider import MockSyncProvider


class TestMemoryDataProvider:
    """Test memory data provider"""
    
    def setup_method(self):
        """Set up test provider"""
        self.provider = MemoryDataProvider()
    
    def test_save_and_load(self):
        """Test basic save and load operations"""
        data = {"key": "value", "number": 42}
        
        # Save data
        success = self.provider.save_data("test", data)
        assert success is True
        
        # Load data
        loaded = self.provider.load_data("test")
        assert loaded == data
    
    def test_exists(self):
        """Test exists check"""
        assert not self.provider.exists("test")
        
        self.provider.save_data("test", {"data": "value"})
        assert self.provider.exists("test")
    
    def test_list_identifiers(self):
        """Test listing identifiers"""
        assert self.provider.list_identifiers() == []
        
        self.provider.save_data("test1", {})
        self.provider.save_data("test2", {})
        
        identifiers = self.provider.list_identifiers()
        assert "test1" in identifiers
        assert "test2" in identifiers
        assert len(identifiers) == 2
    
    def test_backup_data(self):
        """Test data backup"""
        original_data = {"original": True}
        self.provider.save_data("original", original_data)
        
        backup_id = self.provider.backup_data("original")
        assert backup_id is not None
        assert backup_id.startswith("original_backup_")
        
        # Verify backup exists and has same data
        backup_data = self.provider.load_data(backup_id)
        assert backup_data == original_data
    
    def test_clear(self):
        """Test clearing all data"""
        self.provider.save_data("test1", {})
        self.provider.save_data("test2", {})
        
        self.provider.clear()
        assert self.provider.list_identifiers() == []


class TestMockMediaProvider:
    """Test mock media provider"""
    
    def setup_method(self):
        """Set up test provider"""
        self.provider = MockMediaProvider()
    
    def test_supported_types(self):
        """Test supported media types"""
        types = self.provider.supported_types
        assert 'image' in types
        assert 'audio' in types
    
    def test_generate_media(self):
        """Test media generation"""
        request = MediaRequest(
            type='image',
            content='test image',
            params={'filename': 'test.jpg'}
        )
        
        result = self.provider.generate_media(request)
        assert result.success is True
        assert result.file_path is not None
        assert result.metadata['mock'] is True
    
    def test_generate_image_convenience(self):
        """Test generate_image convenience method"""
        result = self.provider.generate_image('test prompt', filename='test.jpg')
        assert result.success is True
        assert 'test.jpg' in str(result.file_path)
    
    def test_unsupported_type(self):
        """Test unsupported media type"""
        provider = MockMediaProvider(['image'])  # Only supports images
        
        request = MediaRequest(
            type='video',  # Unsupported
            content='test video',
            params={}
        )
        
        result = provider.generate_media(request)
        assert result.success is False
        assert "doesn't support media type" in result.error
    
    def test_failure_mode(self):
        """Test failure mode"""
        provider = MockMediaProvider(should_fail=True)
        
        request = MediaRequest(type='image', content='test', params={})
        result = provider.generate_media(request)
        
        assert result.success is False
        assert result.error is not None
    
    def test_cost_estimation(self):
        """Test cost estimation"""
        requests = [
            MediaRequest(type='image', content='img1', params={}),
            MediaRequest(type='image', content='img2', params={}),
            MediaRequest(type='audio', content='audio1', params={})
        ]
        
        cost = self.provider.get_cost_estimate(requests)
        assert cost['total_cost'] > 0
        assert cost['breakdown']['image_requests'] == 2
        assert cost['breakdown']['audio_requests'] == 1
    
    def test_request_history(self):
        """Test request history tracking"""
        request1 = MediaRequest(type='image', content='test1', params={})
        request2 = MediaRequest(type='audio', content='test2', params={})
        
        self.provider.generate_media(request1)
        self.provider.generate_media(request2)
        
        history = self.provider.get_request_history()
        assert len(history) == 2
        
        image_requests = self.provider.get_requests_by_type('image')
        assert len(image_requests) == 1
        assert image_requests[0].content == 'test1'


class TestMockSyncProvider:
    """Test mock sync provider"""
    
    def setup_method(self):
        """Set up test provider"""
        self.provider = MockSyncProvider()
    
    def test_test_connection(self):
        """Test connection testing"""
        assert self.provider.test_connection() is True
        
        self.provider.set_connection_available(False)
        assert self.provider.test_connection() is False
    
    def test_sync_templates(self):
        """Test template syncing"""
        templates = [
            {'Name': 'Card 1', 'Front': 'Front HTML', 'Back': 'Back HTML'}
        ]
        
        result = self.provider.sync_templates('test_type', templates)
        assert result.success is True
        assert result.metadata['target_id'] == 'test_type'
        assert result.metadata['template_count'] == 1
    
    def test_sync_cards(self):
        """Test card syncing"""
        cards = [
            {'CardID': 'card1', 'SpanishWord': 'hola'},
            {'CardID': 'card2', 'SpanishWord': 'adiós'}
        ]
        
        result = self.provider.sync_cards(cards)
        assert result.success is True
        assert result.metadata['total_cards'] == 2
        assert len(result.created_ids) == 2
    
    def test_sync_media(self):
        """Test media syncing"""
        media_files = [
            Path('/test/image1.jpg'),
            Path('/test/audio1.mp3')
        ]
        
        result = self.provider.sync_media(media_files)
        assert result.success is True
        assert result.metadata['total_files'] == 2
    
    def test_list_existing(self):
        """Test listing existing items"""
        # Set some existing cards
        existing = [
            {'CardID': 'existing1', 'SpanishWord': 'palabra'},
        ]
        self.provider.set_existing_cards(existing)
        
        result = self.provider.list_existing('mock')
        assert len(result) == 1
        assert result[0]['CardID'] == 'existing1'
    
    def test_failure_mode(self):
        """Test failure mode"""
        self.provider.set_failure_mode(True)
        
        result = self.provider.sync_cards([{'CardID': 'test'}])
        assert result.success is False
        assert result.error_message is not None and result.error_message != ""
    
    def test_sync_counts(self):
        """Test sync operation counting"""
        # Perform some operations
        self.provider.sync_templates('type1', [{'Name': 'template1'}])
        self.provider.sync_cards([{'CardID': 'card1'}])
        self.provider.sync_media([Path('/test/file.jpg')])
        
        counts = self.provider.get_sync_counts()
        assert counts['template_syncs'] == 1
        assert counts['card_syncs'] == 1
        assert counts['media_syncs'] == 1
        assert counts['total_templates'] == 1
        assert counts['total_cards'] == 1
        assert counts['total_media'] == 1