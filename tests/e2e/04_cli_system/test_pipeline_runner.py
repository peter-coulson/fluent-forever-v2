#!/usr/bin/env python3
"""
Session 5 Validation Gate: Universal Pipeline Runner

Tests the contract for the unified CLI pipeline execution system.
These tests define how the CLI should provide consistent access
to all pipeline functionality.

CONTRACT BEING TESTED:
- Universal CLI runner executes any pipeline stage
- Consistent command structure across all pipelines
- Proper argument parsing and validation
- Error handling and user feedback
- Help system and discoverability
"""

import pytest
from typing import Dict, Any, List
from tests.e2e.conftest import MockPipeline


class TestPipelineRunnerContract:
    """Test universal pipeline runner contracts"""
    
    def test_basic_pipeline_execution(self):
        """Contract: CLI can execute any pipeline stage"""
        runner = MockPipelineRunner()
        
        # Register test pipeline
        pipeline = MockPipeline("vocabulary", stages=["claude_batch", "media_gen", "sync"])
        runner.register_pipeline(pipeline)
        
        # Should execute pipeline stage
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "claude_batch", 
            "--words", "casa,haber"
        ])
        
        assert result["status"] == "success"
        assert result["pipeline"] == "vocabulary"
        assert result["stage"] == "claude_batch"
        assert "casa" in result["context"]["words"]
    
    def test_pipeline_discovery(self):
        """Contract: CLI provides pipeline discovery"""
        runner = MockPipelineRunner()
        
        # Register multiple pipelines
        runner.register_pipeline(MockPipeline("vocabulary"))
        runner.register_pipeline(MockPipeline("conjugation"))
        
        # List pipelines
        result = runner.execute_command(["list"])
        
        assert result["status"] == "success"
        assert "vocabulary" in result["pipelines"]
        assert "conjugation" in result["pipelines"]
    
    def test_pipeline_info(self):
        """Contract: CLI provides detailed pipeline information"""
        runner = MockPipelineRunner()
        
        pipeline = MockPipeline("vocabulary", stages=["stage1", "stage2", "stage3"])
        runner.register_pipeline(pipeline)
        
        # Get pipeline info
        result = runner.execute_command(["info", "vocabulary"])
        
        assert result["status"] == "success"
        assert result["pipeline_name"] == "vocabulary"
        assert "stages" in result["info"]
        assert len(result["info"]["stages"]) == 3
    
    def test_stage_listing(self):
        """Contract: CLI lists available stages for pipeline"""
        runner = MockPipelineRunner()
        
        pipeline = MockPipeline("vocabulary", stages=["claude_batch", "media_gen", "sync"])
        runner.register_pipeline(pipeline)
        
        # List stages
        result = runner.execute_command(["stages", "vocabulary"])
        
        assert result["status"] == "success"
        assert "claude_batch" in result["stages"]
        assert "media_gen" in result["stages"]
        assert "sync" in result["stages"]
    
    def test_help_system(self):
        """Contract: CLI provides comprehensive help"""
        runner = MockPipelineRunner()
        
        # General help
        help_result = runner.execute_command(["help"])
        assert help_result["status"] == "success"
        assert "usage" in help_result["help"].lower()
        
        # Pipeline-specific help
        runner.register_pipeline(MockPipeline("vocabulary"))
        pipeline_help = runner.execute_command(["help", "vocabulary"])
        assert pipeline_help["status"] == "success"
        assert "vocabulary" in pipeline_help["help"]


class TestCLIArgumentParsing:
    """Test CLI argument parsing contracts"""
    
    def test_stage_execution_arguments(self):
        """Contract: Stage execution supports required arguments"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["claude_batch"])
        runner.register_pipeline(pipeline)
        
        # Test various argument patterns
        test_cases = [
            # Basic execution
            ["run", "vocabulary", "--stage", "claude_batch", "--words", "casa"],
            # Multiple words
            ["run", "vocabulary", "--stage", "claude_batch", "--words", "casa,haber,ser"],
            # With options
            ["run", "vocabulary", "--stage", "claude_batch", "--words", "casa", "--dry-run"],
            # With config override
            ["run", "vocabulary", "--stage", "claude_batch", "--words", "casa", "--config", "batch_size=3"]
        ]
        
        for args in test_cases:
            result = runner.execute_command(args)
            assert result["status"] == "success", f"Failed with args: {args}"
    
    def test_boolean_flags(self):
        """Contract: Boolean flags are parsed correctly"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["media_gen"])
        runner.register_pipeline(pipeline)
        
        # Test boolean flags
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "media_gen", 
            "--cards", "card1,card2", "--execute", "--no-images"
        ])
        
        assert result["status"] == "success"
        assert result["context"]["execute"] is True
        assert result["context"]["no_images"] is True
    
    def test_config_overrides(self):
        """Contract: Configuration can be overridden via CLI"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["sync"])
        runner.register_pipeline(pipeline)
        
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "sync",
            "--cards", "card1",
            "--config", "timeout=60,retries=3,dry_run=true"
        ])
        
        assert result["status"] == "success"
        context_config = result["context"]["config"]
        assert context_config["timeout"] == 60
        assert context_config["retries"] == 3
        assert context_config["dry_run"] is True
    
    def test_argument_validation(self):
        """Contract: Invalid arguments are rejected with helpful messages"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["claude_batch"])
        runner.register_pipeline(pipeline)
        
        # Missing required arguments
        result = runner.execute_command(["run", "vocabulary", "--stage", "claude_batch"])
        assert result["status"] == "error"
        assert "missing required" in result["error"].lower()
        
        # Invalid pipeline
        result = runner.execute_command(["run", "nonexistent", "--stage", "test"])
        assert result["status"] == "error"
        assert "pipeline not found" in result["error"].lower()
        
        # Invalid stage
        result = runner.execute_command(["run", "vocabulary", "--stage", "nonexistent"])
        assert result["status"] == "error"
        assert "stage not found" in result["error"].lower()


class TestCLIErrorHandling:
    """Test CLI error handling contracts"""
    
    def test_pipeline_execution_errors(self):
        """Contract: Pipeline execution errors are handled gracefully"""
        runner = MockPipelineRunner()
        
        # Pipeline that fails
        failing_pipeline = MockPipeline("failing", stages=["fail_stage"])
        failing_pipeline.should_fail = True
        runner.register_pipeline(failing_pipeline)
        
        result = runner.execute_command([
            "run", "failing", "--stage", "fail_stage", "--words", "test"
        ])
        
        assert result["status"] == "error"
        assert "execution failed" in result["error"].lower()
        assert result["pipeline"] == "failing"
        assert result["stage"] == "fail_stage"
    
    def test_user_interruption(self):
        """Contract: User interruption (Ctrl+C) is handled gracefully"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["long_stage"])
        runner.register_pipeline(pipeline)
        
        # Simulate user interruption
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "long_stage", "--words", "test"
        ], simulate_interrupt=True)
        
        assert result["status"] == "interrupted"
        assert "interrupted by user" in result["message"].lower()
    
    def test_configuration_errors(self):
        """Contract: Configuration errors are reported clearly"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["config_stage"])
        runner.register_pipeline(pipeline)
        
        # Invalid configuration format
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "config_stage",
            "--words", "test", "--config", "invalid_format"
        ])
        
        assert result["status"] == "error"
        assert "configuration" in result["error"].lower()
    
    def test_permission_errors(self):
        """Contract: Permission errors are handled appropriately"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["file_stage"])
        runner.register_pipeline(pipeline)
        
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "file_stage",
            "--words", "test", "--simulate", "permission_error"
        ])
        
        assert result["status"] == "error"
        assert "permission" in result["error"].lower()


class TestCLIOutputFormatting:
    """Test CLI output formatting contracts"""
    
    def test_success_output_format(self):
        """Contract: Success output is formatted consistently"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["test_stage"])
        runner.register_pipeline(pipeline)
        
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "test_stage", "--words", "casa"
        ])
        
        output = runner.format_output(result)
        
        # Should have standard success format
        assert "✓" in output or "SUCCESS" in output
        assert result["pipeline"] in output
        assert result["stage"] in output
    
    def test_error_output_format(self):
        """Contract: Error output is formatted helpfully"""
        runner = MockPipelineRunner()
        
        # Command that causes error
        result = runner.execute_command(["run", "nonexistent"])
        output = runner.format_output(result)
        
        # Should have clear error format
        assert "✗" in output or "ERROR" in output
        assert result["error"] in output
    
    def test_progress_output(self):
        """Contract: Long-running operations show progress"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["batch_stage"])
        runner.register_pipeline(pipeline)
        
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "batch_stage",
            "--words", "casa,haber,ser", "--show-progress"
        ])
        
        assert result["status"] == "success"
        assert "progress_updates" in result
        assert len(result["progress_updates"]) > 0
    
    def test_verbose_output(self):
        """Contract: Verbose mode provides detailed information"""
        runner = MockPipelineRunner()
        pipeline = MockPipeline("vocabulary", stages=["test_stage"])
        runner.register_pipeline(pipeline)
        
        result = runner.execute_command([
            "run", "vocabulary", "--stage", "test_stage", 
            "--words", "casa", "--verbose"
        ])
        
        assert result["status"] == "success"
        assert "debug_info" in result
        assert "execution_details" in result["debug_info"]


# Mock CLI Runner Implementation
class MockPipelineRunner:
    """Mock CLI pipeline runner"""
    
    def __init__(self):
        self.pipelines = {}
    
    def register_pipeline(self, pipeline: MockPipeline):
        """Register a pipeline"""
        self.pipelines[pipeline.name] = pipeline
    
    def execute_command(self, args: List[str], simulate_interrupt: bool = False) -> Dict[str, Any]:
        """Execute CLI command"""
        if simulate_interrupt:
            return {
                "status": "interrupted",
                "message": "Interrupted by user"
            }
        
        if not args:
            return {"status": "error", "error": "No command provided"}
        
        command = args[0]
        
        if command == "list":
            return {
                "status": "success",
                "pipelines": list(self.pipelines.keys())
            }
        
        elif command == "info" and len(args) > 1:
            pipeline_name = args[1]
            if pipeline_name not in self.pipelines:
                return {"status": "error", "error": f"Pipeline {pipeline_name} not found"}
            
            pipeline = self.pipelines[pipeline_name]
            return {
                "status": "success",
                "pipeline_name": pipeline_name,
                "info": pipeline.get_info()
            }
        
        elif command == "stages" and len(args) > 1:
            pipeline_name = args[1]
            if pipeline_name not in self.pipelines:
                return {"status": "error", "error": f"Pipeline {pipeline_name} not found"}
            
            pipeline = self.pipelines[pipeline_name]
            return {
                "status": "success",
                "stages": pipeline.get_available_stages()
            }
        
        elif command == "help":
            if len(args) > 1:
                pipeline_name = args[1]
                return {
                    "status": "success",
                    "help": f"Help for {pipeline_name} pipeline"
                }
            else:
                return {
                    "status": "success", 
                    "help": "Usage: pipeline <command> [options]"
                }
        
        elif command == "run":
            return self._execute_run_command(args[1:])
        
        else:
            return {"status": "error", "error": f"Unknown command: {command}"}
    
    def _execute_run_command(self, args: List[str]) -> Dict[str, Any]:
        """Execute run command"""
        if len(args) < 1:
            return {"status": "error", "error": "Missing required argument: pipeline"}
        
        pipeline_name = args[0]
        if pipeline_name not in self.pipelines:
            return {"status": "error", "error": f"Pipeline not found: {pipeline_name}"}
        
        # Parse arguments
        parsed = self._parse_run_args(args[1:])
        if "error" in parsed:
            return {"status": "error", "error": parsed["error"]}
        
        pipeline = self.pipelines[pipeline_name]
        stage_name = parsed["stage"]
        
        if stage_name not in pipeline.get_available_stages():
            return {"status": "error", "error": f"Stage not found: {stage_name}"}
        
        # Check for simulated errors
        if parsed["context"].get("simulate") == "permission_error":
            return {"status": "error", "error": "Permission denied"}
        
        # Execute pipeline stage
        try:
            if getattr(pipeline, 'should_fail', False):
                raise RuntimeError("Pipeline execution failed")
            
            stage_result = pipeline.execute_stage(stage_name, parsed["context"])
            
            result = {
                "status": "success",
                "pipeline": pipeline_name,
                "stage": stage_name,
                "context": parsed["context"],
                "stage_result": stage_result
            }
            
            # Add verbose info if requested
            if parsed["context"].get("verbose"):
                result["debug_info"] = {
                    "execution_details": "Detailed execution information"
                }
            
            # Add progress if requested
            if parsed["context"].get("show_progress"):
                result["progress_updates"] = [
                    "Step 1 completed", "Step 2 completed", "Stage completed"
                ]
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Execution failed: {str(e)}",
                "pipeline": pipeline_name,
                "stage": stage_name
            }
    
    def _parse_run_args(self, args: List[str]) -> Dict[str, Any]:
        """Parse run command arguments"""
        result = {
            "stage": None,
            "context": {}
        }
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == "--stage":
                if i + 1 >= len(args):
                    return {"error": "Missing value for --stage"}
                result["stage"] = args[i + 1]
                i += 2
            elif arg == "--words":
                if i + 1 >= len(args):
                    return {"error": "Missing value for --words"}
                result["context"]["words"] = args[i + 1].split(",")
                i += 2
            elif arg == "--cards":
                if i + 1 >= len(args):
                    return {"error": "Missing value for --cards"}
                result["context"]["cards"] = args[i + 1].split(",")
                i += 2
            elif arg == "--config":
                if i + 1 >= len(args):
                    return {"error": "Missing value for --config"}
                config_str = args[i + 1]
                try:
                    config = self._parse_config_string(config_str)
                    result["context"]["config"] = config
                except ValueError:
                    return {"error": "Invalid configuration format"}
                i += 2
            elif arg == "--dry-run":
                result["context"]["dry_run"] = True
                i += 1
            elif arg == "--execute":
                result["context"]["execute"] = True
                i += 1
            elif arg == "--no-images":
                result["context"]["no_images"] = True
                i += 1
            elif arg == "--verbose":
                result["context"]["verbose"] = True
                i += 1
            elif arg == "--show-progress":
                result["context"]["show_progress"] = True
                i += 1
            elif arg == "--simulate":
                if i + 1 >= len(args):
                    return {"error": "Missing value for --simulate"}
                result["context"]["simulate"] = args[i + 1]
                i += 2
            else:
                return {"error": f"Unknown argument: {arg}"}
        
        if result["stage"] is None:
            return {"error": "Missing required argument: --stage"}
        
        # Check for required context
        if result["stage"] in ["claude_batch"] and "words" not in result["context"]:
            return {"error": "Missing required argument for claude_batch stage: --words"}
        
        return result
    
    def _parse_config_string(self, config_str: str) -> Dict[str, Any]:
        """Parse configuration string"""
        config = {}
        pairs = config_str.split(",")
        
        for pair in pairs:
            if "=" not in pair:
                raise ValueError("Invalid config format")
            
            key, value = pair.split("=", 1)
            
            # Type conversion
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit():
                value = float(value)
            
            config[key] = value
        
        return config
    
    def format_output(self, result: Dict[str, Any]) -> str:
        """Format command output"""
        if result["status"] == "success":
            if "pipelines" in result:
                return f"✓ Available pipelines: {', '.join(result['pipelines'])}"
            elif "pipeline" in result:
                return f"✓ SUCCESS: {result['pipeline']}.{result.get('stage', 'unknown')}"
            else:
                return "✓ SUCCESS"
        
        elif result["status"] == "error":
            return f"✗ ERROR: {result['error']}"
        
        else:
            return f"Status: {result['status']}"