"""
Validation Stage Base

Base class for data validation stages with common validation patterns.
"""

from abc import abstractmethod
from typing import Dict, Any, List

from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext
from utils.logging_config import get_logger, ICONS


class ValidationStage(Stage):
    """Base class for validation stages"""
    
    def __init__(self, data_key: str):
        """
        Initialize validation stage
        
        Args:
            data_key: Key in context for data to validate
        """
        self.data_key = data_key
        self.logger = get_logger(f'stages.validation.{self.__class__.__name__.lower()}')
    
    @property
    def name(self) -> str:
        return f"validate_{self.data_key}"
    
    @property  
    def display_name(self) -> str:
        return f"Validate {self.data_key.replace('_', ' ').title()}"
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate data and return list of error messages
        
        Args:
            data: Data to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute validation on data from context"""
        data = context.get(self.data_key)
        if data is None:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"No data found for key '{self.data_key}'",
                data={},
                errors=[f"Missing '{self.data_key}' in context"]
            )
        
        # Validate data
        try:
            errors = self.validate_data(data)
        except Exception as e:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Validation failed with exception: {e}",
                data={},
                errors=[f"Validation exception: {e}"]
            )
        
        if errors:
            self.logger.error(f"{ICONS['cross']} Validation failed: {len(errors)} errors")
            for error in errors:
                self.logger.error(f"  - {error}")
            
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Validation failed: {len(errors)} errors",
                data={'validation_errors': errors},
                errors=errors
            )
        
        self.logger.info(f"{ICONS['check']} Validation passed")
        return StageResult(
            status=StageStatus.SUCCESS,
            message="Validation passed",
            data={'validation_status': 'passed'},
            errors=[]
        )