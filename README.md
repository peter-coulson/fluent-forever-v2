# Fluent Forever V2 - Claude-Managed Spanish Learning System

## 🎯 What This System Does

**Claude creates memorable Anki cards with Studio Ghibli imagery following Fluent Forever methodology.**

Transform Spanish vocabulary into unforgettable visual memories through Claude's intelligent management:
- 🤖 **Claude-managed workflow** - Claude controls analysis, requests prompts, coordinates automation
- 🎨 **Studio Ghibli imagery** - Consistent, emotionally engaging visual style via OpenAI API
- 🔊 **Native pronunciation** - Latin American audio from Forvo API
- 📚 **One card per meaning** - Proper Fluent Forever implementation via Claude's analysis
- ✨ **Claude-generated sentences** - Context-perfect examples matching your visual prompts

## 🚀 Quick Start

### Prerequisites
- **Claude Code** terminal
- **Anki** with AnkiConnect addon
- **OpenAI API** account with credits (~$0.25/batch)
- **Forvo API** account (for native audio)
- **Python 3.7+**

### Setup (2 minutes)
```bash
# Clone and setup
git clone [repository]
cd fluent-forever-v2

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your API keys to .env file
echo "OPENAI_API_KEY=your-key-here" >> .env
echo "FORVO_API_KEY=your-key-here" >> .env
```

### Usage
1. **Open Claude Code** in the project directory
2. **Claude asks**: "Process next word from queue or other action?"
3. **Claude analyzes** meanings and requests specific image prompts
4. **You provide** the requested visual scene descriptions
5. **Claude coordinates** automation to generate cards

**That's it!** Claude manages the entire workflow while you provide creative input.

## 🎌 How It Works

### Example: Claude Processing `haber` + `con` (5 cards total)
Claude manages the workflow with your creative input:

**Claude's Process:**
1. **Claude analyzes**: "haber has 3 meanings: auxiliary verb, existential, necessity"
2. **Claude analyzes**: "con has 2 meanings: accompaniment, instrument"
3. **Claude requests**: "I need 5 image prompts for these specific meanings..."
4. **You provide**: Visual scene descriptions
5. **Claude coordinates**: Automation generates media and creates cards

**Example Results:**
1. **haber** (auxiliary verb) → "Boy and father eating fish and chips" → Ghibli-style image
2. **haber** (existential) → "Man chasing cat from garden" → Ghibli-style image  
3. **haber** (necessity) → "Boy jumping out of bed to study" → Ghibli-style image
4. **con** (accompaniment) → "Two guys driving through Italy" → Ghibli-style image
5. **con** (instrument) → "Boy with hammer working in basement" → Ghibli-style image

### Coordinated Processing (via automation)
- ✅ **Downloads audio** - Colombian/Mexican pronunciation priority (Forvo API)
- ✅ **Generates images** - Studio Ghibli style with your scene descriptions (OpenAI API)
- ✅ **Creates contextual sentences** - Claude generates examples matching your prompts
- ✅ **Builds Anki cards** - Complete with IPA pronunciation, definitions, examples
- ✅ **Tracks progress** - Updates vocabulary.json database

## 📁 System Structure

```
fluent-forever-v2/
├── generate_batch.py           # Automation script (Claude coordinates)
├── config.json                 # API settings and preferences
├── vocabulary.json             # Learning progress database
├── word_queue.txt              # Spanish frequency word list
├── requirements.txt            # Python dependencies
├── .env                        # API keys (create this)
├── media/
│   ├── images/                 # Generated Ghibli artwork (OpenAI API)
│   └── audio/                  # Native pronunciations (Forvo API)
├── CLAUDE.md                   # Complete system documentation
├── DESIGN_DECISIONS.md         # Evolution and design rationale
└── CARD_FORMAT.md              # Technical specifications
```

## 🎯 Key Features

### **Contextual Fricative Pronunciation**
Uses optimal Latin American Spanish pronunciation:
- **Word-initial**: Clear stops [b,d,g] for clarity
- **Intervocalic**: Natural fricatives [β,ð,ɣ] for fluency  
- **Result**: Sounds educated and native-like across multiple regions

### **Claude's Intelligent Sentence Generation**
Claude creates sentences that perfectly match your image prompts:
- **Your prompt**: "boy with hammer driving nails"
- **Claude generates**: "El niño trabaja con un martillo" (The boy works with a hammer)
- **Perfect alignment** between visual scene and language example

### **Studio Ghibli Memory System**
- **Consistent artistic style** aids pattern recognition
- **Emotional engagement** enhances memory formation
- **Personal visual associations** through your scene descriptions

## 💰 Cost & Efficiency

- **Per batch**: ~$0.25 (5 cards)
- **Daily practice**: 10-20 cards = $0.50-$1.00
- **Time investment**: 2-3 minutes per batch (mostly automated)
- **Learning effectiveness**: Visual + auditory + contextual memories

## 🔧 Configuration

### API Setup
Edit `.env`:
```bash
OPENAI_API_KEY=your-openai-key
FORVO_API_KEY=your-forvo-key
```

### Preferences
Edit `config.json` for:
- Audio accent preferences (Colombian, Mexican, etc.)
- Image generation settings
- Anki deck configuration
- Media file locations

## 📊 Progress Tracking

The system automatically maintains:
- **vocabulary.json** - Complete word database with meanings and examples
- **word_queue.txt** - Pending/completed word tracking  
- **Media files** - Organized by word and meaning for easy reference

Check `vocabulary.json` to see:
- Total words processed: 8 words (33 cards)  
- Processing dates and batch information
- Generated examples and contextual sentences

## 🎨 Why This System Works

1. **Cognitive Load Optimization** - Claude handles analysis, automation handles repetitive tasks
2. **Memory Enhancement** - Visual + auditory + personal associations  
3. **Systematic Coverage** - Claude processes high-frequency vocabulary methodically
4. **Quality Consistency** - Ghibli style + native audio + proper formatting
5. **Sustainable Practice** - Cost-effective, time-efficient daily routine
6. **Intelligent Management** - Claude ensures proper Fluent Forever methodology

## 🔍 Technical Details

- **Management**: Claude controls workflow and meaning analysis
- **Language Processing**: Claude generates contextual sentences
- **Image Generation**: DALL-E 3 with Studio Ghibli prompting (OpenAI API)
- **Audio Source**: Forvo API with Latin American priority
- **Anki Integration**: AnkiConnect V6 for direct card creation
- **Pronunciation**: Contextual fricative system for optimal comprehension

---

## 📚 Documentation

- **CLAUDE.md** - Complete operational guide and procedures
- **DESIGN_DECISIONS.md** - Evolution history and design rationale  
- **CARD_FORMAT.md** - Technical card specifications and Anki integration

---

**🌟 Transform Spanish vocabulary into unforgettable Ghibli-style memories through Claude's intelligent management!**

*Current Status: Production Ready - Claude-Managed Processing System*