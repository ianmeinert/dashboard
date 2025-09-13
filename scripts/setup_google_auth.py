#!/usr/bin/env python3
"""
One-time Google Calendar authentication setup for headless deployment.
Run this on a machine with GUI access, then copy token.json to your server.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Your constants (update these to match your main code)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "backend","data")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")
TOKEN_FILE = os.path.join(DATA_DIR, "token.json")

def main():
    print("Setting up Google Calendar authentication...")
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found!")
        print("Download it from Google Cloud Console and place it in this directory.")
        return
    
    # Run the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save credentials
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print(f"✅ Authentication successful!")
    print(f"✅ Credentials saved to {TOKEN_FILE}")
    print(f"📋 Copy {TOKEN_FILE} to your server at: /opt/dashboard/{TOKEN_FILE}")
    print("🚀 Your service can now run headless with automatic token refresh!")

if __name__ == '__main__':
    main()