# CLI Utilities

## Output Formatting (`src/cli/utils/output.py`)

### Table Formatting
- **`format_table(headers, rows)`**: Creates aligned columnar output with automatic width calculation
- **Width Calculation**: Dynamic column sizing based on content length
- **Format String**: Uses Python string formatting for consistent alignment

### User Feedback Functions
- **`print_success(message)`**: ✅ Success feedback with green checkmark
- **`print_error(message)`**: ❌ Error feedback with red X
- **`print_warning(message)`**: ⚠️ Warning feedback with yellow warning
- **`print_info(message)`**: ℹ️ Information feedback with blue info icon

### List and Key-Value Formatting
- **`format_list(items, indent="  ")`**: Bullet-point list with configurable indentation
- **`format_key_value_pairs(pairs, indent="")`**: Aligned key-value display for metadata

## Argument Validation (`src/cli/utils/validation.py`)

### Command-Level Validation
- **`validate_arguments(command, args)`**: Core CLI argument validation per command type
- **Required Arguments**: Ensures pipeline name for info/run commands, stage name for run command
- **Stage-Specific Logic**: Validates stage-specific arguments (words for prepare, cards for media)

### File System Validation
- **`validate_file_path(file_path)`**: Checks file existence and type
- **Path Resolution**: Uses `pathlib.Path` for cross-platform compatibility
- **Error Messages**: Descriptive feedback for missing files and non-file paths

### Data Format Validation
- **`validate_word_list(words)`**: Comma-separated word list validation
- **`validate_card_list(cards)`**: Comma-separated card ID validation
- **Input Parsing**: Strips whitespace, filters empty entries

### Network Validation
- **`validate_port(port)`**: Port number range validation (1-65535)
- **Boundary Checking**: Ensures valid TCP port range

### Configuration Validation
- **`parse_and_validate_config(config_dict)`**: Configuration structure validation
- **Type Checking**: Ensures providers and output sections are dictionaries
- **Schema Validation**: Validates expected configuration structure

## Validation Patterns

### Error Collection Strategy
All validation functions return lists of error messages rather than raising exceptions, allowing:
- **Batch Validation**: Collect multiple errors before failing
- **User-Friendly Output**: Present all issues at once
- **Graceful Degradation**: Commands can decide how to handle partial failures

### Stage-Specific Validation Logic
```python
# Example validation pattern
if args.stage == "prepare" and not args.words:
    errors.append("--words is required for prepare stage")
elif args.stage == "media" and not args.cards:
    errors.append("--cards is required for media stage")
```

## Output Consistency

### Icon-Based Feedback
- **Visual Indicators**: Emoji icons provide immediate visual feedback
- **Consistent Messaging**: Standard patterns across all CLI operations
- **Status Clarity**: Clear distinction between success, error, warning, and informational states

### Formatting Standards
- **Alignment**: Table columns auto-align based on content
- **Indentation**: Configurable indentation for hierarchical display
- **Whitespace**: Consistent spacing patterns throughout CLI output

## Extension Guidelines

### Adding New Validation Rules
1. Add function to `src/cli/utils/validation.py`
2. Return list of error strings
3. Integrate into command-specific validation
4. Test with valid and invalid inputs

### Adding New Output Formats
1. Add formatting function to `src/cli/utils/output.py`
2. Follow existing alignment and spacing patterns
3. Use consistent parameter naming (items, indent, etc.)
4. Support configurable formatting options

### Error Message Standards
- **Actionable**: Tell user what to fix
- **Specific**: Include problematic values where relevant
- **Consistent**: Use similar phrasing across validation functions
- **Context-Aware**: Include command or operation context
