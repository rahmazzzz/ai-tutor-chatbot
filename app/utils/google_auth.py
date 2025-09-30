# app/utils/google_auth.py
import os
import pickle
import json
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import streamlit as st

# Load secrets
secrets = st.secrets
SCOPES = secrets["GOOGLE_CALENDAR_SCOPES"].split(",")
CREDS_JSON = secrets["GOOGLE_CLIENT_SECRET_JSON"]

def get_google_credentials():
    creds = None

    # Decode token from base64 if it exists
    if "GOOGLE_CALENDAR_TOKEN" in secrets and secrets["GOOGLE_CALENDAR_TOKEN"]:
        token_bytes = base64.b64decode(secrets["GOOGLE_CALENDAR_TOKEN"])
        creds = pickle.loads(token_bytes)

    # If token is missing or invalid, raise error
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                "Google Calendar token not found or expired. "
                "Generate it locally and update Streamlit secrets."
            )

    return creds
