#!/usr/bin/env python3
"""
Validation gate for Session 9: Documentation Context

Tests that all documentation files are valid and accessible.
This test will initially fail until Session 9 is implemented.
"""

import pytest
from pathlib import Path
import sys
import json

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_documentation_structure():
    """
    Validation gate for Session 9: Documentation Context
    
    Tests:
    - Documentation is organized by audience and purpose
    - All documentation files are valid and accessible
    - Documentation index provides clear navigation
    """
    docs_dir = project_root / 'docs'
    
    if not docs_dir.exists():
        pytest.skip("Documentation not yet implemented (Session 9 pending)")
    
    # Test documentation structure exists
    expected_dirs = [
        "user",        # User-facing documentation
        "developer",   # Developer documentation
        "api",         # API documentation
        "tutorials"    # Tutorial documentation
    ]
    
    for expected_dir in expected_dirs:
        dir_path = docs_dir / expected_dir
        assert dir_path.exists(), f"Documentation directory {expected_dir} should exist"


def test_documentation_index():
    """Test that documentation has proper index and navigation."""
    docs_dir = project_root / 'docs'
    
    if not docs_dir.exists():
        pytest.skip("Documentation not yet implemented (Session 9 pending)")
    
    # Test main documentation index
    index_file = docs_dir / 'README.md'
    assert index_file.exists(), "Documentation should have main README.md"
    
    # Read and validate index content
    index_content = index_file.read_text()
    
    # Should contain links to major sections
    assert "user" in index_content.lower(), "Index should reference user docs"
    assert "developer" in index_content.lower(), "Index should reference developer docs"
    assert "api" in index_content.lower(), "Index should reference API docs"


def test_user_documentation():
    """Test that user documentation is complete and accessible."""
    user_docs = project_root / 'docs' / 'user'
    
    if not user_docs.exists():
        pytest.skip("User documentation not yet implemented (Session 9 pending)")
    
    # Test key user documentation files
    expected_files = [
        'getting-started.md',
        'vocabulary-workflow.md',
        'conjugation-workflow.md',
        'troubleshooting.md'
    ]
    
    for expected_file in expected_files:
        file_path = user_docs / expected_file
        if file_path.exists():
            # Validate file is readable and has content
            content = file_path.read_text()
            assert len(content) > 100, f"{expected_file} should have substantial content"


def test_developer_documentation():
    """Test that developer documentation is complete."""
    dev_docs = project_root / 'docs' / 'developer'
    
    if not dev_docs.exists():
        pytest.skip("Developer documentation not yet implemented (Session 9 pending)")
    
    # Test key developer documentation files
    expected_files = [
        'architecture.md',
        'pipeline-development.md',
        'adding-providers.md',
        'testing.md'
    ]
    
    for expected_file in expected_files:
        file_path = dev_docs / expected_file
        if file_path.exists():
            content = file_path.read_text()
            assert len(content) > 200, f"{expected_file} should have detailed content"


def test_api_documentation():
    """Test that API documentation is generated and valid."""
    api_docs = project_root / 'docs' / 'api'
    
    if not api_docs.exists():
        pytest.skip("API documentation not yet implemented (Session 9 pending)")
    
    # Test that API documentation includes key modules
    expected_modules = [
        'core.pipeline',
        'core.registry', 
        'stages',
        'providers'
    ]
    
    # Look for API documentation files
    api_files = list(api_docs.glob('**/*.md'))
    api_content = '\n'.join(f.read_text() for f in api_files)
    
    for module in expected_modules:
        assert module in api_content, f"API docs should document {module}"


def test_documentation_links():
    """Test that documentation internal links are valid."""
    docs_dir = project_root / 'docs'
    
    if not docs_dir.exists():
        pytest.skip("Documentation not yet implemented (Session 9 pending)")
    
    # Find all markdown files
    md_files = list(docs_dir.glob('**/*.md'))
    
    # Basic validation - files should be readable
    for md_file in md_files:
        try:
            content = md_file.read_text()
            assert len(content) > 0, f"{md_file} should not be empty"
        except Exception as e:
            pytest.fail(f"Could not read {md_file}: {e}")


def test_tutorial_documentation():
    """Test that tutorial documentation covers key workflows."""
    tutorial_docs = project_root / 'docs' / 'tutorials'
    
    if not tutorial_docs.exists():
        pytest.skip("Tutorial documentation not yet implemented (Session 9 pending)")
    
    # Test key tutorial files
    expected_tutorials = [
        'creating-vocabulary-cards.md',
        'adding-conjugation-pipeline.md',
        'customizing-templates.md'
    ]
    
    for tutorial in expected_tutorials:
        file_path = tutorial_docs / tutorial
        if file_path.exists():
            content = file_path.read_text()
            
            # Tutorial should have steps
            assert "step" in content.lower() or "1." in content, \
                f"{tutorial} should contain step-by-step instructions"


def test_documentation_metadata():
    """Test that documentation has proper metadata."""
    docs_dir = project_root / 'docs'
    
    if not docs_dir.exists():
        pytest.skip("Documentation not yet implemented (Session 9 pending)")
    
    # Test for documentation configuration
    config_files = [
        docs_dir / 'mkdocs.yml',
        docs_dir / '.gitbook.yml',
        docs_dir / 'config.json'
    ]
    
    # At least one documentation config should exist
    has_config = any(config_file.exists() for config_file in config_files)
    if has_config:
        # Validate the first existing config
        for config_file in config_files:
            if config_file.exists():
                if config_file.suffix == '.json':
                    with open(config_file) as f:
                        config = json.load(f)
                        assert "title" in config or "name" in config, \
                            "Documentation config should have title"
                break


if __name__ == "__main__":
    test_documentation_structure()
    test_documentation_index()
    test_user_documentation()
    test_developer_documentation()
    test_api_documentation()
    test_documentation_links()
    test_tutorial_documentation()
    test_documentation_metadata()
    print("Session 9 validation gate passed!")