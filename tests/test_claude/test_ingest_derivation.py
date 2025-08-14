#!/usr/bin/env python3
from cli.ingest_claude_batch import derive_fields


def test_derive_fields_generates_ids_and_media_names():
    meaning = {
        'SpanishWord': 'con',
        'MeaningID': 'instrument',
        'MeaningContext': 'using as a tool',
        'MonolingualDef': 'usar algo como herramienta',
        'ExampleSentence': 'Trabaja con un martillo.',
        'GappedSentence': 'Trabaja _____ un martillo.',
        'IPA': '[kon]',
        'prompt': 'boy with hammer'
    }
    d = derive_fields(meaning)
    assert d['CardID'] == 'con_instrument'
    assert d['ImageFile'] == 'con_instrument.png'
    assert d['WordAudio'] == '[sound:con.mp3]'
    assert d['WordAudioAlt'] == ''

