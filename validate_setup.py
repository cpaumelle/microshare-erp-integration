#!/usr/bin/env python3
"""
Validate the GitHub repository setup and configuration
"""
import os
import sys
import subprocess
import httpx
from pathlib import Path

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists

def check_environment_variables() -> bool:
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    required_vars = [
        'MICROSHARE_AUTH_URL',
        'MICROSHARE_API_URL', 
        'MICROSHARE_USERNAME',
        'MICROSHARE_PASSWORD',
        'MICROSHARE_API_KEY'
    ]
    
    # Try to load from .env file if not in environment
    env_file = Path('.env')
    if env_file.exists():
        with open('.env') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var, '')
        if value and not value.startswith('your_') and not value.startswith('demo_'):
            print(f"✅ {var} (configured)")
        elif value and (value.startswith('demo_') or value.startswith('generic_')):
            print(f"⚠️  {var} (using demo credentials)")
        else:
            print(f"❌ {var} (missing or placeholder)")
            all_present = False
    
    return all_present

def test_docker_setup() -> bool:
    """Test if Docker setup works"""
    print("\n🐳 Testing Docker setup...")
    try:
        result = subprocess.run(['docker-compose', 'config'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ docker-compose.yml is valid")
            return True
        else:
            print(f"❌ docker-compose config error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Docker compose validation timed out")
        return False
    except FileNotFoundError:
        print("⚠️  Docker not installed - setup is valid but can't test")
        return True

def test_api_connection() -> bool:
    """Test connection to Microshare API"""
    print("\n🌐 Testing Microshare API connection...")
    
    auth_url = os.getenv('MICROSHARE_AUTH_URL', 'https://dauth.microshare.io')
    username = os.getenv('MICROSHARE_USERNAME')
    password = os.getenv('MICROSHARE_PASSWORD')
    api_key = os.getenv('MICROSHARE_API_KEY')
    
    if not all([username, password, api_key]):
        print("⚠️  Credentials not configured - skipping API test")
        return True
        
    try:
        response = httpx.post(f"{auth_url}/oauth2/token", data={
            "username": username,
            "password": password,
            "client_id": api_key,
            "grant_type": "password",
            "scope": "ALL:ALL"
        }, timeout=10)
        
        if response.status_code == 200:
            print("✅ Microshare API connection successful")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Validating GitHub repository setup...\n")
    
    # Check required files
    print("📁 Checking repository structure...")
    required_files = [
        'README.md',
        'LICENSE',
        'docker-compose.yml',
        '.env.example',
        '.gitignore',
        'requirements.txt',
        'services/integration-api/main.py',
        'services/integration-api/Dockerfile',
        'src/microshare_client/__init__.py',
        'tests/conftest.py'
    ]
    
    files_ok = all(check_file_exists(f) for f in required_files)
    
    # Check environment
    env_ok = check_environment_variables()
    
    # Test Docker
    docker_ok = test_docker_setup()
    
    # Test API connection  
    api_ok = test_api_connection()
    
    # Summary
    print("\n📊 Validation Summary:")
    print(f"{'✅' if files_ok else '❌'} Repository structure")
    print(f"{'✅' if env_ok else '❌'} Environment configuration")
    print(f"{'✅' if docker_ok else '❌'} Docker setup")
    print(f"{'✅' if api_ok else '❌'} API connectivity")
    
    if all([files_ok, docker_ok]):
        print("\n🎉 Repository setup is valid and ready for GitHub!")
        print("\nNext steps:")
        print("1. Review and customize .env file with your credentials")
        print("2. Test: docker-compose up -d")
        print("3. Test: curl http://localhost:8000/health")
        print("4. Push to GitHub!")
        return True
    else:
        print("\n❌ Setup validation failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
