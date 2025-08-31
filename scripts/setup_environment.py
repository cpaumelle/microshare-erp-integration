#!/usr/bin/env python3
"""
Environment validation script for Microshare ERP Integration
Validates that all required environment variables and dependencies are present
"""

import os
import sys
import importlib
from pathlib import Path

def check_environment_variables():
    """Check that all required environment variables are set"""
    required_vars = [
        'MICROSHARE_AUTH_URL',
        'MICROSHARE_API_URL', 
        'MICROSHARE_USERNAME',
        'MICROSHARE_PASSWORD',
        'MICROSHARE_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_python_dependencies():
    """Check that all required Python packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'httpx',
        'pydantic',
        'cachetools'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing Python packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
        
    print("✅ All required Python packages are installed")
    return True

def check_project_structure():
    """Check that project directory structure is correct"""
    required_dirs = [
        'src/microshare_client',
        'services/integration-api',
        'tests'
    ]
    
    project_root = Path(__file__).parent.parent
    missing_dirs = []
    
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    print("✅ Project directory structure is correct")
    return True

if __name__ == "__main__":
    print("🔍 Validating Microshare ERP Integration environment...")
    print("=" * 55)
    
    all_checks_passed = True
    
    all_checks_passed &= check_environment_variables()
    all_checks_passed &= check_python_dependencies() 
    all_checks_passed &= check_project_structure()
    
    print("=" * 55)
    if all_checks_passed:
        print("✅ Environment validation successful! Ready to run.")
        sys.exit(0)
    else:
        print("❌ Environment validation failed. Please fix the issues above.")
        sys.exit(1)

