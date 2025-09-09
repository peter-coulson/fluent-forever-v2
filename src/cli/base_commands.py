"""Base command classes for CLI framework."""

import argparse
from abc import ABC, abstractmethod
from pathlib import Path

from src.core.context import PipelineContext
from src.core.registry import PipelineRegistry


class BaseCommand(ABC):
    """Base class for CLI commands."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name."""
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Command help text."""
        pass

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments to parser."""
        pass

    @abstractmethod
    def execute(self, args: argparse.Namespace, registry: PipelineRegistry) -> int:
        """Execute the command. Return exit code."""
        pass

    def create_context(
        self, pipeline_name: str, project_root: Path, args: argparse.Namespace
    ) -> PipelineContext:
        """Create pipeline context from command arguments."""
        args_dict = vars(args) if args else {}
        return PipelineContext(
            pipeline_name=pipeline_name, project_root=project_root, args=args_dict
        )
