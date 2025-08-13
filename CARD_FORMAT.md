# Anki Card Format Specification - V2.7

## Core Principle: One Card Per Meaning
Each distinct meaning gets its own card with unique Studio Ghibli image and contextually-generated sentences.

## Anki Note Type: "Fluent Forever"

### Current Field Structure (V2.7)
```
1. SpanishWord       - Base word (e.g., "con")
2. IPA              - Latin American contextual fricative pronunciation [kon]
3. MeaningContext   - Specific usage context (e.g., "instrument")
4. MonolingualDef   - Spanish definition for THIS meaning only
5. ExampleSentence  - LLM-generated sentence matching user's image prompt
6. GappedSentence   - Same sentence with word replaced by "______"
7. ImageFile        - Studio Ghibli image generated from user prompt
8. WordAudio        - Native Latin American pronunciation [sound:con.mp3]
9. UsageNote        - Generated from user prompt context for memory aid
10. PersonalMnemonic - Empty field for user's personal memory connections
```

### Key Improvements in V2.7:
- ✅ **Contextual IPA**: Fricatives applied contextually for optimal pronunciation
- ✅ **LLM-Generated Sentences**: Perfect alignment with user's visual scene
- ✅ **Studio Ghibli Imagery**: Consistent artistic style for memory formation
- ✅ **Latin American Audio**: Priority given to clear regional accents

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

## Autonomous System Integration

### Automatic Processing (V2.7)
1. **Virtual environment verification** - Ensures proper Python setup
2. **AnkiConnect availability** - Auto-launches Anki if needed
3. **API key validation** - Verifies OpenAI and Forvo access
4. **Media generation** - Creates images and downloads audio
5. **Contextual sentence generation** - LLM creates examples matching prompts
6. **Card creation** - Uploads media and creates formatted cards
7. **Progress tracking** - Updates vocabulary.json database

### Built-in Validation
```python
# Automatic validation in generate_batch.py:
def create_anki_card(card_data):
    """Create card with complete validation"""
    # Media file verification
    media_folder = config["paths"]["media_folder"]
    image_path = f"{media_folder}/images/{card_data['word']}_{card_data['meaning']}.png"
    audio_path = f"{media_folder}/audio/{card_data['word']}.mp3"
    
    # Field population
    fields = {
        "SpanishWord": card_data['word'],
        "IPA": get_ipa_pronunciation(card_data['word']),  # Contextual fricatives
        "MeaningContext": card_data['meaning'].replace('_', ' '),
        "MonolingualDef": card_data['definition'],
        "ExampleSentence": card_data['example'],  # LLM-generated
        "GappedSentence": card_data['gapped'],    # LLM-generated
        "ImageFile": f"<img src='{card_data['word']}_{card_data['meaning']}.png'>",
        "WordAudio": f"[sound:{card_data['word']}.mp3]",
        "UsageNote": f"Generated from user prompt: {card_data.get('prompt', '')[:100]}...",
        "PersonalMnemonic": ""
    }
```

### Error Recovery
- Log all Anki API responses
- Retry failed uploads with exponential backoff
- Store failed cards for manual recovery
- Never lose user work

## Autonomous Batch Processing (V2.7)

### Current Batch Example: `haber` + `con` (5 cards)
```json
{
  "haber": {
    "auxiliary_verb": "Boy and father eating fish and chips",
    "existential": "Man chasing cat from garden", 
    "necessity": "Boy jumping out of bed to study"
  },
  "con": {
    "accompaniment": "Two guys driving through Italy",
    "instrument": "Boy with hammer working in basement"
  }
}
```

### Autonomous Processing States
1. **pre-configured** - User prompts defined in advance
2. **executing** - Single command: `python generate_batch.py`
3. **generating_media** - OpenAI + Forvo API calls
4. **creating_sentences** - LLM contextual generation
5. **building_cards** - AnkiConnect integration
6. **completed** - All 5 cards created + database updated

**Execution Time**: 2-3 minutes for complete 5-card batch

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

*Card format V2.7: Autonomous system with contextual pronunciation, LLM sentences, and Studio Ghibli imagery*

**Current Status**: Production-ready autonomous processing  
**Execution**: `source venv/bin/activate && python generate_batch.py`  
**Result**: 5 perfectly-formatted Anki cards in 2-3 minutes
