# Fluent Forever V2 - Spanish Learning System

## Quick Start

1. **Setup System**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure APIs**
   - Edit `config.json`
   - Add Forvo API key (get from https://forvo.com/api)
   - Optionally add ElevenLabs key for TTS fallback

3. **Start Services**
   - Start Automatic1111 WebUI (port 7860)
   - Start Anki with AnkiConnect addon (port 8765)

4. **Check Status**
   ```bash
   python3 automation.py status
   ```

## Workflow

1. **Ask Claude to process a word**
   - Claude analyzes meanings
   - You write custom prompts with friends as characters

2. **System generates media**
   - Creates Quentin Blake style images
   - Downloads native pronunciation

3. **Cards created in Anki**
   - One card per meaning
   - Personal imagery for deep memory encoding

## File Structure

```
fluent-forever-v2/
├── automation.py           # Main automation script
├── config.json            # Configuration and API keys
├── vocabulary.json        # Word database
├── word_queue.txt         # Words to process
├── CLAUDE_INSTRUCTIONS.md # System behavior guide
├── SYSTEM_DESIGN.md       # Design principles
├── CARD_FORMAT.md         # Anki card specifications
├── docs/
│   └── LORA_TRAINING_GUIDE.md  # Character LoRA training
├── media/
│   ├── images/           # Generated images
│   └── audio/            # Downloaded pronunciations
└── setup.sh              # Installation script
```

## Commands

- `python3 automation.py status` - Show system status
- `python3 automation.py test` - Test connections
- `python3 automation.py generate [prompt] [word] [meaning]` - Generate image
- `python3 automation.py audio [word]` - Download pronunciation

## Key Features

- **Personal Character System**: Friends as cartoon characters in images
- **One Card Per Meaning**: Complex words split into multiple cards
- **Quentin Blake Style**: Consistent whimsical illustration style
- **Native Audio**: Colombian/Mexican pronunciation preference
- **Simple Architecture**: One script, clear code, easy to modify

## Philosophy

This system automates the tedious parts (image generation, audio download) while preserving the valuable creative work (writing prompts with personal connections). The act of crafting prompts with friends as characters IS the learning process.

---

*Version 2.0 - Complete rewrite for enhanced memory encoding*
