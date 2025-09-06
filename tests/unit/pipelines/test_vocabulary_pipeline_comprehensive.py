"""Comprehensive unit tests for the vocabulary pipeline."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from pipelines.vocabulary.pipeline import VocabularyPipeline
from pipelines.vocabulary.stages.word_analysis import WordAnalysisStage
from pipelines.vocabulary.stages.batch_preparation import BatchPreparationStage
from core.context import PipelineContext
from core.stages import StageStatus


class TestVocabularyPipeline:
    """Test the main VocabularyPipeline class."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly."""
        pipeline = VocabularyPipeline()
        
        assert pipeline.name == "vocabulary"
        assert pipeline.display_name == "Fluent Forever Vocabulary"
        assert pipeline.data_file == "vocabulary.json"
        assert pipeline.anki_note_type == "Fluent Forever"
    
    def test_pipeline_stages(self):
        """Test pipeline has expected stages."""
        pipeline = VocabularyPipeline()
        stages = pipeline.stages
        
        # Should have both new comprehensive stages and backward compatibility stages
        expected_stages = {
            "analyze_words", "prepare_batch", "ingest_batch", "validate_data", "sync_cards",
            "prepare", "claude_batch", "validate", "generate_media", "sync"
        }
        
        assert set(stages) == expected_stages
    
    def test_get_stages_compatibility(self):
        """Test get_stages method for backward compatibility."""
        pipeline = VocabularyPipeline()
        stages = pipeline.get_stages()
        
        assert isinstance(stages, list)
        assert len(stages) > 0
        assert "prepare" in stages
        assert "sync" in stages
    
    def test_get_info(self):
        """Test get_info returns correct pipeline information."""
        pipeline = VocabularyPipeline()
        info = pipeline.get_info()
        
        assert info["name"] == "vocabulary"
        assert info["display_name"] == "Fluent Forever Vocabulary" 
        assert "stages" in info
        assert "description" in info
    
    def test_get_stage(self):
        """Test get_stage returns correct stage instances."""
        pipeline = VocabularyPipeline()
        
        # Test new comprehensive stages
        analyze_stage = pipeline.get_stage("analyze_words")
        assert isinstance(analyze_stage, WordAnalysisStage)
        
        prepare_batch_stage = pipeline.get_stage("prepare_batch")  
        assert isinstance(prepare_batch_stage, BatchPreparationStage)
        
        # Test backward compatibility stages
        prepare_stage = pipeline.get_stage("prepare")
        assert prepare_stage is not None
        
        sync_stage = pipeline.get_stage("sync")
        assert sync_stage is not None
    
    def test_stage_not_found(self):
        """Test error handling for unknown stages."""
        pipeline = VocabularyPipeline()
        
        with pytest.raises(Exception):  # Should raise StageNotFoundError
            pipeline.get_stage("nonexistent_stage")


class TestWordAnalysisStage:
    """Test the WordAnalysisStage implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.stage = WordAnalysisStage()
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
    
    def test_stage_properties(self):
        """Test stage has correct properties."""
        assert self.stage.name == "analyze_words"
        assert self.stage.display_name == "Analyze Word Meanings"
    
    def test_validate_context_success(self):
        """Test context validation with valid data."""
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        context.set('words', ['casa', 'por'])
        
        errors = self.stage.validate_context(context)
        assert len(errors) == 0
    
    def test_validate_context_missing_words(self):
        """Test context validation with missing words."""
        context = PipelineContext(
            pipeline_name="vocabulary", 
            project_root=self.project_root
        )
        
        errors = self.stage.validate_context(context)
        assert len(errors) > 0
        assert "No words provided" in errors[0]
    
    def test_validate_context_invalid_words(self):
        """Test context validation with invalid words format."""
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        context.set('words', "not_a_list")
        
        errors = self.stage.validate_context(context)
        assert len(errors) > 0
        assert "must be provided as a list" in errors[0]
    
    def test_execute_success(self):
        """Test successful word analysis execution."""
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        context.set('words', ['testword'])
        
        result = self.stage.execute(context)
        
        assert result.status == StageStatus.SUCCESS
        assert "Analyzed 1 words" in result.message
        assert result.data['meanings_count'] == 1
        assert len(result.data['meanings']) == 1
    
    def test_execute_with_existing_words(self):
        """Test analysis skips words that already exist in vocabulary."""
        # Create a vocabulary.json with existing words
        vocab_data = {
            "words": {
                "casa": {
                    "meanings": [{"SpanishWord": "casa", "MeaningID": "casa_1"}]
                }
            }
        }
        vocab_file = self.project_root / "vocabulary.json"
        vocab_file.write_text(json.dumps(vocab_data))
        
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        context.set('words', ['casa'])  # Word already exists
        
        result = self.stage.execute(context)
        
        assert result.status == StageStatus.SUCCESS
        assert result.data['meanings_count'] == 0
        assert result.data['skipped_count'] == 1
    
    def test_grammatical_category_identification(self):
        """Test grammatical category identification."""
        stage = WordAnalysisStage()
        
        # Test prepositions
        assert stage._identify_grammatical_category('por') == 'preposition'
        assert stage._identify_grammatical_category('para') == 'preposition'
        assert stage._identify_grammatical_category('de') == 'preposition'
        
        # Test verbs
        assert stage._identify_grammatical_category('hablar') == 'verb'
        assert stage._identify_grammatical_category('comer') == 'verb'
        assert stage._identify_grammatical_category('vivir') == 'verb'
        
        # Test articles/pronouns
        assert stage._identify_grammatical_category('el') == 'article_pronoun'
        assert stage._identify_grammatical_category('la') == 'article_pronoun'
        
        # Test default (noun)
        assert stage._identify_grammatical_category('mesa') == 'noun'
    
    def test_context_analysis(self):
        """Test context analysis for different grammatical categories."""
        stage = WordAnalysisStage()
        
        # Test preposition analysis (should have multiple contexts)
        contexts = stage._analyze_contexts('por', 'preposition')
        assert len(contexts) == 4  # por should have 4 meanings
        assert any('through' in ctx['context'] for ctx in contexts)
        
        # Test verb analysis 
        contexts = stage._analyze_contexts('hablar', 'verb')
        assert len(contexts) == 1  # Regular verbs have one meaning
        
        # Test noun analysis
        contexts = stage._analyze_contexts('mesa', 'noun')
        assert len(contexts) == 1  # Nouns typically have one meaning


class TestBatchPreparationStage:
    """Test the BatchPreparationStage implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.stage = BatchPreparationStage()
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create staging directory
        (self.project_root / "staging").mkdir()
    
    def test_stage_properties(self):
        """Test stage has correct properties."""
        assert self.stage.name == "prepare_batch"
        assert self.stage.display_name == "Prepare Claude Batch"
        assert "analyze_words" in self.stage.dependencies
    
    def test_validate_context_success(self):
        """Test context validation with valid data."""
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        context.set('analyzed_meanings', [
            {'SpanishWord': 'test', 'MeaningID': 'test_1', 'MeaningContext': 'test context', 'CardID': 'test_test_1'}
        ])
        
        errors = self.stage.validate_context(context)
        assert len(errors) == 0
    
    def test_validate_context_missing_meanings(self):
        """Test context validation with missing analyzed meanings."""
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        
        errors = self.stage.validate_context(context)
        assert len(errors) > 0
        assert "No analyzed meanings" in errors[0]
    
    def test_execute_success(self):
        """Test successful batch preparation."""
        analyzed_meanings = [
            {
                'SpanishWord': 'testword',
                'MeaningID': 'testword_meaning_1', 
                'MeaningContext': 'primary meaning',
                'CardID': 'testword_testword_meaning_1',
                'GrammaticalCategory': 'noun',
                'EstimatedDifficulty': 'basic',
                'RequiresPrompt': True
            }
        ]
        
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        context.set('analyzed_meanings', analyzed_meanings)
        
        result = self.stage.execute(context)
        
        assert result.status == StageStatus.SUCCESS
        assert "Created Claude batch with 1 meanings" in result.message
        assert result.data['meaning_count'] == 1
        assert 'batch_file' in result.data
        
        # Check batch file was created
        batch_file_path = Path(result.data['batch_file'])
        assert batch_file_path.exists()
        
        # Check batch file content
        batch_data = json.loads(batch_file_path.read_text())
        assert batch_data['words'] == ['testword']
        assert len(batch_data['meanings']) == 1
        assert batch_data['meanings'][0]['SpanishWord'] == 'testword'
        assert batch_data['meanings'][0]['MonolingualDef'] == ''  # Empty for Claude to fill
        assert batch_data['meanings'][0]['GrammaticalCategory'] == 'noun'
    
    def test_batch_size_limiting(self):
        """Test batch size is limited correctly."""
        # Create more meanings than batch size
        analyzed_meanings = []
        for i in range(10):
            analyzed_meanings.append({
                'SpanishWord': f'word{i}',
                'MeaningID': f'word{i}_meaning_1',
                'MeaningContext': f'meaning {i}',
                'CardID': f'word{i}_word{i}_meaning_1'
            })
        
        # Set batch size to 3
        stage = BatchPreparationStage({'batch_settings': {'cards_per_batch': 3}})
        
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        context.set('analyzed_meanings', analyzed_meanings)
        
        result = stage.execute(context)
        
        assert result.status == StageStatus.SUCCESS
        assert result.data['meaning_count'] == 3  # Limited to batch size
    
    def test_batch_structure_compatibility(self):
        """Test batch structure is compatible with existing ingest system."""
        analyzed_meanings = [
            {
                'SpanishWord': 'por',
                'MeaningID': 'por_meaning_1',
                'MeaningContext': 'through/via',
                'CardID': 'por_por_meaning_1',
                'GrammaticalCategory': 'preposition'
            }
        ]
        
        context = PipelineContext(
            pipeline_name="vocabulary",
            project_root=self.project_root
        )
        context.set('analyzed_meanings', analyzed_meanings)
        
        result = self.stage.execute(context)
        batch_file_path = Path(result.data['batch_file'])
        batch_data = json.loads(batch_file_path.read_text())
        
        # Check required top-level fields
        assert 'metadata' in batch_data
        assert 'words' in batch_data
        assert 'meanings' in batch_data
        assert 'skipped_words' in batch_data
        
        # Check metadata fields
        metadata = batch_data['metadata']
        assert 'created' in metadata
        assert 'source' in metadata
        assert 'pipeline' in metadata
        assert metadata['pipeline'] == 'vocabulary'
        
        # Check meaning template structure
        meaning = batch_data['meanings'][0]
        required_fields = [
            'SpanishWord', 'MeaningID', 'MeaningContext', 'CardID',
            'MonolingualDef', 'ExampleSentence', 'GappedSentence', 'IPA', 'prompt'
        ]
        for field in required_fields:
            assert field in meaning


if __name__ == "__main__":
    pytest.main([__file__])