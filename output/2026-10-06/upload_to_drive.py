#!/usr/bin/env python3
"""
Upload 7 PNG slides and carousel.html to the specified Google Drive folder.

Requirements:
  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

Usage:
  python3 upload_to_drive.py

Authentication (choose one):
  1. Application Default Credentials:
       gcloud auth application-default login
  2. Service Account:
       export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json
  3. OAuth2 client secrets:
       Set CLIENT_SECRET_FILE below to your client_secret.json path.
"""

import os
import pathlib

# ── Config ────────────────────────────────────────────────────────────────────
FOLDER_ID = "1EqO1GQe57F0S7if62s6Uicb4M0TLyXsA"
OUTPUT_DIR = pathlib.Path(__file__).parent

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

# Set to your client_secret.json path for OAuth2 flow (optional)
CLIENT_SECRET_FILE = None
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
# ── End Config ────────────────────────────────────────────────────────────────


def get_credentials():
    """Return credentials using ADC or service account."""
    import google.auth
    from google.oauth2 import service_account

    sa_key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if sa_key and pathlib.Path(sa_key).exists():
        print(f"Using service account: {sa_key}")
        creds = service_account.Credentials.from_service_account_file(
            sa_key, scopes=SCOPES
        )
        return creds

    if CLIENT_SECRET_FILE and pathlib.Path(CLIENT_SECRET_FILE).exists():
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        return creds

    print("Using Application Default Credentials (ADC).")
    creds, _ = google.auth.default(scopes=SCOPES)
    return creds


def upload_files():
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    results = {}
    for filename, mime_type in FILES:
        file_path = OUTPUT_DIR / filename
        if not file_path.exists():
            print(f"  SKIP  {filename} (not found)")
            results[filename] = {"status": "skipped", "reason": "file not found"}
            continue

        print(f"  Uploading {filename} ({file_path.stat().st_size / 1024:.0f} KB) ...", end=" ", flush=True)
        try:
            metadata = {
                "name": filename,
                "parents": [FOLDER_ID],
            }
            media = MediaFileUpload(
                str(file_path),
                mimetype=mime_type,
                resumable=True,
            )
            request = service.files().create(
                body=metadata,
                media_body=media,
                fields="id,name",
                supportsAllDrives=True,
            )
            # Execute resumable upload with progress
            response = None
            while response is None:
                _, response = request.next_chunk()

            file_id = response.get("id")
            print(f"OK  id={file_id}")
            results[filename] = {"status": "success", "id": file_id}
        except Exception as e:
            print(f"FAIL  {e}")
            results[filename] = {"status": "error", "reason": str(e)}

    print("\n── Upload summary ──────────────────────────────────")
    for fname, r in results.items():
        if r["status"] == "success":
            print(f"  ✓  {fname}  →  https://drive.google.com/file/d/{r['id']}/view")
        elif r["status"] == "skipped":
            print(f"  -  {fname}  (skipped: {r['reason']})")
        else:
            print(f"  ✗  {fname}  ERROR: {r['reason']}")


if __name__ == "__main__":
    upload_files()
