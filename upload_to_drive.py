#!/usr/bin/env python3
"""
Upload output files to Google Drive folder.

Prerequisites:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

Authentication — run ONE of these first, then re-run this script:
    Option A (recommended for interactive use):
        gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive

    Option B (service account):
        export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

Usage:
    python3 upload_to_drive.py
"""

import os
import sys

try:
    import google.auth
    import googleapiclient.discovery
    import googleapiclient.http
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

FOLDER_ID = "1MkIhgqVVVEAtvd7hwX2lFp7_jh-YawFh"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "2026-10-14")

FILES = [
    ("slide_01.png", "image/png"),
    ("slide_02.png", "image/png"),
    ("slide_03.png", "image/png"),
    ("slide_04.png", "image/png"),
    ("slide_05.png", "image/png"),
    ("slide_06.png", "image/png"),
    ("slide_07.png", "image/png"),
    ("carousel.html", "text/html"),
]


def build_service():
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds, project = google.auth.default(scopes=scopes)
    return googleapiclient.discovery.build("drive", "v3", credentials=creds)


def upload_file(service, filepath, filename, mime_type, folder_id):
    print(f"  Uploading {filename} ({os.path.getsize(filepath):,} bytes)...")
    file_metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    media = googleapiclient.http.MediaFileUpload(
        filepath,
        mimetype=mime_type,
        resumable=True,
    )
    request = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,size",
        supportsAllDrives=True,
    )
    # Use resumable upload with progress
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"    Progress: {pct}%", end="\r")
    print(f"    Done. Drive ID: {response['id']}")
    return response["id"]


def main():
    print("Building Drive service...")
    try:
        service = build_service()
    except google.auth.exceptions.DefaultCredentialsError as e:
        print(f"\nAuthentication failed: {e}")
        print("\nRun this first, then re-run the script:")
        print("  gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive")
        sys.exit(1)

    results = {}
    errors = {}

    for filename, mime_type in FILES:
        filepath = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP {filename}: file not found at {filepath}")
            errors[filename] = "file not found"
            continue
        try:
            drive_id = upload_file(service, filepath, filename, mime_type, FOLDER_ID)
            results[filename] = drive_id
        except Exception as e:
            print(f"  ERROR uploading {filename}: {e}")
            errors[filename] = str(e)

    print("\n=== RESULTS ===")
    print(f"Folder: https://drive.google.com/drive/folders/{FOLDER_ID}")
    print()
    for filename, drive_id in results.items():
        print(f"  {filename}: {drive_id}")
        print(f"    https://drive.google.com/file/d/{drive_id}")
    if errors:
        print("\nErrors:")
        for filename, err in errors.items():
            print(f"  {filename}: {err}")


if __name__ == "__main__":
    main()
