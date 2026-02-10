#!/usr/bin/env python3
"""
Google Drive to GitHub Pages Deployment Script

This script:
1. Downloads the Excel file from Google Drive
2. Generates the static HTML
3. Commits and pushes to GitHub Pages
"""

import os
import subprocess
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Configuration - UPDATE THESE VALUES
GDRIVE_FILE_ID = "YOUR_FILE_ID_HERE"  # Get this from the Google Drive share link
LOCAL_FILENAME = "PF_Ranks.xlsx"


def get_gdrive_service():
    """Authenticate and return Google Drive service"""
    creds = None
    token_path = Path("token.json")

    # The file token.json stores the user's access and refresh tokens
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path("credentials.json").exists():
                print("❌ Error: credentials.json not found!")
                print("\nTo set up Google Drive access:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Google Drive API")
                print("4. Create OAuth 2.0 credentials (Desktop app)")
                print("5. Download credentials.json to this directory")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        token_path.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


def download_from_gdrive(service, file_id, destination):
    """Download file from Google Drive"""
    print(f"📥 Downloading from Google Drive...")

    try:
        request = service.files().get_media(fileId=file_id)
        with open(destination, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"   Progress: {int(status.progress() * 100)}%")

        print(f"✅ Downloaded to {destination}")
        return True

    except Exception as e:
        print(f"❌ Error downloading file: {e}")
        return False


def generate_html():
    """Generate static HTML from Excel"""
    print("📊 Generating static HTML...")
    try:
        subprocess.run([sys.executable, "export_static.py"], check=True)
        print("✅ HTML generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating HTML: {e}")
        return False


def git_commit_and_push():
    """Commit and push changes to GitHub"""
    print("📝 Committing changes...")

    try:
        # Add files
        subprocess.run(["git", "add", "docs/index.html", LOCAL_FILENAME], check=True)

        # Check if there are changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )

        if result.returncode == 0:
            print("ℹ️  No changes to commit")
            return True

        # Commit
        from datetime import datetime
        commit_msg = f"Update theme dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        # Push
        print("📤 Pushing to GitHub...")
        subprocess.run(["git", "push"], check=True)

        print("✅ Deployment complete!")
        print("🌐 Your site will be updated at: https://araroot.github.io/themes/")
        print("⏱️  GitHub Pages may take 1-2 minutes to rebuild")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error with git operations: {e}")
        return False


def main():
    print("🚀 Starting Google Drive to GitHub Pages deployment...\n")

    # Check configuration
    if GDRIVE_FILE_ID == "YOUR_FILE_ID_HERE":
        print("❌ Error: Please configure GDRIVE_FILE_ID in deploy_from_gdrive.py")
        print("\nTo get your file ID:")
        print("1. Open the file in Google Drive")
        print("2. Click 'Share' and copy the link")
        print("3. Extract the ID from: https://drive.google.com/file/d/FILE_ID_HERE/view")
        sys.exit(1)

    # Step 1: Download from Google Drive
    service = get_gdrive_service()
    if not download_from_gdrive(service, GDRIVE_FILE_ID, LOCAL_FILENAME):
        sys.exit(1)

    # Step 2: Generate HTML
    if not generate_html():
        sys.exit(1)

    # Step 3: Commit and push
    if not git_commit_and_push():
        sys.exit(1)


if __name__ == "__main__":
    main()
