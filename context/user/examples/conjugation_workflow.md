# Conjugation Workflow Example

Complete walkthrough for creating Spanish conjugation practice cards.

## Overview

This example demonstrates creating conjugation cards for Spanish verbs "hablar," "comer," and "vivir" - representing the three main conjugation patterns in Spanish.

## Prerequisites

- System installed and configured 
- Vocabulary pipeline setup complete
- Understanding of Spanish verb conjugation basics

## Step 1: Environment Setup

**→ See [Quick Start Guide](../quick_start.md) for complete setup instructions**

```bash
python -m cli.pipeline info conjugation
```

## Step 2: Verb Analysis

Analyze verbs and create conjugation pairs:
```bash
python -m cli.pipeline run conjugation --stage analyze_verbs --verbs hablar,comer,vivir
```

**Output**:
```
✅ Analyzed 3 verbs:
  - hablar (AR verb): 20 conjugations
  - comer (ER verb): 20 conjugations  
  - vivir (IR verb): 20 conjugations
📊 Total conjugation pairs: 60
```

### Advanced Filtering:
```bash
# Specific tenses and persons
python -m cli.pipeline run conjugation --stage analyze_verbs --verbs hablar --tenses present,preterite --persons yo,tú,él
```

## Step 3: Card Creation

Format conjugations into complete card data:
```bash
python -m cli.pipeline run conjugation --stage create_cards
```

## Step 4: Media Generation

Generate audio for verb pronunciations:
```bash
python -m cli.pipeline run conjugation --stage generate_media --execute
```

## Step 5: Anki Sync

Sync conjugation cards to Anki:
```bash
# Sync templates
python -m cli.pipeline run conjugation --stage sync_templates --execute

# Sync cards
python -m cli.pipeline run conjugation --stage sync_cards --execute
```

## Complete Conjugation Workflow

```bash
# Environment setup - see Quick Start Guide
python -m cli.pipeline run conjugation --stage analyze_verbs --verbs hablar,comer,vivir
python -m cli.pipeline run conjugation --stage create_cards  
python -m cli.pipeline run conjugation --stage generate_media --execute
python -m cli.pipeline run conjugation --stage sync_cards --execute
```

## Result: Practice-Ready Conjugation Cards

Cards include:
- **Verb infinitive** with audio pronunciation
- **Conjugated form** for specific tense/person
- **Example sentence** showing usage in context
- **English translation** for comprehension check

Perfect for systematic conjugation practice!