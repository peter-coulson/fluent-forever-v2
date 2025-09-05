#!/usr/bin/env python3
"""
E2E Test Runner for Fluent Forever V2 Refactor

This script runs the E2E test suite and provides detailed reporting
on test results, performance, and validation gate status.
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any


class E2ETestRunner:
    """E2E test runner with comprehensive reporting"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.test_dir = self.project_root / "tests" / "e2e"
        self.results = {}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all E2E tests and return results"""
        print("🔍 Running Fluent Forever V2 E2E Test Suite")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run tests with pytest
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--tb=short",
            "--durations=10",
            "-v",
            "--maxfail=5"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            execution_time = time.time() - start_time
            
            self.results = {
                "success": result.returncode == 0,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
            self._parse_test_results()
            self._generate_report()
            
            return self.results
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return {"success": False, "error": str(e)}
    
    def run_session_tests(self, session_number: int) -> Dict[str, Any]:
        """Run tests for specific session"""
        marker = f"session{session_number}"
        
        print(f"🔍 Running Session {session_number} E2E Tests")
        print("=" * 40)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", marker,
            "--tb=short",
            "-v"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "session": session_number
        }
    
    def run_quick_validation(self) -> Dict[str, Any]:
        """Run quick validation tests only"""
        print("⚡ Running Quick Validation Tests")
        print("=" * 35)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", "fast",
            "--tb=line",
            "-q"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        execution_time = time.time() - start_time
        
        return {
            "success": result.returncode == 0,
            "execution_time": execution_time,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def validate_test_structure(self) -> Dict[str, Any]:
        """Validate that test structure is complete"""
        print("📋 Validating Test Structure")
        print("=" * 30)
        
        validation = {
            "valid": True,
            "issues": [],
            "session_coverage": {}
        }
        
        # Check session directories
        expected_sessions = [
            "01_core_architecture",
            "02_stage_system", 
            "03_provider_system",
            "04_cli_system",
            "05_configuration",
            "06_vocabulary_pipeline",
            "07_multi_pipeline",
            "08_documentation"
        ]
        
        for session in expected_sessions:
            session_dir = self.test_dir / session
            if not session_dir.exists():
                validation["issues"].append(f"Missing session directory: {session}")
                validation["valid"] = False
            else:
                test_files = list(session_dir.glob("test_*.py"))
                validation["session_coverage"][session] = len(test_files)
                
                if len(test_files) == 0:
                    validation["issues"].append(f"No test files in {session}")
                    validation["valid"] = False
        
        # Check required files
        required_files = [
            self.test_dir / "conftest.py",
            self.test_dir / "README.md",
            self.project_root / "tests" / "pytest.ini"
        ]
        
        for required_file in required_files:
            if not required_file.exists():
                validation["issues"].append(f"Missing required file: {required_file}")
                validation["valid"] = False
        
        return validation
    
    def _parse_test_results(self):
        """Parse pytest output for detailed results"""
        stdout = self.results.get("stdout", "")
        
        # Extract test counts
        if "failed" in stdout or "error" in stdout:
            # Parse failure information
            self.results["has_failures"] = True
        else:
            self.results["has_failures"] = False
        
        # Extract duration information
        if "seconds" in stdout:
            # Extract timing data
            pass
        
        # Parse session results
        session_results = {}
        for session_num in range(2, 10):  # Sessions 2-9
            marker = f"session{session_num}"
            if marker in stdout:
                session_results[session_num] = "present"
        
        self.results["session_results"] = session_results
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 E2E Test Results Summary")
        print("=" * 40)
        
        if self.results["success"]:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
        
        print(f"⏱️  Execution time: {self.results['execution_time']:.2f} seconds")
        
        if self.results["execution_time"] > 30:
            print("⚠️  Tests took longer than 30 seconds - consider optimization")
        else:
            print("✅ Tests completed within performance target (< 30s)")
        
        # Session coverage
        if self.results.get("session_results"):
            print("\n📋 Session Coverage:")
            for session_num, status in self.results["session_results"].items():
                print(f"  Session {session_num}: {status}")
        
        print("\n" + "=" * 40)
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check that test dependencies are available"""
        print("🔧 Checking Test Dependencies")
        print("=" * 30)
        
        dependencies = {
            "pytest": False,
            "python_path": False,
            "project_structure": False
        }
        
        # Check pytest
        try:
            result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                                  capture_output=True, text=True)
            dependencies["pytest"] = result.returncode == 0
        except:
            pass
        
        # Check Python path
        try:
            sys.path.insert(0, str(self.project_root / "src"))
            dependencies["python_path"] = True
        except:
            pass
        
        # Check project structure
        dependencies["project_structure"] = (
            (self.project_root / "src").exists() and
            (self.project_root / "tests").exists()
        )
        
        all_ready = all(dependencies.values())
        
        print(f"✅ pytest available: {dependencies['pytest']}")
        print(f"✅ Python path: {dependencies['python_path']}")  
        print(f"✅ Project structure: {dependencies['project_structure']}")
        
        if all_ready:
            print("✅ All dependencies ready")
        else:
            print("❌ Missing dependencies")
        
        return {"ready": all_ready, "dependencies": dependencies}


def main():
    """Main entry point"""
    runner = E2ETestRunner()
    
    # Check dependencies first
    deps = runner.check_dependencies()
    if not deps["ready"]:
        print("❌ Dependencies not ready. Please check setup.")
        return 1
    
    # Validate test structure
    structure = runner.validate_test_structure()
    if not structure["valid"]:
        print("❌ Test structure validation failed:")
        for issue in structure["issues"]:
            print(f"  - {issue}")
        return 1
    else:
        print("✅ Test structure validation passed")
    
    # Run tests based on command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            result = runner.run_quick_validation()
        elif sys.argv[1].startswith("session"):
            session_num = int(sys.argv[1].replace("session", ""))
            result = runner.run_session_tests(session_num)
        else:
            result = runner.run_all_tests()
    else:
        result = runner.run_all_tests()
    
    # Return appropriate exit code
    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    exit(main())