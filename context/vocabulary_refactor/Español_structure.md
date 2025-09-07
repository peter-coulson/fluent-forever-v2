# Español.jsonl Structure Analysis

## Overview
- Analysis based on first 1000 entries
- Total root-level keys found: 27

## Root-Level Keys

### `antonyms`
- **Types**: array_of_objects
- **Purpose**: Array of antonymous words

### `categories`
- **Types**: array_of_objects
- **Purpose**: Array of semantic/grammatical categories

### `cognates`
- **Types**: array_of_objects

### `compounds`
- **Types**: array_of_objects

### `derived`
- **Types**: array_of_objects

### `descendants`
- **Types**: array_of_objects

### `etymology_text`
- **Types**: string
- **Purpose**: Etymology/word origin information

### `extra_sounds`
- **Types**: object

### `forms`
- **Types**: array_of_objects
- **Purpose**: Array of different word forms (conjugations, declensions)

### `hypernyms`
- **Types**: array_of_objects

### `hyphenations`
- **Types**: array_of_objects

### `hyponyms`
- **Types**: array_of_objects

### `idioms`
- **Types**: array_of_objects

### `lang`
- **Types**: string
- **Purpose**: Language code (typically "es" for Spanish)

### `lang_code`
- **Types**: string
- **Purpose**: ISO language code

### `meronyms`
- **Types**: array_of_objects

### `pos`
- **Types**: string
- **Purpose**: Part of speech (noun, verb, adjective, etc.)

### `pos_title`
- **Types**: string

### `proverbs`
- **Types**: array_of_objects

### `raw_tags`
- **Types**: array_of_strings

### `related`
- **Types**: array_of_objects

### `senses`
- **Types**: array_of_objects
- **Purpose**: Array of different meanings/definitions

### `sounds`
- **Types**: array_of_objects
- **Purpose**: Array of pronunciation information

### `synonyms`
- **Types**: array_of_objects
- **Purpose**: Array of synonymous words

### `tags`
- **Types**: array_of_strings

### `translations`
- **Types**: array_of_objects
- **Purpose**: Array of translations to other languages

### `word`
- **Types**: string
- **Purpose**: The main word/term being defined

## Nested Object Structures

### Objects within `categories` arrays

**Keys found in objects:**
- `kind`: Examples: "other", "other"
- `name`: Examples: "BG:Traducciones incompletas o imprecisas", "ES:Adjetivos"
- `parents`: Examples: [], []
- `source`: Examples: "w", "w"

### Objects within `forms` arrays

**Keys found in objects:**
- `form`: Examples: "japoneses", "japonesa"
- `raw_tags`: Examples: ['Caso'], ['Caso']
- `tags`: Examples: ['plural'], ['feminine']

### Objects within `senses` arrays

**Keys found in objects:**
- `categories`: Examples: [{'name': 'ES:Gentilicios', 'kind': 'other', 'parents': [], 'source': 'w'}], [{'name': 'ES:Gentilicios', 'kind': 'other', 'parents': [], 'source': 'w'}]
- `examples`: Examples: [{'text': "Un romero alemán albergó en casa de Gil Buhón, et estando ý çinco días, et diol' un preçincto a goardar a su muger sin cadenado.", 'bold_text_offsets': [[10, 16]], 'ref': 'Anónimo. Libro de los fueros de Castiella (1284). Editorial: Hispanic Seminary of Medieval Studies. Madison, WI, 1993.'}], [{'text': 'El escritor y filósofo mallorquín Ramón Llull es uno de los exponentes de la literatura catalana.', 'bold_text_offsets': [[88, 96]]}]
- `form_of`: Examples: [{'word': 'amigar'}, {'word': 'amigarse'}], [{'word': 'unir'}]
- `glosses`: Examples: ['Originario, relativo a, o propio de Japón.'], ['Persona originaria de Japón.']
- `id`: Examples: "es-japonés-es-adj-whJ6DQKZ", "es-japonés-es-noun-o3WE460w"
- `raw_tags`: Examples: ['Glotónimos'], ['Glotónimos']
- `sense_index`: Examples: "1", "2"
- `tags`: Examples: ['noun'], ['Southern-Chile']
- `topics`: Examples: ['countries'], ['weekdays']

### Objects within `sounds` arrays

**Keys found in objects:**
- `alternative`: Examples: "ca", "ca"
- `audio`: Examples: "LL-Q1321 (spa)-Rodelar-Japón.wav", "Es-catalán-bo-La Paz.ogg"
- `flac_url`: Examples: "https://commons.wikimedia.org/wiki/Special:FilePath/Letter b es es.flac", "https://commons.wikimedia.org/wiki/Special:FilePath/Letter b es es.flac"
- `homophone`: Examples: "ve", "ve"
- `ipa`: Examples: "[xa.poˈnes]", "[xa.poˈnes]"
- `mp3_url`: Examples: "https://upload.wikimedia.org/wikipedia/commons/transcoded/1/15/LL-Q1321_(spa)-Rodelar-Japón.wav/LL-Q1321_(spa)-Rodelar-Japón.wav.mp3", "https://upload.wikimedia.org/wikipedia/commons/transcoded/5/54/Es-catalán-bo-La_Paz.ogg/Es-catalán-bo-La_Paz.ogg.mp3"
- `not_same_pronunciation`: Examples: True, True
- `note`: Examples: "Río de la Plata", "obsoleta o poco común"
- `ogg_url`: Examples: "https://upload.wikimedia.org/wikipedia/commons/transcoded/1/15/LL-Q1321_(spa)-Rodelar-Japón.wav/LL-Q1321_(spa)-Rodelar-Japón.wav.ogg", "https://commons.wikimedia.org/wiki/Special:FilePath/Es-catalán-bo-La Paz.ogg"
- `raw_tags`: Examples: ['La Paz, Bolivia'], ['La Paz, Bolivia']
- `rhymes`: Examples: "es", "es"
- `tags`: Examples: ['Colombia'], ['Colombia']
- `wav_url`: Examples: "https://commons.wikimedia.org/wiki/Special:FilePath/LL-Q1321 (spa)-Rodelar-Japón.wav", "https://commons.wikimedia.org/wiki/Special:FilePath/LL-Q1321 (spa)-AdrianAbdulBaha-catalán.wav"

### Objects within `synonyms` arrays

**Keys found in objects:**
- `alternative_spelling`: Examples: "noción", "Soga"
- `note`: Examples: "metonímico", "literario"
- `sense`: Examples: "Originario, relativo a, o propio de Japón.", "Originario, relativo a, o propio de Japón."
- `sense_index`: Examples: "1", "1"
- `word`: Examples: "japón", "nipón"

### Objects within `antonyms` arrays

**Keys found in objects:**
- `alternative_spelling`: Examples: "humillarse"
- `note`: Examples: "griego"
- `sense`: Examples: "Fin, final.", "Figuradamente, lo mejor de una cosa o lo más selecto de un grupo."
- `sense_index`: Examples: "2", "5"
- `word`: Examples: "alfa", "hez"

### Objects within `translations` arrays

**Keys found in objects:**
- `lang`: Examples: "Alemán", "Alemán"
- `lang_code`: Examples: "de", "de"
- `raw_tags`: Examples: ['tr.'], ['tr.']
- `roman`: Examples: "almāniyā", "sadīq"
- `sense`: Examples: "propio de Alemania o relativo a ella (adjetivo)", "propio de Alemania o relativo a ella (adjetivo)"
- `sense_index`: Examples: "1", "2-3"
- `tags`: Examples: ['masculine'], ['masculine']
- `word`: Examples: "japanisch", "Japanisch"

## Data Structure Pattern

Each entry in the JSONL file represents a single word/lexeme with:
1. **Basic Information**: word, language, part of speech
2. **Semantic Information**: senses (meanings), categories
3. **Morphological Information**: forms (conjugations, declensions)
4. **Phonological Information**: sounds (pronunciation)
5. **Lexical Relations**: synonyms, antonyms
6. **Translation Information**: translations to other languages
7. **Etymology**: word origins and historical information