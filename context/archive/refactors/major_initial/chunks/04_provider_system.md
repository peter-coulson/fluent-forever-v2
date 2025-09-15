# Session 4: Provider System

## Mission
Abstract all external dependencies (APIs, data sources, sync targets) into pluggable providers that can be mocked, swapped, or configured independently.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `context/refactor/completed_handoffs/03_stage_system_handoff.md` - Stage system context
- `tests/e2e/03_provider_system/` - Validation gates for this session
- `src/core/` and `src/stages/` - Previous session implementations
- Current API clients to abstract: `src/apis/`

## Objectives

### Primary Goal
Create a provider system that abstracts all external dependencies, making the system testable, configurable, and extensible.

### Target Architecture
```
src/
├── providers/
│   ├── __init__.py
│   ├── base/                    # Base provider interfaces
│   │   ├── __init__.py
│   │   ├── data_provider.py    # Data source abstraction
│   │   ├── media_provider.py   # Media generation abstraction
│   │   └── sync_provider.py    # Sync target abstraction
│   ├── data/                    # Data source providers
│   │   ├── __init__.py
│   │   ├── json_provider.py    # JSON file provider
│   │   └── memory_provider.py  # In-memory provider (testing)
│   ├── media/                   # Media generation providers
│   │   ├── __init__.py
│   │   ├── openai_provider.py  # OpenAI image/text
│   │   ├── forvo_provider.py   # Forvo audio
│   │   └── mock_provider.py    # Mock provider (testing)
│   ├── sync/                    # Sync target providers
│   │   ├── __init__.py
│   │   ├── anki_provider.py    # AnkiConnect
│   │   └── mock_provider.py    # Mock sync (testing)
│   └── registry.py             # Provider registry and factory
```

## Implementation Requirements

### 1. Base Provider Interfaces (`src/providers/base/`)

#### Data Provider Interface (`data_provider.py`)
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path

class DataProvider(ABC):
    """Abstract interface for data sources"""

    @abstractmethod
    def load_data(self, identifier: str) -> Dict[str, Any]:
        """Load data by identifier (e.g., filename, key)"""
        pass

    @abstractmethod
    def save_data(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Save data to identifier. Return True if successful."""
        pass

    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """Check if data exists for identifier"""
        pass

    @abstractmethod
    def list_identifiers(self) -> List[str]:
        """List all available data identifiers"""
        pass

    def backup_data(self, identifier: str) -> Optional[str]:
        """Create backup of data. Return backup identifier if successful."""
        return None  # Optional for providers
```

#### Media Provider Interface (`media_provider.py`)
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass

@dataclass
class MediaRequest:
    """Request for media generation"""
    type: str  # 'image' or 'audio'
    content: str  # Prompt for images, text for audio
    params: Dict[str, Any]  # Provider-specific parameters
    output_path: Optional[Path] = None

@dataclass
class MediaResult:
    """Result of media generation"""
    success: bool
    file_path: Optional[Path]
    metadata: Dict[str, Any]
    error: Optional[str] = None

class MediaProvider(ABC):
    """Abstract interface for media generation"""

    @property
    @abstractmethod
    def supported_types(self) -> List[str]:
        """List of supported media types ('image', 'audio', etc.)"""
        pass

    @abstractmethod
    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Generate media from request"""
        pass

    @abstractmethod
    def get_cost_estimate(self, requests: List[MediaRequest]) -> Dict[str, float]:
        """Get cost estimate for batch of requests"""
        pass

    def supports_type(self, media_type: str) -> bool:
        """Check if provider supports media type"""
        return media_type in self.supported_types
```

#### Sync Provider Interface (`sync_provider.py`)
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class SyncRequest:
    """Request for sync operation"""
    operation: str  # 'create', 'update', 'delete'
    target: str     # Target identifier (note type, deck, etc.)
    data: Dict[str, Any]
    options: Dict[str, Any] = None

@dataclass
class SyncResult:
    """Result of sync operation"""
    success: bool
    target_id: Optional[str]  # ID of created/updated item
    metadata: Dict[str, Any]
    error: Optional[str] = None

class SyncProvider(ABC):
    """Abstract interface for sync targets"""

    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to sync target"""
        pass

    @abstractmethod
    def sync_templates(self, note_type: str, templates: List[Dict]) -> SyncResult:
        """Sync templates to target"""
        pass

    @abstractmethod
    def sync_media(self, media_files: List[Path]) -> SyncResult:
        """Sync media files to target"""
        pass

    @abstractmethod
    def sync_cards(self, cards: List[Dict]) -> SyncResult:
        """Sync card data to target"""
        pass

    @abstractmethod
    def list_existing(self, note_type: str) -> List[Dict]:
        """List existing items of specified type"""
        pass
```

### 2. Data Providers (`src/providers/data/`)

#### JSON File Provider (`json_provider.py`)
```python
import json
from pathlib import Path
from typing import Dict, List, Any
from providers.base.data_provider import DataProvider

class JSONDataProvider(DataProvider):
    """Provide data from JSON files"""

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)

    def load_data(self, identifier: str) -> Dict[str, Any]:
        """Load data from JSON file"""
        file_path = self.base_path / f"{identifier}.json"
        if not file_path.exists():
            return {}

        try:
            return json.loads(file_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Error loading {identifier}: {e}")

    def save_data(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Save data to JSON file"""
        file_path = self.base_path / f"{identifier}.json"

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            return True
        except IOError:
            return False

    def exists(self, identifier: str) -> bool:
        """Check if JSON file exists"""
        return (self.base_path / f"{identifier}.json").exists()

    def list_identifiers(self) -> List[str]:
        """List all JSON files (without .json extension)"""
        if not self.base_path.exists():
            return []

        return [f.stem for f in self.base_path.glob("*.json")]

    def backup_data(self, identifier: str) -> Optional[str]:
        """Create backup of JSON file"""
        source = self.base_path / f"{identifier}.json"
        if not source.exists():
            return None

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{identifier}_backup_{timestamp}"
        backup_path = self.base_path / f"{backup_name}.json"

        try:
            backup_path.write_text(source.read_text())
            return backup_name
        except IOError:
            return None
```

#### Memory Provider for Testing (`memory_provider.py`)
```python
from typing import Dict, List, Any, Optional
from providers.base.data_provider import DataProvider

class MemoryDataProvider(DataProvider):
    """In-memory data provider for testing"""

    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}

    def load_data(self, identifier: str) -> Dict[str, Any]:
        return self._data.get(identifier, {}).copy()

    def save_data(self, identifier: str, data: Dict[str, Any]) -> bool:
        self._data[identifier] = data.copy()
        return True

    def exists(self, identifier: str) -> bool:
        return identifier in self._data

    def list_identifiers(self) -> List[str]:
        return list(self._data.keys())

    def clear(self) -> None:
        """Clear all data (testing utility)"""
        self._data.clear()
```

### 3. Media Providers (`src/providers/media/`)

#### OpenAI Provider (`openai_provider.py`)
```python
from pathlib import Path
from typing import List, Dict, Any
from providers.base.media_provider import MediaProvider, MediaRequest, MediaResult

class OpenAIMediaProvider(MediaProvider):
    """OpenAI-based media generation"""

    def __init__(self, api_key: str, base_path: Path):
        self.api_key = api_key
        self.base_path = Path(base_path)
        # Initialize OpenAI client

    @property
    def supported_types(self) -> List[str]:
        return ['image']  # OpenAI supports image generation

    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Generate image using OpenAI DALL-E"""
        if request.type != 'image':
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Unsupported media type: {request.type}"
            )

        try:
            # Extract existing OpenAI logic from apis/openai_client.py
            # Generate image, save to file, return result
            pass
        except Exception as e:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=str(e)
            )

    def get_cost_estimate(self, requests: List[MediaRequest]) -> Dict[str, float]:
        """Estimate cost for OpenAI API calls"""
        # Calculate based on request count and image size
        pass
```

#### Forvo Provider (`forvo_provider.py`)
```python
class ForvoMediaProvider(MediaProvider):
    """Forvo-based audio generation"""

    @property
    def supported_types(self) -> List[str]:
        return ['audio']

    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Generate audio using Forvo API"""
        # Extract from apis/forvo_client.py
        pass
```

#### Mock Provider for Testing (`mock_provider.py`)
```python
class MockMediaProvider(MediaProvider):
    """Mock media provider for testing"""

    def __init__(self, supported_types: List[str] = None):
        self._supported_types = supported_types or ['image', 'audio']
        self.generated_requests: List[MediaRequest] = []

    @property
    def supported_types(self) -> List[str]:
        return self._supported_types

    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Mock media generation"""
        self.generated_requests.append(request)

        # Create fake file for testing
        fake_file = Path(f"mock_{request.type}_{len(self.generated_requests)}.jpg")

        return MediaResult(
            success=True,
            file_path=fake_file,
            metadata={'mock': True, 'request_count': len(self.generated_requests)},
            error=None
        )
```

### 4. Sync Providers (`src/providers/sync/`)

#### Anki Provider (`anki_provider.py`)
```python
from providers.base.sync_provider import SyncProvider, SyncRequest, SyncResult

class AnkiSyncProvider(SyncProvider):
    """AnkiConnect-based sync provider"""

    def __init__(self, anki_client):
        self.anki = anki_client

    def test_connection(self) -> bool:
        """Test AnkiConnect connection"""
        return self.anki.test_connection()

    def sync_templates(self, note_type: str, templates: List[Dict]) -> SyncResult:
        """Sync templates to Anki"""
        # Extract from existing sync logic
        pass

    def sync_cards(self, cards: List[Dict]) -> SyncResult:
        """Sync cards to Anki"""
        # Extract from existing sync logic
        pass
```

#### Mock Sync Provider (`mock_provider.py`)
```python
class MockSyncProvider(SyncProvider):
    """Mock sync provider for testing"""

    def __init__(self):
        self.synced_templates: List[Dict] = []
        self.synced_cards: List[Dict] = []
        self.connection_available = True

    def test_connection(self) -> bool:
        return self.connection_available

    def sync_templates(self, note_type: str, templates: List[Dict]) -> SyncResult:
        self.synced_templates.extend(templates)
        return SyncResult(
            success=True,
            target_id=note_type,
            metadata={'template_count': len(templates)},
            error=None
        )
```

### 5. Provider Registry (`src/providers/registry.py`)

```python
from typing import Dict, Type, Any, Optional
from .base.data_provider import DataProvider
from .base.media_provider import MediaProvider
from .base.sync_provider import SyncProvider

class ProviderRegistry:
    """Registry for provider instances"""

    def __init__(self):
        self._data_providers: Dict[str, DataProvider] = {}
        self._media_providers: Dict[str, MediaProvider] = {}
        self._sync_providers: Dict[str, SyncProvider] = {}

    def register_data_provider(self, name: str, provider: DataProvider) -> None:
        """Register a data provider"""
        self._data_providers[name] = provider

    def register_media_provider(self, name: str, provider: MediaProvider) -> None:
        """Register a media provider"""
        self._media_providers[name] = provider

    def register_sync_provider(self, name: str, provider: SyncProvider) -> None:
        """Register a sync provider"""
        self._sync_providers[name] = provider

    def get_data_provider(self, name: str) -> Optional[DataProvider]:
        """Get data provider by name"""
        return self._data_providers.get(name)

    def get_media_provider(self, name: str) -> Optional[MediaProvider]:
        """Get media provider by name"""
        return self._media_providers.get(name)

    def get_sync_provider(self, name: str) -> Optional[SyncProvider]:
        """Get sync provider by name"""
        return self._sync_providers.get(name)

# Global registry instance
_global_provider_registry = ProviderRegistry()

def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry"""
    return _global_provider_registry
```

## Validation Checklist

### E2E Test Compliance
- [ ] All tests in `tests/e2e/03_provider_system/` pass
- [ ] Data provider abstraction works correctly
- [ ] Media provider abstraction supports multiple types
- [ ] Sync provider abstraction handles all operations

### Implementation Quality
- [ ] All external APIs abstracted behind provider interfaces
- [ ] Mock providers support comprehensive testing
- [ ] Provider registry enables dynamic configuration
- [ ] Existing functionality maintained through providers

### Integration Quality
- [ ] Stages can use providers through context
- [ ] Providers integrate cleanly with stage system
- [ ] Configuration can specify which providers to use
- [ ] Error handling consistent across providers

## Deliverables

### 1. Complete Provider System
- All provider interfaces and implementations
- Provider registry for dynamic management
- Integration with stage system
- Mock providers for testing

### 2. API Extraction
- Move existing API logic into providers
- Maintain existing functionality
- Clean provider interfaces
- Comprehensive error handling

### 3. Unit Tests
- Unit tests for all provider implementations
- Mock provider tests
- Integration tests with stage system
- Error handling and edge cases

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/04_provider_system_handoff.md` with:
- Overview of provider system architecture
- Available providers and their capabilities
- How stages integrate with providers
- Configuration requirements for providers
- Guidance for CLI system integration

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All previous session E2E tests continue to pass
2. ✅ All Session 4 E2E tests pass
3. ✅ All external dependencies abstracted behind providers
4. ✅ Mock providers enable comprehensive testing
5. ✅ Stages can use providers transparently

### Quality Validation
- Provider interfaces are clean and consistent
- All existing API functionality preserved
- Testing is comprehensive with mock providers
- Error handling provides clear debugging information

## Notes for Implementation

### Migration Strategy
- Extract existing API client logic into providers
- Maintain existing interfaces during transition
- Add provider registry integration
- Update stages to use providers from context

### Design Principles
- **Interface Segregation** - Clean provider interfaces
- **Dependency Injection** - Providers injected through context
- **Testability** - Mock providers for all external dependencies
- **Configuration** - Providers configured externally

---

**Remember: This provider system will make the entire application testable and configurable. Focus on clean interfaces and comprehensive mocking capabilities.**
