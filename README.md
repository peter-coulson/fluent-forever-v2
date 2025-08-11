# Fluent Forever V3 - Ghibli Style Spanish Learning

## 🎌 Overview

A streamlined Spanish vocabulary learning system that generates memorable Anki cards using **Studio Ghibli-style** images. Process 5 words at a time with consistent artistic style and personal memory hooks.

## ✨ Features

- **Batch Processing**: 5 words at a time for efficiency
- **Ghibli-Style Images**: Consistent Studio Ghibli/Miyazaki aesthetic
- **User-Driven Prompts**: You provide image descriptions, system formats them
- **Memory-Focused**: Personal scene associations for better retention
- **OpenAI Integration**: DALL-E 3 for high-quality image generation
- **Progress Tracking**: Automatic vocabulary database management

## 🚀 Quick Start

### 1. Prerequisites
- OpenAI API account with credits
- Python 3.7+
- Internet connection

### 2. Setup
```bash
cd fluent-forever-v2
pip3 install requests
```

### 3. Run a Batch
```bash
python3 ghibli_spanish_generator.py
```

The system will prompt you for:
- 5 Spanish words
- English meanings
- Image scene descriptions
- Example sentences

## 💡 Example Workflow

```
Word 1/5
Spanish word: libro
English meaning: book
Image prompt: person reading by window in cozy room
Example sentence: Leo un libro interesante

→ Generated: "person reading by window in cozy room, Studio Ghibli animation style, Hayao Miyazaki art style, anime illustration, soft colors, detailed background"
```

## 📁 File Structure

```
fluent-forever-v2/
├── ghibli_spanish_generator.py  # Main batch processor
├── config.json                 # API keys and settings
├── vocabulary.json             # Your vocabulary database
├── media/                      # Generated images
└── README.md                   # This file
```

## ⚙️ Configuration

Edit `config.json`:
- Update OpenAI API key
- Modify Ghibli style prompt if needed
- Adjust file paths

## 💰 Costs

- **Per batch**: ~$0.20 (5 images × $0.04)
- **Per image**: $0.04 (OpenAI DALL-E 3 standard)
- **Efficient**: Process exactly what you need

## 🎯 Memory System

Each card creates a **Ghibli-style memory hook**:
1. **Spanish word** → **Your scene description** → **Ghibli aesthetic**
2. **Consistent artistic style** aids memory formation
3. **Personal scene associations** enhance recall

## 📊 Progress Tracking

The system automatically tracks:
- Total cards created
- Batch history
- Image/audio file associations
- Creation timestamps

## 🔧 Troubleshooting

**API Errors:**
- Check OpenAI API key in config.json
- Verify account has credits
- Check internet connection

**Image Generation Issues:**
- Simplify scene descriptions
- Avoid overly complex prompts
- Check DALL-E 3 content policies

## 🎌 Why Ghibli Style?

- **Consistent aesthetic** across all cards
- **Well-defined artistic style** for reliable generation
- **Memorable and distinctive** visual style
- **Emotionally engaging** for better retention

## 📚 Next Steps

1. **Process your first batch** of 5 words
2. **Review generated images** for quality
3. **Import cards to Anki** (manual for now)
4. **Repeat batches** as needed for vocabulary building

---

**🎨 Transform your Spanish learning with memorable Ghibli-style visual associations!**
