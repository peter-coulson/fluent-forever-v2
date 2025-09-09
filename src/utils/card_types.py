#!/usr/bin/env python3
"""
Card Type Registry System

Provides a modular way to handle different card types (Fluent Forever, Conjugation, etc.)
with their respective templates, data sources, and field structures.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pathlib import Path

from src.utils.logging_config import get_logger

logger = get_logger("utils.card_types")


class CardType(ABC):
    """Abstract base class for card types"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Card type name (e.g., 'Fluent_Forever', 'Conjugation')"""
        pass

    @property
    @abstractmethod
    def note_type(self) -> str:
        """Anki note type name (e.g., 'Fluent Forever', 'Conjugation')"""
        pass

    @property
    @abstractmethod
    def data_file(self) -> str:
        """Data file name (e.g., 'vocabulary.json', 'conjugations.json')"""
        pass

    @abstractmethod
    def load_data(self, project_root: Path) -> dict[str, Any]:
        """Load card data from the data file"""
        pass

    @abstractmethod
    def find_card_by_id(
        self, data: dict[str, Any], card_id: str
    ) -> dict[str, str] | None:
        """Find a card by its ID in the loaded data"""
        pass

    @abstractmethod
    def list_cards(self, data: dict[str, Any]) -> list[dict[str, str]]:
        """List all cards with their basic info"""
        pass

    @abstractmethod
    def build_fields(self, card_data: dict[str, Any]) -> dict[str, str]:
        """Build template fields from card data"""
        pass


class FluentForeverCardType(CardType):
    """Fluent Forever vocabulary cards"""

    @property
    def name(self) -> str:
        return "Fluent_Forever"

    @property
    def note_type(self) -> str:
        return "Fluent Forever"

    @property
    def data_file(self) -> str:
        return "vocabulary.json"

    def load_data(self, project_root: Path) -> dict[str, Any]:
        vocab_path = project_root / self.data_file
        if not vocab_path.exists():
            logger.warning(f"Data file not found: {vocab_path}")
            return {}
        return cast(dict[str, Any], json.loads(vocab_path.read_text(encoding="utf-8")))

    def find_card_by_id(
        self, data: dict[str, Any], card_id: str
    ) -> dict[str, str] | None:
        """Find a vocabulary card by CardID"""
        for _, wdata in data.get("words", {}).items():
            for meaning in wdata.get("meanings", []):
                if str(meaning.get("CardID", "")).strip() == card_id:
                    return cast(dict[str, str], meaning)
        return None

    def list_cards(self, data: dict[str, Any]) -> list[dict[str, str]]:
        """List all vocabulary cards"""
        cards: list[dict[str, str]] = []
        for _, wdata in data.get("words", {}).items():
            for meaning in wdata.get("meanings", []):
                cards.append(
                    {
                        "CardID": meaning.get("CardID", ""),
                        "SpanishWord": meaning.get("SpanishWord", ""),
                        "MeaningID": meaning.get("MeaningID", ""),
                        "MeaningContext": meaning.get("MeaningContext", ""),
                    }
                )
        return cards

    def build_fields(self, card_data: dict[str, Any]) -> dict[str, str]:
        """Build fields for Fluent Forever templates"""
        from .template_render import build_fields_from_meaning

        return build_fields_from_meaning(card_data)


class ConjugationCardType(CardType):
    """Conjugation practice cards"""

    @property
    def name(self) -> str:
        return "Conjugation"

    @property
    def note_type(self) -> str:
        return "Conjugation"

    @property
    def data_file(self) -> str:
        return "conjugations.json"

    def load_data(self, project_root: Path) -> dict[str, Any]:
        """Load conjugation data - placeholder for now"""
        conj_path = project_root / self.data_file
        if not conj_path.exists():
            # Return placeholder data structure for now
            logger.warning(f"Conjugation data file not found: {conj_path}")
            return {
                "conjugations": {
                    "hablar_present_yo": {
                        "CardID": "hablar_present_yo",
                        "Front": "hablo",
                        "Back": "hablar",
                        "Add Reverse": "1",
                        "Sentence": "Yo _____ español todos los días.",
                        "Extra": "Present tense, first person singular",
                        "Picture": "speaking.jpg",
                    }
                }
            }
        return cast(dict[str, Any], json.loads(conj_path.read_text(encoding="utf-8")))

    def find_card_by_id(
        self, data: dict[str, Any], card_id: str
    ) -> dict[str, str] | None:
        """Find a conjugation card by CardID"""
        conjugations = data.get("conjugations", {})
        return cast(dict[str, str] | None, conjugations.get(card_id))

    def list_cards(self, data: dict[str, Any]) -> list[dict[str, str]]:
        """List all conjugation cards"""
        cards: list[dict[str, str]] = []
        for card_id, card_data in data.get("conjugations", {}).items():
            cards.append(
                {
                    "CardID": card_data.get("CardID", card_id),
                    "Front": card_data.get("Front", ""),
                    "Back": card_data.get("Back", ""),
                    "Sentence": card_data.get("Sentence", ""),
                }
            )
        return cards

    def build_fields(self, card_data: dict[str, Any]) -> dict[str, str]:
        """Build fields for Conjugation templates"""
        # For conjugation cards, just convert all values to strings
        fields = {}
        for key, value in card_data.items():
            fields[key] = str(value) if value is not None else ""

        # Handle image paths
        if "Picture" in fields and fields["Picture"]:
            picture = fields["Picture"].strip()
            if (
                picture
                and "/" not in picture
                and not picture.startswith("media/images/")
            ):
                fields["Picture"] = f"media/images/{picture}"

        return fields


class CardTypeRegistry:
    """Registry for managing different card types"""

    def __init__(self) -> None:
        self._card_types: dict[str, CardType] = {}
        self._register_builtin_types()

    def _register_builtin_types(self) -> None:
        """Register built-in card types"""
        self.register(FluentForeverCardType())
        self.register(ConjugationCardType())

    def register(self, card_type: CardType) -> None:
        """Register a new card type"""
        self._card_types[card_type.name] = card_type
        logger.debug(f"Registered card type: {card_type.name}")

    def get(self, name: str) -> CardType | None:
        """Get a card type by name"""
        return self._card_types.get(name)

    def list_types(self) -> list[str]:
        """List all registered card type names"""
        return list(self._card_types.keys())

    def get_default(self) -> CardType:
        """Get the default card type (Fluent Forever)"""
        return self._card_types["Fluent_Forever"]


# Global registry instance
_registry = CardTypeRegistry()


def get_card_type_registry() -> CardTypeRegistry:
    """Get the global card type registry"""
    return _registry
