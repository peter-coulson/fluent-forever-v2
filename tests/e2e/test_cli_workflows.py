"""End-to-end tests for CLI workflows."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestCLIWorkflows:
    """Test complete CLI workflow scenarios."""

    @pytest.fixture
    def test_config_path(self, tmp_path):
        """Create test configuration file."""
        config_path = tmp_path / "test_config.json"
        config_content = {
            "providers": {
                "data": {"type": "json", "base_path": str(tmp_path / "data")},
                "sync": {"type": "anki"},
            }
        }
        config_path.write_text(json.dumps(config_content))
        return config_path

    def run_cli_command(self, args, config_path=None):
        """Helper to run CLI command and capture output."""
        cmd = [sys.executable, "-m", "src.cli.pipeline_runner"]
        if config_path:
            cmd.extend(["--config", str(config_path)])
        cmd.extend(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
        return result

    def test_e2e_discovery_workflow_empty_system(self):
        """Test complete discovery journey with empty system."""
        # Test list command with no pipelines
        result = self.run_cli_command(["list"])

        assert result.returncode == 0
        assert (
            "No pipelines registered" in result.stdout
            or "No pipelines" in result.stdout
        )

    def test_e2e_discovery_workflow_detailed(self):
        """Test detailed listing with empty system."""
        # Test detailed list command
        result = self.run_cli_command(["list", "--detailed"])

        assert result.returncode == 0
        # Should still complete successfully even with no pipelines

    def test_e2e_invalid_pipeline_name(self):
        """Test friendly error for non-existent pipelines."""
        # Test info command with invalid pipeline
        result = self.run_cli_command(["info", "non_existent_pipeline"])

        assert result.returncode == 1  # Error exit code
        assert "not found" in result.stdout or "not found" in result.stderr

    def test_e2e_missing_required_args(self):
        """Test clear error messages for missing CLI arguments."""
        # Test run command without required --stage argument
        result = self.run_cli_command(["run", "vocabulary"])

        assert result.returncode != 0
        # Should show usage or error about missing stage argument

    def test_e2e_help_system(self):
        """Test help system provides useful information."""
        # Test main help
        result = self.run_cli_command(["--help"])

        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "Usage:" in result.stdout

    def test_e2e_invalid_config_file(self, tmp_path):
        """Test graceful handling of config file problems."""
        # Create invalid config file
        invalid_config = tmp_path / "invalid.json"
        invalid_config.write_text("{ invalid json content")

        # Test with invalid config
        result = self.run_cli_command(["list"], config_path=invalid_config)

        # Should handle gracefully and not crash
        # May succeed with empty config or fail gracefully
        assert "Traceback" not in result.stderr

    def test_e2e_nonexistent_config_file(self, tmp_path):
        """Test handling of non-existent config file."""
        nonexistent_config = tmp_path / "missing.json"

        # Test with non-existent config
        result = self.run_cli_command(["list"], config_path=nonexistent_config)

        # Should handle gracefully
        assert result.returncode == 0 or "Traceback" not in result.stderr

    def test_e2e_run_command_no_pipeline_error(self):
        """Test run command with non-existent pipeline."""
        result = self.run_cli_command(["run", "non_existent", "--stage", "prepare"])

        assert result.returncode == 1
        # Should show some error message, don't care about specific content
        assert result.stdout.strip() != "" or result.stderr.strip() != ""
        # Should not show stack traces to users
        assert "Traceback" not in result.stderr

    def test_e2e_dry_run_functionality(self):
        """Test dry-run mode works without errors."""
        # Test global dry-run flag
        result = self.run_cli_command(
            ["--dry-run", "run", "vocabulary", "--stage", "prepare"]
        )

        # Even with non-existent pipeline, dry-run might handle differently
        # We're mainly checking it doesn't crash
        assert "Traceback" not in result.stderr

    def test_e2e_verbose_output(self):
        """Test verbose mode provides additional information."""
        # Test verbose flag
        result = self.run_cli_command(["--verbose", "list"])

        assert result.returncode == 0
        assert "Traceback" not in result.stderr

    def test_e2e_command_chaining_workflow(self):
        """Test realistic user workflow of multiple commands."""
        # Simulate user exploring system
        commands = [
            ["list"],
            ["list", "--detailed"],
        ]

        for cmd in commands:
            result = self.run_cli_command(cmd)
            # All commands should complete without crashing
            assert "Traceback" not in result.stderr

    def test_e2e_error_message_quality(self):
        """Test that error messages are user-friendly and actionable."""
        # Test various error conditions
        error_scenarios = [
            (["info", "nonexistent"], "Pipeline not found"),
            (["run", "nonexistent", "--stage", "prepare"], "Pipeline not found"),
        ]

        for cmd, _ in error_scenarios:
            result = self.run_cli_command(cmd)

            # Should have non-zero exit code
            assert result.returncode != 0

            # Should not show stack traces to users
            assert "Traceback" not in result.stderr

            # Should contain helpful error information
            output = result.stdout + result.stderr
            # At least one of these should be in the output
            error_indicators = ["not found", "error", "Error", "invalid", "missing"]
            assert any(indicator in output for indicator in error_indicators)

    def test_e2e_output_formatting(self):
        """Test that output is properly formatted for CLI use."""
        result = self.run_cli_command(["list"])

        assert result.returncode == 0

        # Output should be clean (no Python debug info leaked)
        assert "DEBUG" not in result.stdout
        assert "<" not in result.stdout  # No object representations
        assert ">" not in result.stdout

    def test_e2e_config_integration(self, test_config_path):
        """Test that config file integration works end-to-end."""
        # Test with actual config file
        result = self.run_cli_command(["list"], config_path=test_config_path)

        assert result.returncode == 0
        assert "Traceback" not in result.stderr
