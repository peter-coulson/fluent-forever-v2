#!/usr/bin/env python3
"""
Multi-Card Type Preview Server

Extended preview server that supports multiple card types (Fluent Forever, Conjugation, etc.)
while maintaining backwards compatibility with the existing system.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, request, Response, send_from_directory

from utils.logging_config import setup_logging, ICONS
from utils.card_types import get_card_type_registry
from sync.templates_sync import load_local_templates
from utils.template_render import render_template, wrap_html


PROJECT_ROOT = Path(__file__).parents[2]


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    setup_logging()
    
    card_registry = get_card_type_registry()

    @app.get('/api/card_types')
    def list_card_types() -> Response:
        """List available card types"""
        types = []
        for type_name in card_registry.list_types():
            card_type = card_registry.get(type_name)
            if card_type:
                types.append({
                    'name': type_name,
                    'note_type': card_type.note_type,
                    'data_file': card_type.data_file
                })
        return jsonify(types)

    @app.get('/api/cards')
    def list_cards() -> Response:
        """List cards for a specific card type"""
        card_type_name = request.args.get('card_type', 'Fluent_Forever')
        
        card_type = card_registry.get(card_type_name)
        if not card_type:
            return Response(f"{ICONS['cross']} Unknown card type: {card_type_name}", status=400)
        
        try:
            # Reload data on each request to avoid caching
            data = card_type.load_data(PROJECT_ROOT)
            cards = card_type.list_cards(data)
            return jsonify({
                'card_type': card_type_name,
                'cards': cards
            })
        except NotImplementedError:
            return Response(f"{ICONS['cross']} Card type '{card_type_name}' data loading not yet implemented", status=501)
        except Exception as e:
            return Response(f"{ICONS['cross']} Error loading cards: {e}", status=500)

    @app.get('/preview')
    def preview() -> Response:
        """Preview cards with support for multiple card types"""
        # Get parameters
        card_id = request.args.get('card_id', '').strip()
        side = request.args.get('side', 'front').strip().lower()
        template_name = request.args.get('template')
        theme = request.args.get('theme', '').strip().lower()
        custom_bg = request.args.get('bg', '').strip()
        card_type_name = request.args.get('card_type', 'Fluent_Forever')
        
        # Get card type
        card_type = card_registry.get(card_type_name)
        if not card_type:
            return Response(f"{ICONS['cross']} Unknown card type: {card_type_name}", status=400)
        
        # Load templates for this card type
        tmpl_dir = PROJECT_ROOT / 'templates' / 'anki' / card_type.name
        if not tmpl_dir.exists():
            return Response(f"{ICONS['cross']} Template directory not found: {tmpl_dir}", status=404)
        
        try:
            templates_payload, css = load_local_templates(tmpl_dir)
        except Exception as e:
            return Response(f"{ICONS['cross']} Error loading templates: {e}", status=500)
        
        # Load card data
        try:
            data = card_type.load_data(PROJECT_ROOT)
            card_data = card_type.find_card_by_id(data, card_id) if card_id else None
        except NotImplementedError:
            return Response(f"{ICONS['cross']} Card type '{card_type_name}' data loading not yet implemented", status=501)
        except Exception as e:
            return Response(f"{ICONS['cross']} Error loading card data: {e}", status=500)
        
        if not card_data:
            return Response(f"{ICONS['cross']} CardID not found: {card_id}", status=404)

        # Build fields for this card type
        try:
            fields = card_type.build_fields(card_data)
        except NotImplementedError:
            return Response(f"{ICONS['cross']} Card type '{card_type_name}' field building not yet implemented", status=501)
        except Exception as e:
            return Response(f"{ICONS['cross']} Error building fields: {e}", status=500)

        # Build rendered fronts first to support {{FrontSide}}
        rendered_front_by_name: Dict[str, str] = {}
        for t in templates_payload:
            name = t['Name']
            front_src = t['Front']
            rendered_front_by_name[name] = render_template(front_src, fields)

        # Theme override CSS (e.g., dark mode)
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
                doc = wrap_html(front_html, effective_css, title=f"{card_id} • {name} • Front • {card_type_name}")
                outputs.append(doc)
            else:
                fields_with_front = dict(fields)
                fields_with_front['FrontSide'] = front_html
                back_html = render_template(t['Back'], fields_with_front)
                doc = wrap_html(back_html, effective_css, title=f"{card_id} • {name} • Back • {card_type_name}")
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
        card_types = card_registry.list_types()
        types_html = ', '.join([f'<code>{ct}</code>' for ct in card_types])
        
        return Response(f'''
            <h2>Multi-Card Type Preview Server</h2>
            <p>Available card types: {types_html}</p>
            <h3>Examples:</h3>
            <ul>
                <li><a href="/preview?card_id=lo_neuter_article&card_type=Fluent_Forever">Fluent Forever Card</a></li>
                <li><a href="/preview?card_id=hablar_present_yo&card_type=Conjugation">Conjugation Card</a></li>
                <li><a href="/api/cards?card_type=Fluent_Forever">List Fluent Forever Cards</a></li>
                <li><a href="/api/cards?card_type=Conjugation">List Conjugation Cards</a></li>
            </ul>
            <p>URL Parameters:</p>
            <ul>
                <li><code>card_id</code> - The card ID to preview</li>
                <li><code>card_type</code> - Card type (default: Fluent_Forever)</li>
                <li><code>side</code> - front or back (default: front)</li>
                <li><code>template</code> - Specific template name (optional)</li>
            </ul>
        ''', mimetype='text/html')

    return app


def main() -> int:
    parser = argparse.ArgumentParser(description='Run multi-card type preview server for Anki templates')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=True, use_reloader=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())