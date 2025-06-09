"""
Simple script to help get AliExpress access token
"""

import os
from dotenv import load_dotenv
from oauth_helper import AliExpressOAuth

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if we have the required credentials
    app_key = os.getenv('ALIEXPRESS_APP_KEY')
    app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
    
    if not app_key or not app_secret:
        print("❌ Missing ALIEXPRESS_APP_KEY or ALIEXPRESS_APP_SECRET in .env file")
        print("Please add them first before running this script.")
        return
    
    print("🔑 AliExpress Access Token Generator")
    print("=" * 50)
    print()
    
    oauth = AliExpressOAuth()
    
    print("Choose an option:")
    print("1. Generate authorization URL (for new token)")
    print("2. Exchange authorization code for token")
    print("3. Refresh existing token")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        auth_url = oauth.get_authorization_url()
        print(f"\n📋 Visit this URL to authorize your application:")
        print(f"{auth_url}")
        print("\nAfter authorization, you'll get a code. Use option 2 to exchange it for a token.")
        
    elif choice == "2":
        auth_code = input("\n🔐 Enter the authorization code: ").strip()
        if auth_code:
            print("🔄 Exchanging code for access token...")
            token_data = oauth.exchange_code_for_token(auth_code)
            
            if token_data:
                print("\n✅ Success! Your tokens:")
                print(f"Access Token: {token_data['access_token']}")
                print(f"Refresh Token: {token_data['refresh_token']}")
                print(f"Expires In: {token_data['expires_in']} seconds")
                print()
                print("📝 Add these to your .env file:")
                print(f"ALIEXPRESS_ACCESS_TOKEN={token_data['access_token']}")
                print(f"ALIEXPRESS_REFRESH_TOKEN={token_data['refresh_token']}")
            else:
                print("\n❌ Failed to get access token.")
        else:
            print("No authorization code provided.")
            
    elif choice == "3":
        refresh_token = input("\n🔄 Enter your refresh token: ").strip()
        if refresh_token:
            print("🔄 Refreshing access token...")
            token_data = oauth.refresh_access_token(refresh_token)
            
            if token_data:
                print("\n✅ Token refreshed successfully!")
                print(f"New Access Token: {token_data['access_token']}")
                print(f"New Refresh Token: {token_data['refresh_token']}")
                print(f"Expires In: {token_data['expires_in']} seconds")
                print()
                print("📝 Update your .env file:")
                print(f"ALIEXPRESS_ACCESS_TOKEN={token_data['access_token']}")
                print(f"ALIEXPRESS_REFRESH_TOKEN={token_data['refresh_token']}")
            else:
                print("\n❌ Failed to refresh token.")
        else:
            print("No refresh token provided.")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()