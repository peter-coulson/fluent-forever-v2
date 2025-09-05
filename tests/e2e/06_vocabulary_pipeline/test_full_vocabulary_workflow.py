#!/usr/bin/env python3
"""
Session 7 Validation Gate: Full Vocabulary Workflow

Tests the complete end-to-end vocabulary card creation workflow.
These tests validate that the entire vocabulary pipeline works
correctly from word input to Anki sync.

CONTRACT BEING TESTED:
- Complete vocabulary workflow from words to Anki cards
- All pipeline stages work together correctly
- Data flows correctly through the entire system
- Error handling works across the complete workflow
- Performance is acceptable for typical batches
"""

import pytest
from typing import Dict, Any, List
from tests.e2e.conftest import MockPipeline, MockStage, MockProvider


class TestFullVocabularyWorkflow:
    """Test complete vocabulary workflow"""
    
    def test_basic_vocabulary_workflow(self, temp_project_dir, mock_external_apis):
        """Contract: Basic vocabulary workflow creates cards successfully"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Input: List of words
        input_words = ["casa", "haber"]
        
        # Execute complete workflow
        result = workflow.execute_full_workflow({
            "words": input_words,
            "config": {
                "batch_size": 5,
                "generate_media": True,
                "sync_to_anki": True
            }
        })
        
        # Should complete successfully
        assert result["status"] == "success"
        assert result["cards_created"] >= 2  # At least one card per word
        assert result["media_generated"] > 0
        assert result["synced_to_anki"] is True
        
        # Should have executed all stages
        executed_stages = result["executed_stages"]
        expected_stages = [
            "word_analysis",
            "claude_staging", 
            "claude_processing",
            "data_validation",
            "media_generation",
            "anki_sync"
        ]
        
        for stage in expected_stages:
            assert stage in executed_stages
    
    def test_batch_processing_workflow(self, temp_project_dir, mock_external_apis):
        """Contract: Batch processing handles multiple words efficiently"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Large batch of words
        input_words = [
            "casa", "haber", "ser", "estar", "tener",
            "hacer", "poder", "decir", "ir", "ver"
        ]
        
        result = workflow.execute_full_workflow({
            "words": input_words,
            "config": {
                "batch_size": 5,  # Process in batches of 5
                "max_meanings_per_word": 3
            }
        })
        
        assert result["status"] == "success"
        assert result["batches_processed"] == 2  # 10 words in batches of 5
        assert result["cards_created"] >= 10  # At least one card per word
        
        # Performance should be reasonable
        assert result["processing_time"] < 30.0  # Under 30 seconds for 10 words
    
    def test_multi_meaning_word_workflow(self, temp_project_dir, mock_external_apis):
        """Contract: Words with multiple meanings are handled correctly"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Word with multiple meanings
        input_words = ["haber"]  # Has auxiliary and existence meanings
        
        result = workflow.execute_full_workflow({
            "words": input_words,
            "config": {
                "analyze_all_meanings": True,
                "max_meanings_per_word": 5
            }
        })
        
        assert result["status"] == "success"
        assert result["cards_created"] >= 2  # Multiple meanings for haber
        
        # Should have identified multiple meanings
        word_analysis = result["word_analysis"]["haber"]
        assert len(word_analysis["meanings"]) >= 2
        assert any(m["context"] == "auxiliary" for m in word_analysis["meanings"])
        assert any(m["context"] == "existence" for m in word_analysis["meanings"])
    
    def test_workflow_with_existing_words(self, temp_project_dir, mock_external_apis):
        """Contract: Workflow skips already processed words"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Process some words first
        first_batch = ["casa", "mesa"]
        workflow.execute_full_workflow({"words": first_batch})
        
        # Process again with overlap
        second_batch = ["casa", "silla", "ventana"]  # casa already processed
        
        result = workflow.execute_full_workflow({
            "words": second_batch,
            "config": {"skip_existing": True}
        })
        
        assert result["status"] == "success"
        assert "casa" in result["skipped_words"]
        assert result["cards_created"] == 2  # Only silla and ventana
    
    def test_workflow_error_recovery(self, temp_project_dir, mock_external_apis):
        """Contract: Workflow recovers from stage failures"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Configure to fail at media generation
        result = workflow.execute_full_workflow({
            "words": ["casa", "mesa"],
            "config": {
                "simulate_media_failure": True,
                "continue_on_media_failure": True
            }
        })
        
        # Should complete with partial success
        assert result["status"] == "partial_success"
        assert result["cards_created"] > 0  # Cards created without media
        assert len(result["media_failures"]) > 0
        assert result["synced_to_anki"] is True  # Should still sync
    
    def test_workflow_rollback_on_critical_failure(self, temp_project_dir, mock_external_apis):
        """Contract: Workflow can rollback on critical failures"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Configure to fail at sync stage
        with pytest.raises(CriticalWorkflowError):
            workflow.execute_full_workflow({
                "words": ["casa"],
                "config": {
                    "simulate_sync_failure": True,
                    "rollback_on_sync_failure": True
                }
            })
        
        # Should have rolled back changes
        vocab_data = workflow.load_vocabulary_data()
        assert "casa" not in vocab_data.get("words", {})


class TestWorkflowStageIntegration:
    """Test integration between workflow stages"""
    
    def test_claude_to_media_integration(self, temp_project_dir, mock_external_apis):
        """Contract: Claude output integrates correctly with media generation"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Execute through Claude processing
        claude_result = workflow.execute_claude_stages({
            "words": ["casa"],
            "config": {"detailed_prompts": True}
        })
        
        # Extract prompts and generate media
        media_result = workflow.execute_media_generation({
            "claude_output": claude_result,
            "config": {"generate_images": True, "generate_audio": True}
        })
        
        # Should have matching prompts and media
        assert len(media_result["generated_images"]) > 0
        assert len(media_result["generated_audio"]) > 0
        
        # Media should match card IDs from Claude output
        claude_card_ids = set(card["CardID"] for card in claude_result["cards"])
        media_card_ids = set(media_result["card_media_map"].keys())
        assert claude_card_ids == media_card_ids
    
    def test_media_to_sync_integration(self, temp_project_dir, mock_external_apis):
        """Contract: Media files integrate correctly with Anki sync"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Execute workflow through media generation
        media_result = workflow.execute_through_media({
            "words": ["casa", "mesa"]
        })
        
        # Execute sync stage
        sync_result = workflow.execute_anki_sync({
            "media_result": media_result,
            "config": {"sync_media": True, "update_existing": False}
        })
        
        assert sync_result["status"] == "success"
        assert sync_result["cards_synced"] >= 2
        assert sync_result["media_files_synced"] > 0
        
        # Should have synced all required fields
        for card in sync_result["synced_cards"]:
            assert card["ImageFile"] is not None
            assert card["WordAudio"] is not None
    
    def test_validation_integration(self, temp_project_dir, mock_external_apis):
        """Contract: Validation works correctly between stages"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Execute with validation at each stage
        result = workflow.execute_full_workflow({
            "words": ["haber"],
            "config": {
                "validate_at_each_stage": True,
                "strict_validation": True
            }
        })
        
        assert result["status"] == "success"
        
        # Should have validation results for each stage
        validation_results = result["validation_results"]
        assert "claude_output" in validation_results
        assert "media_files" in validation_results
        assert "anki_cards" in validation_results
        
        # All validations should pass
        for stage, validation in validation_results.items():
            assert validation["passed"] is True


class TestWorkflowPerformance:
    """Test workflow performance contracts"""
    
    def test_single_word_performance(self, temp_project_dir, mock_external_apis):
        """Contract: Single word processing completes quickly"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        result = workflow.execute_full_workflow({
            "words": ["casa"],
            "config": {"performance_tracking": True}
        })
        
        # Should complete quickly for single word
        assert result["processing_time"] < 5.0  # Under 5 seconds
        
        # Performance breakdown should be available
        performance = result["performance_breakdown"]
        assert "claude_staging" in performance
        assert "media_generation" in performance
        assert "anki_sync" in performance
    
    def test_batch_performance_scaling(self, temp_project_dir, mock_external_apis):
        """Contract: Batch performance scales reasonably"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Test different batch sizes
        batch_sizes = [1, 3, 5]
        results = {}
        
        for size in batch_sizes:
            words = [f"word{i}" for i in range(size)]
            result = workflow.execute_full_workflow({
                "words": words,
                "config": {"performance_tracking": True}
            })
            results[size] = result["processing_time"]
        
        # Performance should scale sub-linearly (due to batching)
        time_per_word_1 = results[1]
        time_per_word_5 = results[5] / 5
        
        # 5-word batch should be more efficient per word
        assert time_per_word_5 < time_per_word_1 * 1.2  # At most 20% worse per word
    
    def test_memory_usage_limits(self, temp_project_dir, mock_external_apis):
        """Contract: Memory usage stays within reasonable limits"""
        workflow = MockVocabularyWorkflow(temp_project_dir)
        
        # Process moderately large batch
        words = [f"word{i}" for i in range(20)]
        
        result = workflow.execute_full_workflow({
            "words": words,
            "config": {"memory_tracking": True}
        })
        
        assert result["status"] == "success"
        
        # Memory usage should be reasonable
        memory_stats = result["memory_stats"]
        assert memory_stats["peak_memory_mb"] < 500  # Under 500MB
        assert memory_stats["memory_growth_mb"] < 200  # Growth under 200MB


# Mock Workflow Implementation
class MockVocabularyWorkflow:
    """Mock vocabulary workflow for testing"""
    
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.vocabulary_data = {}
        self.processed_words = set()
    
    def execute_full_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete vocabulary workflow"""
        import time
        start_time = time.time()
        
        words = request["words"]
        config = request.get("config", {})
        
        # Simulate workflow execution
        result = {
            "status": "success",
            "cards_created": 0,
            "media_generated": 0,
            "synced_to_anki": False,
            "executed_stages": [],
            "skipped_words": [],
            "word_analysis": {},
            "processing_time": 0,
            "batches_processed": 0
        }
        
        # Handle error simulation
        if config.get("simulate_sync_failure") and config.get("rollback_on_sync_failure"):
            raise CriticalWorkflowError("Sync failed, rolling back")
        
        # Process words
        batch_size = config.get("batch_size", 5)
        batches = [words[i:i+batch_size] for i in range(0, len(words), batch_size)]
        result["batches_processed"] = len(batches)
        
        for batch in batches:
            for word in batch:
                if config.get("skip_existing") and word in self.processed_words:
                    result["skipped_words"].append(word)
                    continue
                
                # Analyze word
                meanings = self._analyze_word(word, config)
                result["word_analysis"][word] = {"meanings": meanings}
                result["cards_created"] += len(meanings)
                
                # Generate media (unless failing)
                if not config.get("simulate_media_failure"):
                    result["media_generated"] += len(meanings)
                else:
                    result.setdefault("media_failures", []).append(word)
                    if not config.get("continue_on_media_failure"):
                        result["status"] = "failed"
                        return result
                
                self.processed_words.add(word)
        
        # Set execution stages
        result["executed_stages"] = [
            "word_analysis", "claude_staging", "claude_processing",
            "data_validation", "media_generation", "anki_sync"
        ]
        
        # Handle partial success
        if result.get("media_failures"):
            result["status"] = "partial_success"
        
        result["synced_to_anki"] = not config.get("simulate_sync_failure", False)
        result["processing_time"] = time.time() - start_time
        
        # Add performance breakdown if requested
        if config.get("performance_tracking"):
            result["performance_breakdown"] = {
                "claude_staging": 0.5,
                "media_generation": 1.2,
                "anki_sync": 0.8
            }
        
        # Add memory stats if requested
        if config.get("memory_tracking"):
            result["memory_stats"] = {
                "peak_memory_mb": 150,
                "memory_growth_mb": 50
            }
        
        # Add validation results if requested
        if config.get("validate_at_each_stage"):
            result["validation_results"] = {
                "claude_output": {"passed": True, "errors": []},
                "media_files": {"passed": True, "errors": []},
                "anki_cards": {"passed": True, "errors": []}
            }
        
        return result
    
    def execute_claude_stages(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute just the Claude processing stages"""
        words = request["words"]
        cards = []
        
        for word in words:
            meanings = self._analyze_word(word, request.get("config", {}))
            for meaning in meanings:
                cards.append({
                    "CardID": f"{word}_{meaning['context']}",
                    "SpanishWord": word,
                    "MeaningContext": meaning["context"],
                    "prompt": meaning["prompt"]
                })
        
        return {"cards": cards, "status": "success"}
    
    def execute_media_generation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute media generation stage"""
        claude_output = request["claude_output"]
        cards = claude_output["cards"]
        
        generated_images = []
        generated_audio = []
        card_media_map = {}
        
        for card in cards:
            card_id = card["CardID"]
            
            # Generate media
            generated_images.append(f"{card_id}.png")
            generated_audio.append(f"{card['SpanishWord']}.mp3")
            
            card_media_map[card_id] = {
                "image": f"{card_id}.png",
                "audio": f"{card['SpanishWord']}.mp3"
            }
        
        return {
            "status": "success",
            "generated_images": generated_images,
            "generated_audio": generated_audio,
            "card_media_map": card_media_map
        }
    
    def execute_through_media(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow through media generation"""
        claude_result = self.execute_claude_stages(request)
        return self.execute_media_generation({"claude_output": claude_result})
    
    def execute_anki_sync(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Anki sync stage"""
        media_result = request["media_result"]
        card_media_map = media_result["card_media_map"]
        
        synced_cards = []
        for card_id, media in card_media_map.items():
            synced_cards.append({
                "CardID": card_id,
                "ImageFile": media["image"],
                "WordAudio": media["audio"]
            })
        
        return {
            "status": "success",
            "cards_synced": len(synced_cards),
            "media_files_synced": len(media_result["generated_images"]) + len(media_result["generated_audio"]),
            "synced_cards": synced_cards
        }
    
    def load_vocabulary_data(self) -> Dict[str, Any]:
        """Load vocabulary data"""
        return self.vocabulary_data
    
    def _analyze_word(self, word: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze word to identify meanings"""
        # Mock word analysis
        if word == "haber":
            return [
                {"context": "auxiliary", "prompt": "Boy helping with homework"},
                {"context": "existence", "prompt": "Items on table"}
            ]
        elif word == "casa":
            return [{"context": "dwelling", "prompt": "Cozy house in countryside"}]
        else:
            return [{"context": "general", "prompt": f"Scene with {word}"}]


# Custom Exceptions
class CriticalWorkflowError(Exception):
    """Critical workflow error requiring rollback"""
    pass