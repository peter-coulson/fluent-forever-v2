# Pipeline Template

This template provides a complete starting point for creating new pipeline types in the Fluent Forever V2 system.

## Quick Start

1. **Copy the template directory**:
   ```bash
   cp -r src/pipelines/__template src/pipelines/your_pipeline_name
   ```

2. **Rename and customize the main pipeline file**:
   - Rename `template_pipeline.py` to `your_pipeline_pipeline.py`
   - Update the class name from `TemplatePipeline` to `YourPipelinePipeline`
   - Update all the TODO comments with your specific values

3. **Create configuration file**:
   ```bash
   cp config/pipelines/_template.json config/pipelines/your_pipeline.json
   ```
   Update the configuration with your pipeline settings.

4. **Register your pipeline**:
   Add to `src/pipelines/__init__.py`:
   ```python
   from .your_pipeline.your_pipeline_pipeline import YourPipelinePipeline
   
   def register_builtin_pipelines():
       registry = get_pipeline_registry()
       
       # ... existing pipelines ...
       
       your_pipeline = YourPipelinePipeline()
       registry.register(your_pipeline)
   ```

## Pipeline Architecture

Each pipeline consists of:

### Core Components
- **Pipeline Class**: Main orchestrator (inherits from `core.pipeline.Pipeline`)
- **Stages**: Individual processing steps (inherit from `core.stages.Stage`)  
- **Configuration**: Pipeline-specific settings in `config/pipelines/`
- **Data Handlers**: Manage pipeline-specific data files

### Stage System
Stages are the building blocks of pipelines:

```python
class YourStage(Stage):
    @property
    def name(self) -> str:
        return "your_stage_name"
    
    @property 
    def display_name(self) -> str:
        return "Human Readable Name"
    
    @property
    def dependencies(self) -> List[str]:
        return ["prerequisite_stage"]  # Optional
    
    def execute(self, context: PipelineContext) -> StageResult:
        # Your stage logic here
        return StageResult.success("Stage completed", {"data": "value"})
    
    def validate_context(self, context: PipelineContext) -> List[str]:
        # Optional validation
        errors = []
        if not context.get("required_field"):
            errors.append("Missing required_field")
        return errors
```

### Configuration Integration
Your pipeline automatically loads configuration from:
- `config/pipelines/your_pipeline.json` - Pipeline-specific settings
- `config/core.json` - System-wide settings  
- Environment variables with `FF_` prefix

Access configuration in your pipeline:
```python
config_manager = get_config_manager()
pipeline_config = config_manager.get_pipeline_config(self.name)
setting_value = pipeline_config.get('your_setting', default_value)
```

## CLI Integration

Once registered, your pipeline works automatically with the CLI:

```bash
# List available pipelines
python -m cli.pipeline list

# Get pipeline information  
python -m cli.pipeline info your_pipeline

# Run pipeline stages
python -m cli.pipeline run your_pipeline --stage analyze --input data
python -m cli.pipeline run your_pipeline --stage prepare --dry-run
```

## Testing

Create tests for your pipeline in `tests/unit/pipelines/test_your_pipeline.py`:

```python
def test_your_pipeline():
    pipeline = YourPipelinePipeline()
    
    context = PipelineContext(
        pipeline_name=pipeline.name,
        project_root=Path.cwd()
    )
    context.set("test_data", ["item1", "item2"])
    
    result = pipeline.execute_stage("analyze", context)
    assert result.status == StageStatus.SUCCESS
```

## Best Practices

### Stage Design
- **Single Responsibility**: Each stage should do one thing well
- **Idempotent**: Stages should be safe to run multiple times
- **Error Handling**: Always validate inputs and handle errors gracefully
- **Context Usage**: Use the context to pass data between stages

### Data Management  
- Store pipeline data in a dedicated JSON file (e.g., `your_pipeline.json`)
- Use the provider system for external API calls
- Implement proper data validation

### Configuration
- Use configuration files for all customizable behavior
- Support environment variable overrides with `FF_` prefix
- Provide sensible defaults

### Performance
- Cache expensive operations
- Use the provider system's built-in retry and failover
- Consider memory usage for large datasets

## Example: Conjugation Pipeline

Here's how you might customize this template for a Spanish verb conjugation pipeline:

1. **Rename to conjugation pipeline**
2. **Update pipeline properties**:
   ```python
   @property
   def name(self) -> str:
       return "conjugation"
   
   @property  
   def display_name(self) -> str:
       return "Spanish Verb Conjugations"
   
   @property
   def data_file(self) -> str:
       return "conjugation.json"
   ```

3. **Implement conjugation-specific stages**:
   - `verb_analysis`: Parse verbs and identify conjugation patterns
   - `conjugation_generation`: Generate all conjugation forms  
   - `card_creation`: Create Anki cards for each conjugation
   - `pattern_validation`: Validate conjugation accuracy

4. **Configure for your needs**:
   ```json
   {
     "pipeline": {
       "name": "conjugation",
       "display_name": "Spanish Verb Conjugations",
       "tenses": ["present", "preterite", "imperfect", "future"],
       "persons": ["1s", "2s", "3s", "1p", "2p", "3p"]
     }
   }
   ```

This modular approach ensures your pipeline integrates seamlessly with the existing system while providing complete flexibility for your specific card type.