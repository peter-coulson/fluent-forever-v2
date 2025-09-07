# Vocabulary Refactor Planning 

## Refactor Goal

To eliminate all manual inputs and claude usage outside of prompt writing

## High Level Method

All required inputs should be available in the Español.jsonl dictionary. By pulling the pipeline inputs from the dictionary we can eliminate all generation. Improving performance and efficiency. 

## Required from Dictionary per Sense:

- **Word**: Pulled from root key "word"
- **IPA**: Pulled from root key "sounds" with the correct "raw_tags"
- **Monolingual Definition**: Pulled from root key "senses" dict "glosses" value
- **English Translation**: Pulled from root key "translations" dict "translations" value. Mapped from the "senses" key "sense_index"
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
- "MeaningID": English Translation formatted to be all lowercase joined with underscores
- "MonolingualDef": Spanish Definition
- "ExampleSentence": Spanish example from dictionary
- "GappedSentence": Spanish example from dictionary gapped
- "IPA": From Dict 
- "Prompt": The prompt from the user
- "CardID": spanish word + meaning id joined by _
- "ImageFile": cardID + .png 
- "WordAudio": SpanishWord + .mp3

## New Fields
- "Type": Pulled directly from Dictionary
- "Gender": Optional, pulled from the dictionary if it is the correct type

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

### Spanish dict to word queue 
#### Word Queue Structure
- The word queue entries will be a sequencial list of meanings with the same keys the meanings for words in vocabulary.json
- Every entry will be filled with the exception of Prompt and Gender which is an optional field that may be empty

#### Filling the Word Queue
- Input the number of new words to add to the queue 
- Pulls that many new words from the spanish_dictionary.json in order of rank that are not already in vocabulary as words, or skipped words, or in the word queue
- For each word "senses" value, appends a new meaning instance in the word_queue.json with the same fields as vocabulary.json filling the fields as described above 
- **Critical Problem** The dictionary contains all possible meanings of words defined as "senses". We need a small subset of only the most used senses
