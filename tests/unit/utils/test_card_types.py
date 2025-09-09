"""Unit tests for card types system."""

import json
from unittest.mock import patch

import pytest
from src.utils.card_types import (
    CardTypeRegistry,
    ConjugationCardType,
    FluentForeverCardType,
    get_card_type_registry,
)


class TestFluentForeverCardType:
    """Test cases for FluentForeverCardType class."""

    def test_card_type_properties(self):
        """Test card type property values."""
        card_type = FluentForeverCardType()

        assert card_type.name == "Fluent_Forever"
        assert card_type.note_type == "Fluent Forever"
        assert card_type.data_file == "vocabulary.json"

    def test_file_missing_handling(self, tmp_path):
        """Test load_data handles non-existent vocabulary.json gracefully."""
        card_type = FluentForeverCardType()

        # Test with non-existent file
        with patch("src.utils.card_types.logger"):
            data = card_type.load_data(tmp_path)

        assert data == {}

    def test_invalid_json_handling(self, tmp_path):
        """Test load_data handles malformed JSON files."""
        card_type = FluentForeverCardType()
        vocab_file = tmp_path / "vocabulary.json"

        # Create malformed JSON
        vocab_file.write_text('{"words": {"test":')

        with pytest.raises(json.JSONDecodeError):
            card_type.load_data(tmp_path)

    def test_valid_file_loading(self, tmp_path):
        """Test load_data with valid vocabulary.json."""
        card_type = FluentForeverCardType()
        vocab_file = tmp_path / "vocabulary.json"

        test_data = {
            "words": {
                "casa": {
                    "meanings": [
                        {
                            "CardID": "casa_001",
                            "SpanishWord": "casa",
                            "MeaningID": "house",
                            "MeaningContext": "building",
                        }
                    ]
                }
            }
        }

        vocab_file.write_text(json.dumps(test_data))
        data = card_type.load_data(tmp_path)

        assert data == test_data

    def test_card_id_matching_existing(self, tmp_path):
        """Test find_card_by_id finds existing cards."""
        card_type = FluentForeverCardType()

        test_data = {
            "words": {
                "casa": {
                    "meanings": [
                        {
                            "CardID": "casa_001",
                            "SpanishWord": "casa",
                            "MeaningID": "house",
                        }
                    ]
                }
            }
        }

        result = card_type.find_card_by_id(test_data, "casa_001")
        assert result is not None
        assert result["SpanishWord"] == "casa"

    def test_card_id_matching_nonexistent(self, tmp_path):
        """Test find_card_by_id returns None for non-existent IDs."""
        card_type = FluentForeverCardType()

        test_data = {
            "words": {
                "casa": {"meanings": [{"CardID": "casa_001", "SpanishWord": "casa"}]}
            }
        }

        result = card_type.find_card_by_id(test_data, "nonexistent")
        assert result is None

    def test_empty_data_structure_handling(self):
        """Test find_card_by_id and list_cards handle empty/missing words key."""
        card_type = FluentForeverCardType()

        # Test with empty dict
        result = card_type.find_card_by_id({}, "any_id")
        assert result is None

        cards = card_type.list_cards({})
        assert cards == []

        # Test with missing words key
        result = card_type.find_card_by_id({"other": "data"}, "any_id")
        assert result is None

    def test_missing_meaning_fields(self):
        """Test handles cards with missing CardID, SpanishWord, etc. fields."""
        card_type = FluentForeverCardType()

        test_data = {
            "words": {
                "casa": {
                    "meanings": [
                        {},  # Empty meaning
                        {"CardID": "partial"},  # Partial meaning
                    ]
                }
            }
        }

        cards = card_type.list_cards(test_data)

        assert len(cards) == 2
        # Should handle missing fields gracefully with empty strings
        assert cards[0]["CardID"] == ""
        assert cards[0]["SpanishWord"] == ""
        assert cards[1]["CardID"] == "partial"
        assert cards[1]["SpanishWord"] == ""


class TestConjugationCardType:
    """Test cases for ConjugationCardType class."""

    def test_card_type_properties(self):
        """Test card type property values."""
        card_type = ConjugationCardType()

        assert card_type.name == "Conjugation"
        assert card_type.note_type == "Conjugation"
        assert card_type.data_file == "conjugations.json"

    def test_file_missing_fallback(self, tmp_path):
        """Test returns placeholder data when conjugations.json doesn't exist."""
        card_type = ConjugationCardType()

        with patch("src.utils.card_types.logger"):
            data = card_type.load_data(tmp_path)

        # Should return placeholder data structure
        assert "conjugations" in data
        assert "hablar_present_yo" in data["conjugations"]
        placeholder_card = data["conjugations"]["hablar_present_yo"]
        assert placeholder_card["CardID"] == "hablar_present_yo"
        assert placeholder_card["Front"] == "hablo"

    def test_valid_file_loading(self, tmp_path):
        """Test loads actual conjugations.json when present."""
        card_type = ConjugationCardType()
        conj_file = tmp_path / "conjugations.json"

        test_data = {
            "conjugations": {
                "test_card": {
                    "CardID": "test_card",
                    "Front": "conjugated",
                    "Back": "infinitive",
                }
            }
        }

        conj_file.write_text(json.dumps(test_data))
        data = card_type.load_data(tmp_path)

        assert data == test_data

    def test_card_retrieval_existing(self):
        """Test find_card_by_id correctly retrieves existing cards."""
        card_type = ConjugationCardType()

        test_data = {
            "conjugations": {
                "test_card": {"CardID": "test_card", "Front": "conjugated"}
            }
        }

        result = card_type.find_card_by_id(test_data, "test_card")
        assert result is not None
        assert result["Front"] == "conjugated"

    def test_card_retrieval_missing(self):
        """Test find_card_by_id handles missing cards."""
        card_type = ConjugationCardType()

        test_data = {"conjugations": {}}

        result = card_type.find_card_by_id(test_data, "nonexistent")
        assert result is None

    def test_empty_conjugations_handling(self):
        """Test list_cards handles empty conjugations dict."""
        card_type = ConjugationCardType()

        test_data = {"conjugations": {}}
        cards = card_type.list_cards(test_data)

        assert cards == []

    def test_missing_card_fields(self):
        """Test handles conjugation cards with missing Front, Back, Sentence fields."""
        card_type = ConjugationCardType()

        test_data = {
            "conjugations": {
                "partial_card": {
                    "CardID": "partial_card"
                    # Missing Front, Back, Sentence
                }
            }
        }

        cards = card_type.list_cards(test_data)

        assert len(cards) == 1
        card = cards[0]
        assert card["CardID"] == "partial_card"
        assert card["Front"] == ""
        assert card["Back"] == ""
        assert card["Sentence"] == ""


class TestCardTypeRegistry:
    """Test cases for CardTypeRegistry class."""

    def test_builtin_registration(self):
        """Test both FluentForeverCardType and ConjugationCardType are registered on init."""
        registry = CardTypeRegistry()

        registered_types = registry.list_types()
        assert "Fluent_Forever" in registered_types
        assert "Conjugation" in registered_types

        # Should be able to retrieve both
        ff_type = registry.get("Fluent_Forever")
        assert isinstance(ff_type, FluentForeverCardType)

        conj_type = registry.get("Conjugation")
        assert isinstance(conj_type, ConjugationCardType)

    def test_custom_registration(self):
        """Test register() adds new card types to registry."""
        registry = CardTypeRegistry()

        # Create mock card type
        class CustomCardType:
            name = "Custom"

        custom_type = CustomCardType()
        registry.register(custom_type)

        assert "Custom" in registry.list_types()
        assert registry.get("Custom") is custom_type

    def test_type_retrieval_existing_and_missing(self):
        """Test get() returns correct card type for existing names, None for missing."""
        registry = CardTypeRegistry()

        # Existing type
        ff_type = registry.get("Fluent_Forever")
        assert isinstance(ff_type, FluentForeverCardType)

        # Missing type
        missing_type = registry.get("NonExistent")
        assert missing_type is None

    def test_type_listing(self):
        """Test list_types() returns all registered card type names."""
        registry = CardTypeRegistry()

        types = registry.list_types()
        assert isinstance(types, list)
        assert len(types) >= 2  # At least the built-in types
        assert "Fluent_Forever" in types
        assert "Conjugation" in types

    def test_default_type(self):
        """Test get_default() returns FluentForeverCardType."""
        registry = CardTypeRegistry()

        default_type = registry.get_default()
        assert isinstance(default_type, FluentForeverCardType)

    def test_name_collision(self):
        """Test behavior when registering card type with existing name."""
        registry = CardTypeRegistry()

        # Create mock card type with same name as built-in
        class NewFluentForeverType:
            name = "Fluent_Forever"

        new_type = NewFluentForeverType()
        registry.register(new_type)

        # Should replace the existing type
        retrieved_type = registry.get("Fluent_Forever")
        assert retrieved_type is new_type
        assert not isinstance(retrieved_type, FluentForeverCardType)


class TestGlobalRegistry:
    """Test cases for global registry functionality."""

    def test_singleton_behavior(self):
        """Test get_card_type_registry() returns same instance across calls."""
        registry1 = get_card_type_registry()
        registry2 = get_card_type_registry()

        assert registry1 is registry2

    def test_initial_state(self):
        """Test registry has built-in types registered on import."""
        registry = get_card_type_registry()

        registered_types = registry.list_types()
        assert "Fluent_Forever" in registered_types
        assert "Conjugation" in registered_types

        # Should be able to get default type
        default_type = registry.get_default()
        assert isinstance(default_type, FluentForeverCardType)
