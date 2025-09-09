# Troubleshooting Guide

Common issues and solutions for Fluent Forever V2.

## 🚨 Critical Setup Issues

### Environment Not Activated
**Problem**: `ModuleNotFoundError: No module named 'cli'`

**Solution**: Always run activation script first - see [Quick Start Guide](quick_start.md#installation)

**Why**: The activation script sets up virtual environment and PYTHONPATH correctly.

### Anki Connection Failed
**Problem**: `Could not connect to Anki`

**Solutions**:
1. **Start Anki** and ensure AnkiConnect addon is installed
2. **Check Anki URL** in configuration
3. **Verify AnkiConnect addon** is enabled

```bash
# Test Anki connection
python -m cli.pipeline run vocabulary --stage sync_templates --dry-run
```

### API Keys Not Working
**Problem**: `Invalid API key` or `Authentication failed`

**Solutions**:
1. **Check .env file** exists and has correct format:
   ```bash
   cat .env
   # Should show:
   # OPENAI_API_KEY=sk-...
   # FORVO_API_KEY=...
   ```

2. **Verify key format** - no extra spaces or quotes
3. **Test API access** directly

## 🔧 Pipeline Issues

### Word Analysis Problems

#### Claude Batch Files Not Found
**Problem**: `FileNotFoundError: staging/claude_batch_*.json`

**Solutions**:
1. **Run prepare_batch first** - see [CLI Reference](../reference/cli_reference.md#vocabulary-pipeline)
2. **Check staging directory** exists and has files

#### IPA Validation Failures
**Problem**: `IPA validation failed for word 'trabajo'`

**Solutions**:
1. **Check IPA format** - use syllable markers: `[tra.βa.xo]`
2. **Skip validation** if certain IPA is correct:
   ```bash
   python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/file.json --skip-ipa-validation
   ```

3. **Verify Mexican Spanish dictionary** is available

### Media Generation Issues

#### Image Generation Fails
**Problem**: `OpenAI API error` or `Image generation failed`

**Solutions**:
1. **Check API limits** and quotas
2. **Verify prompts** don't violate OpenAI policies:
   - No violence or NSFW content
   - Clear, specific descriptions
   - Studio Ghibli style appropriate

3. **Test with simpler prompts** first
4. **Use --no-images** flag to skip image generation:
   ```bash
   python -m cli.pipeline run vocabulary --stage generate_media --execute --no-images
   ```

#### Audio Generation Fails
**Problem**: `Forvo API error` or `No audio found`

**Solutions**:
1. **Check Forvo API key** and limits
2. **Try different country preferences** in configuration
3. **Use --no-audio** flag to skip:
   ```bash
   python -m cli.pipeline run vocabulary --stage generate_media --execute --no-audio
   ```

## 📊 Diagnostic Commands

### System Health Check

**→ See [CLI Reference](../reference/cli_reference.md) for complete command list**

Key diagnostic commands:
- Check pipeline availability: `python -m cli.pipeline list`
- Test Anki connection: `python -m cli.pipeline run vocabulary --stage sync_templates --dry-run`
- Validate configuration: `python -m cli.pipeline info vocabulary`

## 🆘 Emergency Recovery

### Complete System Reset
If all else fails, reset to clean state:

```bash
# Backup important data
cp vocabulary.json vocabulary_backup.json
cp conjugations.json conjugations_backup.json

# Clean generated files
rm -rf media/images/* media/audio/*
rm -rf staging/*
rm -rf logs/*

# Reset configuration
cp config/core.json.example config/core.json

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Test basic functionality
source activate_env.sh
python -m cli.pipeline list
```

## 📞 Getting Additional Help

### Information to Include in Bug Reports
- **Exact command** that failed
- **Complete error message**
- **System environment** (OS, Python version)
- **Configuration details** (anonymized)
- **Log excerpts** showing the issue

---

Most issues can be resolved by following the activation script requirement and checking API connectivity!
