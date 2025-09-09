"""
Validation Stages

Stages for validating data integrity and correctness:
- Data structure validation
- IPA pronunciation validation
- Media file validation
"""

from .data_stage import DataValidationStage
from .ipa_stage import IPAValidationStage
from .media_stage import MediaValidationStage

# Compatibility alias for validation gate tests
ValidationStage = DataValidationStage

__all__ = [
    "DataValidationStage",
    "IPAValidationStage",
    "MediaValidationStage",
    "ValidationStage",  # Compatibility alias
]
