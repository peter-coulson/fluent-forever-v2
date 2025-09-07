<!-- 
ARCHIVED DOCUMENT
Original: MULTI_CARD_SYSTEM.md
Archived Location: context/archive/legacy/old_MULTI_CARD_SYSTEM.md
Archive Date: 2025-09-06T19:46:52.107983

This document has been archived as part of the documentation reorganization.
For current documentation, see context/README.md
-->

# Multi-Card Type System

A modular extension to the Fluent Forever system that supports multiple card types with local representation, preview, and sync functionality.

## Overview

This system extends the original Fluent Forever implementation to support multiple card types in a modular way:

- **Fluent Forever**: Original vocabulary cards (`vocabulary.json`)
- **Conjugation**: New verb conjugation cards (`conjugations.json`)
- **Future card types**: Easy to add with the registry system

## Key Features

✅ **Local Representation**: Each card type has its own templates and data structure  
✅ **Preview System**: Preview any card type in browser with live reload  
✅ **Sync Functionality**: Sync templates and styling to Anki  
✅ **Modular Design**: Easy to add new card types  
✅ **Backwards Compatible**: Existing Fluent Forever system unchanged  

## Quick Start

```bash
# Test the system
./multi_card_preview.sh test

# List available card types
./multi_card_preview.sh list

# Start preview server
./multi_card_preview.sh start

# Sync all card types to Anki
./multi_card_preview.sh sync

# Sync specific card type
./multi_card_preview.sh sync Conjugation
```

## Directory Structure

```
templates/anki/
├── Fluent_Forever/           # Original system (unchanged)
│   ├── manifest.json
│   ├── styling.css
│   └── templates/
└── Conjugation/              # New conjugation cards
    ├── manifest.json
    ├── styling.css
    └── templates/
        ├── Card1_Front.html
        ├── Card1_Back.html
        ├── Card2_Front.html
        └── Card2_Back.html
```

## Data Files

- `vocabulary.json` - Fluent Forever vocabulary cards (existing)
- `conjugations.json` - Conjugation practice cards (new)

## Conjugation Cards

Based on the Fluent Forever methodology for grammar cards:

### Card 1: Root Form Production
- **Front**: Shows conjugated verb + context sentence
- **Back**: Reveals the infinitive form
- **Purpose**: Connect conjugated forms to root verbs

### Card 2: Root Form Comprehension  
- **Front**: Shows infinitive verb
- **Back**: Shows usage in context with example sentence
- **Purpose**: Understand verb usage patterns

### Example Cards

```json
{
  "CardID": "hablar_present_yo",
  "Front": "hablo",
  "Back": "hablar", 
  "Sentence": "Yo _____ español todos los días.",
  "Extra": "Present tense, first person singular (I speak)",
  "Add Reverse": "1"
}
```

## Preview System

### Multi-Card Preview Server

Start: `./multi_card_preview.sh start [port]`

**URLs:**
- Main page: `http://127.0.0.1:8001/`
- Card types API: `http://127.0.0.1:8001/api/card_types`
- List cards: `http://127.0.0.1:8001/api/cards?card_type=Conjugation`
- Preview card: `http://127.0.0.1:8001/preview?card_id=hablar_present_yo&card_type=Conjugation`

**Parameters:**
- `card_id` - The card ID to preview
- `card_type` - Card type (Fluent_Forever, Conjugation)
- `side` - front or back (default: front)
- `template` - Specific template name (optional)

## Sync System

### Multi-Card Sync

```bash
# Sync all card types
python -m cli.sync_anki_multi

# Sync specific card type
python -m cli.sync_anki_multi --card-type Conjugation

# List available card types
python -m cli.sync_anki_multi --list-types
```

**Features:**
- ✅ Templates sync (HTML + CSS)
- ⚠️ Card data sync (placeholder - not yet implemented)
- ✅ Multiple note types support
- ✅ Backwards compatibility

## Adding New Card Types

1. **Create Template Directory**:
   ```bash
   mkdir -p templates/anki/MyCardType/templates
   ```

2. **Add Manifest**:
   ```json
   {
     "note_type": "My Card Type",
     "templates": [...],
     "fields": [...],
     "css": "styling.css"
   }
   ```

3. **Create Templates**: Add HTML files for front/back

4. **Register Card Type**: Extend `CardType` class in `utils/card_types.py`

5. **Add Data Structure**: Define JSON structure for card data

## Technical Architecture

### Card Type Registry
- `CardType` abstract base class
- Registry pattern for managing card types
- Extensible design for new card types

### Template System  
- Each card type has its own template directory
- Manifest-based template definition
- Shared CSS styling system

### Preview System
- Flask-based preview server
- Real-time template rendering
- Multi-card type support via URL parameters

### Sync System
- AnkiConnect integration
- Per-card-type sync functionality
- Template and styling updates

## API Reference

### Card Type Registry

```python
from utils.card_types import get_card_type_registry

registry = get_card_type_registry()
card_type = registry.get('Conjugation')
data = card_type.load_data(project_root)
cards = card_type.list_cards(data)
```

### Preview Server

```python
# Start multi-card preview server
python -m cli.preview_server_multi --port 8001
```

### Sync System

```python
# Sync specific card type
python -m cli.sync_anki_multi --card-type Conjugation
```

## Integration Notes

- **Backwards Compatible**: Existing Fluent Forever workflows unchanged
- **Template System**: Uses same template loading mechanism
- **Styling**: Shares CSS styling between card types
- **Preview**: Compatible with existing preview infrastructure
- **Sync**: Extends existing sync system architecture

## Future Enhancements

- [ ] Complete card data sync implementation
- [ ] Media sync for conjugation cards
- [ ] CLI tools for managing conjugation data
- [ ] Integration with existing batch processing
- [ ] Additional card types (grammar, pronunciation, etc.)

---

This modular system provides a foundation for expanding beyond vocabulary cards while maintaining the quality and methodology of the Fluent Forever approach.