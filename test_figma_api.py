"""
Test Figma API Key and Basic Functionality
HVDC PROJECT | Samsung C&T | ADNOC·DSV Partnership
"""

import os
import requests
import json
from datetime import datetime

def test_figma_api():
    """Test Figma API key and basic functionality"""
    
    # Get API key from environment
    api_key = os.getenv('FIGMA_API_KEY')
    
    if not api_key:
        print("❌ FIGMA_API_KEY environment variable not set")
        return False
    
    print(f"🔑 Figma API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test API connection
    headers = {
        'X-Figma-Token': api_key
    }
    
    # Test with a sample file (Figma's public demo file)
    test_file_id = "FigmaCommunityFile_2_1_0"
    
    try:
        print("🔍 Testing Figma API connection...")
        
        # Get file info
        url = f"https://api.figma.com/v1/files/{test_file_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Figma API connection successful!")
            file_data = response.json()
            print(f"📁 File name: {file_data.get('name', 'Unknown')}")
            print(f"📅 Last modified: {file_data.get('lastModified', 'Unknown')}")
            return True
        elif response.status_code == 404:
            print("⚠️ Test file not found, but API key is valid")
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_user_info():
    """Test getting user information"""
    
    api_key = os.getenv('FIGMA_API_KEY')
    if not api_key:
        return False
    
    headers = {
        'X-Figma-Token': api_key
    }
    
    try:
        print("👤 Getting user information...")
        
        url = "https://api.figma.com/v1/me"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User information retrieved successfully!")
            print(f"👤 User: {user_data.get('handle', 'Unknown')}")
            print(f"📧 Email: {user_data.get('email', 'Unknown')}")
            print(f"🏢 Team: {user_data.get('team_id', 'Personal')}")
            return True
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return False

def list_user_files():
    """List user's Figma files"""
    
    api_key = os.getenv('FIGMA_API_KEY')
    if not api_key:
        return False
    
    headers = {
        'X-Figma-Token': api_key
    }
    
    try:
        print("📁 Listing user files...")
        
        url = "https://api.figma.com/v1/me/files"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            files_data = response.json()
            files = files_data.get('files', [])
            
            print(f"✅ Found {len(files)} files:")
            
            for i, file in enumerate(files[:5], 1):  # Show first 5 files
                print(f"  {i}. {file.get('name', 'Unknown')}")
                print(f"     ID: {file.get('key', 'Unknown')}")
                print(f"     Last modified: {file.get('last_modified', 'Unknown')}")
                print()
            
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more files")
            
            return files
        else:
            print(f"❌ Failed to list files: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return False

def main():
    """Main test function"""
    print("🎨 Figma API Test for HVDC Project")
    print("=" * 50)
    print()
    
    # Test API connection
    api_ok = test_figma_api()
    
    if api_ok:
        print()
        # Test user info
        user_ok = test_user_info()
        
        if user_ok:
            print()
            # List files
            files = list_user_files()
            
            if files:
                print()
                print("🎯 Next Steps:")
                print("1. Choose a file ID from the list above")
                print("2. Run: python figma_mcp_commands.py extract_tokens <FILE_ID>")
                print("3. Run: python figma_mcp_commands.py generate_components <FILE_ID>")
                print()
                print("📋 Example:")
                if files and len(files) > 0:
                    sample_file_id = files[0].get('key', 'YOUR_FILE_ID')
                    print(f"   python figma_mcp_commands.py extract_tokens {sample_file_id}")
    
    print()
    print("🔧 Available Commands:")
    print("   python figma_mcp_commands.py help")
    print("   python figma_mcp_commands.py setup_server")
    print("   python figma_mcp_commands.py create_template")

if __name__ == "__main__":
    main() 