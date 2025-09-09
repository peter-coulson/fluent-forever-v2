#!/usr/bin/env python3
"""
Documentation Context Management System

Organizes all documentation into a logical context system that serves different
audiences and maintains clear separation between operational, development, and
user documentation.
"""

from datetime import datetime
from pathlib import Path


class DocumentationManager:
    """Manage documentation organization and context system"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.context_root = self.project_root / "context"

    def organize_documentation(self) -> None:
        """Organize all documentation into context system"""
        print("🗂️  Organizing documentation into context system...")

        # Create context directory structure
        self._create_context_structure()

        # Move existing documentation to archive
        self._archive_existing_docs()

        print("✅ Documentation organization complete!")

    def _create_context_structure(self) -> None:
        """Create the context directory structure"""
        directories = [
            "user",
            "user/examples",
            "development",
            "operations",
            "reference",
            "archive",
            "archive/legacy",
        ]

        for directory in directories:
            dir_path = self.context_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: context/{directory}")

    def _archive_existing_docs(self) -> None:
        """Archive existing documentation to legacy folder"""
        existing_docs = [
            "README.md",
            "CLAUDE.md",
            "DESIGN_DECISIONS.md",
            "MULTI_CARD_SYSTEM.md",
            "QUEUE_OPTIMIZATIONS.md",
            "CLI_COMMAND_MAPPING.md",
        ]

        for doc in existing_docs:
            source_path = self.project_root / doc
            if source_path.exists():
                # Archive to legacy folder with migration header
                target_path = self.context_root / "archive" / "legacy" / f"old_{doc}"
                content = self._add_migration_header(
                    source_path.read_text(), doc, f"archive/legacy/old_{doc}"
                )
                target_path.write_text(content)
                print(f"📋 Archived {doc} → context/archive/legacy/old_{doc}")

    def _add_migration_header(self, content: str, source: str, target: str) -> str:
        """Add migration header to archived documentation"""
        header = f"""<!--
ARCHIVED DOCUMENT
Original: {source}
Archived Location: context/{target}
Archive Date: {datetime.now().isoformat()}

This document has been archived as part of the documentation reorganization.
For current documentation, see context/README.md
-->

"""
        return header + content


if __name__ == "__main__":
    # Can be run directly for testing
    manager = DocumentationManager(Path("."))
    manager.organize_documentation()
