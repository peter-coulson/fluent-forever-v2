"""Unit tests for stage system."""

from pathlib import Path

import pytest
from src.core.context import PipelineContext
from src.core.stages import Stage, StageResult, StageStatus


class TestStageStatus:
    """Test cases for StageStatus enum."""

    def test_stage_status_enum_values(self):
        """Test all StageStatus enum values exist with correct string representations."""
        assert StageStatus.SUCCESS.value == "success"
        assert StageStatus.FAILURE.value == "failure"
        assert StageStatus.PARTIAL.value == "partial"
        assert StageStatus.SKIPPED.value == "skipped"

    def test_stage_status_enum_count(self):
        """Test that enum has exactly 4 values."""
        assert len(list(StageStatus)) == 4

    def test_stage_status_enum_comparison(self):
        """Test enum comparison and equality."""
        assert StageStatus.SUCCESS == StageStatus.SUCCESS
        assert StageStatus.SUCCESS != StageStatus.FAILURE
        assert StageStatus.SUCCESS is StageStatus.SUCCESS


class TestStageResult:
    """Test cases for StageResult dataclass functionality."""

    def test_stage_result_creation_with_all_parameters(self):
        """Test StageResult creation with all parameters."""
        data = {"key": "value"}
        errors = ["error1", "error2"]

        result = StageResult(
            status=StageStatus.SUCCESS, message="Test message", data=data, errors=errors
        )

        assert result.status == StageStatus.SUCCESS
        assert result.message == "Test message"
        assert result.data == data
        assert result.errors == errors

    def test_stage_result_success_property_logic(self):
        """Test success property logic - only SUCCESS status returns True."""
        # Test SUCCESS returns True
        success_result = StageResult(
            status=StageStatus.SUCCESS, message="Success", data={}, errors=[]
        )
        assert success_result.success is True

        # Test all other statuses return False
        for status in [StageStatus.FAILURE, StageStatus.PARTIAL, StageStatus.SKIPPED]:
            result = StageResult(status=status, message="Test", data={}, errors=[])
            assert result.success is False

    def test_stage_result_dict_access_patterns(self):
        """Test dict-like access patterns (__contains__, __getitem__, get)."""
        result = StageResult(
            status=StageStatus.SUCCESS,
            message="Test message",
            data={"test": "data"},
            errors=[],
        )

        # Test __contains__ method - existing attributes
        assert "status" in result
        assert "message" in result
        assert "data" in result
        assert "errors" in result

        # Test __contains__ method - non-existent attributes
        assert "nonexistent" not in result
        assert "missing" not in result

        # Test __getitem__ method - valid access
        assert result["status"] == StageStatus.SUCCESS
        assert result["message"] == "Test message"
        assert result["data"] == {"test": "data"}
        assert result["errors"] == []

        # Test __getitem__ method - missing attributes return None
        assert result["nonexistent"] is None
        assert result["missing_key"] is None

        # Test get() method - default behavior (None)
        assert result.get("status") == StageStatus.SUCCESS
        assert result.get("message") == "Test message"
        assert result.get("nonexistent") is None

        # Test get() method - custom default values
        assert result.get("nonexistent", "default") == "default"
        assert result.get("missing", 42) == 42
        assert (
            result.get("status", "fallback") == StageStatus.SUCCESS
        )  # Existing value wins


class TestStageResultFactories:
    """Test cases for StageResult factory methods with edge cases."""

    def test_success_result_factory_message_only(self):
        """Test success_result factory with message only."""
        result = StageResult.success_result("Success message")

        assert result.status == StageStatus.SUCCESS
        assert result.message == "Success message"
        assert result.data == {}
        assert result.errors == []
        assert result.success is True

    def test_success_result_factory_with_data_dict(self):
        """Test success_result factory with data dict."""
        data = {"key1": "value1", "key2": 42}
        result = StageResult.success_result("Success with data", data)

        assert result.status == StageStatus.SUCCESS
        assert result.message == "Success with data"
        assert result.data == data
        assert result.errors == []

    def test_success_result_factory_none_data_handling(self):
        """Test success_result factory with None data handling."""
        result = StageResult.success_result("Success message", None)

        assert result.status == StageStatus.SUCCESS
        assert result.data == {}  # None converts to empty dict
        assert result.errors == []

    def test_failure_factory_message_only(self):
        """Test failure factory with message only."""
        result = StageResult.failure("Failure message")

        assert result.status == StageStatus.FAILURE
        assert result.message == "Failure message"
        assert result.data == {}
        assert result.errors == []
        assert result.success is False

    def test_failure_factory_with_errors_list(self):
        """Test failure factory with errors list."""
        errors = ["error1", "error2", "error3"]
        result = StageResult.failure("Failure with errors", errors)

        assert result.status == StageStatus.FAILURE
        assert result.message == "Failure with errors"
        assert result.data == {}
        assert result.errors == errors

    def test_failure_factory_none_errors_handling(self):
        """Test failure factory with None errors handling."""
        result = StageResult.failure("Failure message", None)

        assert result.status == StageStatus.FAILURE
        assert result.errors == []  # None converts to empty list

    def test_partial_factory_all_parameter_combinations(self):
        """Test partial factory with all parameter combinations."""
        # Message only
        result1 = StageResult.partial("Partial message")
        assert result1.status == StageStatus.PARTIAL
        assert result1.message == "Partial message"
        assert result1.data == {}
        assert result1.errors == []

        # Message with data
        data = {"partial": "data"}
        result2 = StageResult.partial("Partial with data", data)
        assert result2.data == data
        assert result2.errors == []

        # Message with errors
        errors = ["partial error"]
        result3 = StageResult.partial("Partial with errors", errors=errors)
        assert result3.data == {}
        assert result3.errors == errors

        # All parameters
        result4 = StageResult.partial("Partial complete", data, errors)
        assert result4.data == data
        assert result4.errors == errors

    def test_partial_factory_none_defaults(self):
        """Test partial factory None parameter defaults."""
        result = StageResult.partial("Partial message", None, None)

        assert result.status == StageStatus.PARTIAL
        assert result.data == {}  # None converts to empty dict
        assert result.errors == []  # None converts to empty list

    def test_skipped_factory_proper_defaults(self):
        """Test skipped factory ensures proper defaults."""
        result = StageResult.skipped("Skipped message")

        assert result.status == StageStatus.SKIPPED
        assert result.message == "Skipped message"
        assert result.data == {}  # Must be empty dict
        assert result.errors == []  # Must be empty list
        assert result.success is False


class TestStageABC:
    """Test cases for Stage abstract base class contract validation."""

    def test_stage_abstract_cannot_instantiate(self):
        """Test that Stage abstract class cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class Stage"):
            Stage()

    def test_stage_missing_implementations_fails(self):
        """Test that concrete class without required methods fails."""

        # Class missing all abstract methods
        class IncompleteStage(Stage):
            pass

        with pytest.raises(TypeError):
            IncompleteStage()

        # Class missing _execute_impl method
        class PartialStage(Stage):
            def __init__(self):
                super().__init__()

            @property
            def name(self) -> str:
                return "partial"

            @property
            def display_name(self) -> str:
                return "Partial Stage"

        with pytest.raises(TypeError):
            PartialStage()

    def test_stage_concrete_implementation_contract(self):
        """Test that proper concrete implementation works correctly."""

        class TestStage(Stage):
            def __init__(self):
                super().__init__()

            @property
            def name(self) -> str:
                return "test_stage"

            @property
            def display_name(self) -> str:
                return "Test Stage"

            def _execute_impl(self, context):
                return StageResult.success_result("Test executed")

        # Should create successfully
        stage = TestStage()

        # Test required abstract properties
        assert stage.name == "test_stage"
        assert stage.display_name == "Test Stage"

        # Test required abstract method
        context = PipelineContext("test", Path("/tmp"))
        result = stage.execute(context)
        assert isinstance(result, StageResult)
        assert result.success is True

    def test_stage_required_abstract_methods_properties(self):
        """Test all required abstract methods and properties are defined."""
        # Check that Stage ABC defines the right abstract members
        abstract_methods = Stage.__abstractmethods__

        # Should have exactly these abstract members
        expected_abstracts = {"name", "display_name", "_execute_impl"}
        assert abstract_methods == expected_abstracts


class TestStageDefaultMethods:
    """Test cases for Stage default method implementations."""

    def test_stage_dependencies_property_default(self):
        """Test dependencies property empty list default behavior."""

        class MockStage(Stage):
            def __init__(self):
                super().__init__()

            @property
            def name(self) -> str:
                return "mock"

            @property
            def display_name(self) -> str:
                return "Mock Stage"

            def _execute_impl(self, context):
                return StageResult.success_result("Mock")

        stage = MockStage()
        assert stage.dependencies == []
        assert isinstance(stage.dependencies, list)

    def test_stage_validate_context_method_default(self):
        """Test validate_context method empty error list default."""

        class MockStage(Stage):
            def __init__(self):
                super().__init__()

            @property
            def name(self) -> str:
                return "mock"

            @property
            def display_name(self) -> str:
                return "Mock Stage"

            def _execute_impl(self, context):
                return StageResult.success_result("Mock")

        stage = MockStage()
        context = PipelineContext("test", Path("/tmp"))

        errors = stage.validate_context(context)
        assert errors == []
        assert isinstance(errors, list)

    def test_stage_method_overrides_work_properly(self):
        """Test that subclass overriding defaults works properly."""

        class CustomStage(Stage):
            def __init__(self):
                super().__init__()

            @property
            def name(self) -> str:
                return "custom"

            @property
            def display_name(self) -> str:
                return "Custom Stage"

            def _execute_impl(self, context):
                return StageResult.success_result("Custom")

            @property
            def dependencies(self) -> list[str]:
                return ["prep", "validate"]

            def validate_context(self, context) -> list[str]:
                if not context.get("required_data"):
                    return ["Missing required_data"]
                return []

        stage = CustomStage()

        # Test overridden dependencies
        assert stage.dependencies == ["prep", "validate"]

        # Test overridden validation
        context_without_data = PipelineContext("test", Path("/tmp"))
        assert stage.validate_context(context_without_data) == ["Missing required_data"]

        context_with_data = PipelineContext("test", Path("/tmp"))
        context_with_data.set("required_data", "present")
        assert stage.validate_context(context_with_data) == []


class TestStageIntegration:
    """Integration tests for stage execution and context interaction."""

    def test_stage_execution_flow_concrete_implementation(self):
        """Test stage execution flow with concrete stage implementation."""

        class IntegrationStage(Stage):
            def __init__(self):
                super().__init__()

            @property
            def name(self) -> str:
                return "integration_test"

            @property
            def display_name(self) -> str:
                return "Integration Test Stage"

            def _execute_impl(self, context):
                # Simulate some work
                context.set("stage_data", {"processed": True})
                return StageResult.success_result(
                    "Integration test completed", {"items_processed": 5}
                )

        stage = IntegrationStage()
        context = PipelineContext("test_pipeline", Path("/tmp"))

        result = stage.execute(context)

        # Test result properties
        assert result.success is True
        assert result.status == StageStatus.SUCCESS
        assert "completed" in result.message
        assert result.data["items_processed"] == 5

        # Test context was modified
        assert context.get("stage_data") == {"processed": True}

    def test_stage_context_validation_integration(self):
        """Test stage with validation errors vs clean validation."""

        class ValidatingStage(Stage):
            def __init__(self):
                super().__init__()

            @property
            def name(self) -> str:
                return "validating_stage"

            @property
            def display_name(self) -> str:
                return "Validating Stage"

            def _execute_impl(self, context):
                return StageResult.success_result("Validation passed")

            def validate_context(self, context) -> list[str]:
                errors = []

                if not context.get("input_file"):
                    errors.append("Missing input_file")
                if not context.get("output_dir"):
                    errors.append("Missing output_dir")
                if context.get("max_items", 0) <= 0:
                    errors.append("max_items must be positive")

                return errors

        stage = ValidatingStage()

        # Test with validation errors
        empty_context = PipelineContext("test", Path("/tmp"))
        validation_errors = stage.validate_context(empty_context)

        assert len(validation_errors) == 3
        assert "Missing input_file" in validation_errors
        assert "Missing output_dir" in validation_errors
        assert "max_items must be positive" in validation_errors

        # Test with clean validation
        valid_context = PipelineContext("test", Path("/tmp"))
        valid_context.set("input_file", "/path/to/input")
        valid_context.set("output_dir", "/path/to/output")
        valid_context.set("max_items", 100)

        clean_validation = stage.validate_context(valid_context)
        assert clean_validation == []

    def test_stage_dependencies_handling_integration(self):
        """Test stage with dependencies list vs empty default."""

        class DependentStage(Stage):
            def __init__(self):
                super().__init__()

            @property
            def name(self) -> str:
                return "dependent_stage"

            @property
            def display_name(self) -> str:
                return "Dependent Stage"

            def _execute_impl(self, context):
                return StageResult.success_result("Executed with dependencies")

            @property
            def dependencies(self) -> list[str]:
                return ["prepare", "validate", "setup"]

        stage = DependentStage()

        # Test dependencies are properly returned
        deps = stage.dependencies
        assert len(deps) == 3
        assert "prepare" in deps
        assert "validate" in deps
        assert "setup" in deps

        # Test execution still works
        context = PipelineContext("test", Path("/tmp"))
        result = stage.execute(context)
        assert result.success is True

    def test_stage_error_handling_during_execution(self):
        """Test stage that raises exceptions during execution."""

        class ErrorStage(Stage):
            def __init__(self, should_raise=False):
                super().__init__()
                self.should_raise = should_raise

            @property
            def name(self) -> str:
                return "error_stage"

            @property
            def display_name(self) -> str:
                return "Error Stage"

            def _execute_impl(self, context):
                if self.should_raise:
                    raise ValueError("Simulated execution error")
                return StageResult.success_result("No error")

        # Test normal execution
        normal_stage = ErrorStage(should_raise=False)
        context = PipelineContext("test", Path("/tmp"))

        result = normal_stage.execute(context)
        assert result.success is True

        # Test error execution
        error_stage = ErrorStage(should_raise=True)

        with pytest.raises(ValueError, match="Simulated execution error"):
            error_stage.execute(context)
