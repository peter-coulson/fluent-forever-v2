# FLUENT FOREVER V2 - CLAUDE OPERATIONAL GUIDE

## SYSTEM OVERVIEW
**Purpose**: Create high-quality Spanish Anki cards with Studio Ghibli imagery, following Fluent Forever methodology.
**Primary Priority**: Produce cards efficiently and reliably; handle errors gracefully; propose focused code edits only when needed.
**Core Principle**: One card per distinct meaning = one unique memory anchor.

### Operating principles (for Claude)
- Prioritize card production. Ask only for information that unblocks the next step.
- Make minimal, safe changes. Use dry-runs, caps, and validators before executing expensive actions.
- Be explicit about approvals. Never bypass interactive confirmations; do not auto-approve destructive operations.
- Prefer structured workflows and logs over ad-hoc actions.
- No duplication rule. Never duplicate meanings, CardIDs, prompts, media, or audio:
  - One CardID per (SpanishWord, MeaningID)
  - Reuse audio per word; do not request multiple pronunciations for the same word
  - Do not regenerate media if files already exist unless explicitly requested

## CLAUDE-MANAGED WORKFLOW (Card Creation)
Perform the semantic work; then hand off to automation.

**PRE-STEP: Word Selection and Validation**
   - **MANDATORY**: Check vocabulary.json first for any words already processed or skipped
   - **CRITICAL**: Skip entire words if they are already completed or in vocabulary.json "skipped_words" array
   - Never process words that are already in vocabulary.json "words" section or "skipped_words" array

1. Analyze meanings and request prompts
   - Identify ALL distinct semantic meanings per word
   - Request specific image prompts from the user for each meaning
2. Prompt validation (must pass before proceeding)
   - Keep prompts human-centered, Studio Ghibli style.
   - Include: a single clearly described subject (age, hair/eyes/clothing), a specific action, and a simple setting.
   - Avoid: multiple focal actions, modern tech, text/watermarks, violence/NSFW, ambiguous or crowded scenes.
   - Length: concise but complete (1–3 sentences). No policy violations.
   - Examples:
     - PASS: "Teenage boy, messy black hair, green eyes, red striped shirt, hammering nails into wooden board on a workbench in a sunlit workshop." (clear subject + action + setting)
     - FAIL: "people doing many things in a city" (ambiguous, crowded)
     - FAIL: "ultra-realistic photo of celebrity" (restricted content)
   - Prompt + comment format (for better sentence relevance):
     - Write the visual prompt, then add a bracketed comment for sentence context, e.g.
       - "A blond boy on a green train through the countryside with lots of sheep around [Me going home from boarding school as a child]"
     - **CRITICAL**: The bracketed comment informs sentence generation only; Claude MUST remove brackets from the image prompt
     - **MANDATORY SENTENCE RELEVANCE**: Claude MUST create sentences that match the visual prompt AND bracketed context, regardless of how abstract, unusual, or challenging the prompt may be
     - **PROCESS**: 
       1. Remove bracketed content from prompt for image generation
       2. Use bracketed context AND visual prompt details to create relevant Spanish sentences
       3. Never include brackets in the actual image prompt field
       4. Sentences must connect to the user's intended meaning, no exceptions
3. Produce sentences and IPA
   - ExampleSentence must closely match the prompt's action and setting; include details implied by the bracketed comment when appropriate.
   - GappedSentence is the same sentence with the target word replaced by `_____`.
   - **SPANISH NOUN GENDER REQUIREMENT**:
     - **MANDATORY**: ALL Spanish nouns MUST include their grammatical gender with the appropriate article
     - **Format**: Use definite articles (el/la/los/las) or indefinite articles (un/una/unos/unas) consistently
     - **Examples**: "un día" (not "día"), "la casa" (not "casa"), "el problema" (not "problema")
     - **Application**: Both ExampleSentence and GappedSentence must include the article with the noun
     - **Memory Formation**: Articles help learners internalize noun gender from the beginning
   - IPA (Neutral Latin American with Syllable Markers):
     - **MANDATORY**: Include syllable markers (dots) in ALL IPA transcriptions: `tra.βa.xo`, `a.βeɾ`, `ˈme.ði.ko`
     - Seseo: c/z → [s]
     - Yeísmo: ll/y → [ʝ]
     - Contextual fricatives: intervocalic b/d/g → [β, ð, ɣ]; word‑initial b/d/g remain stops
     - Stress marks: Use ˈ for primary stress, following Spanish phonological rules
     - No vowel reduction; keep clear vowel quality
     - Format: Always use bracket notation [tra.βa.xo] for consistency
     - **CRITICAL**: All IPA will be validated against authoritative Mexican Spanish dictionary
4. Provide the final per-meaning fields to the system
   - Required: `SpanishWord, MeaningID, MeaningContext, MonolingualDef, ExampleSentence, GappedSentence (contains "_____"), IPA, prompt`.

## BATCH COMPOSITION RULES - ALWAYS 5 CARDS

**Claude-Managed Batch System:**
- **MANDATORY PRE-CHECK**: Before analyzing any word, Claude MUST verify it's not already in vocabulary.json "words" or "skipped_words" sections
- **Claude determines**: Exactly 5 cards per batch (combines multiple words as needed)
- **Claude handles overflow**: If word exceeds 5 cards, Claude defers entire word to next batch
- **Claude handles skipping**: Add skipped words to "skipped_words" section in batch staging file
- **Claude requests prompts**: Claude tells user which specific prompts are needed for the batch

**Example Batch Compositions (Claude decides):**
- **Batch A**: "haber" (3 meanings) + "con" (2 meanings) = 5 cards
- **Batch B**: "por" (5 meanings) = 5 cards (Claude would defer if would exceed)
- **Batch C**: 5 single-meaning words = 5 cards

## MEANING ANALYSIS METHODOLOGY

### MANDATORY ANALYSIS CHECKLIST FOR EVERY WORD
**Claude NEVER assumes a word is simple - analyzes systematically:**

## MANDATORY 4-STEP PROCESS FOR EVERY WORD (NO EXCEPTIONS)

**STEP 1: Grammatical Category Check**
- **Prepositions** (por, para, de, en, con, desde, hasta, sobre, etc.) → Usually multi-meaning
- **Verbs** → Check auxiliary uses, idiomatic expressions, different contexts
- **Nouns** → **CRITICAL**: MUST include grammatical gender with appropriate article (el/la/un/una)
- **Articles/Pronouns** → Usually single meaning but verify
- **Conjunctions** → Usually single meaning but check for multiple functions
- **Adverbs/Adjectives** → Check degree, manner, time variations

**STEP 2: Multi-Context Analysis**
Claude MUST ask these questions for EVERY word:
- Can this word function in different grammatical roles?
- Does it have literal vs figurative meanings?
- Are there idiomatic expressions using this word?
- Does it express different semantic concepts in different contexts?
- Can I create example sentences where the word means something completely different?

**STEP 3: Distinct Meaning Verification**
For each potential meaning Claude identifies:
- Create distinct example sentences for each potential meaning
- Test: Can meanings be substituted for each other? If YES → combine them
- Test: Does each meaning create a different mental image/concept? If NO → combine them
- Each meaning must represent a truly DISTINCT concept for memory formation

**STEP 4: Final Count Verification**
Before proceeding to batch composition:
- List all meanings identified with clear distinctions
- Double-check each meaning is truly distinct
- Count total cards needed for the word
- NEVER proceed without completing this 4-step process for EVERY word

## EXAMPLES OF PROPER SYSTEMATIC ANALYSIS

**sobre (preposition):**
- STEP 1: Preposition → likely multi-meaning ✓
- STEP 2: Check contexts: "sobre la mesa" vs "sobre el tema" vs "sobre las cinco" → Different concepts ✓
- STEP 3: Create examples:
  * Physical: "El libro está sobre la mesa" (on/above)
  * Topic: "Hablamos sobre el clima" (about/concerning) 
  * Approximation: "Llegó sobre las cinco" (around/approximately)
- STEP 4: 3 distinct meanings → 3 cards needed

**casa (noun):**
- STEP 1: Noun → check for multiple uses + MUST include gender (la casa) ✓
- STEP 2: Check contexts: always means dwelling/house ✓
- STEP 3: Create examples: "La casa tiene tres habitaciones" (all refer to same concept) ✓
- STEP 4: 1 meaning → 1 card needed

### REFERENCE EXAMPLES (NOT EXHAUSTIVE PATTERNS)
**Complex Multi-Meaning Examples:**
- **ser**: identity, qualities, time, origin (4 meanings)
- **estar**: location, states, actions, presence (4 meanings)  
- **por**: through/via, by means of, because of, in exchange for (4 meanings)
- **para**: purpose, deadline, destination, recipient (4 meanings)

**Single Meaning Examples:**
- **la casa**: dwelling, **comer**: to eat, **rojo**: red color
- **el día**: day, **una mesa**: table, **el problema**: problem

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
**CRITICAL: Claude NEVER edits user prompts - only reviews and suggests improvements**
**Claude ALWAYS validates each prompt has**:
- ✅ Specific age range and physical description
- ✅ Clear emotional state or activity  
- ✅ Detailed setting/environment
- ✅ Simple scene (not complex multi-action)
- ✅ Human-centered (fits Ghibli aesthetic)
- ❌ Avoid: generic people, abstract concepts, modern technology, complex scenes

**PROMPT POLICY**:
- Claude may CRITIQUE prompts and SUGGEST improvements
- Claude may WARN about potential generation issues
- Claude MUST NEVER override or edit user-provided prompts
- If Claude suggestions are rejected, Claude MUST use user prompts exactly as provided, even if suboptimal

### MEMORY CONNECTION PROCESS
**Critical**: Claude connects each prompt to meaning through character details
- **Word**: estudiar (to study)
- **Prompt**: "Teenage girl, brown braids, blue uniform, focused at desk"
- **Memory Link**: User creates specific visual anchor for "studying" concept
- **Card Result**: When seeing "estudiar", user recalls this exact girl studying

## API COST PROTECTION (Claude's checklist)
- Always validate prompts first; do not request generation until prompts are ready.
- Use dry-runs and caps on generation:
  - Preview media plan: `python -m cli.media_generate --cards <CardID,...>` (no API calls)
  - Max limit automatically set from config (default 6 items for 5-card batches)
  - Skip providers: `--no-images`, `--no-audio` as needed
- Never regenerate existing media unless explicitly requested (e.g., regenerate-images)
- **Standard batch command**: `python -m cli.run_media_then_sync --cards <CardID,...> --execute`

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
- **NOUN GENDER**: Always include articles with nouns (el/la/un/una) for gender learning

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

# ⚠️ ⚠️ ⚠️ CRITICAL: ALWAYS USE THE ACTIVATION SCRIPT ⚠️ ⚠️ ⚠️
# ⚠️ ⚠️ ⚠️ NEVER RUN COMMANDS WITHOUT IT ⚠️ ⚠️ ⚠️

**MANDATORY**: Use the activation script for ALL Python commands:
```bash
# ALWAYS run this first:
source activate_env.sh

# Then run your commands:
python -m cli.prepare_claude_batch --words word1,word2
python -m cli.ingest_claude_batch --input staging/file.json
python -m cli.run_media_then_sync --cards CardID1,CardID2 --execute
```

**The activation script (`activate_env.sh`) automatically:**
- Activates the virtual environment
- Sets PYTHONPATH correctly
- Changes to the project directory
- Displays confirmation of proper setup

# ⚠️ ⚠️ ⚠️ DO NOT USE MANUAL ACTIVATION COMMANDS ⚠️ ⚠️ ⚠️
# ⚠️ ⚠️ ⚠️ ALWAYS USE: source activate_env.sh ⚠️ ⚠️ ⚠️

**If you get "ModuleNotFoundError: No module named 'cli'":**
- You forgot to run `source activate_env.sh` first
- STOP and run the activation script before proceeding

## CLAUDE-COORDINATED EXECUTION

Main commands (use as needed; do not mention internal implementation details to users):

# ⚠️ ⚠️ ⚠️ PREREQUISITE: ALWAYS RUN ACTIVATION SCRIPT FIRST ⚠️ ⚠️ ⚠️
```bash
source activate_env.sh
```

- Prepare batch staging (for Claude to fill):
  - `source activate_env.sh && python -m cli.prepare_claude_batch --words por,para`
- Ingest staging (validate first, then execute):
  - `source activate_env.sh && python -m cli.ingest_claude_batch --input staging/claude_batch_*.json --dry-run`
  - `source activate_env.sh && python -m cli.ingest_claude_batch --input staging/claude_batch_*.json`
- Media & sync (fast path):
  - `source activate_env.sh && python -m cli.run_media_then_sync --cards <CardID,...> --execute`
- Media only (fine-grained):
  - `source activate_env.sh && python -m cli.media_generate --cards <CardID,...>` (preview)
  - `source activate_env.sh && python -m cli.media_generate --cards <CardID,...> --execute [--no-images] [--no-audio]`
- Full deck sync:
  - `source activate_env.sh && python -m cli.sync_anki_all [--delete-extras]` (will require interactive human confirmation for deletions)
- Templates:
  - `source activate_env.sh && python -m validation.anki.template_validator` (compare HTML/CSS and placeholders)

## CRITICAL ERROR HANDLING

Use the smallest corrective step and keep card creation moving:

- Staging ingest fails:
  - Fix fields; ensure `GappedSentence` contains `_____`.
  - Re-run: `ingest-claude-batch --input ... --dry-run`, then execute.
- Missing media after generation:
  - Preview: `media-generate --cards <CardID,...>`; execute with `--execute` and `--max` as needed.
- Bad image outcome:
  - **CRITICAL**: First update the prompt in vocabulary.json manually, THEN regenerate
  - `regenerate-images --cards <CardID> --execute` (TTY required; backups stored automatically)
  - **Process**: 1) Edit vocabulary.json prompt field, 2) Run regenerate command
- Template mismatches:
  - `validate-anki-templates` then `sync-anki-all` to apply updates.
- Anki inconsistencies:
  - `sync-anki-all` prints missing words/meanings and field diffs; fix sources and re-run.
- Anki unavailable:
  - System auto-launches Anki; otherwise launch manually and retry.

## WORD QUEUE MANAGEMENT

**NEW SYSTEM**: Programmatic JSON-based word queue generation from spanish_dictionary.json.

**word_queue.json Structure:**
- **JSON array**: Simple list of Spanish words ordered by frequency
- **Metadata**: Creation date, source, counts of excluded words
- **Format**: `{"metadata": {...}, "words": ["word1", "word2", ...]}`

**Word Queue Generation:**
- **Command**: `python -m cli.generate_word_queue --count N`
- **Source**: spanish_dictionary.json (frequency-ranked Spanish dictionary)
- **Filtering**: Automatically excludes already processed and skipped words
- **Deduplication**: Removes duplicate entries
- **Quality**: Filters out English words and invalid entries

**Usage Examples:**
```bash
source activate_env.sh
python -m cli.generate_word_queue --count 100          # Generate 100 words
python -m cli.generate_word_queue --count 50 --dry-run # Preview without creating file
python -m cli.generate_word_queue --output my_queue.json --count 25  # Custom output file
```

**Integration:**
- Claude should read from word_queue.json for next words to process
- Words are selected in order from the "words" array
- System automatically excludes words already in vocabulary.json
- Regenerate queue when needed with fresh words

## SYSTEM FUNCTIONALITY (for Claude’s context)

- Staging → Ingestion → Vocabulary
  - You provide per-meaning fields via staging; the system derives IDs & media fields and merges into `vocabulary.json` (golden source) after validation.
- Media generation
  - Idempotent, capped, and validated. Cost estimation is logged. Provenance (.index.json) avoids accidental re-generation; lockfiles prevent concurrent runs.
- Anki sync
  - Validates templates, uploads media, upserts cards by CardID, logs precise field diffs on mismatch, and requires interactive confirmation before deletions.
- Logging
  - High-signal, structured logs at each step with clear summaries; use dry-run modes to preview actions.

## CARD CREATION FIELDS (Fluent Forever Format)

**Each meaning → card with:**
- SpanishWord, IPA, MeaningContext, MonolingualDef
- ExampleSentence, GappedSentence, ImageFile, WordAudio  
- Generated from: word + meaning_context + user_prompt + memory connection

## COMMANDS CHEAT SHEET (Claude)

# ⚠️ ⚠️ ⚠️ STEP 1: ALWAYS ACTIVATE ENVIRONMENT FIRST ⚠️ ⚠️ ⚠️
```bash
source activate_env.sh
```

# ⚠️ ⚠️ ⚠️ STEP 2: THEN RUN YOUR COMMANDS ⚠️ ⚠️ ⚠️

- Generate word queue: `python -m cli.generate_word_queue --count 50 [--dry-run]`
- Prepare staging: `python -m cli.prepare_claude_batch --words por,para`
- Ingest (validate → execute):
  - `python -m cli.ingest_claude_batch --input staging/claude_batch_*.json --dry-run`
  - `python -m cli.ingest_claude_batch --input staging/claude_batch_*.json`
  - `python -m cli.ingest_claude_batch --input staging/claude_batch_*.json --skip-ipa-validation` (override IPA failures)
- Media and sync (cards-only): `python -m cli.run_media_then_sync --cards <CardID,...> --execute`
- Media only: `python -m cli.media_generate --cards <CardID,...> [--execute] [--no-images] [--no-audio]`
- Full sync: `python -m cli.sync_anki_all [--delete-extras]` (interactive TTY required for deletions)
- Templates: `python -m validation.anki.template_validator`

# ⚠️ ⚠️ ⚠️ REMEMBER: source activate_env.sh MUST BE RUN FIRST ⚠️ ⚠️ ⚠️

## TEMPLATES: Local Preview and Editing

- **Start local preview server** (auto-reloads on file save):
  ```bash
  source activate_env.sh
  python -m cli.preview_server --port 8000
  ```

- **Open a card in the browser** (uses local templates, CSS, vocabulary, and media):
  - Front: `http://127.0.0.1:8000/preview?card_id=<CardID>&side=front`
  - Back: `http://127.0.0.1:8000/preview?card_id=<CardID>&side=back`
  - Full card: `http://127.0.0.1:8000/preview?card_id=<CardID>` (shows both front and back)

- **What it renders like**:
  - Full page background is white; the card area uses a dark Anki‑like background with centered content
  - The divider between front/back is shown via `<hr id="answer">` as in Anki
  - Your `styling.css` is inlined after a minimal Anki‑like base so your styles take precedence

- **Edit and refresh** (no extra steps):
  - Edit `templates/anki/Fluent_Forever/templates/*.html` or `styling.css` → save → browser refresh
  - Edit `vocabulary.json` fields (e.g., sentences, defs) → save → refresh
  - Images and audio are served from `media/images` and `media/audio`

- **Quick CardID lookup**:
  - `http://127.0.0.1:8000/api/cards` returns a JSON list of available `CardID`s with brief metadata

- **Notes/limits**:
  - Supports section tags `{{#Field}}...{{/Field}}`, simple `{{Field}}` replacements, and injects `{{FrontSide}}` when rendering the back
  - Audio fields like `[sound:file.mp3]` are previewed as HTML `<audio>` controls

## SYSTEM FILES
- `generate_batch.py`: Claude coordinates this automation script
- `vocabulary.json`: Progress tracking + meaning examples
- `word_queue.txt`: Queue management with PENDING/SKIPPED/COMPLETED sections
- `config.json`: API settings verification

## IPA VALIDATION SYSTEM

**Authoritative Dictionary-Based Validation:**
- ✅ **595,885+ Mexican Spanish dictionary entries** from open-dict-data project
- ✅ **Automatic validation** during Claude batch ingestion
- ✅ **Smart comparison**: Ignores syllable markers (.), handles stress intelligently
- ✅ **Multi-word support**: Validates `tener que` by checking only `tener`
- ✅ **Override option**: `--skip-ipa-validation` for dictionary discrepancies

**Validation Process:**
1. **Claude provides IPA** with syllable markers: `[tra.βa.xo]`
2. **System validates** against Mexican Spanish dictionary during ingestion
3. **Failures halt ingestion** with detailed error reporting
4. **Override available** when certain your IPA is correct

**Key Features:**
- **Contextual fricatives**: Validates `β, ð, ɣ` vs `b, d, g` correctly
- **Stress patterns**: Only enforces stress when dictionary has stress marks
- **Syllable markers**: Automatically removed for comparison (`tra.βa.xo` = `traβaxo`)
- **Latin American**: Validates seseo (s not θ) and yeísmo (ʝ not ʎ)

**Commands:**
- Validate single word: `python -m validation.ipa_validator trabajo tra.βa.xo`
- Batch validation: Automatic during `ingest_claude_batch`
- Override failures: `ingest_claude_batch --skip-ipa-validation`

## QUALITY ASSURANCE BUILT-IN

**Automatic Validation:**
- ✅ Virtual environment verification
- ✅ API key availability checking
- ✅ Anki/AnkiConnect connectivity
- ✅ Media file existence before card creation
- ✅ Complete field population validation
- ✅ Vocabulary database integrity maintenance
- ✅ **IPA pronunciation validation** against authoritative dictionary

---

**WORKFLOW**: Claude analyzes + fills staging → ingest to vocabulary → generate media → sync to Anki → validate