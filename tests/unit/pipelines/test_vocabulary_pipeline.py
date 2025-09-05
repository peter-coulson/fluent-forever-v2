"""Unit tests for vocabulary pipeline."""

import pytest
from pathlib import Path
from pipelines.vocabulary import VocabularyPipeline
from pipelines.vocabulary.stages import PrepareStage, MediaGenerationStage, SyncStage
from core.context import PipelineContext
from core.stages import StageStatus
from core.exceptions import StageNotFoundError


class TestVocabularyPipeline:
    """Test cases for VocabularyPipeline class."""
    
    def test_pipeline_properties(self):
        """Test pipeline property access."""
        pipeline = VocabularyPipeline()
        
        assert pipeline.name == "vocabulary"
        assert pipeline.display_name == "Fluent Forever Vocabulary"
        assert pipeline.data_file == "vocabulary.json"
        assert pipeline.anki_note_type == "Fluent Forever"
        assert set(pipeline.stages) == {"prepare", "media", "sync"}
    
    def test_get_stage(self):
        """Test getting stages by name."""
        pipeline = VocabularyPipeline()
        
        prepare_stage = pipeline.get_stage("prepare")
        assert isinstance(prepare_stage, PrepareStage)
        assert prepare_stage.name == "prepare"
        
        media_stage = pipeline.get_stage("media")
        assert isinstance(media_stage, MediaGenerationStage)
        assert media_stage.name == "media"
        
        sync_stage = pipeline.get_stage("sync")
        assert isinstance(sync_stage, SyncStage)
        assert sync_stage.name == "sync"
    
    def test_get_nonexistent_stage(self):
        """Test getting non-existent stage raises error."""
        pipeline = VocabularyPipeline()
        
        with pytest.raises(StageNotFoundError) as exc_info:
            pipeline.get_stage("nonexistent")
        
        assert "not found in vocabulary pipeline" in str(exc_info.value)
    
    def test_stage_execution(self):
        """Test executing stages through pipeline."""
        pipeline = VocabularyPipeline()
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=Path("/test")
        )
        context.set("words", ["test", "word"])
        
        # Execute prepare stage
        result = pipeline.execute_stage("prepare", context)
        assert result.status == StageStatus.SUCCESS
        assert "prepare" in context.completed_stages
        
        # Execute media stage (depends on prepare)
        result = pipeline.execute_stage("media", context)
        assert result.status == StageStatus.SUCCESS
        assert "media" in context.completed_stages
        
        # Execute sync stage (depends on prepare and media)
        result = pipeline.execute_stage("sync", context)
        assert result.status == StageStatus.SUCCESS
        assert "sync" in context.completed_stages
    
    def test_description_and_info(self):
        """Test pipeline description and stage info."""
        pipeline = VocabularyPipeline()
        
        description = pipeline.get_description()
        assert "Fluent Forever Vocabulary" in description
        assert "vocabulary.json" in description
        
        # Test stage info
        prepare_info = pipeline.get_stage_info("prepare")
        assert prepare_info["name"] == "prepare"
        assert prepare_info["display_name"] == "Prepare Vocabulary Data"
        assert prepare_info["dependencies"] == []
        
        media_info = pipeline.get_stage_info("media")
        assert media_info["name"] == "media"
        assert media_info["dependencies"] == ["prepare"]


class TestPrepareStage:
    """Test cases for PrepareStage."""
    
    def test_stage_properties(self):
        """Test stage property access."""
        stage = PrepareStage()
        
        assert stage.name == "prepare"
        assert stage.display_name == "Prepare Vocabulary Data"
        assert stage.dependencies == []
    
    def test_successful_execution(self):
        """Test successful stage execution."""
        stage = PrepareStage()
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=Path("/test")
        )
        context.set("words", ["test", "word"])
        
        result = stage.execute(context)
        
        assert result.status == StageStatus.SUCCESS
        assert "Prepared 2 words" in result.message
        assert context.get("prepared_data") is not None
        assert context.get("prepared_data")["prepared_words"] == ["test", "word"]
    
    def test_execution_without_words(self):
        """Test execution without words."""
        stage = PrepareStage()
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=Path("/test")
        )
        
        result = stage.execute(context)
        
        assert result.status == StageStatus.FAILURE
        assert "No words provided" in result.message
    
    def test_context_validation(self):
        """Test context validation."""
        stage = PrepareStage()
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=Path("/test")
        )
        
        # Without words
        errors = stage.validate_context(context)
        assert "Context must contain 'words' list" in errors
        
        # With words
        context.set("words", ["test"])
        errors = stage.validate_context(context)
        assert errors == []


class TestMediaGenerationStage:
    """Test cases for MediaGenerationStage."""
    
    def test_stage_properties(self):
        """Test stage property access."""
        stage = MediaGenerationStage()
        
        assert stage.name == "media"
        assert stage.display_name == "Generate Media"
        assert stage.dependencies == ["prepare"]
    
    def test_successful_execution(self):
        """Test successful execution with prepared data."""
        stage = MediaGenerationStage()
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=Path("/test")
        )
        context.set("prepared_data", {"prepared_words": ["test"]})
        
        result = stage.execute(context)
        
        assert result.status == StageStatus.SUCCESS
        assert "Media generation completed" in result.message
        assert context.get("media_data") is not None
    
    def test_execution_without_prepared_data(self):
        """Test execution without prepared data."""
        stage = MediaGenerationStage()
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=Path("/test")
        )
        
        result = stage.execute(context)
        
        assert result.status == StageStatus.FAILURE
        assert "No prepared data found" in result.message


class TestSyncStage:
    """Test cases for SyncStage."""
    
    def test_stage_properties(self):
        """Test stage property access."""
        stage = SyncStage()
        
        assert stage.name == "sync"
        assert stage.display_name == "Sync to Anki"
        assert stage.dependencies == ["prepare", "media"]
    
    def test_successful_execution(self):
        """Test successful execution with media data."""
        stage = SyncStage()
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=Path("/test")
        )
        context.set("media_data", {"generated_media": True})
        
        result = stage.execute(context)
        
        assert result.status == StageStatus.SUCCESS
        assert "Sync to Anki completed" in result.message
        assert context.get("sync_data") is not None
    
    def test_execution_without_media_data(self):
        """Test execution without media data."""
        stage = SyncStage()
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=Path("/test")
        )
        
        result = stage.execute(context)
        
        assert result.status == StageStatus.FAILURE
        assert "No media data found" in result.message