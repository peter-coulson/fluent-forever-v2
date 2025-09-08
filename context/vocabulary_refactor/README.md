# Vocabulary Refactor Planning 

## Refactor Goal

To eliminate all manual inputs and claude usage outside of prompt writing

## High Level Method

All required inputs should be available in the Español.jsonl dictionary. By pulling the pipeline inputs from the dictionary we can eliminate all generation. Improving performance and efficiency. 

## Required from Dictionary per Sense:

- **Word**: Pulled from root key "word"
- **Sense ID**: For debugging purposes
- **IPA**: Pulled from root key "sounds" with the correct "raw_tags"
- **Monolingual Definition**: Pulled from root key "senses" dict "glosses" value
- **English Translation**: Pulled from root key "translations" dict "translations" value. Mapped from the "senses" key "sense_index". Pull all translations for the monolingual definition joined by ", ".
- **Example Sentence**: Pulled from root key "senses" dict "examples" value. If multiple examples pull the first.
- **Gapped Example Sentence**: Same as above, however, the word is removed from the sentence and replaced with a _____ using the "bold_text_offsets" value
- **Type**: Found under key "pos" as a string. Denotes tye type such as "noun"
- **Gender**: If gender applies to the word, it can be found under "tags" inside a list as ["masculine"] or ["feminine"]

## Pulled from APIs
- **Image from Prompt**: Generated per sense
- **Native Audio**: Generated per word

## Fields in vocabulary.json:
### Mappings from the dictionary
- "SpanishWord": word
- "MeaningID": Transliations field formatted to be all lowercase, commas removed, and spaces replaced with underscores
- "MonolingualDef": Spanish Definition
- "ExampleSentence": Spanish example from dictionary
- "GappedSentence": Spanish example from dictionary gapped
- "IPA": From Dict 
- "Prompt": The prompt from the user
- "CardID": spanish word + meaning id joined by _
- "ImageFile": cardID + .png 
- "WordAudio": SpanishWord + .mp3

## New Fields
- "Translations": Every translation that maps to the meaning id joined with commas. E.g. ""call, name, refer to""
- "Type": Pulled directly from Dictionary
- "Gender": Optional, pulled from the dictionary if it is the correct type
- "SenseID": For debugging or future reference, will not be visible

### Removals:
- "UsageNote"
- "WordAudioAlt"
- "MeaningContext"

## New Workflow

### Structure Before Sync
We divide the structure into four seperate and modular workflows:
1) From Spanish dict to word queue. 
2) Filling prompt creation for word queue 
3) Word queue to vocabulary
4) Vocabulary sync with Anki

### 1. Spanish dict to word queue 
#### Word Queue Structure
- The word queue entries will be a sequencial list of meanings with the same keys the meanings for words in vocabulary.json
- Every entry will be filled with the exception of Prompt and Gender which is an optional field that may be empty

#### Modular Architecture
The word queue population is divided into three configurable modules:

**WordSelector Module** - Configurable input strategies:
- **Rank-based**: Input number of words, pulls by rank order (default)
- **Specific words**: Input specific word list (comma-separated or file)
- **Custom filters**: Filter by word type, frequency range, etc.

**DictionaryFetcher Module** - Pure dictionary operations:
- Retrieves word entries from spanish_dictionary.json
- Validates word exists and has required fields
- Returns structured dictionary data for processing

**WordQueuePopulator Module** - Queue management:
- Takes processed dictionary data and creates queue entries
- Filters out words already in vocabulary, skipped words, or current queue
- Appends new meaning instances to word_queue.json with vocabulary.json field structure

#### Default Workflow (Rank-based)
- Input the number of new words to add to the queue 
- WordSelector pulls that many new words from spanish_dictionary.json in order of rank
- DictionaryFetcher retrieves and validates each word's dictionary data
- WordQueuePopulator filters existing entries and creates new queue entries
- For each word "senses" value, appends a new meaning instance in the word_queue.json with the same fields as vocabulary.json filling the fields as described above 
- **Critical Problem**: Dictionary contains all possible senses. We need only the most essential ones.
- **Solution**: Group senses by English translations, keeping only unique groups (no subsets):
      - Group senses with identical English translations
      - Eliminate subset groups (e.g., "call" is subset of "call, name, refer to")
      - Example grouping: [{1,2: "call, name, refer to"}, {3: "summon"}, {10: "knock, ring"}, {11: "attract, appeal"}]
- **Sense Selection**: For each group, select the first sense number that has an example sentence. If no senses in the group have examples, use the first sense number and log a warning.

### 2. Filling Prompt Creation
Will leave undefined for now. Options are either the user directly editing the word queue and calling a sync script that checks for any words where the prompt value is filled. Or we create some other batch file where the user inputs the CardID: "prompt". We also need some skip word function. I think this would probably be easiest to have some cli script for skipping word queue where we input the words to be skipped --skipped-words ya,yo,hay

### 3. Word Queue to Vocabulary
We generate the media as part of this pipeline. This would constitue a form of sync as described above. It should validate prompts are a certain number of characters to prevent accidental typos. Then it should validate that the media with the same name is not already in the media folder and the CardID is not already in vocabulary. Then proceed to generate all media. Once all media is generated, update vocabulary. 

### 4. Vocabulary Sync
This logic will remain largely unchanged
