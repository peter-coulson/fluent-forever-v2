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
     - The bracketed comment informs sentence generation only; do not treat it as part of the image prompt.
3. Produce sentences and IPA
   - ExampleSentence must closely match the prompt’s action and setting; include details implied by the bracketed comment when appropriate.
   - GappedSentence is the same sentence with the target word replaced by `_____`.
   - IPA (Neutral Latin American):
     - Seseo: c/z → [s]
     - Yeísmo: ll/y → [ʝ]
     - Contextual fricatives: intervocalic b/d/g → [β, ð, ɣ]; word‑initial b/d/g remain stops
     - No vowel reduction; keep clear vowel quality
     - Bracket IPA like [kon], or /.../ where appropriate; ensure one of these formats
4. Provide the final per-meaning fields to the system
   - Required: `SpanishWord, MeaningID, MeaningContext, MonolingualDef, ExampleSentence, GappedSentence (contains "_____"), IPA, prompt`.

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

**ALWAYS use virtual environment and PYTHONPATH to avoid dependency issues:**
```bash
# If venv doesn't exist, create it:
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# If venv exists, activate and set PYTHONPATH:
source venv/bin/activate
export PYTHONPATH=$(pwd)/src
```

**Critical**: Never use system Python3 directly - always activate venv first AND set PYTHONPATH.

## CLAUDE-COORDINATED EXECUTION

Main commands (use as needed; do not mention internal implementation details to users):

**PREREQUISITE: Always run environment setup first:**
```bash
source venv/bin/activate && export PYTHONPATH=$(pwd)/src
```

- Prepare batch staging (for Claude to fill):
  - `python -m cli.prepare_claude_batch --words por,para`
- Ingest staging (validate first, then execute):
  - `python -m cli.ingest_claude_batch --input staging/claude_batch_*.json --dry-run`
  - `python -m cli.ingest_claude_batch --input staging/claude_batch_*.json`
- Media & sync (fast path):
  - `python -m cli.run_media_then_sync --cards <CardID,...> --execute`
- Media only (fine-grained):
  - `python -m cli.media_generate --cards <CardID,...>` (preview)
  - `python -m cli.media_generate --cards <CardID,...> --execute [--no-images] [--no-audio]`
- Full deck sync:
  - `python -m cli.sync_anki_all [--delete-extras]` (will require interactive human confirmation for deletions)
- Templates:
  - `python -m validation.anki.template_validator` (compare HTML/CSS and placeholders)

## CRITICAL ERROR HANDLING

Use the smallest corrective step and keep card creation moving:

- Staging ingest fails:
  - Fix fields; ensure `GappedSentence` contains `_____`.
  - Re-run: `ingest-claude-batch --input ... --dry-run`, then execute.
- Missing media after generation:
  - Preview: `media-generate --cards <CardID,...>`; execute with `--execute` and `--max` as needed.
- Bad image outcome:
  - `regenerate-images --cards <CardID> --execute` (TTY required; backups stored automatically).
- Template mismatches:
  - `validate-anki-templates` then `sync-anki-all` to apply updates.
- Anki inconsistencies:
  - `sync-anki-all` prints missing words/meanings and field diffs; fix sources and re-run.
- Anki unavailable:
  - System auto-launches Anki; otherwise launch manually and retry.

## WORD QUEUE MANAGEMENT

**word_queue.txt Structure:**
- **PENDING WORDS**: Next words to process (top section)
- **SKIPPED WORDS**: User already knows, moved immediately when user requests skip
- **COMPLETED WORDS**: Successfully created cards, moved only after Anki cards generated

**Queue Update Protocol:**
1. **Skip Request**: Immediately move word from PENDING → SKIPPED with reason
2. **Completion**: Move word from PENDING → COMPLETED only after successful Anki card creation
3. **Format**: `word - meanings (X cards) - completion date`

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
**All commands require environment setup first:**
```bash
source venv/bin/activate && export PYTHONPATH=$(pwd)/src
```

**Then run commands with python -m:**
- Prepare staging: `python -m cli.prepare_claude_batch --words por,para`
- Ingest (validate → execute):
  - `python -m cli.ingest_claude_batch --input staging/claude_batch_*.json --dry-run`
  - `python -m cli.ingest_claude_batch --input staging/claude_batch_*.json`
- Media and sync (cards-only): `python -m cli.run_media_then_sync --cards <CardID,...> --execute`
- Media only: `python -m cli.media_generate --cards <CardID,...> [--execute] [--no-images] [--no-audio]`
- Full sync: `python -m cli.sync_anki_all [--delete-extras]` (interactive TTY required for deletions)
- Templates: `python -m validation.anki.template_validator`

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

**WORKFLOW**: Claude analyzes + fills staging → ingest to vocabulary → generate media → sync to Anki → validate