#!/bin/bash
# Multi-Card Preview System Launcher
# Usage examples:
#   ./multi_card_preview.sh start              # Start preview server
#   ./multi_card_preview.sh sync               # Sync all card types
#   ./multi_card_preview.sh sync Conjugation   # Sync specific card type
#   ./multi_card_preview.sh list               # List card types

set -e

# Ensure we're in the right directory and environment is activated
source activate_env.sh

case "${1:-help}" in
    start)
        PORT=${2:-8001}
        echo "🚀 Starting multi-card preview server on port $PORT..."
        echo "   🔗 Main page: http://127.0.0.1:$PORT/"
        echo "   📋 Card types: http://127.0.0.1:$PORT/api/card_types"
        echo "   📝 Conjugation cards: http://127.0.0.1:$PORT/api/cards?card_type=Conjugation"
        echo "   🎨 Preview example: http://127.0.0.1:$PORT/preview?card_id=hablar_present_yo&card_type=Conjugation"
        echo ""
        exec python -m cli.preview_server_multi --port "$PORT"
        ;;
    
    sync)
        CARD_TYPE=${2:-}
        if [[ -n "$CARD_TYPE" ]]; then
            echo "🔄 Syncing card type: $CARD_TYPE"
            exec python -m cli.sync_anki_multi --card-type "$CARD_TYPE"
        else
            echo "🔄 Syncing all card types"
            exec python -m cli.sync_anki_multi
        fi
        ;;
    
    list|types)
        echo "📋 Available card types:"
        python -m cli.sync_anki_multi --list-types
        ;;
    
    test)
        echo "🧪 Testing modular card system..."
        echo "1. Testing card type registry..."
        python -c "
from utils.card_types import get_card_type_registry
registry = get_card_type_registry()
print(f'✅ Found {len(registry.list_types())} card types')
for ct in registry.list_types():
    print(f'   - {ct}')
"
        echo ""
        echo "2. Testing Conjugation cards..."
        python -c "
from utils.card_types import get_card_type_registry
from pathlib import Path
registry = get_card_type_registry()
conj = registry.get('Conjugation')
data = conj.load_data(Path('.'))
cards = conj.list_cards(data)
print(f'✅ Found {len(cards)} conjugation cards')
"
        echo ""
        echo "✅ System test completed successfully!"
        ;;
    
    help|*)
        echo "Multi-Card Preview & Sync System"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  start [port]          Start preview server (default port: 8001)"
        echo "  sync [card_type]      Sync cards to Anki (all types or specific)"
        echo "  list                  List available card types"
        echo "  test                  Test the system"
        echo "  help                  Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 start                    # Start server on port 8001"
        echo "  $0 start 8000               # Start server on port 8000"
        echo "  $0 sync                     # Sync all card types"
        echo "  $0 sync Conjugation         # Sync only Conjugation cards"
        echo "  $0 list                     # Show available card types"
        echo ""
        echo "Card Types Available:"
        echo "  - Fluent_Forever: Vocabulary cards (vocabulary.json)"
        echo "  - Conjugation: Verb conjugation cards (conjugations.json)"
        echo ""
        ;;
esac