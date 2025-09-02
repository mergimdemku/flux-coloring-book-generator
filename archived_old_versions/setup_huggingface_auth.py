#!/usr/bin/env python3
"""
Setup HuggingFace Authentication for FLUX Model Access
This script helps set up the required authentication to access the FLUX.1-schnell model
"""

import os
import sys
from pathlib import Path

def setup_huggingface_auth():
    """Guide user through HuggingFace authentication setup"""
    
    print("🔐 HuggingFace Authentication Setup")
    print("=" * 50)
    print()
    print("To use FLUX.1-schnell, you need to:")
    print("1. Create a HuggingFace account at https://huggingface.co")
    print("2. Request access to FLUX.1-schnell model")
    print("3. Create an access token")
    print("4. Authenticate with this script")
    print()
    
    # Check if already authenticated
    try:
        import huggingface_hub
        try:
            # Try to access the model
            info = huggingface_hub.model_info("black-forest-labs/FLUX.1-schnell")
            print("✅ Already authenticated and have access to FLUX.1-schnell!")
            return True
        except Exception as e:
            if "401" in str(e) or "authentication" in str(e).lower():
                print("❌ Authentication required")
            elif "403" in str(e) or "access" in str(e).lower():
                print("❌ No access to FLUX.1-schnell model")
                print("   Visit: https://huggingface.co/black-forest-labs/FLUX.1-schnell")
                print("   Click 'Request Access' and wait for approval")
                return False
            else:
                print(f"❌ Error checking model access: {e}")
                return False
    except ImportError:
        print("Installing huggingface_hub...")
        os.system("pip install huggingface_hub")
        import huggingface_hub
    
    # Get token from user
    print("\n🔑 Authentication Options:")
    print("1. Login with browser (recommended)")
    print("2. Enter token manually")
    print("3. Set token in environment variable")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        # Browser login
        print("\n🌐 Opening browser for authentication...")
        try:
            huggingface_hub.login()
            print("✅ Authentication successful!")
        except Exception as e:
            print(f"❌ Browser authentication failed: {e}")
            return False
    
    elif choice == "2":
        # Manual token entry
        print("\n📝 To get your token:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create a new token with 'Read' access")
        print("3. Copy the token")
        print()
        
        token = input("Enter your HuggingFace token: ").strip()
        if not token:
            print("❌ No token provided")
            return False
        
        try:
            huggingface_hub.login(token=token)
            print("✅ Authentication successful!")
        except Exception as e:
            print(f"❌ Token authentication failed: {e}")
            return False
    
    elif choice == "3":
        # Environment variable
        print("\n🔧 Set environment variable:")
        print("Linux/Mac: export HUGGINGFACE_HUB_TOKEN=your_token_here")
        print("Windows: set HUGGINGFACE_HUB_TOKEN=your_token_here")
        print()
        print("Then restart your terminal and run the generator")
        return False
    
    else:
        print("❌ Invalid choice")
        return False
    
    # Verify access
    print("\n🔍 Verifying model access...")
    try:
        info = huggingface_hub.model_info("black-forest-labs/FLUX.1-schnell")
        print("✅ Successfully authenticated and have access to FLUX.1-schnell!")
        print()
        print("🎉 Setup complete! You can now run:")
        print("   python find_sweet_spot.py")
        print("   python automated_coloring_book_pipeline.py")
        return True
        
    except Exception as e:
        if "403" in str(e):
            print("❌ Authenticated but no access to FLUX.1-schnell")
            print("   Visit: https://huggingface.co/black-forest-labs/FLUX.1-schnell")
            print("   Click 'Request Access' and wait for approval")
        else:
            print(f"❌ Error verifying access: {e}")
        return False

def create_env_file():
    """Create .env file with authentication token"""
    env_path = Path(".env")
    
    if env_path.exists():
        print("📄 .env file already exists")
        return
    
    print("\n📄 Creating .env file for token storage...")
    token = input("Enter your HuggingFace token (optional): ").strip()
    
    env_content = f"""# HuggingFace Authentication
HUGGINGFACE_HUB_TOKEN={token}

# FLUX Generation Settings  
FLUX_MODEL_PATH=./models/flux
FLUX_CACHE_DIR=./cache
"""
    
    env_path.write_text(env_content)
    print(f"✅ Created {env_path}")
    print("   Add your token there if needed")

if __name__ == "__main__":
    print("🎨 FLUX Coloring Book Generator - Authentication Setup")
    print()
    
    success = setup_huggingface_auth()
    
    if not success:
        print("\n⚠️  Authentication not complete")
        print("The generator will not work until you have access to FLUX.1-schnell")
        
    create_env_file()
    
    print("\n📚 Next Steps:")
    print("1. Ensure you have access to FLUX.1-schnell model")
    print("2. Run: python find_sweet_spot.py")
    print("3. If it works, run: python automated_coloring_book_pipeline.py")