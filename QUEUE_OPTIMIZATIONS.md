# Queue and Batch Planning – Proposed Optimizations (Future Work)

## Goals
- Minimize token spend while preserving Claude-led semantics
- Make batching deterministic, auditable, and safe
- Prevent duplicate/overflow scenarios and keep `vocabulary.json` authoritative

## Recommended Architecture
- Keep Claude for: meaning discovery, IPA (Neutral LA), sentences, prompts
- Add a local Batch Planner (CLI) to select words per batch (max 5 meanings)
- Use a small staging JSON file for Claude (not `vocabulary.json` directly)
- Ingest staging → derive IDs/media fields → validate → merge into `vocabulary.json`

## Batch Planner Logic
- Input: pending words (preferably structured; can read `word_queue.txt` initially)
- Greedy fill up to 5 meaning slots per batch:
  - If a word fits (≤5 meanings), keep its meanings together
  - If a word exceeds 5 meanings, defer the entire word to a future batch (never split)
  - If a word has remaining meanings (from prior deferral), schedule it wholly in a future batch
- Round-robin or FIFO fairness so large words don’t starve others
- Emit a run manifest: planned words, predicted slots, spillovers

## Source of Truth and Deduplication
- Treat `vocabulary.json` as the canonical ledger; add per-word status:
  - `status: pending|completed|skipped`
  - `processed_date|skipped_date`
  - `batch_id` for traceability
- Store skipped words in `vocabulary.json` (with `skip_reason`); keep `word_queue.txt` pending-only or deprecate it later
- Before planning: compute
  - `completed_words` = words with `status=completed`
  - `skipped_words` = words with `status=skipped`
  - `queue_words` = `word_queue.txt` − completed − skipped (case/diacritic-normalized)
- Validate no duplicates across these sets

## Collision and Overflow Handling
- Pre-staging: detect CardID collisions (`SpanishWord_MeaningID`) among planned content; exclude duplicates and log
- If a word’s meanings exceed capacity, skip the entire word, log “overflow: needs X slots,” carry the word intact to next batch

## Validation Gates
- Queue reconcile (pre-plan):
  - Ensure queue has no words already completed or skipped
  - Optional: consult a meaning-size cache to predict batch feasibility without Claude tokens
- Post-ingestion:
  - Verify unique CardIDs and field patterns
  - Update per-word status/date, `cards_created`, and global metadata in `vocabulary.json`

## Token-Saving Optimizations
- Maintain a local “meaning cache” (last-known MeaningIDs per word) to estimate batch sizes
- Keep Claude’s view scoped to a small staging file, not the full database

## Safety and Concurrency
- Use a lockfile for planning to avoid concurrent batch creation
- Strong logs with run ID and concise per-step summaries

## CLI Sketch (Future)
- `plan-batch` → selects words, writes `staging/batch_<id>_manifest.json` + `staging/claude_batch_<id>.json`
- `ingest-claude-batch --input staging/claude_batch_<id>.json` → validates/merges into `vocabulary.json`
- `run-media-then-sync --cards <CardID,...> --execute` → media + Anki sync if generation passes

## Rationale
- Keeps Claude focused on language semantics
- Reduces token usage via small staging files
- Ensures deterministic batching and simple recovery paths
- Centralizes history and statuses inside `vocabulary.json`

## Additional user notes

The system would work best as a single word processor, each time a word is processed, we create a staging file. The staging files are then auto-converted into vocabulary.json + generation + sync etc. This script doesn't require LLM control so it can be ran entirely without the LLM assistance. 

In fact, all we need the LLM for, is processing the meanings of the words, and putting them into the json format. Eventually, we could just make a pydantic model for a word etc. 

So, we would have two queues. The word queue, and the meaning queue. The word queue is automatically converted into the meaning queue as the meaning queue get's too short. This could perhaps be automatically be done by a dictionary rather than an LLM. There's probably also IPA dictionaries that one could choose from so that isn't needed. The LLM use could be put into a very small box.

In this scenario, the user would never have to wait. LLM processing and image generation would always be done in the background. 


