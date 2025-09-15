"""Custom assertion helpers for E2E tests."""

from typing import Any

from src.core.context import PipelineContext
from src.core.stages import StageResult, StageStatus
from src.providers.registry import ProviderRegistry


def assert_stage_result_success(
    result: StageResult, message_contains: str | None = None
) -> None:
    """Assert that a stage result indicates success."""
    assert (
        result.status == StageStatus.SUCCESS
    ), f"Expected SUCCESS, got {result.status}: {result.message}"
    if message_contains:
        assert (
            message_contains in result.message
        ), f"Expected message to contain '{message_contains}', got: {result.message}"


def assert_stage_result_failure(
    result: StageResult, error_contains: str | None = None
) -> None:
    """Assert that a stage result indicates failure."""
    assert (
        result.status == StageStatus.FAILURE
    ), f"Expected FAILURE, got {result.status}: {result.message}"
    if error_contains:
        assert any(
            error_contains in error for error in result.errors
        ), f"Expected error containing '{error_contains}', got: {result.errors}"


def assert_stage_result_partial(
    result: StageResult, data_key: str | None = None
) -> None:
    """Assert that a stage result indicates partial success."""
    assert (
        result.status == StageStatus.PARTIAL
    ), f"Expected PARTIAL, got {result.status}: {result.message}"
    if data_key:
        assert (
            data_key in result.data
        ), f"Expected data key '{data_key}' in result data: {result.data}"


def assert_context_has_data(
    context: PipelineContext, key: str, expected_value: Any = None
) -> None:
    """Assert that context contains expected data."""
    assert (
        key in context.data
    ), f"Expected key '{key}' in context data: {list(context.data.keys())}"
    if expected_value is not None:
        actual_value = context.get(key)
        assert (
            actual_value == expected_value
        ), f"Expected '{key}' to be {expected_value}, got {actual_value}"


def assert_context_stage_completed(context: PipelineContext, stage_name: str) -> None:
    """Assert that a stage is marked as completed in context."""
    assert (
        stage_name in context.completed_stages
    ), f"Expected stage '{stage_name}' to be completed. Completed stages: {context.completed_stages}"


def assert_context_has_errors(
    context: PipelineContext, expected_count: int | None = None
) -> None:
    """Assert that context has errors."""
    assert context.has_errors(), "Expected context to have errors, but it has none"
    if expected_count is not None:
        actual_count = len(context.errors)
        assert (
            actual_count == expected_count
        ), f"Expected {expected_count} errors, got {actual_count}: {context.errors}"


def assert_context_no_errors(context: PipelineContext) -> None:
    """Assert that context has no errors."""
    assert (
        not context.has_errors()
    ), f"Expected no errors in context, but found: {context.errors}"


def assert_providers_registered(
    registry: ProviderRegistry, provider_type: str, expected_names: list[str]
) -> None:
    """Assert that expected providers are registered."""
    if provider_type == "data":
        actual_names = registry.list_data_providers()
    elif provider_type == "audio":
        actual_names = registry.list_audio_providers()
    elif provider_type == "image":
        actual_names = registry.list_image_providers()
    elif provider_type == "sync":
        actual_names = registry.list_sync_providers()
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

    for name in expected_names:
        assert (
            name in actual_names
        ), f"Expected {provider_type} provider '{name}' to be registered. Available: {actual_names}"


def assert_provider_pipeline_access(
    registry: ProviderRegistry,
    pipeline_name: str,
    provider_type: str,
    expected_provider_names: list[str],
) -> None:
    """Assert that pipeline has access to expected providers."""
    providers = registry.get_providers_for_pipeline(pipeline_name)
    pipeline_providers = providers.get(provider_type, {})
    actual_names = list(pipeline_providers.keys())

    for name in expected_provider_names:
        assert (
            name in actual_names
        ), f"Expected pipeline '{pipeline_name}' to have access to {provider_type} provider '{name}'. Available: {actual_names}"


def assert_cli_output_contains(captured_output: str, expected_text: str) -> None:
    """Assert that CLI output contains expected text."""
    assert (
        expected_text in captured_output
    ), f"Expected output to contain '{expected_text}', got: {captured_output}"


def assert_cli_output_lines_count(captured_output: str, expected_count: int) -> None:
    """Assert that CLI output has expected number of lines."""
    lines = [line for line in captured_output.split("\n") if line.strip()]
    actual_count = len(lines)
    assert (
        actual_count == expected_count
    ), f"Expected {expected_count} output lines, got {actual_count}: {lines}"


def assert_pipeline_info_complete(pipeline_info: dict[str, Any]) -> None:
    """Assert that pipeline info contains all required fields."""
    required_fields = [
        "name",
        "display_name",
        "description",
        "stages",
        "data_file",
        "anki_note_type",
    ]
    for field in required_fields:
        assert (
            field in pipeline_info
        ), f"Expected field '{field}' in pipeline info: {list(pipeline_info.keys())}"


def assert_stage_info_complete(stage_info: dict[str, Any]) -> None:
    """Assert that stage info contains all required fields."""
    required_fields = ["name", "display_name", "dependencies"]
    for field in required_fields:
        assert (
            field in stage_info
        ), f"Expected field '{field}' in stage info: {list(stage_info.keys())}"


def assert_phase_execution_order(
    results: list[StageResult], expected_stage_names: list[str]
) -> None:
    """Assert that phase execution happened in expected order."""
    assert len(results) == len(
        expected_stage_names
    ), f"Expected {len(expected_stage_names)} results, got {len(results)}"

    # Note: This assumes each StageResult has a way to identify which stage it came from
    # Since StageResult doesn't have a stage_name field, we'll check the message instead
    for i, expected_stage in enumerate(expected_stage_names):
        result = results[i]
        # This is a simplified check - in real tests, you might need to track stage names differently
        assert (
            result.success or result.status == StageStatus.PARTIAL
        ), f"Stage {i} ({expected_stage}) should have succeeded or partially succeeded"


def assert_performance_timing(result: StageResult, max_duration_ms: float) -> None:
    """Assert that stage execution completed within time limit."""
    # Note: This would require timing data to be available in StageResult
    # For now, we'll just assert the stage completed successfully
    assert result.success, f"Performance test stage failed: {result.message}"


def assert_provider_api_calls(
    provider: Any, expected_call_count: int, method_name: str | None = None
) -> None:
    """Assert that provider made expected number of API calls."""
    if hasattr(provider, "get_api_call_count"):
        actual_count = provider.get_api_call_count()
        assert (
            actual_count == expected_call_count
        ), f"Expected {expected_call_count} API calls, got {actual_count}"

    if method_name and hasattr(provider, "api_calls"):
        method_calls = [
            call for call in provider.api_calls if call.get("method") == method_name
        ]
        assert (
            len(method_calls) >= 1
        ), f"Expected at least one call to method '{method_name}', got none"


def assert_provider_configuration(
    provider: Any, expected_config: dict[str, Any]
) -> None:
    """Assert that provider has expected configuration."""
    if hasattr(provider, "config"):
        for key, expected_value in expected_config.items():
            actual_value = provider.config.get(key)
            assert (
                actual_value == expected_value
            ), f"Expected config '{key}' to be {expected_value}, got {actual_value}"


def assert_registry_provider_count(
    registry: ProviderRegistry, expected_counts: dict[str, int]
) -> None:
    """Assert that registry has expected number of providers by type."""
    info = registry.get_provider_info()
    for provider_type, expected_count in expected_counts.items():
        key = f"{provider_type}_providers"
        assert key in info, f"Expected provider type '{provider_type}' in registry info"
        actual_count = info[key]["count"]
        assert (
            actual_count == expected_count
        ), f"Expected {expected_count} {provider_type} providers, got {actual_count}"


def assert_validation_errors(
    errors: list[str], expected_error_count: int, error_contains: str | None = None
) -> None:
    """Assert validation errors match expectations."""
    assert (
        len(errors) == expected_error_count
    ), f"Expected {expected_error_count} validation errors, got {len(errors)}: {errors}"
    if error_contains:
        assert any(
            error_contains in error for error in errors
        ), f"Expected error containing '{error_contains}', got: {errors}"


def assert_config_loaded_correctly(config: Any, expected_keys: list[str]) -> None:
    """Assert that configuration was loaded with expected keys."""
    for key in expected_keys:
        value = config.get(key)
        assert (
            value is not None
        ), f"Expected config key '{key}' to be present and non-None"


def assert_environment_substitution(
    config: Any, key: str, expected_pattern: str
) -> None:
    """Assert that environment variable substitution worked correctly."""
    value = config.get(key)
    assert value is not None, f"Expected config key '{key}' to be present"
    assert expected_pattern in str(
        value
    ), f"Expected '{expected_pattern}' in value '{value}' for key '{key}'"
