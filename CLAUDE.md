# FLUENT FOREVER V2 - CLAUDE OPERATIONAL GUIDE

## SYSTEM OVERVIEW
**Purpose**: Automated Spanish Anki cards with Studio Ghibli imagery following Fluent Forever methodology
**Default Action**: Ask user "Process next word from queue or other action?" 
**Current Status**: 6 words processed (26 cards), next word: `un`
**Core Principle**: One card per distinct meaning = one unique memory anchor

## PRIMARY WORKFLOW
1. **Launch**: Always ask user intent first
2. **Analyze**: Identify ALL distinct semantic meanings of Spanish word  
3. **Batch Planning**: Always exactly 5 cards per batch
4. **Collect**: User provides character-specific image prompts
5. **Review**: Validate prompts follow memory-formation guidelines
6. **Generate**: Create images + download audio + make Anki cards
7. **Update**: Save progress to vocabulary.json

## MEANING ANALYSIS METHODOLOGY - MEMORIZE THESE PATTERNS

### Complex Multi-Meaning Words
**ser** (4 meanings):
- identity: "Soy médico" (profession/identity)
- qualities: "Es inteligente" (permanent characteristics)  
- time: "Son las tres" (time/dates)
- origin: "Es de Colombia" (geographical origin)

**estar** (4 meanings):
- location: "Estoy aquí" (physical position)
- states: "Está feliz" (temporary emotions/conditions)
- actions: "Está trabajando" (progressive tenses)
- presence: "¿Está María?" (availability/presence)

**haber** (3 meanings):
- auxiliary: "He comido" (perfect tenses)
- existence: "Hay libros" (there is/there are)
- obligation: "Hay que estudiar" (impersonal necessity)

**tener** (4 meanings):
- possession: "Tengo coche" (ownership)
- age: "Tiene 20 años" (age expressions)
- obligation: "Tengo que irme" (personal necessity)
- feelings: "Tengo hambre" (physical/emotional states)

**para** (4 meanings):
- purpose: "Para estudiar" (in order to)
- deadline: "Para mañana" (by/for time)
- destination: "Para Madrid" (toward place)
- recipient: "Para ti" (for person)

### Single Meaning Words
**casa**: dwelling ("La casa es grande")
**comer**: to eat ("Como pizza") 
**dormir**: to sleep ("Duermo ocho horas")
**rojo**: red color ("El coche es rojo")
**hermano**: male sibling ("Mi hermano estudia")

## BATCH COMPOSITION RULES - ALWAYS 5 CARDS

**Examples**:
- **Batch A**: "tener" (4 meanings) + "casa" (1 meaning) = 5 cards
- **Batch B**: "para" (2 meanings) + "comer" (1) + "dormir" (1) + "rojo" (1) = 5 cards  
- **Batch C**: 5 single-meaning words = 5 cards
- **Overflow**: If next word exceeds 5 cards, defer entire word to next batch

## PROMPT CREATION & MEMORY FORMATION

### CHARACTER-SPECIFIC REQUIREMENTS
**Good Memory-Forming Prompts**:
- "A teenage girl with long brown hair in braids, blue school uniform, focused expression, sitting at wooden desk in sunlit classroom reading thick textbook"
- "Boy around 10, messy black hair, green eyes, red striped shirt, running joyfully through meadow of tall grass and wildflowers"
- "Middle-aged man, gray beard, kind eyes, brown leather apron, crafting at wooden workbench with warm window light"

### PROMPT REVIEW CHECKLIST
**ALWAYS validate each prompt has**:
- ✅ Specific age range and physical description
- ✅ Clear emotional state or activity  
- ✅ Detailed setting/environment
- ✅ Simple scene (not complex multi-action)
- ✅ Human-centered (fits Ghibli aesthetic)
- ❌ Avoid: generic people, abstract concepts, modern technology, complex scenes

### MEMORY CONNECTION PROCESS
**Critical**: Connect each prompt to meaning through character details
- **Word**: estudiar (to study)
- **Prompt**: "Teenage girl, brown braids, blue uniform, focused at desk"
- **Memory Link**: User creates specific visual anchor for "studying" concept
- **Card Result**: When seeing "estudiar", user recalls this exact girl studying

## API COST PROTECTION - ESSENTIAL

**Before ANY generation, check existing files**:
```bash
ls media/images/word_meaning.png
ls media/audio/word.mp3
```
**Skip generation if files exist - APIs are expensive**

## CONTEXTUAL SENTENCE CREATION
**Match sentences to user's image prompt**:
- Prompt: "boy nervous on airplane with mother" 
- Sentence: "El niño está nervioso en el avión con su madre"
- Gapped: "El niño _____ nervioso en el avión con su madre"

## CRITICAL ERROR HANDLING

**Before API Calls**: Check existing media files first
**Common Failures & Actions**:
- **AnkiConnect not responding**: Verify Anki open + restart AnkiConnect addon
- **OpenAI rate limit**: Wait 60s, retry once, defer batch if still failing
- **Forvo no audio**: Try base word, document missing, continue batch
- **Duplicate card**: Update existing instead of creating new
- **Media upload failed**: Verify local file exists, check Anki permissions

**Mid-Batch Recovery**:
- Save progress after each successful card
- Never regenerate existing media
- Preserve user prompts immediately after collection

## SYSTEM FILES
- `fluent_forever_automation.py`: Call `automation.process_batch()`
- `vocabulary.json`: Progress tracking + meaning examples
- `word_queue.txt`: Next words to process
- `config.json`: API settings verification

## CARD CREATION FIELDS (Fluent Forever Format)
Each meaning → card with:
- SpanishWord, IPA, MeaningContext, MonolingualDef
- ExampleSentence, GappedSentence, ImageFile, WordAudio  
- Generated from: word + meaning_context + user_prompt + memory connection