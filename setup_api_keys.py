#!/usr/bin/env python
"""
API Key Management - Setup & Testing Script

This script helps:
1. Initialize the database with API key tables
2. Test API key creation and usage
3. Verify authentication methods
"""

import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"✓ {text}")
    print("="*60)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def test_basic_endpoints():
    """Test that basic API is working"""
    print_header("Testing Basic API Endpoints")
    
    try:
        # Health check
        response = requests.get(f"{BASE_URL}/health")
        print_success("Health check: OK")
        
        # Root endpoint
        response = requests.get(f"{BASE_URL}/")
        print_success("Root endpoint: OK")
        
        return True
    except Exception as e:
        print_error(f"Basic endpoints failed: {e}")
        return False

def test_api_key_creation(jwt_token):
    """Test creating an API key"""
    print_header("Testing API Key Creation")
    
    try:
        payload = {
            "name": "Test API Key",
            "expires_in_days": 30,
            "can_read_tasks": True,
            "can_create_tasks": True,
            "can_update_tasks": True,
            "can_delete_tasks": False,
            "can_read_dashboard": True
        }
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/api-keys",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success("API key created successfully")
            print_info(f"Key ID: {data['id']}")
            print_info(f"Key prefix: {data['prefix']}")
            print_info(f"Full key: {data['api_key']}")
            return data
        else:
            print_error(f"Failed to create API key: {response.status_code}")
            print_info(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"API key creation failed: {e}")
        return None

def test_api_key_usage(api_key):
    """Test using the API key"""
    print_header("Testing API Key Usage")
    
    try:
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        # Test getting tasks with API key
        response = requests.get(
            f"{BASE_URL}/api/tasks",
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("API key authentication works!")
            print_info(f"Tasks retrieved: {len(response.json())}")
            return True
        else:
            print_error(f"API key usage failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"API key usage test failed: {e}")
        return False

def test_list_api_keys(jwt_token):
    """Test listing API keys"""
    print_header("Testing List API Keys")
    
    try:
        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/api-keys",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API keys retrieved: {len(data)}")
            for key in data:
                print_info(f"- {key['name']} (prefix: {key['prefix']})")
            return True
        else:
            print_error(f"List API keys failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"List API keys test failed: {e}")
        return False

def setup_test_user():
    """Create test user and get JWT token"""
    print_header("Setting Up Test User")
    
    try:
        # Register user
        register_payload = {
            "username": "test_api_key_user",
            "email": "test_api_key@example.com",
            "full_name": "Test API Key",
            "password": "test123456"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/users/register",
            json=register_payload
        )
        
        if response.status_code in [200, 201]:
            user = response.json()
            print_success(f"User created: {user['username']}")
        elif response.status_code == 400:
            print_info("User already exists (using existing)")
        else:
            print_error(f"Failed to create user: {response.status_code}")
            return None
        
        # Login user
        login_payload = {
            "username": "test_api_key_user",
            "password": "test123456"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/users/login",
            json=login_payload
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access_token']
            print_success("User logged in successfully")
            return token
        else:
            print_error(f"Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"User setup failed: {e}")
        return None

def main():
    """Run all tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   API KEY MANAGEMENT - SETUP & TESTING SCRIPT            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    print_info("Make sure the API is running: python -m uvicorn app.main:app --reload")
    
    # Test basic endpoints
    if not test_basic_endpoints():
        print_error("API is not responding. Please start the server first!")
        sys.exit(1)
    
    # Setup test user
    jwt_token = setup_test_user()
    if not jwt_token:
        print_error("Failed to setup test user")
        sys.exit(1)
    
    # Test API key creation
    api_key_data = test_api_key_creation(jwt_token)
    if not api_key_data:
        print_error("Failed to create API key")
        sys.exit(1)
    
    # Test API key usage
    if not test_api_key_usage(api_key_data['api_key']):
        print_error("Failed to use API key")
        sys.exit(1)
    
    # Test listing API keys
    if not test_list_api_keys(jwt_token):
        print_error("Failed to list API keys")
        sys.exit(1)
    
    # Summary
    print_header("✨ All Tests Completed Successfully!")
    print("""
Your API Key Management System is ready!

Next Steps:
1. Create API keys for your applications
2. Store keys securely in .env files
3. Use X-API-Key header in requests
4. Monitor key usage and rotation

Example usage:
  curl -H "X-API-Key: tm_your_key" \\
       http://localhost:8000/api/tasks

Documentation:
- API_KEY_MANAGEMENT_GUIDE.md (comprehensive)
- API_KEY_QUICK_START.md (quick reference)
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
