#!/usr/bin/env python3
"""
Universal Pipeline Runner

Provides consistent CLI interface for all pipeline operations.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from core.registry import get_pipeline_registry
from core.context import PipelineContext
from core.exceptions import PipelineError
from utils.logging_config import setup_logging, ICONS


def create_base_parser() -> argparse.ArgumentParser:
    """Create base argument parser."""
    parser = argparse.ArgumentParser(
        description='Universal pipeline runner for card creation workflows'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available pipelines')
    
    # Info command  
    info_parser = subparsers.add_parser('info', help='Show pipeline information')
    info_parser.add_argument('pipeline', help='Pipeline name')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run pipeline stage')
    run_parser.add_argument('pipeline', help='Pipeline name')
    run_parser.add_argument('--stage', required=True, help='Stage to execute')
    run_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    run_parser.add_argument('--config', help='Override config file')
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    setup_logging()
    logger = setup_logging().getChild('cli.pipeline_runner')
    
    parser = create_base_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    registry = get_pipeline_registry()
    project_root = Path(__file__).parents[2]
    
    try:
        if args.command == 'list':
            return cmd_list(registry)
        elif args.command == 'info':
            return cmd_info(registry, args.pipeline)
        elif args.command == 'run':
            return cmd_run(registry, args.pipeline, args.stage, project_root, args)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
            
    except PipelineError as e:
        logger.error(f"{ICONS['cross']} {e}")
        return 1
    except Exception as e:
        logger.error(f"{ICONS['cross']} Unexpected error: {e}")
        return 1


def cmd_list(registry) -> int:
    """List available pipelines."""
    pipelines = registry.list_pipelines()
    
    if not pipelines:
        print("No pipelines registered.")
        return 0
    
    print("Available pipelines:")
    for pipeline_name in pipelines:
        try:
            info = registry.get_pipeline_info(pipeline_name)
            print(f"  {pipeline_name}: {info.get('description', 'No description')}")
        except Exception as e:
            print(f"  {pipeline_name}: Error getting info - {e}")
    
    return 0


def cmd_info(registry, pipeline_name: str) -> int:
    """Show pipeline information."""
    try:
        info = registry.get_pipeline_info(pipeline_name)
        
        print(f"Pipeline: {info['name']}")
        print(f"Display Name: {info['display_name']}")
        print(f"Description: {info['description']}")
        print(f"Data File: {info['data_file']}")
        print(f"Anki Note Type: {info['anki_note_type']}")
        print(f"Stages: {', '.join(info['stages'])}")
        
        return 0
    except PipelineError as e:
        print(f"Error: {e}")
        return 1


def cmd_run(registry, pipeline_name: str, stage_name: str, 
           project_root: Path, args) -> int:
    """Run pipeline stage."""
    try:
        pipeline = registry.get(pipeline_name)
        
        # Create context
        context = PipelineContext(
            pipeline_name=pipeline_name,
            project_root=project_root,
            args=vars(args)
        )
        
        if args.dry_run:
            print(f"Would execute stage '{stage_name}' on pipeline '{pipeline_name}'")
            return 0
        
        # Execute stage
        result = pipeline.execute_stage(stage_name, context)
        
        print(f"Stage '{stage_name}' completed with status: {result.status.value}")
        print(f"Message: {result.message}")
        
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")
                
        return 0 if result.status.value in ['success', 'partial'] else 1
        
    except PipelineError as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    raise SystemExit(main())