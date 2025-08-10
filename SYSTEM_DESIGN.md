# Fluent Forever V2 - System Design Document

## Core Design Principles

### 1. **Memory-First Learning**
Personal cartoon avatars of friends in custom scenarios create deep emotional memory anchors. The creative act of writing prompts is part of the learning process, not a task to automate.

### 2. **Intelligent Automation**
Automate only mechanical tasks (audio download, image generation, file management). Preserve human creativity in prompt writing and meaning analysis.

### 3. **Radical Simplicity**
Every component must be understandable at a glance. Prefer 10 lines of clear code over 100 lines of clever code. Documentation lives in the code, not separate files.

### 4. **Single Source of Truth**
One configuration file, one instruction file, one automation script. No duplicate information across multiple documents.

### 5. **Fail Gracefully**
System continues working even if APIs are down. Local fallbacks for everything. Never lose user work.

## System Aims

### Primary Goals
1. **Transform Spanish vocabulary into memorable Anki cards** using personal cartoon imagery
2. **Create one card per meaning** for complex words (following Fluent Forever methodology)
3. **Generate consistent Quentin Blake-style illustrations** featuring user and friends as characters
4. **Automate audio acquisition** from native speakers (Forvo/TTS fallback)
5. **Maintain zero-friction workflow** from word analysis to card creation

### Success Metrics
- **Time per word**: <2 minutes total (including prompt writing)
- **Image generation success**: >90% acceptable on first generation
- **Audio availability**: 100% coverage (Forvo or TTS)
- **Memory retention**: 2x improvement over generic images (user-reported)
- **System reliability**: Works offline except for API calls

### Non-Goals
- Not trying to automate prompt creation (this is valuable thinking time)
- Not building a general-purpose language learning platform
- Not optimizing for multiple users (single-user focus)
- Not creating perfect images (memorable is better than beautiful)

## Technical Architecture

### Components
1. **claude_instructions.md**: Complete system behavior specification
2. **automation.py**: Single Python script handling all automation
3. **config.json**: API keys, preferences, and settings
4. **vocabulary.json**: Word database with meanings and media references
5. **word_queue.txt**: Simple text list of words to process

### Data Flow
```
word_queue.txt → Claude analyzes meanings → User writes prompts →
→ automation.py generates images → automation.py downloads audio →
→ Creates Anki cards → Updates vocabulary.json → Git commit
```

### API Integrations
- **Automatic1111 WebUI**: Local image generation (port 7860)
- **Forvo API**: Native pronunciation downloads
- **AnkiConnect**: Card creation and media upload (port 8765)
- **ElevenLabs** (optional): TTS fallback for missing pronunciations

## Key Innovations

### 1. Personal Character System
- User and friends as cartoon characters via LoRA models
- Consistent character appearance across all cards
- Emotional memory encoding through familiar faces

### 2. Meaning-Specific Imagery
- Each word meaning gets unique image
- Images directly illustrate the specific usage
- Visual disambiguation of similar concepts

### 3. Prompt-Based Learning
- Writing prompts forces semantic processing
- Creative engagement enhances encoding
- Personal context selection improves recall

### 4. Hybrid Automation
- Human creativity for high-value tasks
- Machine efficiency for mechanical tasks
- Optimal cognitive load distribution

---

*Created: August 10, 2025*
*Purpose: Spanish learning through personalized visual memory encoding*
*Philosophy: Automate the tedious, preserve the meaningful*
