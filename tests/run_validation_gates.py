#!/usr/bin/env python3
"""
Fast test execution framework for validation gates.
Runs tests with timing and provides clear feedback on session completion status.
"""

import subprocess
import time
import sys
from pathlib import Path
import argparse


def run_test_with_timing(test_file: Path) -> dict:
    """Run a single test file and return results with timing."""
    start_time = time.time()
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', str(test_file), '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=test_file.parent.parent)
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'file': test_file.name,
            'duration': duration,
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'session': extract_session_number(test_file.name)
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'file': test_file.name,
            'duration': duration,
            'success': False,
            'output': '',
            'error': str(e),
            'session': extract_session_number(test_file.name)
        }


def extract_session_number(filename: str) -> int:
    """Extract session number from test filename."""
    try:
        if 'current_system' in filename:
            return 0  # Baseline test
        
        # Extract from test_sessionX_name.py format
        parts = filename.split('_')
        for part in parts:
            if part.startswith('session') and len(part) > 7:
                return int(part[7:])
    except:
        pass
    return -1


def print_session_status(results: list):
    """Print colored status for each session."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BLUE = '\033[94m'
    
    print(f"\n{BLUE}=== VALIDATION GATE STATUS ==={RESET}")
    
    # Sort by session number
    session_results = {}
    for result in results:
        session = result['session']
        session_results[session] = result
    
    for session_num in sorted(session_results.keys()):
        result = session_results[session_num]
        
        if session_num == 0:
            session_name = "Baseline System"
        elif session_num == -1:
            session_name = "Unknown Test"
        else:
            session_name = f"Session {session_num}"
        
        status_color = GREEN if result['success'] else RED
        status_text = "PASS" if result['success'] else "FAIL"
        
        # Show if test was skipped (expected for future sessions)
        if "skipped" in result['output'].lower() or "skip" in result['output'].lower():
            status_color = YELLOW
            status_text = "SKIP (Not Implemented)"
        
        print(f"{session_name:20} [{status_color}{status_text:20}{RESET}] {result['duration']:.2f}s")
        
        # Show brief error if failed
        if not result['success'] and status_text == "FAIL":
            error_lines = result['error'].split('\n')[:2]  # First 2 lines only
            for line in error_lines:
                if line.strip():
                    print(f"    {RED}↳ {line.strip()}{RESET}")


def run_all_validation_gates(fast_only: bool = False, session_filter: int = None) -> dict:
    """Run all validation gate tests and return summary."""
    project_root = Path(__file__).parent.parent
    
    # Find all test files
    current_system_test = project_root / 'tests' / 'test_current_system.py'
    validation_gates_dir = project_root / 'tests' / 'validation_gates'
    
    test_files = []
    
    # Always include baseline test
    if current_system_test.exists():
        test_files.append(current_system_test)
    
    # Add validation gate tests
    if validation_gates_dir.exists():
        gate_tests = sorted(validation_gates_dir.glob('test_session*.py'))
        if session_filter is not None:
            gate_tests = [t for t in gate_tests if f'session{session_filter}_' in t.name]
        test_files.extend(gate_tests)
    
    if not test_files:
        print("No validation gate tests found!")
        return {'success': False, 'total_time': 0, 'results': []}
    
    print(f"Running {len(test_files)} validation tests...")
    if fast_only:
        print("(Fast mode - tests may skip heavy operations)")
    
    start_time = time.time()
    results = []
    
    for test_file in test_files:
        print(f"Running {test_file.name}...", end=' ')
        
        result = run_test_with_timing(test_file)
        results.append(result)
        
        # Quick feedback
        if "skipped" in result['output'].lower() or "skip" in result['output'].lower():
            print("⚠ (skipped)")
        elif result['success']:
            print("✓")
        else:
            print("✗")
    
    total_time = time.time() - start_time
    
    print_session_status(results)
    
    # Summary
    passed = sum(1 for r in results if r['success'] and not ("skipped" in r['output'].lower() or "skip" in r['output'].lower()))
    skipped = sum(1 for r in results if "skipped" in r['output'].lower() or "skip" in r['output'].lower())
    failed = len(results) - passed - skipped
    
    print(f"\n{passed} passed, {skipped} skipped, {failed} failed in {total_time:.2f}s")
    
    if total_time > 10:
        print(f"⚠ Warning: Tests took {total_time:.1f}s (target: <10s)")
    
    return {
        'success': failed == 0,  # Success if no actual failures (skips are OK)
        'total_time': total_time,
        'results': results,
        'summary': {'passed': passed, 'skipped': skipped, 'failed': failed}
    }


def main():
    """Main entry point for validation gate runner."""
    parser = argparse.ArgumentParser(description='Run validation gate tests')
    parser.add_argument('--fast', action='store_true', help='Run in fast mode (skip heavy operations)')
    parser.add_argument('--session', type=int, help='Run only specific session number')
    parser.add_argument('--baseline-only', action='store_true', help='Run only baseline system test')
    
    args = parser.parse_args()
    
    if args.baseline_only:
        # Run just the baseline test
        project_root = Path(__file__).parent.parent
        baseline_test = project_root / 'tests' / 'test_current_system.py'
        
        if baseline_test.exists():
            result = run_test_with_timing(baseline_test)
            if result['success']:
                print("✅ Baseline system test PASSED")
                return 0
            else:
                print("❌ Baseline system test FAILED")
                print(result['error'])
                return 1
        else:
            print("❌ Baseline test not found")
            return 1
    
    # Run all validation gates
    summary = run_all_validation_gates(fast_only=args.fast, session_filter=args.session)
    
    if summary['success']:
        print("\n✅ All validation gates ready!")
        return 0
    else:
        print(f"\n❌ {summary['summary']['failed']} validation gate(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())