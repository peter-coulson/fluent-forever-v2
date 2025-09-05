#!/usr/bin/env python3
"""
Session 3 Validation Gate: Stage Chaining System

Tests the contract for chaining multiple stages in sequence.
These tests define how stages should work together in pipelines.

CONTRACT BEING TESTED:
- Stages can be chained in sequence
- Context flows correctly between chained stages
- Stage dependencies are managed
- Error handling in stage chains
- Partial execution recovery
"""

import pytest
from typing import Dict, Any, List
from tests.e2e.conftest import MockStage


class TestStageChaining:
    """Test stage chaining contracts"""
    
    def test_linear_stage_chain(self):
        """Contract: Stages can be executed in linear sequence"""
        stages = [
            MockStage("prepare"),
            MockStage("process"),
            MockStage("finalize")
        ]
        
        context = {"data": {"initial": "value"}}
        results = []
        
        # Execute stages in sequence
        for stage in stages:
            result = stage.execute(context)
            results.append(result)
            
            # Update context with stage result
            context["data"][f"{stage.name}_result"] = result["output"]
        
        # All stages should have executed successfully
        assert len(results) == 3
        assert all(result["status"] == "success" for result in results)
        
        # Context should accumulate results
        assert "prepare_result" in context["data"]
        assert "process_result" in context["data"]
        assert "finalize_result" in context["data"]
    
    def test_conditional_stage_execution(self):
        """Contract: Stages can be conditionally executed based on context"""
        prepare_stage = MockStage("prepare")
        optional_stage = MockStage("optional")
        finalize_stage = MockStage("finalize")
        
        context = {"data": {"skip_optional": True}}
        
        # Execute prepare stage
        result1 = prepare_stage.execute(context)
        assert result1["status"] == "success"
        
        # Skip optional stage based on context
        if not context["data"].get("skip_optional", False):
            optional_stage.execute(context)
        
        # Execute finalize stage
        result3 = finalize_stage.execute(context)
        assert result3["status"] == "success"
        
        # Only prepare and finalize should have executed
        assert prepare_stage.executed
        assert not optional_stage.executed
        assert finalize_stage.executed
    
    def test_error_recovery_in_chain(self):
        """Contract: Stage chains can handle errors and recovery"""
        stages = [
            MockStage("stage1"),
            MockStage("failing_stage", should_fail=True),
            MockStage("recovery_stage"),
            MockStage("final_stage")
        ]
        
        context = {"data": {}, "errors": []}
        
        # Execute stages with error handling
        for i, stage in enumerate(stages):
            try:
                result = stage.execute(context)
                context["data"][f"stage{i+1}_result"] = result
            except RuntimeError as e:
                # Record error and continue with recovery logic
                context["errors"].append(str(e))
                
                # Skip to recovery stage if available
                if stage.name == "failing_stage":
                    continue
        
        # Should have recorded the error
        assert len(context["errors"]) == 1
        assert "failing_stage failed" in context["errors"][0]
        
        # Recovery and final stages should still execute
        assert stages[2].executed  # recovery_stage
        assert stages[3].executed  # final_stage
    
    def test_parallel_stage_branches(self):
        """Contract: Stages can branch and merge in parallel paths"""
        prepare_stage = MockStage("prepare")
        
        # Parallel branches
        branch_a_stage = MockStage("branch_a")
        branch_b_stage = MockStage("branch_b")
        
        merge_stage = MockStage("merge")
        
        context = {"data": {"input": "data"}}
        
        # Prepare stage
        prepare_result = prepare_stage.execute(context)
        context["data"]["prepared"] = prepare_result["output"]
        
        # Execute branches in parallel (simulated)
        branch_results = []
        for branch_stage in [branch_a_stage, branch_b_stage]:
            branch_context = context.copy()  # Separate context for each branch
            branch_result = branch_stage.execute(branch_context)
            branch_results.append(branch_result)
        
        # Merge results
        context["data"]["branch_results"] = branch_results
        merge_result = merge_stage.execute(context)
        
        # All stages should have executed
        assert prepare_stage.executed
        assert branch_a_stage.executed
        assert branch_b_stage.executed
        assert merge_stage.executed
        
        # Merge result should be successful
        assert merge_result["status"] == "success"
    
    def test_stage_dependencies(self):
        """Contract: Stages can declare and validate dependencies"""
        dependency_chain = MockDependentStageChain()
        
        # Stages with dependencies
        stages = [
            MockDependentStage("base", dependencies=[]),
            MockDependentStage("dependent1", dependencies=["base"]),
            MockDependentStage("dependent2", dependencies=["base", "dependent1"])
        ]
        
        context = {"completed_stages": set()}
        
        # Execute stages, checking dependencies
        for stage in stages:
            # Validate dependencies are met
            missing_deps = stage.check_dependencies(context)
            assert len(missing_deps) == 0, f"Missing dependencies: {missing_deps}"
            
            # Execute stage
            result = stage.execute(context)
            assert result["status"] == "success"
            
            # Mark stage as completed
            context["completed_stages"].add(stage.name)
    
    def test_stage_output_transformation(self):
        """Contract: Stages can transform outputs for next stage"""
        transformer_stage = MockTransformerStage("transformer")
        consumer_stage = MockConsumerStage("consumer")
        
        context = {
            "data": {
                "raw_input": ["word1", "word2", "word3"]
            }
        }
        
        # Transform data
        transform_result = transformer_stage.execute(context)
        
        # Pass transformed data to consumer
        context["data"]["transformed"] = transform_result["transformed_data"]
        consumer_result = consumer_stage.execute(context)
        
        assert consumer_result["status"] == "success"
        assert "consumed_count" in consumer_result
        assert consumer_result["consumed_count"] == 3


class TestChainErrorHandling:
    """Test error handling in stage chains"""
    
    def test_chain_interruption_on_error(self):
        """Contract: Stage chains can be interrupted on critical errors"""
        stages = [
            MockStage("stage1"),
            MockStage("critical_stage", should_fail=True),
            MockStage("stage3"),
        ]
        
        context = {"data": {}}
        
        # Execute until error
        for stage in stages:
            try:
                stage.execute(context)
            except RuntimeError:
                # Stop chain on critical error
                break
        
        # Only first stage should have executed successfully
        assert stages[0].executed
        # Second stage should have been attempted (execution flag set) but failed
        assert stages[1].executed  # MockStage sets executed=True even when failing
        assert not stages[2].executed  # Never reached
    
    def test_chain_with_retry_logic(self):
        """Contract: Failed stages can be retried in chains"""
        retryable_stage = MockRetryableStage("retryable", fail_times=2)
        final_stage = MockStage("final")
        
        context = {"data": {}}
        
        # Retry logic for failing stage
        max_retries = 3
        for attempt in range(max_retries):
            try:
                retryable_stage.execute(context)
                break  # Success, exit retry loop
            except RuntimeError:
                if attempt == max_retries - 1:
                    raise  # Final attempt failed
                continue
        
        # Execute final stage
        final_result = final_stage.execute(context)
        
        # Should eventually succeed
        assert retryable_stage.executed
        assert final_result["status"] == "success"
    
    def test_chain_with_rollback(self):
        """Contract: Stage chains can rollback on errors"""
        stages = [
            MockRollbackableStage("stage1"),
            MockRollbackableStage("stage2"),
            MockRollbackableStage("failing_stage", should_fail=True),
        ]
        
        context = {"data": {}, "executed_stages": []}
        
        # Execute stages with rollback capability
        try:
            for stage in stages:
                result = stage.execute(context)
                context["executed_stages"].append(stage.name)
        except RuntimeError:
            # Rollback executed stages in reverse order
            for stage_name in reversed(context["executed_stages"]):
                # Find and rollback stage
                for stage in stages:
                    if stage.name == stage_name:
                        stage.rollback(context)
                        break
        
        # First two stages should have been rolled back
        assert len(context["executed_stages"]) == 2
        for stage in stages[:2]:
            assert stage.rolled_back


# Mock Implementations for Chain Testing
class MockDependentStage(MockStage):
    """Mock stage with dependencies"""
    
    def __init__(self, name: str, dependencies: List[str] = None, should_fail: bool = False):
        super().__init__(name, should_fail)
        self.dependencies = dependencies or []
    
    def check_dependencies(self, context: Dict[str, Any]) -> List[str]:
        """Check if dependencies are satisfied"""
        completed = context.get("completed_stages", set())
        missing = [dep for dep in self.dependencies if dep not in completed]
        return missing


class MockDependentStageChain:
    """Mock stage chain with dependency management"""
    
    def execute_with_dependencies(self, stages: List[MockDependentStage], context: Dict[str, Any]):
        """Execute stages respecting dependencies"""
        remaining = stages.copy()
        completed = set()
        
        while remaining:
            # Find stages with satisfied dependencies
            ready = [s for s in remaining if all(dep in completed for dep in s.dependencies)]
            
            if not ready:
                raise RuntimeError("Circular dependencies detected")
            
            # Execute ready stages
            for stage in ready:
                stage.execute(context)
                completed.add(stage.name)
                remaining.remove(stage)


class MockTransformerStage(MockStage):
    """Mock stage that transforms data"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        super().execute(context)
        
        raw_input = context["data"]["raw_input"]
        transformed = [{"word": item, "processed": True} for item in raw_input]
        
        return {
            "status": "success",
            "stage": self.name,
            "transformed_data": transformed
        }


class MockConsumerStage(MockStage):
    """Mock stage that consumes transformed data"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        super().execute(context)
        
        transformed_data = context["data"]["transformed"]
        consumed_count = len(transformed_data)
        
        return {
            "status": "success",
            "stage": self.name,
            "consumed_count": consumed_count
        }


class MockRetryableStage(MockStage):
    """Mock stage that fails a certain number of times then succeeds"""
    
    def __init__(self, name: str, fail_times: int = 1):
        super().__init__(name, should_fail=True)
        self.fail_times = fail_times
        self.attempt_count = 0
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.attempt_count += 1
        
        if self.attempt_count <= self.fail_times:
            raise RuntimeError(f"Stage {self.name} failed (attempt {self.attempt_count})")
        
        # Success after enough attempts
        self.executed = True
        self.should_fail = False
        return {"status": "success", "stage": self.name, "attempt": self.attempt_count}


class MockRollbackableStage(MockStage):
    """Mock stage that can be rolled back"""
    
    def __init__(self, name: str, should_fail: bool = False):
        super().__init__(name, should_fail)
        self.rolled_back = False
    
    def rollback(self, context: Dict[str, Any]):
        """Rollback this stage's changes"""
        self.rolled_back = True
        # Remove stage result from context if present
        result_key = f"{self.name}_result"
        if result_key in context.get("data", {}):
            del context["data"][result_key]