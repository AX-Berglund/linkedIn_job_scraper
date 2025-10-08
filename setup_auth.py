#!/usr/bin/env python3
"""
Interactive script to set up LinkedIn authentication.
"""

import os
from pathlib import Path
import getpass

def main():
    print("="*60)
    print("🔐 LinkedIn Authentication Setup")
    print("="*60)
    
    print("\n⚠️  WARNING:")
    print("  Storing LinkedIn credentials may violate their Terms of Service.")
    print("  Use at your own risk for personal use only.\n")
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Setup cancelled.")
        return
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        print("\n⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (yes/no): ")
        if overwrite.lower() not in ['yes', 'y']:
            print("Setup cancelled.")
            return
    
    print("\n📧 Enter your LinkedIn credentials:")
    print("   (Your password will be hidden as you type)\n")
    
    # Get email
    email = input("LinkedIn email: ").strip()
    
    # Get password (hidden)
    password = getpass.getpass("LinkedIn password: ")
    
    # Confirm
    print("\n✅ Credentials received.")
    enable_auto_login = input("\nEnable automatic login? (yes/no): ")
    
    auto_login = "true" if enable_auto_login.lower() in ['yes', 'y'] else "false"
    
    # Write to .env file
    env_content = f"""# LinkedIn Credentials (for automatic login)
# WARNING: Keep this file private! Never commit it to git.

LINKEDIN_EMAIL={email}
LINKEDIN_PASSWORD={password}

# Set to 'true' to enable automatic login
LINKEDIN_AUTO_LOGIN={auto_login}
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        
        # Set file permissions (Unix-like systems)
        try:
            os.chmod(".env", 0o600)  # Read/write for owner only
            print("\n✅ .env file created with secure permissions (600)")
        except:
            print("\n✅ .env file created")
            print("   ⚠️  Set file permissions manually: chmod 600 .env")
        
        print("\n" + "="*60)
        print("✅ Setup complete!")
        print("="*60)
        print("\nYour LinkedIn credentials are saved in .env")
        print("This file is automatically ignored by git.\n")
        
        if auto_login == "true":
            print("🚀 Auto-login is ENABLED")
            print("   The scraper will automatically log in to LinkedIn.\n")
        else:
            print("⏸️  Auto-login is DISABLED")
            print("   To enable: Edit .env and set LINKEDIN_AUTO_LOGIN=true\n")
        
        print("Next steps:")
        print("  1. Run: python scrape_jobs.py")
        print("  2. For more info: See AUTHENTICATION.md")
        
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

