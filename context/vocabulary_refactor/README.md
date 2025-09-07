# Vocabulary Refactor Planning 

## Refactor Goal

To eliminate all manual inputs and claude usage outside of prompt writing

## High Level Method

All required inputs should be available in the Español.jsonl dictionary. By pulling the pipeline inputs from the dictionary we can eliminate all generation. Improving performance and efficiency. 

## Problem Areas

The dictionary contains all possible meanings of words defined as "senses". We need a small subset of only the critical senses.

## Required from Dictionary per Sense:

- **Word**: Pulled from root key "word"
- **IPA**: Pulled from root key "sounds" with the correct "raw_tags"
- **Monolingual Definition**: Pulled from root key "senses" dict "glosses" value
- **English Translation**: Pulled from root key "translations" dict "translations" value. Mapped from the "senses" key "sense_index"
- **Example Sentence**: Pulled from root key "senses" dict "examples" value. If multiple examples pull the first.
- **Gapped Example Sentence**: Same as above, however, the word is removed from the sentence and replaced with a _____ using the "bold_text_offsets" value

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
- "prompt": The prompt from the user
- "CardID": spanish word + meaning id joined by _
- "ImageFile": cardID + .png 
- "WordAudio": SpanishWord + .mp3

### Removals:
- "UsageNote"
- "WordAudioAlt"
- "MeaningContext"

