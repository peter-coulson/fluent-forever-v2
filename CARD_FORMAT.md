# Anki Card Format Specification

## Core Principle: One Card Per Meaning
Each distinct meaning or usage gets its own card with unique image but shared audio.

## Anki Note Type: "Fluent Forever"

### Fields Structure
```
1. SpanishWord       - The base word (e.g., "que")
2. IPA              - Phonetic transcription [ke]
3. MeaningContext   - Specific usage (e.g., "pronombre relativo")
4. MonolingualDef   - Spanish definition for THIS meaning only
5. ExampleSentence  - ONE example showing this specific usage
6. GappedSentence   - Same sentence with word blanked out
7. ImageFile        - Single image for this meaning
8. WordAudio        - Primary pronunciation [sound:que_audio.mp3]
9. WordAudioAlt     - Alternative pronunciation for gendered words [sound:que_audio_fem.mp3]
10. UsageNote       - Brief grammatical/usage note
11. PersonalMnemonic - Optional memory aid
12. MeaningID       - Semantic identifier (e.g., "relative_pronoun")
```

## Card Templates

### Front Template (What User Sees First)
```html
<div class="card-front">
  {{WordAudio}}
  {{#WordAudioAlt}}{{WordAudioAlt}}{{/WordAudioAlt}}
  <div class="image-container">
    {{ImageFile}}
  </div>
  <div class="definition">
    {{MonolingualDef}}
  </div>
</div>
```

### Back Template (Answer Side)
```html
<div class="card-back">
  <div class="word-main">
    <span class="spanish">{{SpanishWord}}</span>
    <span class="ipa">{{IPA}}</span>
  </div>
  
  <div class="audio-back">
    {{WordAudio}}
    {{#WordAudioAlt}}{{WordAudioAlt}}{{/WordAudioAlt}}
  </div>
  
  <div class="meaning-context">
    {{MeaningContext}}
  </div>
  
  <div class="example">
    <div class="full-sentence">{{ExampleSentence}}</div>
    <div class="gapped">{{GappedSentence}}</div>
  </div>
  
  {{#UsageNote}}
  <div class="usage-note">
    📝 {{UsageNote}}
  </div>
  {{/UsageNote}}
  
  {{#PersonalMnemonic}}
  <div class="mnemonic">
    💭 {{PersonalMnemonic}}
  </div>
  {{/PersonalMnemonic}}
</div>
```

### CSS Styling
```css
.card {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #333;
  background: #fafafa;
}

.image-container img {
  max-width: 400px;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.definition {
  margin-top: 20px;
  font-size: 18px;
  color: #666;
  font-style: italic;
}

.word-main {
  margin-bottom: 15px;
}

.audio-back {
  margin-bottom: 15px;
}

.spanish {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
}

.ipa {
  font-size: 18px;
  color: #7f8c8d;
  margin-left: 10px;
}

.meaning-context {
  background: #ecf0f1;
  padding: 8px 15px;
  border-radius: 5px;
  display: inline-block;
  margin-bottom: 15px;
  font-size: 16px;
  color: #34495e;
}

.example {
  margin: 20px 0;
}

.full-sentence {
  font-size: 22px;
  margin-bottom: 10px;
}

.gapped {
  font-size: 18px;
  color: #7f8c8d;
  font-style: italic;
}

.usage-note, .mnemonic {
  margin-top: 15px;
  padding: 10px;
  background: #fff;
  border-left: 3px solid #3498db;
  text-align: left;
  font-size: 16px;
}
```

## Media Handling

### Audio Files
- **Primary**: `[word]_audio.mp3` - standard pronunciation
- **Alternative**: `[word]_audio_fem.mp3` - feminine form (if applicable)
- **Format**: MP3, under 100KB per file
- **Sources**: Forvo (preferred) or TTS fallback

### Image Files  
- **Format**: PNG or JPEG, 512x512px
- **Naming**: `[word]_[meaning_id].png`
- **Style**: Studio Ghibli animation style for consistent visual learning
- **One per meaning**: Never share images between meanings

## Gendered Words Special Handling

For words with masculine/feminine forms:
```json
{
  "base_word": "un",
  "forms": {
    "masculine": "un",
    "feminine": "una"
  },
  "audio_files": {
    "primary": "un_audio.mp3",
    "alternative": "una_audio.mp3"
  },
  "display": "un/una"
}
```

## Bulletproof Anki Integration

### Pre-Creation Checks
1. Verify all media files exist locally
2. Upload media to Anki before card creation
3. Validate field content (no null values)
4. Escape HTML in user content

### Field Validation Rules
```python
def validate_card_fields(fields):
    """Ensure all fields are properly formatted"""
    required = ['SpanishWord', 'IPA', 'MonolingualDef', 'ExampleSentence']
    
    for field in required:
        if not fields.get(field) or fields[field].strip() == '':
            raise ValueError(f"Required field {field} is empty")
    
    # Ensure audio format
    if fields.get('WordAudio') and not fields['WordAudio'].startswith('[sound:'):
        fields['WordAudio'] = f"[sound:{fields['WordAudio']}]"
    
    # Ensure image format
    if fields.get('ImageFile') and not fields['ImageFile'].startswith('<img'):
        fields['ImageFile'] = f"<img src='{fields['ImageFile']}'>"
    
    return fields
```

### Error Recovery
- Log all Anki API responses
- Retry failed uploads with exponential backoff
- Store failed cards for manual recovery
- Never lose user work

## Batch Processing Workflow

### 5-Word Batch Structure
```json
{
  "batch_id": "2025-08-10-001",
  "words": [
    {
      "base_word": "que",
      "meanings": [
        {"id": "relative", "prompt": "Zach pointing at book"},
        {"id": "conjunction", "prompt": "Maria connecting thoughts"}
      ]
    },
    // ... 4 more words
  ],
  "status": "pending_prompts"
}
```

### Batch States
1. **analyzing** - Claude processing meanings
2. **pending_prompts** - Awaiting user prompts
3. **pending_audio_approval** - User reviewing audio options
4. **generating_media** - Creating images/downloading audio
5. **creating_cards** - Adding to Anki
6. **completed** - Batch fully processed

## Quality Assurance

### Card Creation Checklist
- [ ] All required fields populated
- [ ] Image displays correctly (512x512)
- [ ] Audio plays properly
- [ ] No formatting errors in HTML
- [ ] Meaning-specific content verified
- [ ] No cross-contamination between meanings

### Testing Protocol
```python
def test_card_creation(card_data):
    """Verify card will display correctly in Anki"""
    # Test media files exist
    assert os.path.exists(card_data['image_path'])
    assert os.path.exists(card_data['audio_path'])
    
    # Test field content
    assert len(card_data['monolingual_def']) > 0
    assert len(card_data['example_sentence']) > 0
    
    # Test Anki formatting
    assert '[sound:' in card_data['audio_field']
    assert '<img' in card_data['image_field']
    
    return True
```

## Common Issues Prevention

### From V1 System
- **Missing lines**: Always validate gapped sentences
- **Audio not playing**: Ensure [sound:] wrapper format
- **Images not showing**: Verify <img> tag and file upload
- **Encoding issues**: UTF-8 everywhere, escape HTML

### Solutions Implemented
- Pre-upload media validation
- Field content verification
- Atomic card creation (all or nothing)
- Comprehensive error logging

---

*Card format designed for maximum retention through focused, meaning-specific practice*
