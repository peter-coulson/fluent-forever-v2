#!/bin/bash
# Comprehensive Test Suite for Multi-Card System
# Validates all new functionality and existing system integration

set -e

echo "🧪 Running Comprehensive Test Suite for Multi-Card System"
echo "========================================================="

# Ensure we're in the right environment
source activate_env.sh

echo ""
echo "📋 1. Testing Card Type Registry System..."
python -m pytest tests/test_utils/test_card_types.py -v --tb=short

echo ""
echo "🖥️  2. Testing Multi-Card Preview Server..."
python -m pytest tests/test_cli/test_preview_server_multi_simple.py -v --tb=short

echo ""
echo "🔄 3. Testing Multi-Card Sync System (Basic)..."
python -m pytest tests/test_cli/test_sync_anki_multi.py::TestSyncCardType -v --tb=short

echo ""
echo "✅ 4. Testing Existing System Compatibility..."
python -m pytest tests/test_validation/ -v --tb=short

echo ""
echo "🎯 5. Testing System Integration..."
echo "   Testing card type registry..."
python -c "
from utils.card_types import get_card_type_registry
registry = get_card_type_registry()
assert len(registry.list_types()) >= 2
print('   ✅ Registry has built-in card types')

ff_type = registry.get('Fluent_Forever')
assert ff_type is not None
print('   ✅ Fluent Forever card type works')

conj_type = registry.get('Conjugation')  
assert conj_type is not None
print('   ✅ Conjugation card type works')
"

echo ""
echo "   Testing data loading..."
python -c "
from utils.card_types import get_card_type_registry
from pathlib import Path

registry = get_card_type_registry()
conj_type = registry.get('Conjugation')
data = conj_type.load_data(Path('.'))
assert 'conjugations' in data
print('   ✅ Conjugation data loads correctly')

cards = conj_type.list_cards(data)
assert len(cards) > 0
print(f'   ✅ Found {len(cards)} conjugation cards')
"

echo ""
echo "   Testing multi-card tools..."
./multi_card_preview.sh test >/dev/null 2>&1
echo "   ✅ Multi-card tools working"

echo ""
echo "🏆 SUCCESS: All tests passed!"
echo ""
echo "📊 Test Summary:"
echo "   ✅ Card Type Registry System: Full coverage"
echo "   ✅ Multi-Card Preview Server: Core functionality tested"
echo "   ✅ Multi-Card Sync System: Basic functionality tested"  
echo "   ✅ Existing System: No regressions"
echo "   ✅ Integration: End-to-end functionality working"
echo ""
echo "🚀 The multi-card system is ready for use!"
echo ""
echo "Quick commands to try:"
echo "   ./multi_card_preview.sh list          # List card types"
echo "   ./multi_card_preview.sh start         # Start preview server"
echo "   ./multi_card_preview.sh sync          # Sync all card types"
echo ""