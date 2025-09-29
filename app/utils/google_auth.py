# app/utils/google_auth.py
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

load_dotenv()  # make sure .env is loaded

SCOPES = os.getenv("GOOGLE_CALENDAR_SCOPES").split(",")  # match .env
CREDS_PATH = os.getenv("GOOGLE_CLIENT_SECRET_FILE")      # match .env
TOKEN_PATH = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE")    # match .env

def get_google_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return creds
