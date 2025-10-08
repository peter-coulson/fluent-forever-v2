"""Unit tests for StageResult factory and properties."""


from src.core.stages import StageResult, StageStatus


class TestStageResult:
    """Test StageResult factory methods and properties."""

    def test_success_result_factory(self):
        """Test success result factory method."""
        message = "Operation completed successfully"
        data = {"items_processed": 5, "output_file": "test.txt"}

        result = StageResult.success_result(message, data)

        assert result.status == StageStatus.SUCCESS
        assert result.message == message
        assert result.data == data
        assert result.errors == []
        assert result.success is True

    def test_success_result_factory_no_data(self):
        """Test success result factory method without data."""
        message = "Operation completed successfully"

        result = StageResult.success_result(message)

        assert result.status == StageStatus.SUCCESS
        assert result.message == message
        assert result.data == {}
        assert result.errors == []
        assert result.success is True

    def test_failure_result_factory(self):
        """Test failure result factory method."""
        message = "Operation failed"
        errors = ["Error 1", "Error 2"]

        result = StageResult.failure(message, errors)

        assert result.status == StageStatus.FAILURE
        assert result.message == message
        assert result.data == {}
        assert result.errors == errors
        assert result.success is False

    def test_failure_result_factory_no_errors(self):
        """Test failure result factory method without errors."""
        message = "Operation failed"

        result = StageResult.failure(message)

        assert result.status == StageStatus.FAILURE
        assert result.message == message
        assert result.data == {}
        assert result.errors == []
        assert result.success is False

    def test_partial_result_factory(self):
        """Test partial result factory method."""
        message = "Operation partially completed"
        data = {"processed": 3, "failed": 2}
        errors = ["Failed item 1", "Failed item 2"]

        result = StageResult.partial(message, data, errors)

        assert result.status == StageStatus.PARTIAL
        assert result.message == message
        assert result.data == data
        assert result.errors == errors
        assert result.success is False

    def test_partial_result_factory_minimal(self):
        """Test partial result factory method with minimal parameters."""
        message = "Operation partially completed"

        result = StageResult.partial(message)

        assert result.status == StageStatus.PARTIAL
        assert result.message == message
        assert result.data == {}
        assert result.errors == []
        assert result.success is False

    def test_skipped_result_factory(self):
        """Test skipped result factory method."""
        message = "Operation skipped"

        result = StageResult.skipped(message)

        assert result.status == StageStatus.SKIPPED
        assert result.message == message
        assert result.data == {}
        assert result.errors == []
        assert result.success is False

    def test_success_property_access(self):
        """Test success property for different status types."""
        success_result = StageResult.success_result("Success")
        failure_result = StageResult.failure("Failure")
        partial_result = StageResult.partial("Partial")
        skipped_result = StageResult.skipped("Skipped")

        assert success_result.success is True
        assert failure_result.success is False
        assert partial_result.success is False
        assert skipped_result.success is False

    def test_status_property_access(self):
        """Test status property access."""
        success_result = StageResult.success_result("Success")
        failure_result = StageResult.failure("Failure")
        partial_result = StageResult.partial("Partial")
        skipped_result = StageResult.skipped("Skipped")

        assert success_result.status == StageStatus.SUCCESS
        assert failure_result.status == StageStatus.FAILURE
        assert partial_result.status == StageStatus.PARTIAL
        assert skipped_result.status == StageStatus.SKIPPED

    def test_message_property_access(self):
        """Test message property access."""
        messages = [
            "Success message",
            "Failure message",
            "Partial message",
            "Skipped message",
        ]

        success_result = StageResult.success_result(messages[0])
        failure_result = StageResult.failure(messages[1])
        partial_result = StageResult.partial(messages[2])
        skipped_result = StageResult.skipped(messages[3])

        assert success_result.message == messages[0]
        assert failure_result.message == messages[1]
        assert partial_result.message == messages[2]
        assert skipped_result.message == messages[3]

    def test_data_property_access(self):
        """Test data property access."""
        test_data = {"key1": "value1", "key2": 42}

        success_result = StageResult.success_result("Success", test_data)
        partial_result = StageResult.partial("Partial", test_data)

        assert success_result.data == test_data
        assert partial_result.data == test_data

        # Test empty data for results without data
        failure_result = StageResult.failure("Failure")
        skipped_result = StageResult.skipped("Skipped")

        assert failure_result.data == {}
        assert skipped_result.data == {}

    def test_errors_property_access(self):
        """Test errors property access."""
        test_errors = ["Error 1", "Error 2", "Error 3"]

        failure_result = StageResult.failure("Failure", test_errors)
        partial_result = StageResult.partial("Partial", errors=test_errors)

        assert failure_result.errors == test_errors
        assert partial_result.errors == test_errors

        # Test empty errors for results without errors
        success_result = StageResult.success_result("Success")
        skipped_result = StageResult.skipped("Skipped")

        assert success_result.errors == []
        assert skipped_result.errors == []

    def test_contains_method(self):
        """Test __contains__ method for attribute checking."""
        result = StageResult.success_result("Success")

        assert "status" in result
        assert "message" in result
        assert "data" in result
        assert "errors" in result
        assert "success" in result
        assert "nonexistent_attr" not in result

    def test_getitem_method(self):
        """Test __getitem__ method for attribute access."""
        message = "Test message"
        data = {"test": "value"}
        result = StageResult.success_result(message, data)

        assert result["status"] == StageStatus.SUCCESS
        assert result["message"] == message
        assert result["data"] == data
        assert result["errors"] == []
        assert result["success"] is True
        assert result["nonexistent_attr"] is None

    def test_get_method(self):
        """Test get method for attribute access with defaults."""
        message = "Test message"
        result = StageResult.success_result(message)

        assert result.get("status") == StageStatus.SUCCESS
        assert result.get("message") == message
        assert result.get("nonexistent_attr") is None
        assert result.get("nonexistent_attr", "default") == "default"
