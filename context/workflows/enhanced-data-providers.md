# Enhanced Data Provider Workflows

## Overview
Phase 2 enhanced data providers support permission control and file-specific access management for improved security and organization.

## Configuration Examples

### Multiple Named Data Providers
```json
{
  "providers": {
    "data": {
      "source_data": {
        "type": "json",
        "base_path": "./sources",
        "files": ["spanish_dictionary", "conjugation_patterns"],
        "read_only": true,
        "pipelines": ["vocabulary"]
      },
      "working_data": {
        "type": "json",
        "base_path": "./working",
        "files": ["word_queue", "progress_tracking"],
        "read_only": false,
        "pipelines": ["vocabulary"]
      }
    }
  }
}
```

### Read-Only Source Protection
```json
{
  "providers": {
    "data": {
      "reference_materials": {
        "type": "json",
        "base_path": "./reference",
        "read_only": true,
        "pipelines": ["*"]
      }
    }
  }
}
```

## Permission System Usage

### Write Protection
- **Read-only providers** reject all write operations with `PermissionError`
- Protects source data from accidental modification during pipeline execution
- Ideal for reference dictionaries, lookup tables, and configuration data

### File Access Control
- **File-specific providers** manage only assigned files via `files` array
- Prevents cross-contamination between different data categories
- Enables multiple providers to share base directory with segregated access

### Error Handling
```python
try:
    provider.save_data("protected_file", data)
except PermissionError as e:
    # Handle read-only provider write attempt
    logger.error(f"Write denied: {e}")
except ValueError as e:
    # Handle file access violation
    logger.error(f"Access denied: {e}")
```

## Common Patterns

### Source/Working/Output Segregation
- **Source providers**: Read-only reference materials
- **Working providers**: Temporary processing data with file restrictions
- **Output providers**: Final results with write access

### File Conflict Prevention
- Registry automatically validates no file overlap during initialization
- Configuration errors detected early with clear error messages
- Prevents accidental data corruption from overlapping provider assignments

### Backward Compatibility
- Existing configurations continue working unchanged
- New fields optional with sensible defaults
- Legacy provider registration still supported

## Troubleshooting

### Permission Errors
- **PermissionError**: Check `read_only` setting in provider configuration
- **ValueError**: Verify file name in provider's `files` array
- **File conflicts**: Review provider configurations for overlapping file assignments

### Configuration Validation
- Registry validates file conflicts during startup
- Missing `pipelines` field causes configuration rejection
- Invalid provider types generate clear error messages with supported options
