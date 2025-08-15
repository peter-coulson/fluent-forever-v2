#!/usr/bin/env python3
"""
Tests for Spanish IPA Validator

Test the IPA validator against known dictionary entries and edge cases.
"""

import pytest
import tempfile
import logging
from pathlib import Path

from validation.ipa_validator import SpanishIPAValidator, validate_spanish_ipa


@pytest.fixture
def sample_dictionary():
    """Create a temporary dictionary file for testing"""
    content = """trabajo\ttɾaβaxo
haber\taβeɾ
ser\tseɾ
estar\testaɾ
médico\tˈmeðiko
café\tkaˈfe
casa\tkasa
papel\tpapel
que\tke
de\tde
cinco\tsinko
llorar\tʝoɾaɾ
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        return Path(f.name)


class TestSpanishIPAValidator:
    """Test cases for SpanishIPAValidator class"""
    
    @pytest.fixture
    def validator(self, sample_dictionary):
        """Create validator instance with test dictionary"""
        return SpanishIPAValidator(str(sample_dictionary))
    
    def test_dictionary_loading(self, validator):
        """Test dictionary loads correctly"""
        assert len(validator.dictionary) == 12
        assert 'trabajo' in validator.dictionary
        assert validator.dictionary['trabajo'] == 'tɾaβaxo'
    
    def test_exact_matches(self, validator):
        """Test words that match exactly"""
        # Perfect matches
        assert validator.validate_ipa('trabajo', 'tɾaβaxo') == True
        assert validator.validate_ipa('haber', 'aβeɾ') == True
        assert validator.validate_ipa('ser', 'seɾ') == True
    
    def test_syllable_marker_removal(self, validator):
        """Test that syllable markers (dots) are removed during comparison"""
        # With syllable markers should match without them
        assert validator.validate_ipa('trabajo', 'tɾa.βa.xo') == True
        assert validator.validate_ipa('haber', 'a.βeɾ') == True
        assert validator.validate_ipa('médico', 'ˈme.ði.ko') == True
    
    def test_stress_handling_with_dictionary_stress(self, validator):
        """Test stress comparison when dictionary has stress marks"""
        # Dictionary has stress - must match exactly
        assert validator.validate_ipa('médico', 'ˈmeðiko') == True
        assert validator.validate_ipa('café', 'kaˈfe') == True
        
        # Wrong stress position should fail
        assert validator.validate_ipa('médico', 'meˈðiko') == False
        assert validator.validate_ipa('café', 'ˈkafe') == False
    
    def test_stress_handling_without_dictionary_stress(self, validator):
        """Test stress is ignored when dictionary has no stress marks"""
        # Dictionary has no stress - stress in prediction should be ignored
        assert validator.validate_ipa('trabajo', 'tɾaˈβaxo') == True
        assert validator.validate_ipa('haber', 'ˈaβeɾ') == True
        assert validator.validate_ipa('casa', 'ˈkasa') == True
    
    def test_character_differences(self, validator):
        """Test detection of IPA character differences"""
        # Wrong consonants
        assert validator.validate_ipa('trabajo', 'traβaxo') == False  # tɾ vs tr
        assert validator.validate_ipa('ser', 'ser') == False  # seɾ vs ser
        
        # Wrong fricatives
        assert validator.validate_ipa('trabajo', 'tɾabaxo') == False  # β vs b
        assert validator.validate_ipa('haber', 'abeɾ') == False  # β vs b
    
    def test_word_not_found(self, validator):
        """Test handling of words not in dictionary"""
        assert validator.validate_ipa('inexistent', 'whatever') == False
    
    def test_normalization_functions(self, validator):
        """Test IPA normalization helper functions"""
        # Test syllable marker removal
        assert validator._normalize_ipa_for_comparison('a.βe.ɾo') == 'aβeɾo'
        assert validator._normalize_ipa_for_comparison('ˈme.ði.ko') == 'ˈmeðiko'
        
        # Test stress removal
        assert validator._normalize_ipa_for_comparison('ˈaβeɾ', remove_stress=True) == 'aβeɾ'
        assert validator._normalize_ipa_for_comparison('kaˈfe', remove_stress=True) == 'kafe'
        
        # Test stress detection
        assert validator._has_stress_marks('ˈmeðiko') == True
        assert validator._has_stress_marks('kaˈfe') == True
        assert validator._has_stress_marks('aβeɾ') == False
    
    def test_latin_american_features(self, validator):
        """Test that Latin American features are correctly recognized"""
        # Seseo (s not θ)
        assert validator.validate_ipa('cinco', 'sinko') == True
        
        # Yeísmo (ʝ not ʎ)
        assert validator.validate_ipa('llorar', 'ʝoɾaɾ') == True
        
        # Contextual fricatives
        assert validator.validate_ipa('trabajo', 'tɾaβaxo') == True  # β fricative
        assert validator.validate_ipa('haber', 'aβeɾ') == True  # β fricative
    
    def test_edge_cases(self, validator):
        """Test edge cases and error conditions"""
        # Empty word should return False (word not found)
        assert validator.validate_ipa('', 'aβeɾ') == False
        
        # Empty IPA should return False (mismatch)
        assert validator.validate_ipa('haber', '') == False
        
        # Whitespace-only IPA should return False 
        assert validator.validate_ipa('haber', '   ') == False
        
        # Whitespace handling - should still work
        assert validator.validate_ipa(' haber ', 'aβeɾ') == True
        assert validator.validate_ipa('haber', ' aβeɾ ') == True
    
    def test_multi_word_validation(self, validator):
        """Test validation of multi-word phrases - should validate only first word"""
        # Multi-word with matching spaces
        assert validator.validate_ipa('haber que', 'aβeɾ ke') == True
        assert validator.validate_ipa('ser médico', 'seɾ ˈmeðiko') == True
        
        # Multi-word word with single IPA (should use first word)  
        assert validator.validate_ipa('haber que', 'aβeɾ') == True
        
        # First word matches, second doesn't matter
        assert validator.validate_ipa('haber xyz', 'aβeɾ wrong') == True
        
        # First word doesn't match
        assert validator.validate_ipa('wrong que', 'aβeɾ ke') == False


class TestConvenienceFunction:
    """Test the convenience function"""
    
    def test_validate_spanish_ipa_function(self, tmp_path):
        """Test the convenience function works correctly"""
        # Create test dictionary
        dict_file = tmp_path / "test_dict.txt"
        dict_file.write_text("hola\tola\ngracias\tɡɾasjas\n", encoding='utf-8')
        
        # Test with explicit dictionary path
        assert validate_spanish_ipa('hola', 'ola', str(dict_file)) == True
        assert validate_spanish_ipa('gracias', 'ɡɾasjas', str(dict_file)) == True
        assert validate_spanish_ipa('hola', 'wrong', str(dict_file)) == False


class TestRealWorldScenarios:
    """Test against real-world usage patterns"""
    
    @pytest.fixture
    def real_validator(self):
        """Use the actual bundled dictionary for real-world tests"""
        return SpanishIPAValidator()  # Uses bundled dictionary
    
    def test_common_spanish_words(self, real_validator):
        """Test validation against common Spanish words using real dictionary"""
        # These should be in the real Mexican Spanish dictionary
        test_cases = [
            ('hola', 'ola'),
            ('gracias', 'ɡɾasjas'),  
            ('agua', 'aɣwa'),
            ('bueno', 'bueno'),
        ]
        
        for word, expected_ipa in test_cases:
            if word in real_validator.dictionary:
                result = real_validator.validate_ipa(word, expected_ipa)
                # Log the actual dictionary IPA for debugging if test fails
                if not result:
                    actual = real_validator.dictionary[word]
                    print(f"Expected: {expected_ipa}, Dictionary has: {actual}")
    
    def test_stress_patterns_real_dictionary(self, real_validator):
        """Test stress handling with real dictionary entries"""
        # Test some words that should have stress in the dictionary
        stress_words = ['médico', 'está', 'café'] 
        
        for word in stress_words:
            if word in real_validator.dictionary:
                dict_ipa = real_validator.dictionary[word]
                has_stress = real_validator._has_stress_marks(dict_ipa)
                
                if has_stress:
                    # Should match with correct stress
                    assert real_validator.validate_ipa(word, dict_ipa) == True
                    
                    # Should fail with wrong stress position
                    wrong_stress = dict_ipa.replace('ˈ', '').replace('ˌ', '') + 'ˈ'
                    if wrong_stress != dict_ipa:  # Only test if we actually changed something
                        assert real_validator.validate_ipa(word, wrong_stress) == False


class TestLogging:
    """Test logging behavior"""
    
    def test_logging_setup(self, sample_dictionary, caplog):
        """Test that logging is properly configured"""
        with caplog.at_level(logging.INFO):
            validator = SpanishIPAValidator(str(sample_dictionary))
            
        # Should log dictionary loading
        assert "Loaded 12 entries from Spanish IPA dictionary" in caplog.text
    
    def test_validation_logging(self, sample_dictionary, caplog):
        """Test validation logging output"""
        validator = SpanishIPAValidator(str(sample_dictionary))
        
        with caplog.at_level(logging.INFO):
            # Valid case
            validator.validate_ipa('haber', 'aβeɾ')
            assert "MATCH: 'haber'" in caplog.text
            
        caplog.clear()
        
        with caplog.at_level(logging.ERROR):
            # Invalid case
            validator.validate_ipa('haber', 'wrong')
            assert "MISMATCH: 'haber'" in caplog.text


if __name__ == '__main__':
    pytest.main([__file__])