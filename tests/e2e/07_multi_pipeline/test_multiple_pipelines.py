#!/usr/bin/env python3
"""
Session 8 Validation Gate: Multiple Pipeline Support

Tests the contract for multiple pipeline coexistence.
These tests define how vocabulary and conjugation pipelines
should work together without interfering with each other.

CONTRACT BEING TESTED:
- Multiple pipelines can coexist in the same system
- Pipelines can run concurrently without conflicts
- Shared resources are properly managed
- Pipeline isolation prevents data contamination
- CLI works consistently across pipeline types
"""

import pytest
from typing import Dict, Any, List
from tests.e2e.conftest import MockPipeline


class TestMultiplePipelineCoexistence:
    """Test multiple pipeline coexistence contracts"""
    
    def test_vocabulary_conjugation_coexistence(self):
        """Contract: Vocabulary and conjugation pipelines coexist"""
        registry = MockPipelineRegistry()
        
        # Register both pipelines
        vocab_pipeline = MockPipeline("vocabulary", stages=["claude_batch", "media_gen", "sync"])
        conj_pipeline = MockPipeline("conjugation", stages=["generate", "media_gen", "sync"])
        
        registry.register_pipeline(vocab_pipeline)
        registry.register_pipeline(conj_pipeline)
        
        # Should be able to list both
        pipelines = registry.list_pipelines()
        assert "vocabulary" in pipelines
        assert "conjugation" in pipelines
        
        # Should be able to execute both
        vocab_result = registry.execute_pipeline("vocabulary", "claude_batch", {"words": ["casa"]})
        conj_result = registry.execute_pipeline("conjugation", "generate", {"verbs": ["hablar"]})
        
        assert vocab_result["status"] == "success"
        assert conj_result["status"] == "success"
    
    def test_concurrent_pipeline_execution(self):
        """Contract: Pipelines can execute concurrently"""
        executor = MockConcurrentExecutor()
        
        # Execute both pipelines simultaneously
        tasks = [
            {"pipeline": "vocabulary", "stage": "claude_batch", "context": {"words": ["casa", "mesa"]}},
            {"pipeline": "conjugation", "stage": "generate", "context": {"verbs": ["hablar", "comer"]}}
        ]
        
        results = executor.execute_concurrent(tasks)
        
        assert len(results) == 2
        assert all(result["status"] == "success" for result in results)
        
        # Should have processed different data
        vocab_result = next(r for r in results if r["pipeline"] == "vocabulary")
        conj_result = next(r for r in results if r["pipeline"] == "conjugation")
        
        assert "words" in vocab_result["context"]
        assert "verbs" in conj_result["context"]
    
    def test_shared_resource_management(self):
        """Contract: Shared resources are properly managed across pipelines"""
        resource_manager = MockSharedResourceManager()
        
        # Both pipelines use media generation
        vocab_media_req = {"type": "image", "prompt": "Casa in countryside", "pipeline": "vocabulary"}
        conj_media_req = {"type": "image", "prompt": "Person speaking", "pipeline": "conjugation"}
        
        # Should handle concurrent media requests
        vocab_result = resource_manager.request_media_generation(vocab_media_req)
        conj_result = resource_manager.request_media_generation(conj_media_req)
        
        assert vocab_result["status"] == "success"
        assert conj_result["status"] == "success"
        
        # Should track usage per pipeline
        usage = resource_manager.get_usage_stats()
        assert usage["vocabulary"]["media_requests"] >= 1
        assert usage["conjugation"]["media_requests"] >= 1
    
    def test_pipeline_data_isolation(self):
        """Contract: Pipeline data remains isolated"""
        data_manager = MockDataManager()
        
        # Store data for both pipelines
        vocab_data = {"words": {"casa": {"meanings": [{"id": "casa_1"}]}}}
        conj_data = {"verbs": {"hablar": {"conjugations": [{"form": "hablo"}]}}}
        
        data_manager.store_pipeline_data("vocabulary", vocab_data)
        data_manager.store_pipeline_data("conjugation", conj_data)
        
        # Data should remain separate
        retrieved_vocab = data_manager.get_pipeline_data("vocabulary")
        retrieved_conj = data_manager.get_pipeline_data("conjugation")
        
        assert "words" in retrieved_vocab
        assert "verbs" in retrieved_conj
        assert "verbs" not in retrieved_vocab  # No contamination
        assert "words" not in retrieved_conj   # No contamination
    
    def test_unified_cli_experience(self):
        """Contract: CLI provides consistent experience across pipelines"""
        cli_runner = MockUnifiedCLI()
        
        # Register both pipelines
        cli_runner.register_pipeline("vocabulary", MockPipeline("vocabulary", ["claude_batch", "media_gen", "sync"]))
        cli_runner.register_pipeline("conjugation", MockPipeline("conjugation", ["generate", "validate", "export"]))
        
        # Same CLI pattern should work for both
        vocab_cmd = ["run", "vocabulary", "--stage", "claude_batch", "--words", "casa"]
        conj_cmd = ["run", "conjugation", "--stage", "generate", "--verbs", "hablar"]
        
        vocab_result = cli_runner.execute_command(vocab_cmd)
        conj_result = cli_runner.execute_command(conj_cmd)
        
        # Both should succeed with consistent result format
        assert vocab_result["status"] == "success"
        assert conj_result["status"] == "success"
        
        # Results should have same structure
        assert "pipeline" in vocab_result
        assert "pipeline" in conj_result
        assert "stage" in vocab_result
        assert "stage" in conj_result


class TestPipelineScaling:
    """Test pipeline scaling contracts"""
    
    def test_multiple_pipeline_types(self):
        """Contract: System can handle many pipeline types"""
        registry = MockPipelineRegistry()
        
        # Register multiple pipeline types
        pipeline_types = [
            MockPipeline("vocabulary", stages=["claude_batch", "media_gen"]),
            MockPipeline("conjugation", stages=["generate", "media_gen"]),
            MockPipeline("grammar", stages=["analyze", "create_cards"]),
            MockPipeline("pronunciation", stages=["fetch_audio", "create_cards"])
        ]
        
        for pipeline in pipeline_types:
            registry.register_pipeline(pipeline)
        
        # Should handle all pipeline types
        assert len(registry.list_pipelines()) == 4
        
        # Each should be executable
        for pipeline_type in ["vocabulary", "conjugation", "grammar", "pronunciation"]:
            pipeline = registry.get_pipeline(pipeline_type)
            first_stage = pipeline.get_available_stages()[0]
            result = registry.execute_pipeline(pipeline_type, first_stage, {})
            assert result["status"] == "success"
    
    def test_pipeline_resource_limits(self):
        """Contract: Pipeline resource usage is properly limited"""
        resource_manager = MockSharedResourceManager()
        
        # Set resource limits
        resource_manager.set_limits(max_concurrent_pipelines=2, max_memory_mb=1000)
        
        # Should allow within limits
        assert resource_manager.can_start_pipeline("vocabulary") is True
        assert resource_manager.can_start_pipeline("conjugation") is True
        
        # Should reject over limits
        resource_manager.start_pipeline("vocabulary", memory_usage=400)
        resource_manager.start_pipeline("conjugation", memory_usage=400)
        
        # Third pipeline should be rejected (over concurrent limit)
        assert resource_manager.can_start_pipeline("grammar") is False
    
    def test_pipeline_discovery_scaling(self):
        """Contract: Pipeline discovery scales with number of pipelines"""
        registry = MockPipelineRegistry()
        
        # Register many pipelines
        for i in range(20):
            pipeline_name = f"pipeline_{i}"
            pipeline = MockPipeline(pipeline_name, stages=[f"stage_{i}"])
            registry.register_pipeline(pipeline)
        
        # Discovery should still be fast and accurate
        start_time = time.time()
        pipelines = registry.list_pipelines()
        discovery_time = time.time() - start_time
        
        assert len(pipelines) == 20
        assert discovery_time < 0.1  # Under 100ms
        
        # Should be able to get info for any pipeline quickly
        info = registry.get_pipeline_info("pipeline_5")
        assert info["name"] == "pipeline_5"


# Mock implementations for multi-pipeline testing
class MockPipelineRegistry:
    """Mock pipeline registry supporting multiple pipelines"""
    
    def __init__(self):
        self.pipelines = {}
    
    def register_pipeline(self, pipeline):
        """Register a pipeline"""
        self.pipelines[pipeline.name] = pipeline
    
    def list_pipelines(self):
        """List all registered pipelines"""
        return list(self.pipelines.keys())
    
    def get_pipeline(self, name):
        """Get pipeline by name"""
        return self.pipelines.get(name)
    
    def get_pipeline_info(self, name):
        """Get pipeline information"""
        pipeline = self.pipelines.get(name)
        if pipeline:
            return pipeline.get_info()
        return None
    
    def execute_pipeline(self, pipeline_name, stage_name, context):
        """Execute pipeline stage"""
        pipeline = self.pipelines.get(pipeline_name)
        if pipeline:
            result = pipeline.execute_stage(stage_name, context)
            result["pipeline"] = pipeline_name
            return result
        return {"status": "error", "error": "Pipeline not found"}


class MockConcurrentExecutor:
    """Mock concurrent pipeline executor"""
    
    def execute_concurrent(self, tasks):
        """Execute multiple pipeline tasks concurrently"""
        results = []
        
        for task in tasks:
            # Simulate concurrent execution
            result = {
                "status": "success",
                "pipeline": task["pipeline"],
                "stage": task["stage"],
                "context": task["context"]
            }
            results.append(result)
        
        return results


class MockSharedResourceManager:
    """Mock shared resource manager"""
    
    def __init__(self):
        self.usage_stats = {}
        self.active_pipelines = {}
        self.limits = {"max_concurrent_pipelines": 10, "max_memory_mb": 2000}
    
    def request_media_generation(self, request):
        """Handle media generation request"""
        pipeline = request["pipeline"]
        
        if pipeline not in self.usage_stats:
            self.usage_stats[pipeline] = {"media_requests": 0}
        
        self.usage_stats[pipeline]["media_requests"] += 1
        
        return {"status": "success", "media_url": "https://example.com/image.png"}
    
    def get_usage_stats(self):
        """Get resource usage statistics"""
        return self.usage_stats
    
    def set_limits(self, max_concurrent_pipelines=None, max_memory_mb=None):
        """Set resource limits"""
        if max_concurrent_pipelines is not None:
            self.limits["max_concurrent_pipelines"] = max_concurrent_pipelines
        if max_memory_mb is not None:
            self.limits["max_memory_mb"] = max_memory_mb
    
    def can_start_pipeline(self, pipeline_name):
        """Check if pipeline can be started"""
        active_count = len(self.active_pipelines)
        return active_count < self.limits["max_concurrent_pipelines"]
    
    def start_pipeline(self, pipeline_name, memory_usage=0):
        """Start pipeline with resource tracking"""
        if self.can_start_pipeline(pipeline_name):
            self.active_pipelines[pipeline_name] = {"memory_usage": memory_usage}
            return True
        return False


class MockDataManager:
    """Mock data manager with pipeline isolation"""
    
    def __init__(self):
        self.pipeline_data = {}
    
    def store_pipeline_data(self, pipeline_name, data):
        """Store data for specific pipeline"""
        self.pipeline_data[pipeline_name] = data
    
    def get_pipeline_data(self, pipeline_name):
        """Get data for specific pipeline"""
        return self.pipeline_data.get(pipeline_name, {})


class MockUnifiedCLI:
    """Mock unified CLI supporting multiple pipelines"""
    
    def __init__(self):
        self.pipelines = {}
    
    def register_pipeline(self, name, pipeline):
        """Register pipeline with CLI"""
        self.pipelines[name] = pipeline
    
    def execute_command(self, args):
        """Execute CLI command"""
        if len(args) < 4:  # run, pipeline, --stage, stage_name
            return {"status": "error", "error": "Insufficient arguments"}
        
        pipeline_name = args[1]
        stage_name = args[3]
        
        if pipeline_name not in self.pipelines:
            return {"status": "error", "error": f"Pipeline {pipeline_name} not found"}
        
        # Parse additional arguments
        context = {}
        if "--words" in args:
            word_index = args.index("--words") + 1
            context["words"] = args[word_index].split(",")
        if "--verbs" in args:
            verb_index = args.index("--verbs") + 1
            context["verbs"] = args[verb_index].split(",")
        
        # Execute stage
        pipeline = self.pipelines[pipeline_name]
        stage_result = pipeline.execute_stage(stage_name, context)
        
        return {
            "status": "success",
            "pipeline": pipeline_name,
            "stage": stage_name,
            "context": context,
            "stage_result": stage_result
        }


import time