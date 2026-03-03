import os
import io
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveOAuthService:
    def __init__(self):
        self.service = None
        self.creds = None
        self.initialize_service()

    def initialize_service(self):
        try:
            token_file = 'token.pickle'

            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    self.creds = pickle.load(token)

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'oauth_credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)

                with open(token_file, 'wb') as token:
                    pickle.dump(self.creds, token)

            self.service = build('drive', 'v3', credentials=self.creds)
            print("✅ Google Drive OAuth service initialized successfully")

        except Exception as e:
            print(f"❌ Error initializing Google Drive OAuth service: {e}")
            self.service = None

    def create_folder(self, folder_name, parent_folder_id=None):
        if not self.service:
            print("❌ Google Drive service not initialized")
            return None

        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_folder_id and parent_folder_id != "None":
                folder_metadata['parents'] = [parent_folder_id]

            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            print(f"✅ Folder created: {folder_name} (ID: {folder_id})")
            return folder_id

        except HttpError as error:
            print(f"❌ Error creating folder: {error}")
            return None

    def upload_voice_message(self, file_content, filename, folder_id, mime_type='audio/ogg'):
        if not self.service:
            print("❌ Google Drive service not initialized")
            return None

        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }

            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            file_id = file.get('id')
            print(f"✅ File uploaded: {filename} (ID: {file_id})")
            return file_id

        except HttpError as error:
            print(f"❌ Error uploading file: {error}")
            return None

    def upload_text_file(self, file_content, filename, folder_id, mime_type='text/plain'):
        if not self.service:
            print("❌ Google Drive service not initialized")
            return None

        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id],
                'mimeType': mime_type
            }

            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            file_id = file.get('id')
            print(f"✅ Text file uploaded: {filename} (ID: {file_id})")
            return file_id

        except HttpError as error:
            print(f"❌ Error uploading text file: {error}")
            return None

    def get_folder_url(self, folder_id):
        return f"https://drive.google.com/drive/folders/{folder_id}"

    def check_folder_access(self, folder_id):
        if not self.service:
            return False

        try:
            self.service.files().get(
                fileId=folder_id,
                fields='id'
            ).execute()
            return True
        except HttpError:
            return False


drive_service = GoogleDriveOAuthService()