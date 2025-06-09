"""
AliExpress OAuth Helper
Helps generate access tokens for user authorization
"""

import os
import hashlib
import time
import urllib.parse
import requests
from typing import Optional, Dict, Any

class AliExpressOAuth:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI', 'http://localhost:8080/callback')
        self.base_url = 'https://api.aliexpress.com/sync'
        
    def get_authorization_url(self) -> str:
        """Generate authorization URL for OAuth flow"""
        params = {
            'response_type': 'code',
            'client_id': self.app_key,
            'redirect_uri': self.redirect_uri,
            'state': 'random_state_string'  # Use a random string in production
        }
        
        auth_url = f"https://api.aliexpress.com/oauth/authorize?{urllib.parse.urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            params = {
                'app_key': self.app_key,
                'method': 'aliexpress.system.oauth.token',
                'timestamp': timestamp,
                'format': 'json',
                'v': '2.0',
                'sign_method': 'md5',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri
            }
            
            # Generate signature
            params['sign'] = self._generate_signature(params)
            
            response = requests.post(self.base_url, data=params)
            
            if response.status_code == 200:
                result = response.json()
                if 'aliexpress_system_oauth_token_response' in result:
                    token_data = result['aliexpress_system_oauth_token_response']
                    return {
                        'access_token': token_data.get('access_token'),
                        'refresh_token': token_data.get('refresh_token'),
                        'expires_in': token_data.get('expires_in'),
                        'token_type': token_data.get('token_type')
                    }
            
            return None
            
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh an expired access token"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            params = {
                'app_key': self.app_key,
                'method': 'aliexpress.system.oauth.token.refresh',
                'timestamp': timestamp,
                'format': 'json',
                'v': '2.0',
                'sign_method': 'md5',
                'refresh_token': refresh_token
            }
            
            # Generate signature
            params['sign'] = self._generate_signature(params)
            
            response = requests.post(self.base_url, data=params)
            
            if response.status_code == 200:
                result = response.json()
                if 'aliexpress_system_oauth_token_refresh_response' in result:
                    token_data = result['aliexpress_system_oauth_token_refresh_response']
                    return {
                        'access_token': token_data.get('access_token'),
                        'refresh_token': token_data.get('refresh_token'),
                        'expires_in': token_data.get('expires_in'),
                        'token_type': token_data.get('token_type')
                    }
            
            return None
            
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate API signature for AliExpress API"""
        # Sort parameters by key
        sorted_params = sorted(params.items())
        
        # Create parameter string
        param_string = ''.join([f"{k}{v}" for k, v in sorted_params])
        
        # Add app secret at the beginning and end
        sign_string = f"{self.app_secret}{param_string}{self.app_secret}"
        
        # Generate MD5 hash
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        
        return signature

def main():
    """Helper script to get access token"""
    oauth = AliExpressOAuth()
    
    print("AliExpress OAuth Helper")
    print("=" * 50)
    
    # Step 1: Get authorization URL
    auth_url = oauth.get_authorization_url()
    print(f"1. Visit this URL to authorize your application:")
    print(f"   {auth_url}")
    print()
    
    # Step 2: Get authorization code from user
    print("2. After authorization, you'll be redirected to your callback URL.")
    print("   Copy the 'code' parameter from the URL.")
    print()
    
    auth_code = input("3. Enter the authorization code: ").strip()
    
    if auth_code:
        # Step 3: Exchange code for token
        print("\n4. Exchanging code for access token...")
        token_data = oauth.exchange_code_for_token(auth_code)
        
        if token_data:
            print("\n✅ Success! Your access token:")
            print(f"Access Token: {token_data['access_token']}")
            print(f"Refresh Token: {token_data['refresh_token']}")
            print(f"Expires In: {token_data['expires_in']} seconds")
            print(f"Token Type: {token_data['token_type']}")
            print()
            print("Add this to your .env file:")
            print(f"ALIEXPRESS_ACCESS_TOKEN={token_data['access_token']}")
            print(f"ALIEXPRESS_REFRESH_TOKEN={token_data['refresh_token']}")
        else:
            print("\n❌ Failed to get access token. Please check your credentials and try again.")
    else:
        print("No authorization code provided.")

if __name__ == "__main__":
    main()