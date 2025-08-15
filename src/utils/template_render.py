#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Dict


def load_vocab(vocab_path: Path) -> Dict:
    return json.loads(vocab_path.read_text(encoding='utf-8'))


def build_fields_from_meaning(meaning: Dict[str, str]) -> Dict[str, str]:
    fields = {k: ('' if v is None else str(v)) for k, v in meaning.items()}

    img = fields.get('ImageFile', '').strip()
    if img and '/' not in img and not img.startswith('media/images/'):
        fields['ImageFile'] = f"media/images/{img}"

    def sound_to_audio_tag(value: str) -> str:
        m = re.match(r"\[sound:(.+?)\]", value.strip())
        if not m:
            return html.escape(value)
        fname = m.group(1)
        src = f"media/audio/{fname}" if '/' not in fname else fname
        return f'<audio controls preload="none" src="{html.escape(src)}"></audio>'

    if fields.get('WordAudio'):
        fields['WordAudio'] = sound_to_audio_tag(fields['WordAudio'])
    if fields.get('WordAudioAlt'):
        fields['WordAudioAlt'] = sound_to_audio_tag(fields['WordAudioAlt'])

    return fields


def render_template(template: str, fields: Dict[str, str]) -> str:
    section_pattern = re.compile(r"{{#(\w+)}}([\s\S]*?){{/\1}}")

    def replace_section(match: re.Match[str]) -> str:
        key = match.group(1)
        body = match.group(2)
        val = fields.get(key, '').strip()
        return body if val else ''

    out = section_pattern.sub(replace_section, template)

    def replace_field(m: re.Match[str]) -> str:
        key = m.group(1)
        return fields.get(key, '')

    out = re.sub(r"{{(\w+)}}", replace_field, out)
    return out


def wrap_html(doc_body: str, css: str, title: str) -> str:
    # Wrap in a .card container to mimic how Anki applies base styles
    wrapped = f'<div class="card">\n{doc_body}\n</div>'
    anki_base_css = (
        "/* Minimal Anki-like base styling for preview */\n"
        "html, body {\n"
        "  margin: 0;\n"
        "  padding: 0;\n"
        "  background: #ffffff; /* full-page background */\n"
        "}\n"
        ".card {\n"
        "  font-family: Arial, Helvetica, sans-serif;\n"
        "  font-size: 20px;\n"
        "  color: #ffffff;\n"
        "  background: rgb(44, 44, 44) !important; /* approximate Anki dark mode card background */\n"
        "  text-align: center;\n"
        "  line-height: 1.4;\n"
        "  max-width: 720px;\n"
        "  margin: 48px auto;\n"
        "  padding: 24px;\n"
        "  border-radius: 8px;\n"
        "  box-shadow: 0 0 0 1px rgba(255,255,255,0.08) inset;\n"
        "}\n"
        "hr#answer {\n"
        "  border: 0;\n"
        "  height: 1px;\n"
        "  width: 80%;\n"
        "  margin: 24px auto;\n"
        "  background: linear-gradient(to right, rgba(255,255,255,0), rgba(255,255,255,0.55), rgba(255,255,255,0));\n"
        "}\n"
    )
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"es\">\n"
        "<head>\n"
        f"  <meta charset=\"utf-8\">\n  <title>{html.escape(title)}</title>\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "  <style>\n" + anki_base_css + "\n" + css + "\n  </style>\n"
        "</head>\n"
        "<body>\n"
        + wrapped +
        "\n</body>\n</html>\n"
    )


def find_meaning_by_cardid(vocab: Dict, card_id: str) -> Dict[str, str] | None:
    for _, wdata in vocab.get('words', {}).items():
        for m in wdata.get('meanings', []):
            if str(m.get('CardID', '')).strip() == card_id:
                return m
    return None


