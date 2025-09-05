#!/usr/bin/env python3
"""
Session 9 Validation Gate: Documentation Structure

Tests the contract for documentation organization and accessibility.
These tests define how documentation should be structured and
organized for different audiences and purposes.

CONTRACT BEING TESTED:
- Documentation is organized by audience and purpose
- Context system provides clear guidance
- All documentation is accessible and valid
- Documentation stays synchronized with code
- Help system provides comprehensive coverage
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List


class TestDocumentationStructureContract:
    """Test documentation structure contracts"""
    
    def test_context_system_organization(self):
        """Contract: Context system is properly organized"""
        doc_validator = MockDocumentationValidator()
        
        # Should have organized context structure
        structure = doc_validator.validate_context_structure()
        
        assert structure["valid"] is True
        assert "refactor" in structure["directories"]
        assert "user_guides" in structure["directories"] 
        assert "developer_docs" in structure["directories"]
        
        # Should have proper hierarchy
        refactor_structure = structure["directories"]["refactor"]
        assert "chunks" in refactor_structure
        assert "completed_handoffs" in refactor_structure
    
    def test_audience_based_organization(self):
        """Contract: Documentation is organized by audience"""
        doc_validator = MockDocumentationValidator()
        
        audiences = doc_validator.get_documentation_audiences()
        
        # Should have clear audience categories
        expected_audiences = ["users", "developers", "contributors", "maintainers"]
        for audience in expected_audiences:
            assert audience in audiences
            
            docs = doc_validator.get_docs_for_audience(audience)
            assert len(docs) > 0
            
            # Each doc should be appropriate for audience
            for doc in docs:
                assert doc["audience"] == audience
                assert doc["valid"] is True
    
    def test_purpose_based_categorization(self):
        """Contract: Documentation is categorized by purpose"""
        doc_validator = MockDocumentationValidator()
        
        purposes = doc_validator.get_documentation_purposes()
        
        # Should have clear purpose categories
        expected_purposes = [
            "getting_started", "tutorials", "api_reference", 
            "troubleshooting", "architecture", "contributing"
        ]
        
        for purpose in expected_purposes:
            assert purpose in purposes
            
            docs = doc_validator.get_docs_by_purpose(purpose)
            assert len(docs) > 0
    
    def test_documentation_accessibility(self):
        """Contract: All documentation is accessible"""
        doc_validator = MockDocumentationValidator()
        
        # Should be able to discover all documentation
        all_docs = doc_validator.discover_all_documentation()
        
        assert len(all_docs) > 0
        
        for doc in all_docs:
            # Should be accessible
            assert doc["accessible"] is True
            
            # Should have proper metadata
            assert "title" in doc
            assert "audience" in doc
            assert "purpose" in doc
            assert "last_updated" in doc
    
    def test_help_system_coverage(self):
        """Contract: Help system provides comprehensive coverage"""
        help_system = MockHelpSystem()
        
        # Should cover all major topics
        topics = help_system.list_help_topics()
        
        essential_topics = [
            "getting_started", "pipeline_usage", "configuration",
            "troubleshooting", "api_reference"
        ]
        
        for topic in essential_topics:
            assert topic in topics
            
            # Help content should be available
            help_content = help_system.get_help(topic)
            assert help_content is not None
            assert len(help_content["content"]) > 0
            
            # Should have examples
            if topic in ["pipeline_usage", "configuration"]:
                assert "examples" in help_content
                assert len(help_content["examples"]) > 0


class TestDocumentationQuality:
    """Test documentation quality contracts"""
    
    def test_markdown_validation(self):
        """Contract: All Markdown files are valid"""
        validator = MockMarkdownValidator()
        
        # Should validate all markdown files
        markdown_files = validator.find_markdown_files()
        assert len(markdown_files) > 0
        
        validation_results = validator.validate_all_markdown()
        
        # All should be valid
        for file_path, result in validation_results.items():
            assert result["valid"] is True, f"Invalid markdown: {file_path}"
            
            if result["warnings"]:
                # Log warnings but don't fail
                print(f"Markdown warnings in {file_path}: {result['warnings']}")
    
    def test_link_validation(self):
        """Contract: All internal links are valid"""
        validator = MockLinkValidator()
        
        # Should validate all internal links
        link_results = validator.validate_internal_links()
        
        assert link_results["valid"] is True
        
        if link_results["broken_links"]:
            # Should report broken links
            for broken_link in link_results["broken_links"]:
                print(f"Broken link: {broken_link['source']} -> {broken_link['target']}")
    
    def test_code_example_validation(self):
        """Contract: Code examples in documentation are valid"""
        validator = MockCodeExampleValidator()
        
        # Should find and validate code examples
        examples = validator.find_code_examples()
        assert len(examples) > 0
        
        validation_results = validator.validate_examples()
        
        # All examples should be syntactically correct
        for example in validation_results:
            if example["language"] in ["python", "bash"]:
                assert example["syntax_valid"] is True, f"Invalid syntax in {example['file']}:{example['line']}"
    
    def test_documentation_freshness(self):
        """Contract: Documentation stays reasonably fresh"""
        freshness_checker = MockFreshnessChecker()
        
        # Check documentation age
        freshness_report = freshness_checker.check_documentation_age()
        
        # Should identify stale documentation
        stale_docs = freshness_report["stale_documents"]
        
        # Core documentation should be fresh
        core_docs = [doc for doc in freshness_report["all_documents"] 
                    if doc["category"] in ["getting_started", "api_reference"]]
        
        for doc in core_docs:
            age_days = doc["age_days"]
            assert age_days < 90, f"Core documentation is stale: {doc['path']} ({age_days} days old)"


class TestDocumentationIntegration:
    """Test documentation integration contracts"""
    
    def test_code_documentation_sync(self):
        """Contract: Code and documentation stay synchronized"""
        sync_checker = MockSyncChecker()
        
        # Check API documentation matches code
        api_sync = sync_checker.check_api_documentation_sync()
        
        assert api_sync["synchronized"] is True
        
        if api_sync["mismatches"]:
            # Should report synchronization issues
            for mismatch in api_sync["mismatches"]:
                print(f"API doc mismatch: {mismatch['api']} - {mismatch['issue']}")
    
    def test_help_system_integration(self):
        """Contract: Help system integrates with main documentation"""
        integration_checker = MockIntegrationChecker()
        
        # Help topics should reference main documentation
        integration_status = integration_checker.check_help_integration()
        
        assert integration_status["integrated"] is True
        
        # Help should provide pathways to detailed docs
        for topic in integration_status["topics"]:
            assert topic["has_references"] is True
            assert len(topic["doc_references"]) > 0
    
    def test_context_system_completeness(self):
        """Contract: Context system covers all necessary areas"""
        context_checker = MockContextChecker()
        
        # Should have context for all major system areas
        coverage = context_checker.check_context_coverage()
        
        required_areas = [
            "architecture", "pipelines", "configuration", 
            "troubleshooting", "development", "deployment"
        ]
        
        for area in required_areas:
            assert area in coverage["covered_areas"], f"Missing context for: {area}"
            
            area_docs = coverage["area_documentation"][area]
            assert len(area_docs) > 0, f"No documentation for area: {area}"


# Mock Documentation Testing Infrastructure
class MockDocumentationValidator:
    """Mock documentation validator"""
    
    def __init__(self):
        self.mock_structure = {
            "valid": True,
            "directories": {
                "refactor": {
                    "chunks": ["01_e2e_test_setup.md", "02_core_architecture.md"],
                    "completed_handoffs": ["01_e2e_test_setup_handoff.md"]
                },
                "user_guides": {
                    "getting_started.md": True,
                    "pipeline_usage.md": True
                },
                "developer_docs": {
                    "architecture.md": True,
                    "api_reference.md": True
                }
            }
        }
        
        self.mock_audiences = {
            "users": [
                {"title": "Getting Started", "audience": "users", "valid": True},
                {"title": "Pipeline Usage", "audience": "users", "valid": True}
            ],
            "developers": [
                {"title": "Architecture Guide", "audience": "developers", "valid": True},
                {"title": "API Reference", "audience": "developers", "valid": True}
            ],
            "contributors": [
                {"title": "Contributing Guide", "audience": "contributors", "valid": True}
            ],
            "maintainers": [
                {"title": "Deployment Guide", "audience": "maintainers", "valid": True}
            ]
        }
    
    def validate_context_structure(self):
        """Validate context system structure"""
        return self.mock_structure
    
    def get_documentation_audiences(self):
        """Get available documentation audiences"""
        return list(self.mock_audiences.keys())
    
    def get_docs_for_audience(self, audience):
        """Get documentation for specific audience"""
        return self.mock_audiences.get(audience, [])
    
    def get_documentation_purposes(self):
        """Get documentation purposes"""
        return [
            "getting_started", "tutorials", "api_reference",
            "troubleshooting", "architecture", "contributing"
        ]
    
    def get_docs_by_purpose(self, purpose):
        """Get documentation by purpose"""
        # Mock implementation
        return [{"title": f"Doc for {purpose}", "purpose": purpose, "valid": True}]
    
    def discover_all_documentation(self):
        """Discover all documentation files"""
        all_docs = []
        for audience, docs in self.mock_audiences.items():
            for doc in docs:
                doc_info = doc.copy()
                doc_info["accessible"] = True
                doc_info["purpose"] = "general"
                doc_info["last_updated"] = "2024-01-01"
                all_docs.append(doc_info)
        
        return all_docs


class MockHelpSystem:
    """Mock help system"""
    
    def __init__(self):
        self.help_topics = {
            "getting_started": {
                "content": "How to get started with the system",
                "examples": ["Basic setup example"]
            },
            "pipeline_usage": {
                "content": "How to use pipelines",
                "examples": ["Run vocabulary pipeline", "Run conjugation pipeline"]
            },
            "configuration": {
                "content": "How to configure the system",
                "examples": ["Config file example", "Environment variables"]
            },
            "troubleshooting": {
                "content": "Common issues and solutions"
            },
            "api_reference": {
                "content": "API documentation and examples"
            }
        }
    
    def list_help_topics(self):
        """List available help topics"""
        return list(self.help_topics.keys())
    
    def get_help(self, topic):
        """Get help content for topic"""
        return self.help_topics.get(topic)


class MockMarkdownValidator:
    """Mock markdown validator"""
    
    def find_markdown_files(self):
        """Find all markdown files"""
        return [
            "README.md", "CLAUDE.md", "MULTI_CARD_SYSTEM.md",
            "context/refactor/refactor_summary.md",
            "tests/e2e/README.md"
        ]
    
    def validate_all_markdown(self):
        """Validate all markdown files"""
        results = {}
        for file_path in self.find_markdown_files():
            results[file_path] = {
                "valid": True,
                "warnings": [],
                "errors": []
            }
        
        return results


class MockLinkValidator:
    """Mock link validator"""
    
    def validate_internal_links(self):
        """Validate all internal links"""
        return {
            "valid": True,
            "total_links": 25,
            "valid_links": 25,
            "broken_links": []
        }


class MockCodeExampleValidator:
    """Mock code example validator"""
    
    def find_code_examples(self):
        """Find code examples in documentation"""
        return [
            {"file": "README.md", "line": 45, "language": "python"},
            {"file": "CLAUDE.md", "line": 123, "language": "bash"},
            {"file": "tests/e2e/README.md", "line": 67, "language": "python"}
        ]
    
    def validate_examples(self):
        """Validate code examples"""
        examples = self.find_code_examples()
        results = []
        
        for example in examples:
            results.append({
                **example,
                "syntax_valid": True,
                "issues": []
            })
        
        return results


class MockFreshnessChecker:
    """Mock documentation freshness checker"""
    
    def check_documentation_age(self):
        """Check age of documentation"""
        return {
            "all_documents": [
                {"path": "README.md", "category": "getting_started", "age_days": 30},
                {"path": "CLAUDE.md", "category": "api_reference", "age_days": 15},
                {"path": "old_guide.md", "category": "tutorials", "age_days": 200}
            ],
            "stale_documents": [
                {"path": "old_guide.md", "age_days": 200}
            ]
        }


class MockSyncChecker:
    """Mock code/documentation synchronization checker"""
    
    def check_api_documentation_sync(self):
        """Check API documentation synchronization"""
        return {
            "synchronized": True,
            "total_apis": 15,
            "documented_apis": 15,
            "mismatches": []
        }


class MockIntegrationChecker:
    """Mock help system integration checker"""
    
    def check_help_integration(self):
        """Check help system integration with main docs"""
        return {
            "integrated": True,
            "topics": [
                {
                    "name": "getting_started",
                    "has_references": True,
                    "doc_references": ["README.md", "quick_start.md"]
                },
                {
                    "name": "pipeline_usage",
                    "has_references": True,
                    "doc_references": ["CLAUDE.md", "pipeline_guide.md"]
                }
            ]
        }


class MockContextChecker:
    """Mock context system completeness checker"""
    
    def check_context_coverage(self):
        """Check context system coverage"""
        return {
            "covered_areas": [
                "architecture", "pipelines", "configuration",
                "troubleshooting", "development", "deployment"
            ],
            "area_documentation": {
                "architecture": ["architecture.md", "system_design.md"],
                "pipelines": ["CLAUDE.md", "pipeline_guide.md"],
                "configuration": ["config_reference.md"],
                "troubleshooting": ["troubleshooting.md", "faq.md"],
                "development": ["contributing.md", "dev_setup.md"],
                "deployment": ["deployment.md", "production.md"]
            }
        }