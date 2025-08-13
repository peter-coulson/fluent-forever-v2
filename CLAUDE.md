# FLUENT FOREVER V2 - CLAUDE OPERATIONAL GUIDE

## SYSTEM OVERVIEW
**Purpose**: Claude-managed Spanish Anki cards with Studio Ghibli imagery following Fluent Forever methodology
**Architecture**: Claude initiates workflow, manages analysis, requests user prompts, coordinates automation
**Current Status**: 8 words processed (33 cards), next word: `por`
**Core Principle**: One card per distinct meaning = one unique memory anchor

## CLAUDE-MANAGED WORKFLOW
**Claude controls the entire process** from the Claude Code terminal:

1. **Claude Initiates**: Claude asks user intent and manages entire workflow
2. **Claude Analyzes**: Claude identifies ALL distinct semantic meanings of Spanish word
3. **Claude Plans Batches**: Claude creates exactly 5 cards per batch with intelligent grouping
4. **Claude Requests Prompts**: Claude tells user which specific image prompts are needed
5. **Claude Coordinates**: Claude manages automation script to generate media + create cards
6. **Claude Updates**: Claude saves progress and manages all tracking through automation

## BATCH COMPOSITION RULES - ALWAYS 5 CARDS

**Claude-Managed Batch System:**
- **Claude determines**: Exactly 5 cards per batch (combines multiple words as needed)
- **Claude handles overflow**: If word exceeds 5 cards, Claude defers entire word to next batch
- **Claude requests prompts**: Claude tells user which specific prompts are needed for the batch

**Example Batch Compositions (Claude decides):**
- **Batch A**: "haber" (3 meanings) + "con" (2 meanings) = 5 cards
- **Batch B**: "por" (5 meanings) = 5 cards (Claude would defer if would exceed)
- **Batch C**: 5 single-meaning words = 5 cards

## MEANING ANALYSIS METHODOLOGY

### MANDATORY ANALYSIS CHECKLIST FOR EVERY WORD
**Claude NEVER assumes a word is simple - analyzes systematically:**

**1. Grammatical Category Check:**
- **Prepositions** (por, para, de, en, con, desde, hasta, etc.) → Usually multi-meaning
- **Verbs** → Check auxiliary uses, idiomatic expressions, different contexts
- **Articles/Pronouns** → Usually single meaning but verify
- **Conjunctions** → Usually single meaning but check for multiple functions

**2. Contextual Usage Analysis:**
- Can this word function in different grammatical roles?
- Does it have literal vs figurative meanings?
- Are there idiomatic expressions using this word?
- Does it express different semantic concepts in different contexts?

**3. Meaning Verification Process:**
- Create distinct example sentences for each potential meaning
- Ensure meanings cannot be substituted for each other
- If meanings overlap semantically, consider combining them
- Each meaning must represent a truly DISTINCT concept for memory formation

### REFERENCE EXAMPLES (NOT EXHAUSTIVE PATTERNS)
**Complex Multi-Meaning Examples:**
- **ser**: identity, qualities, time, origin (4 meanings)
- **estar**: location, states, actions, presence (4 meanings)  
- **por**: through/via, by means of, because of, in exchange for (4 meanings)
- **para**: purpose, deadline, destination, recipient (4 meanings)

**Single Meaning Examples:**
- **casa**: dwelling, **comer**: to eat, **rojo**: red color

**WARNING: Do NOT use these examples as rigid templates. Every word requires independent analysis.**

## MEANING EXPLANATION REQUIREMENT

### CLAUDE ALWAYS PROVIDES BEFORE COLLECTING PROMPTS
**For each meaning in the batch, Claude provides:**
- **Clear description** - Simple explanation of what the meaning expresses
- **Example sentence** - Spanish sentence demonstrating the meaning in context  
- **Context note** - When/how this meaning is typically used

**Format Example:**
```
**1. Auxiliary verb** - Creates past tenses like "I have eaten"
- Example: "He comido tacos" (I have eaten tacos)
- Context: Used with past participle to show completed actions
```

**Purpose**: Helps user understand each meaning clearly before creating memory-forming prompts

## PROMPT CREATION & MEMORY FORMATION

### CHARACTER-SPECIFIC REQUIREMENTS
**Good Memory-Forming Prompts**:
- "A teenage girl with long brown hair in braids, blue school uniform, focused expression, sitting at wooden desk in sunlit classroom reading thick textbook"
- "Boy around 10, messy black hair, green eyes, red striped shirt, running joyfully through meadow of tall grass and wildflowers"
- "Middle-aged man, gray beard, kind eyes, brown leather apron, crafting at wooden workbench with warm window light"

### PROMPT REVIEW CHECKLIST
**Claude ALWAYS validates each prompt has**:
- ✅ Specific age range and physical description
- ✅ Clear emotional state or activity  
- ✅ Detailed setting/environment
- ✅ Simple scene (not complex multi-action)
- ✅ Human-centered (fits Ghibli aesthetic)
- ❌ Avoid: generic people, abstract concepts, modern technology, complex scenes

### MEMORY CONNECTION PROCESS
**Critical**: Claude connects each prompt to meaning through character details
- **Word**: estudiar (to study)
- **Prompt**: "Teenage girl, brown braids, blue uniform, focused at desk"
- **Memory Link**: User creates specific visual anchor for "studying" concept
- **Card Result**: When seeing "estudiar", user recalls this exact girl studying

## API COST PROTECTION - ESSENTIAL

**Before ANY generation, Claude checks existing files**:
```bash
ls media/images/word_meaning.png
ls media/audio/word.mp3
```
**Skip generation if files exist - APIs are expensive**

## CONTEXTUAL SENTENCE GENERATION

### CLAUDE-POWERED SENTENCE CREATION
**Claude generates** contextual sentences matching user image prompts:

**Process:**
1. **Claude requests specific prompt**: Claude tells user "I need a visual prompt for 'con' meaning instrument"
2. **User provides visual prompt**: "boy with hammer driving nails"
3. **Claude analyzes**: word + meaning + visual context
4. **Claude generates**: Perfect Spanish sentence matching scene
5. **Result**: "El niño trabaja con un martillo" + "El niño trabaja _____ un martillo"

**Quality Standards:**
- Sentences match visual scene exactly
- Use simple, clear Spanish appropriate for learning
- Make word-meaning connection obvious
- Natural, authentic Spanish construction

## PRONUNCIATION SYSTEM - CONTEXTUAL FRICATIVES

### LATIN AMERICAN SPANISH IPA
**Optimal pronunciation strategy**: "Neutral Latin American"
- **Sounds native in**: Colombia, Mexico, Venezuela, Costa Rica
- **Understood everywhere**: No problematic regional markers
- **Perceived as**: Educated, sophisticated, formal

### KEY FEATURES:
- ✅ **Seseo**: 'c/z' → [s] (universal LA feature)
- ✅ **Yeísmo**: 'll/y' → [ʝ] (modern standard)
- ✅ **Contextual fricatives**: Stops word-initially, fricatives intervocalically
- ✅ **Clear vowels**: No reduction like Spain

### CONTEXTUAL FRICATIVE RULES:
- **Word-initial consonants**: Clear stops [b,d,g] for clarity
- **Intervocalic consonants**: Natural fricatives [β,ð,ɣ] for fluency
- **Examples**: 
  - bueno [ˈbweno] - word-initial b = stop
  - trabajo [traˈβaxo] - intervocalic b = fricative β
  - cada [ˈkaða] - intervocalic d = fricative ð

## FORVO AUDIO PRIORITIES

### LATIN AMERICAN COUNTRIES PRIORITIZED:
1. **CO** (Colombia) - Very clear, neutral accent
2. **MX** (Mexico) - Most common globally
3. **PE** (Peru) - Clear pronunciation
4. **VE** (Venezuela) - Clear pronunciation
5. **AR** (Argentina) - Distinct but understandable
6. **EC** (Ecuador) - Clear pronunciation
7. **UY** (Uruguay) - Clear pronunciation
8. **CR** (Costa Rica) - Clear pronunciation
9. **ES** (Spain) - BACKUP ONLY (different pronunciation)

**Excluded**: Countries with challenging pronunciation patterns (Chile avoided)

## PYTHON ENVIRONMENT SETUP

**ALWAYS use virtual environment to avoid dependency issues:**
```bash
# If venv doesn't exist, create it:
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# If venv exists, just activate:
source venv/bin/activate
```

**Critical**: Never use system Python3 directly - always activate venv first.

## CLAUDE-COORDINATED EXECUTION

**Claude manages the workflow:**
1. **Claude initiates**: "Process next word from queue or other action?"
2. **Claude analyzes**: Word meanings and creates batch plan
3. **Claude requests**: Specific image prompts from user
4. **Claude coordinates**: Runs automation script with collected data
5. **Claude validates**: Results and updates progress

```bash
# Claude runs when ready:
source venv/bin/activate && python generate_batch.py
```

**Automation script handles (under Claude's coordination):**
- ✅ AnkiConnect availability checking + Anki launch
- ✅ API key validation and error handling  
- ✅ Media file generation (images + audio)
- ✅ IPA pronunciation with contextual fricatives
- ✅ Anki card creation with all fields
- ✅ Vocabulary database updates
- ✅ Word queue progression management

## CRITICAL ERROR HANDLING

**Before API Calls**: Claude checks existing media files first
**Common Failures & Actions**:
- **AnkiConnect not responding**: Verify Anki open + restart AnkiConnect addon
- **OpenAI rate limit**: Wait 60s, retry once, defer batch if still failing
- **Forvo no audio**: Try base word, document missing, continue batch
- **Duplicate card**: Update existing instead of creating new
- **Media upload failed**: Verify local file exists, check Anki permissions

**Mid-Batch Recovery:**
- Save progress after each successful card
- Never regenerate existing media
- Preserve user prompts immediately after collection

## WORD QUEUE MANAGEMENT

**word_queue.txt Structure:**
- **PENDING WORDS**: Next words to process (top section)
- **SKIPPED WORDS**: User already knows, moved immediately when user requests skip
- **COMPLETED WORDS**: Successfully created cards, moved only after Anki cards generated

**Queue Update Protocol:**
1. **Skip Request**: Immediately move word from PENDING → SKIPPED with reason
2. **Completion**: Move word from PENDING → COMPLETED only after successful Anki card creation
3. **Format**: `word - meanings (X cards) - completion date`

## VOCABULARY DATABASE MANAGEMENT

**vocabulary.json** automatically maintains:
- **Complete word records**: All meanings with examples and context
- **Progress metadata**: Total words/cards, last update timestamps
- **Generated content**: LLM-created sentences matching user prompts
- **Media associations**: File paths for images and audio
- **Processing dates**: When each word was completed

## CARD CREATION FIELDS (Fluent Forever Format)

**Each meaning → card with:**
- SpanishWord, IPA, MeaningContext, MonolingualDef
- ExampleSentence, GappedSentence, ImageFile, WordAudio  
- Generated from: word + meaning_context + user_prompt + memory connection

## CURRENT BATCH CONFIGURATION

**Active Batch**: haber (3) + con (2) = 5 cards
**Next Batch**: por (5) = 5 cards  
**Status**: System ready for autonomous processing

**Pre-configured prompts available for immediate processing.**

## SYSTEM FILES
- `generate_batch.py`: Claude coordinates this automation script
- `vocabulary.json`: Progress tracking + meaning examples
- `word_queue.txt`: Queue management with PENDING/SKIPPED/COMPLETED sections
- `config.json`: API settings verification

## QUALITY ASSURANCE BUILT-IN

**Automatic Validation:**
- ✅ Virtual environment verification
- ✅ API key availability checking
- ✅ Anki/AnkiConnect connectivity
- ✅ Media file existence before card creation
- ✅ Complete field population validation
- ✅ Vocabulary database integrity maintenance

---

**CURRENT STATUS**: Production-ready Claude-managed processing system. Claude controls entire workflow from analysis through card creation, using automation for media generation only.

**WORKFLOW**: Claude initiates → requests prompts → coordinates automation → validates results