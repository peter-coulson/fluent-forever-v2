#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, request, Response, send_from_directory

from utils.logging_config import setup_logging, ICONS
from sync.templates_sync import load_local_templates
from utils.template_render import (
    load_vocab,
    find_meaning_by_cardid,
    build_fields_from_meaning,
    render_template,
    wrap_html,
)


PROJECT_ROOT = Path(__file__).parents[2]


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    setup_logging()

    note_type_folder = 'Fluent_Forever'
    tmpl_dir = PROJECT_ROOT / 'templates' / 'anki' / note_type_folder
    templates_payload, css = load_local_templates(tmpl_dir)
    vocab_path = PROJECT_ROOT / 'vocabulary.json'
    vocab = load_vocab(vocab_path)

    @app.get('/api/cards')
    def list_cards() -> Response:
        cards: List[Dict[str, str]] = []
        for _, wdata in vocab.get('words', {}).items():
            for m in wdata.get('meanings', []):
                cards.append({
                    'CardID': m.get('CardID', ''),
                    'SpanishWord': m.get('SpanishWord', ''),
                    'MeaningID': m.get('MeaningID', ''),
                    'MeaningContext': m.get('MeaningContext', ''),
                })
        return jsonify(cards)

    @app.get('/preview')
    def preview() -> Response:
        card_id = request.args.get('card_id', '').strip()
        side = request.args.get('side', 'front').strip().lower()
        template_name = request.args.get('template')
        theme = request.args.get('theme', '').strip().lower()
        custom_bg = request.args.get('bg', '').strip()

        meaning = find_meaning_by_cardid(vocab, card_id) if card_id else None
        if not meaning:
            return Response(f"{ICONS['cross']} CardID not found: {card_id}", status=404)

        fields = build_fields_from_meaning(meaning)

        # Build rendered fronts first to support {{FrontSide}}
        rendered_front_by_name: Dict[str, str] = {}
        for t in templates_payload:
            name = t['Name']
            front_src = t['Front']
            rendered_front_by_name[name] = render_template(front_src, fields)

        # Theme override CSS (e.g., dark mode). Assumed dark bg: rgb(37, 150, 190)
        effective_css = css
        if custom_bg or theme == 'dark':
            card_bg = custom_bg if custom_bg else 'rgb(37, 150, 190)'
            override = (
                f"\n/* Preview theme override */\n"
                f".card {{ background: {card_bg} !important; color: #ffffff; }}\n"
                f"body {{ background: #0f0f0f; }}\n"
                f"hr#answer {{ background: linear-gradient(to right, rgba(255,255,255,0), rgba(255,255,255,.6), rgba(255,255,255,0)); }}\n"
            )
            effective_css = css + override

        outputs: List[str] = []
        for t in templates_payload:
            name = t['Name']
            if template_name and name != template_name:
                continue
            front_html = rendered_front_by_name[name]
            if side == 'front':
                doc = wrap_html(front_html, effective_css, title=f"{card_id} • {name} • Front")
                outputs.append(doc)
            else:
                fields_with_front = dict(fields)
                fields_with_front['FrontSide'] = front_html
                back_html = render_template(t['Back'], fields_with_front)
                doc = wrap_html(back_html, effective_css, title=f"{card_id} • {name} • Back")
                outputs.append(doc)

        return Response("\n\n<!-- ========== NEXT TEMPLATE ========== -->\n\n".join(outputs), mimetype='text/html')

    # Serve media from repo so previews render
    @app.get('/media/images/<path:filename>')
    def media_images(filename: str):
        return send_from_directory(PROJECT_ROOT / 'media' / 'images', filename, conditional=True)

    @app.get('/media/audio/<path:filename>')
    def media_audio(filename: str):
        return send_from_directory(PROJECT_ROOT / 'media' / 'audio', filename, conditional=True)

    @app.get('/')
    def root() -> Response:
        return Response(
            '<p>Preview server running. Try: <code>/preview?card_id=lo_neuter_article</code></p>',
            mimetype='text/html'
        )

    return app


def main() -> int:
    parser = argparse.ArgumentParser(description='Run local preview server for Anki templates')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=True, use_reloader=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


