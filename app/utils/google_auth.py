# app/utils/google_auth.py
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

load_dotenv()  # <-- make sure this is here

SCOPES = [os.getenv("GOOGLE_CALENDAR_SCOPES")]
creds_path = os.getenv("GOOGLE_CLIENT_SECRET_FILE")
token_path = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE")

def get_google_credentials():
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return creds
