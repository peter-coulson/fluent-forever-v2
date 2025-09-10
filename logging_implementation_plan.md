# Logging Implementation Plan

## Overview
This document outlines the comprehensive logging implementation for the Fluent Forever v2 pipeline infrastructure. The plan provides specific implementation details for each module without reasoning or justification.

## Logging Configuration Updates

### Enhanced `src/utils/logging_config.py`

```python
# Add these constants
DEFAULT_LOG_LEVELS = {
    "fluent_forever.cli": logging.INFO,
    "fluent_forever.core": logging.INFO,
    "fluent_forever.providers": logging.INFO,
    "fluent_forever.stages": logging.INFO,
}

# Add performance logging formatter
class PerformanceFormatter(ColoredFormatter):
    def format(self, record: logging.LogRecord) -> str:
        if hasattr(record, 'duration'):
            record.msg = f"{record.msg} (took {record.duration:.2f}s)"
        return super().format(record)

# Add context-aware logging
def get_context_logger(module_name: str, context_id: str = None) -> logging.Logger:
    logger_name = f"fluent_forever.{module_name}"
    if context_id:
        logger_name += f".{context_id}"
    return logging.getLogger(logger_name)
```

## Module-Specific Implementation

### 1. CLI Layer (`src/cli/`)

#### `src/cli/pipeline_runner.py`
```python
# Add at module level
logger = get_logger("cli.runner")

# In main() function
def main() -> int:
    logger.info(f"{ICONS['gear']} Starting Fluent Forever v2 Pipeline Runner")

    # After args parsing
    logger.info(f"{ICONS['info']} Command: {args.command}")
    logger.debug(f"Full arguments: {vars(args)}")

    # Before config loading
    logger.info(f"{ICONS['gear']} Loading configuration...")

    # After successful config load
    logger.info(f"{ICONS['check']} Configuration loaded successfully")

    # Before registry setup
    logger.info(f"{ICONS['gear']} Initializing registries...")

    # After registry setup
    logger.info(f"{ICONS['check']} Registries initialized")

    # Before command execution
    logger.info(f"{ICONS['gear']} Executing {args.command} command...")

    # On successful completion
    logger.info(f"{ICONS['check']} Command completed successfully")

    # On error
    logger.error(f"{ICONS['cross']} Command failed: {e}")
```

#### `src/cli/commands/run_command.py`
```python
# Add at class level
def __init__(self, ...):
    self.logger = get_logger("cli.commands.run")

def execute(self, args: Any) -> int:
    self.logger.info(f"{ICONS['gear']} Executing pipeline '{args.pipeline}' stage '{args.stage}'")

    # After pipeline retrieval
    self.logger.info(f"{ICONS['check']} Pipeline '{args.pipeline}' loaded")

    # Before context creation
    self.logger.debug("Creating pipeline context...")

    # After context creation
    self.logger.debug("Pipeline context created successfully")

    # Before stage execution
    self.logger.info(f"{ICONS['gear']} Starting stage '{args.stage}' execution...")

    # After successful execution
    self.logger.info(f"{ICONS['check']} Stage '{args.stage}' completed successfully")
```

#### `src/cli/commands/list_command.py`
```python
# Add logger
self.logger = get_logger("cli.commands.list")

def execute(self, args: Any) -> int:
    self.logger.info(f"{ICONS['search']} Discovering available pipelines...")

    # After pipeline discovery
    pipeline_count = len(pipelines)
    self.logger.info(f"{ICONS['check']} Found {pipeline_count} pipeline(s)")
```

#### `src/cli/commands/info_command.py`
```python
# Add logger
self.logger = get_logger("cli.commands.info")

def execute(self, args: Any) -> int:
    self.logger.info(f"{ICONS['search']} Getting info for pipeline '{args.pipeline}'")

    # After successful info retrieval
    self.logger.debug(f"Retrieved pipeline info: {pipeline_info}")
```

### 2. Core Framework (`src/core/`)

#### `src/core/registry.py`
```python
# Add at class level
def __init__(self) -> None:
    self._pipelines: dict[str, Pipeline] = {}
    self.logger = get_logger("core.registry")

def register(self, pipeline: Pipeline) -> None:
    self.logger.info(f"{ICONS['gear']} Registering pipeline '{pipeline.name}'")

    # After successful registration
    self.logger.info(f"{ICONS['check']} Pipeline '{pipeline.name}' registered successfully")

    # On duplicate registration
    self.logger.error(f"{ICONS['cross']} Pipeline '{pipeline.name}' already registered")

def get(self, name: str) -> Pipeline:
    self.logger.debug(f"Retrieving pipeline '{name}'")

    # On not found
    self.logger.error(f"{ICONS['cross']} Pipeline '{name}' not found")
```

#### `src/core/pipeline.py`
```python
# Add to Pipeline base class
def execute_stage(self, stage_name: str, context: PipelineContext) -> StageResult:
    logger = get_context_logger("core.pipeline", context.pipeline_name)

    logger.info(f"{ICONS['gear']} Executing stage '{stage_name}' in pipeline '{self.name}'")

    # Before stage retrieval
    logger.debug(f"Retrieving stage '{stage_name}'...")

    # After stage retrieval
    logger.debug(f"Stage '{stage_name}' retrieved successfully")

    # Before context validation
    logger.debug("Validating context for stage execution...")

    # On validation errors
    logger.error(f"{ICONS['cross']} Context validation failed for stage '{stage_name}': {validation_errors}")

    # After successful validation
    logger.debug("Context validation passed")

    # Before stage execution
    logger.info(f"{ICONS['gear']} Starting stage '{stage_name}' execution...")

    # After successful execution
    logger.info(f"{ICONS['check']} Stage '{stage_name}' completed successfully")

    # On stage failure
    logger.error(f"{ICONS['cross']} Stage '{stage_name}' failed: {result.message}")

    # On unexpected error
    logger.error(f"{ICONS['cross']} Unexpected error in stage '{stage_name}': {str(e)}")
```

#### `src/core/stages.py`
```python
# Add to Stage base class
class Stage(ABC):
    def __init__(self):
        self.logger = get_logger(f"stages.{self.__class__.__name__.lower()}")

    def execute(self, context: "PipelineContext") -> StageResult:
        self.logger.info(f"{ICONS['gear']} Executing stage '{self.name}'")

        # Add timing
        import time
        start_time = time.time()

        try:
            result = self._execute_impl(context)
            duration = time.time() - start_time

            if result.success:
                self.logger.info(f"{ICONS['check']} Stage '{self.name}' completed",
                               extra={'duration': duration})
            else:
                self.logger.error(f"{ICONS['cross']} Stage '{self.name}' failed: {result.message}")

            return result
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"{ICONS['cross']} Stage '{self.name}' error: {e}",
                            extra={'duration': duration})
            raise

    @abstractmethod
    def _execute_impl(self, context: "PipelineContext") -> StageResult:
        pass
```

#### `src/core/context.py`
```python
# Add to PipelineContext
def __post_init__(self):
    self.logger = get_context_logger("core.context", self.pipeline_name)
    self.logger.debug(f"Created context for pipeline '{self.pipeline_name}'")

def set(self, key: str, value: Any) -> None:
    self.logger.debug(f"Setting context data: {key}")
    self.data[key] = value

def mark_stage_complete(self, stage_name: str) -> None:
    self.logger.info(f"{ICONS['check']} Marking stage '{stage_name}' as complete")
    if stage_name not in self.completed_stages:
        self.completed_stages.append(stage_name)

def add_error(self, error: str) -> None:
    self.logger.error(f"{ICONS['cross']} Context error: {error}")
    self.errors.append(error)
```

### 3. Provider System (`src/providers/`)

#### `src/providers/registry.py`
```python
# Add at class level
def __init__(self) -> None:
    self.logger = get_logger("providers.registry")
    # ... existing init

@classmethod
def from_config(cls, config: "Config") -> "ProviderRegistry":
    logger = get_logger("providers.registry")
    logger.info(f"{ICONS['gear']} Initializing providers from configuration...")

    registry = cls()

    # Data providers
    logger.info(f"{ICONS['gear']} Setting up data providers...")
    data_config = config.get("providers.data", {})
    if data_config.get("type") == "json":
        logger.info(f"{ICONS['check']} Registered JSON data provider")

    # Audio providers
    logger.info(f"{ICONS['gear']} Setting up audio providers...")
    audio_config = config.get("providers.audio", {})
    if audio_config:
        logger.info(f"{ICONS['check']} Registered {audio_config.get('type')} audio provider")
    else:
        logger.info(f"{ICONS['info']} No audio provider configured")

    # Image providers
    logger.info(f"{ICONS['gear']} Setting up image providers...")
    image_config = config.get("providers.image", {})
    if image_config:
        logger.info(f"{ICONS['check']} Registered {image_config.get('type')} image provider")
    else:
        logger.info(f"{ICONS['info']} No image provider configured")

    # Sync providers
    logger.info(f"{ICONS['gear']} Setting up sync providers...")
    sync_config = config.get("providers.sync", {})
    logger.info(f"{ICONS['check']} Registered {sync_config.get('type', 'anki')} sync provider")

    logger.info(f"{ICONS['check']} All providers initialized successfully")
    return registry
```

#### Base Provider Classes

##### `src/providers/base/data_provider.py`
```python
class DataProvider(ABC):
    def __init__(self):
        self.logger = get_logger(f"providers.data.{self.__class__.__name__.lower()}")

    def load_data(self, file_path: Path) -> dict:
        self.logger.info(f"{ICONS['file']} Loading data from {file_path}")
        # Implementation
        self.logger.debug(f"Loaded {len(data)} records from {file_path}")

    def save_data(self, file_path: Path, data: dict) -> None:
        self.logger.info(f"{ICONS['file']} Saving data to {file_path}")
        # Implementation
        self.logger.debug(f"Saved {len(data)} records to {file_path}")
```

##### `src/providers/base/media_provider.py`
```python
class MediaProvider(ABC):
    def __init__(self):
        self.logger = get_logger(f"providers.media.{self.__class__.__name__.lower()}")

    def get_media(self, query: str) -> MediaResult:
        self.logger.info(f"{ICONS['search']} Requesting media for: {query}")

        # Before API call
        self.logger.debug(f"Making API request...")

        # After successful API call
        self.logger.info(f"{ICONS['check']} Media retrieved successfully")

        # On API error
        self.logger.error(f"{ICONS['cross']} Media request failed: {error}")
```

##### `src/providers/base/sync_provider.py`
```python
class SyncProvider(ABC):
    def __init__(self):
        self.logger = get_logger(f"providers.sync.{self.__class__.__name__.lower()}")

    def connect(self) -> bool:
        self.logger.info(f"{ICONS['gear']} Connecting to sync service...")

        # On successful connection
        self.logger.info(f"{ICONS['check']} Connected to sync service")

        # On connection failure
        self.logger.error(f"{ICONS['cross']} Failed to connect: {error}")

    def sync_data(self, data: list) -> SyncResult:
        self.logger.info(f"{ICONS['gear']} Syncing {len(data)} items...")

        # Progress logging
        for i, item in enumerate(data, 1):
            if i % 10 == 0 or i == len(data):
                self.logger.info(f"{ICONS['info']} Synced {i}/{len(data)} items")

        # Final result
        self.logger.info(f"{ICONS['check']} Sync completed: {result.stats}")
```

### 4. Stage System (`src/stages/`)

#### `src/stages/base/api_stage.py`
```python
def execute(self, context: PipelineContext) -> StageResult:
    self.logger.info(f"{ICONS['gear']} Executing API stage '{self.name}'")

    # Provider check
    provider = context.get(f"providers.{self.provider_key}")
    if not provider and self.required:
        self.logger.error(f"{ICONS['cross']} Required provider '{self.provider_key}' not available")
        # return failure
    elif not provider:
        self.logger.info(f"{ICONS['info']} Optional provider '{self.provider_key}' not available, skipping")
        # return success

    self.logger.info(f"{ICONS['gear']} Making API call using {self.provider_key} provider...")

    try:
        result = self.execute_api_call(context, provider)
        self.logger.info(f"{ICONS['check']} API call completed successfully")
        return result
    except Exception as e:
        self.logger.error(f"{ICONS['cross']} API call failed: {e}")
        # return failure
```

#### `src/stages/base/file_stage.py`
```python
def execute(self, context: PipelineContext) -> StageResult:
    self.logger.info(f"{ICONS['gear']} Executing file stage '{self.name}'")

    # File operation logging
    file_path = self.get_file_path(context)
    self.logger.info(f"{ICONS['file']} Operating on file: {file_path}")

    if not file_path.exists():
        self.logger.warning(f"{ICONS['warning']} File does not exist: {file_path}")

    # After successful file operation
    self.logger.info(f"{ICONS['check']} File operation completed")
```

#### `src/stages/base/validation_stage.py`
```python
def execute(self, context: PipelineContext) -> StageResult:
    self.logger.info(f"{ICONS['gear']} Executing validation stage '{self.name}'")

    # Before validation
    self.logger.debug("Starting data validation...")

    validation_errors = self.validate_data(context)

    if validation_errors:
        self.logger.error(f"{ICONS['cross']} Validation failed with {len(validation_errors)} errors")
        for error in validation_errors:
            self.logger.error(f"  - {error}")
    else:
        self.logger.info(f"{ICONS['check']} Validation passed")
```

## Performance Logging

### Timing Decorators
```python
# Add to src/utils/logging_config.py
import functools
import time

def log_performance(logger_name: str = None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or f"fluent_forever.performance.{func.__name__}")
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
                raise
        return wrapper
    return decorator
```

### Usage in Critical Methods
```python
# Apply to key methods:
@log_performance("fluent_forever.core.pipeline")
def execute_stage(self, stage_name: str, context: PipelineContext) -> StageResult:

@log_performance("fluent_forever.providers.registry")
def from_config(cls, config: "Config") -> "ProviderRegistry":

@log_performance("fluent_forever.stages.api")
def execute_api_call(self, context: PipelineContext, provider: Any) -> StageResult:
```

## Error Context Logging

### Enhanced Error Information
```python
# Add to src/utils/logging_config.py
class ContextualError(Exception):
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context or {}

def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None):
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **(context or {}),
    }

    if hasattr(error, 'context'):
        error_context.update(error.context)

    logger.error(f"{ICONS['cross']} {error}", extra={"context": error_context})
```

## Configuration Integration

### Environment-Based Log Levels
```python
# Add to src/utils/logging_config.py
import os

def get_log_level_from_env() -> int:
    level_str = os.getenv('FLUENT_FOREVER_LOG_LEVEL', 'INFO').upper()
    return getattr(logging, level_str, logging.INFO)

def setup_module_log_levels():
    """Configure module-specific log levels from environment"""
    for module, default_level in DEFAULT_LOG_LEVELS.items():
        env_var = f"FLUENT_FOREVER_{module.replace('.', '_').upper()}_LOG_LEVEL"
        level_str = os.getenv(env_var, logging.getLevelName(default_level))
        level = getattr(logging, level_str.upper(), default_level)
        logging.getLogger(module).setLevel(level)
```

### Debug Mode Support
```python
# Add to main() in pipeline_runner.py
if args.verbose or os.getenv('FLUENT_FOREVER_DEBUG'):
    setup_logging(level=logging.DEBUG, log_to_file=True)
else:
    setup_logging(level=logging.INFO)
```
