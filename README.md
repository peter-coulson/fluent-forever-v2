# Fluent Forever V2 - End-to-End Spanish Learning System

## 🎯 Core Philosophy
**Automate repetitive tasks, Claude handles intelligent decisions.** This system creates memorable Anki cards using Ghibli-style imagery through complete automation of the Fluent Forever methodology.

## ✨ Complete Workflow

### 1. **Intelligent Word Analysis** (Claude)
- Analyzes Spanish words from queue
- Identifies multiple meanings per word
- Creates batches of ≤5 cards maximum
- Handles meaning overflow between batches

### 2. **User Input Collection** (Once per batch)
- Claude presents all meanings needing prompts
- User provides image descriptions for each meaning
- System automatically formats with Ghibli style

### 3. **Automated Media Generation**
- Downloads native audio (Forvo API)
- Generates Ghibli-style images (OpenAI DALL-E 3)
- Creates one card per meaning

### 4. **Direct Anki Integration**
- Uploads media to Anki automatically
- Creates V4 format cards via AnkiConnect
- Updates vocabulary database

## 🚀 Quick Start

### Prerequisites
- **OpenAI API** account with credits
- **Forvo API** account (for native audio)
- **Anki** with AnkiConnect addon installed
- **Python 3.7+**

### Setup
```bash
cd fluent-forever-v2
pip3 install -r requirements.txt    # Install dependencies
# Update API keys in config.json
# Ensure Anki is running with AnkiConnect addon
```

### Usage with Claude
```
You: "Process the next batch from my Spanish word queue"

Claude: "Analyzing 'ser'... I found 2 distinct meanings:

1. **ser** (identity) - permanent characteristics 
   Example: 'Soy médico' (I am a doctor)
   
2. **ser** (existence) - to exist/be
   Example: 'Es importante' (It is important)

Please provide image descriptions for each:
1. Identity meaning: 
2. Existence meaning: "

You: "1. Doctor in white coat in hospital
2. Glowing important symbol on pedestal"

Claude: "Perfect! Generating your cards..."
✅ Downloaded audio: ser.mp3
✅ Generated images: ser_identity.png, ser_existence.png  
✅ Created 2 Anki cards
```

## 📁 System Structure

```
fluent-forever-v2/
├── fluent_forever_automation.py    # Main automation engine
├── word_queue.txt                  # Spanish words to process (Mark Davies frequency list)
├── config.json                     # API keys and settings
├── vocabulary.json                 # Complete learning database
├── requirements.txt                # Python dependencies
├── media/
│   ├── images/                     # Generated Ghibli artwork
│   └── audio/                      # Native pronunciations (Forvo API)
├── CARD_FORMAT.md                  # V4 Anki card specification
└── docs/                          # Technical documentation
```

## 🎌 Ghibli Memory System

Each card creates a **Studio Ghibli memory anchor**:
- **Spanish word** → **Your scene** → **Ghibli aesthetic**
- **One card per meaning** (core Fluent Forever principle)
- **Native pronunciation** for proper accent learning
- **Personal visual associations** enhance recall

## ⚙️ Configuration

Edit `config.json`:
```json
{
  "apis": {
    "openai": {
      "api_key": "your-openai-key",
      "enabled": true
    },
    "forvo": {
      "api_key": "your-forvo-key", 
      "enabled": true,
      "preferred_accents": ["Colombian", "Mexican"]
    }
  }
}
```

## 🔄 Smart Batch Management

- **Automatic overflow**: If word has >5 meanings, completes current batch first
- **Queue processing**: Works through word_queue.txt systematically  
- **State persistence**: Never lose progress if interrupted
- **One prompt session**: Collect all descriptions upfront, then automate everything

## 💰 Cost Transparency

- **Per card**: ~$0.04 (image) + ~$0.01 (audio) = $0.05
- **Typical batch**: 5 cards = ~$0.25
- **Daily learning**: 10-20 cards = $0.50-$1.00
- **Complete frequency list**: 100 words ≈ $25-50

## 🎯 Fluent Forever Integration

### Core Principles Respected
1. **One card per meaning** - Complex words get multiple cards
2. **Native audio** - Colombian/Mexican preferred accents  
3. **Personal imagery** - Your scene descriptions become memories
4. **Spaced repetition** - Direct Anki integration
5. **No translation** - Spanish definitions where possible

### V4 Card Format
- **Front**: Image + Spanish definition + Audio
- **Back**: Word + IPA + Example + Context
- **Fields**: 12 specialized fields for optimal learning

## 🤖 Claude Integration

This system is designed to work **with Claude** for:
- **Meaning analysis**: Complex grammatical understanding
- **Batch optimization**: Smart grouping of words/meanings  
- **User guidance**: Clear prompting for image descriptions
- **Quality assurance**: Ensuring proper card creation

**Claude handles intelligence, system handles automation.**

## 📊 Progress Tracking

The system automatically tracks:
- Words processed and remaining in queue
- Total cards created across all meanings
- Audio/image file associations
- Processing timestamps and batch history

## 🎨 Why This System Works

1. **Cognitive Load Optimization**: One creative task (prompt writing), everything else automated
2. **Memory Enhancement**: Visual + auditory + personal associations
3. **Systematic Coverage**: Process high-frequency vocabulary methodically
4. **Quality Consistency**: Ghibli style + native audio + V4 formatting
5. **Sustainable Practice**: Cost-effective, time-efficient daily routine

---

**🌟 Transform Spanish vocabulary into unforgettable Ghibli-style memories through intelligent automation!**