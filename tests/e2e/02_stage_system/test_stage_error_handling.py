#!/usr/bin/env python3
"""
Session 3 Validation Gate: Stage Error Handling System

Tests the contract for stage error handling and recovery.
These tests define how stages should handle errors, failures,
and exceptional conditions.

CONTRACT BEING TESTED:
- Stages handle various error conditions gracefully
- Error information is properly propagated
- Recovery mechanisms work correctly
- Partial failures are managed appropriately
- Error context is preserved
"""

import pytest
from typing import Dict, Any, Optional
from tests.e2e.conftest import MockStage


class TestStageErrorHandling:
    """Test stage error handling contracts"""
    
    def test_stage_runtime_error_propagation(self):
        """Contract: Runtime errors are properly propagated"""
        failing_stage = MockStage("failing_stage", should_fail=True)
        
        context = {"data": {}}
        
        # Should propagate the runtime error
        with pytest.raises(RuntimeError) as exc_info:
            failing_stage.execute(context)
        
        # Error message should contain stage information
        assert "failing_stage failed" in str(exc_info.value)
    
    def test_stage_validation_error_handling(self):
        """Contract: Validation errors are handled appropriately"""
        validation_stage = MockValidationStage("validator")
        
        # Invalid context should trigger validation error
        invalid_context = {
            "data": {},  # Missing required 'input_data' field
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validation_stage.execute(invalid_context)
        
        assert "Missing required field" in str(exc_info.value)
    
    def test_stage_timeout_handling(self):
        """Contract: Stages handle timeout conditions"""
        timeout_stage = MockTimeoutStage("timeout_stage", timeout_after=0.1)
        
        context = {"data": {"delay": 0.2}}  # Longer than timeout
        
        with pytest.raises(TimeoutError):
            timeout_stage.execute(context)
    
    def test_stage_resource_error_handling(self):
        """Contract: Resource errors are handled gracefully"""
        resource_stage = MockResourceStage("resource_stage")
        
        # Simulate resource unavailable
        context = {
            "data": {"resource_available": False}
        }
        
        with pytest.raises(ResourceError) as exc_info:
            resource_stage.execute(context)
        
        assert "Resource unavailable" in str(exc_info.value)
    
    def test_stage_partial_failure_handling(self):
        """Contract: Partial failures are handled appropriately"""
        partial_stage = MockPartialFailureStage("partial_stage")
        
        context = {
            "data": {
                "items": ["item1", "item2", "item3", "item4"],
                "fail_items": ["item2", "item4"]  # These will fail
            }
        }
        
        result = partial_stage.execute(context)
        
        # Should report partial success
        assert result["status"] == "partial_success"
        assert len(result["successful_items"]) == 2
        assert len(result["failed_items"]) == 2
        assert result["errors"] is not None
    
    def test_stage_error_context_preservation(self):
        """Contract: Error context is preserved for debugging"""
        error_context_stage = MockErrorContextStage("error_stage")
        
        context = {
            "data": {"trigger_error": True},
            "metadata": {"session_id": "test123", "user": "test_user"}
        }
        
        try:
            error_context_stage.execute(context)
        except DetailedError as e:
            # Error should preserve original context
            assert e.context is not None
            assert e.context["metadata"]["session_id"] == "test123"
            assert e.stage_name == "error_stage"
        else:
            pytest.fail("Expected DetailedError was not raised")


class TestStageRecovery:
    """Test stage recovery mechanisms"""
    
    def test_stage_retry_mechanism(self):
        """Contract: Stages can implement retry mechanisms"""
        retry_stage = MockRetryStage("retry_stage", fail_attempts=2, max_retries=3)
        
        context = {"data": {}}
        
        # Should eventually succeed after retries
        result = retry_stage.execute_with_retry(context)
        
        assert result["status"] == "success"
        assert result["attempts"] == 3  # Failed twice, succeeded on third
    
    def test_stage_graceful_degradation(self):
        """Contract: Stages can degrade gracefully on errors"""
        degrading_stage = MockDegradingStage("degrading_stage")
        
        context = {
            "data": {"primary_service_available": False}
        }
        
        result = degrading_stage.execute(context)
        
        # Should succeed with degraded functionality
        assert result["status"] == "success"
        assert result["degraded"] is True
        assert "fallback_used" in result
    
    def test_stage_compensation_on_failure(self):
        """Contract: Stages can compensate for failures"""
        compensating_stage = MockCompensatingStage("compensating_stage")
        
        context = {
            "data": {"should_fail": True},
            "stage_history": []
        }
        
        try:
            compensating_stage.execute(context)
        except RuntimeError:
            # Should have recorded compensation action
            assert len(context["stage_history"]) > 0
            assert any("compensation" in entry for entry in context["stage_history"])
    
    def test_stage_error_reporting(self):
        """Contract: Stages provide detailed error reporting"""
        reporting_stage = MockReportingStage("reporting_stage")
        
        context = {"data": {"cause_error": "network_timeout"}}
        
        try:
            reporting_stage.execute(context)
        except DetailedError as e:
            # Should provide detailed error report
            assert e.error_code is not None
            assert e.error_details is not None
            assert e.suggested_action is not None
        else:
            pytest.fail("Expected detailed error was not raised")


class TestStageErrorTypes:
    """Test different types of stage errors"""
    
    def test_configuration_error(self):
        """Contract: Configuration errors are properly identified"""
        config_stage = MockConfigurationStage("config_stage")
        
        # Missing required configuration
        context = {"config": {}}  # Empty config
        
        with pytest.raises(ConfigurationError) as exc_info:
            config_stage.execute(context)
        
        assert "Missing required configuration" in str(exc_info.value)
    
    def test_dependency_error(self):
        """Contract: Dependency errors are properly handled"""
        dependency_stage = MockDependencyStage("dependency_stage")
        
        context = {
            "data": {"dependencies_available": False}
        }
        
        with pytest.raises(DependencyError):
            dependency_stage.execute(context)
    
    def test_data_integrity_error(self):
        """Contract: Data integrity errors are detected"""
        integrity_stage = MockDataIntegrityStage("integrity_stage")
        
        context = {
            "data": {
                "items": [
                    {"id": "1", "checksum": "invalid"},
                    {"id": "2", "checksum": "also_invalid"}
                ]
            }
        }
        
        with pytest.raises(DataIntegrityError) as exc_info:
            integrity_stage.execute(context)
        
        assert "Data integrity check failed" in str(exc_info.value)


# Custom Exception Classes for Testing
class ValidationError(Exception):
    """Validation error"""
    pass


class ResourceError(Exception):
    """Resource unavailable error"""
    pass


class DetailedError(Exception):
    """Error with detailed context"""
    
    def __init__(self, message: str, stage_name: str, context: Dict[str, Any] = None,
                 error_code: str = None, error_details: str = None, suggested_action: str = None):
        super().__init__(message)
        self.stage_name = stage_name
        self.context = context
        self.error_code = error_code
        self.error_details = error_details
        self.suggested_action = suggested_action


class ConfigurationError(Exception):
    """Configuration error"""
    pass


class DependencyError(Exception):
    """Dependency error"""
    pass


class DataIntegrityError(Exception):
    """Data integrity error"""
    pass


# Mock Stage Implementations for Error Testing
class MockValidationStage(MockStage):
    """Mock stage that performs validation"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if "input_data" not in context:
            raise ValidationError("Missing required field: input_data")
        
        return super().execute(context)


class MockTimeoutStage(MockStage):
    """Mock stage that simulates timeout"""
    
    def __init__(self, name: str, timeout_after: float = 1.0):
        super().__init__(name)
        self.timeout_after = timeout_after
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        import time
        
        delay = context.get("data", {}).get("delay", 0)
        
        if delay > self.timeout_after:
            raise TimeoutError(f"Stage {self.name} timed out after {self.timeout_after}s")
        
        return super().execute(context)


class MockResourceStage(MockStage):
    """Mock stage that checks resource availability"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not context.get("data", {}).get("resource_available", True):
            raise ResourceError("Resource unavailable")
        
        return super().execute(context)


class MockPartialFailureStage(MockStage):
    """Mock stage that handles partial failures"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        items = context.get("data", {}).get("items", [])
        fail_items = context.get("data", {}).get("fail_items", [])
        
        successful_items = []
        failed_items = []
        errors = []
        
        for item in items:
            if item in fail_items:
                failed_items.append(item)
                errors.append(f"Failed to process {item}")
            else:
                successful_items.append(item)
        
        return {
            "status": "partial_success" if failed_items else "success",
            "stage": self.name,
            "successful_items": successful_items,
            "failed_items": failed_items,
            "errors": errors
        }


class MockErrorContextStage(MockStage):
    """Mock stage that preserves error context"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if context.get("data", {}).get("trigger_error", False):
            raise DetailedError(
                "Triggered error",
                stage_name=self.name,
                context=context
            )
        
        return super().execute(context)


class MockRetryStage(MockStage):
    """Mock stage with retry mechanism"""
    
    def __init__(self, name: str, fail_attempts: int = 1, max_retries: int = 3):
        super().__init__(name)
        self.fail_attempts = fail_attempts
        self.max_retries = max_retries
        self.attempt_count = 0
    
    def execute_with_retry(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                self.attempt_count = attempt + 1
                return self.execute(context)
            except RuntimeError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    continue
                else:
                    raise last_error
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if self.attempt_count <= self.fail_attempts:
            raise RuntimeError(f"Stage {self.name} failed (attempt {self.attempt_count})")
        
        return {
            "status": "success",
            "stage": self.name,
            "attempts": self.attempt_count
        }


class MockDegradingStage(MockStage):
    """Mock stage with graceful degradation"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        primary_available = context.get("data", {}).get("primary_service_available", True)
        
        if not primary_available:
            # Degrade to fallback functionality
            return {
                "status": "success",
                "stage": self.name,
                "degraded": True,
                "fallback_used": "secondary_service"
            }
        
        return super().execute(context)


class MockCompensatingStage(MockStage):
    """Mock stage that compensates for failures"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        should_fail = context.get("data", {}).get("should_fail", False)
        
        if should_fail:
            # Record compensation action before failing
            history = context.setdefault("stage_history", [])
            history.append(f"Stage {self.name} performing compensation")
            raise RuntimeError(f"Stage {self.name} failed after compensation")
        
        return super().execute(context)


class MockReportingStage(MockStage):
    """Mock stage with detailed error reporting"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        error_type = context.get("data", {}).get("cause_error")
        
        if error_type:
            raise DetailedError(
                f"Stage failed due to {error_type}",
                stage_name=self.name,
                context=context,
                error_code="E001",
                error_details=f"Detailed information about {error_type}",
                suggested_action="Check network connectivity and retry"
            )
        
        return super().execute(context)


class MockConfigurationStage(MockStage):
    """Mock stage that validates configuration"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        config = context.get("config", {})
        
        required_fields = ["api_key", "timeout", "max_retries"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ConfigurationError(f"Missing required configuration: {missing_fields}")
        
        return super().execute(context)


class MockDependencyStage(MockStage):
    """Mock stage that checks dependencies"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not context.get("data", {}).get("dependencies_available", True):
            raise DependencyError("Required dependencies are not available")
        
        return super().execute(context)


class MockDataIntegrityStage(MockStage):
    """Mock stage that checks data integrity"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        items = context.get("data", {}).get("items", [])
        
        for item in items:
            if item.get("checksum") == "invalid" or item.get("checksum") == "also_invalid":
                raise DataIntegrityError("Data integrity check failed")
        
        return super().execute(context)