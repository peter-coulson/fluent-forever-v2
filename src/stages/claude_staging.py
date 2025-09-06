"""
Claude Staging Compatibility Module

Provides compatibility aliases for the validation gate tests.
"""

from .claude.batch_stage import BatchPreparationStage


class ClaudeStagingStage(BatchPreparationStage):
    """Claude staging stage for compatibility with validation gate tests"""
    
    def __init__(self):
        super().__init__()
    
    def execute(self, context):
        """Execute stage with context dict (validation gate compatibility)"""
        # Convert dict context to PipelineContext if needed
        if isinstance(context, dict):
            from core.context import PipelineContext
            from pathlib import Path
            
            project_root = Path(context.get('project_root', Path.cwd()))
            pipeline_name = context.get('pipeline_name', 'test_pipeline')
            
            pipeline_context = PipelineContext(
                pipeline_name=pipeline_name,
                project_root=project_root
            )
            
            for key, value in context.items():
                pipeline_context.set(key, value)
            
            result = super().execute(pipeline_context)
            
            # Convert result back to dict for compatibility
            result_dict = {
                'status': 'success' if result.status.value == 'success' else 'failure',
                'message': result.message,
                'data': result.data,
                'errors': result.errors
            }
            
            # Copy input data to output for chaining
            result_dict.update(context)
            
            return result_dict
        
        # If it's already a PipelineContext, use normal flow
        return super().execute(context)