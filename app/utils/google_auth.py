# app/utils/google_auth.py

import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from pathlib import Path

# Load Google settings from Streamlit secrets
GOOGLE_SECRETS = st.secrets["google"]

SCOPES = [GOOGLE_SECRETS["scopes"]]

# Paths for storing token (locally only – Streamlit Cloud restarts containers so sessions reset)
TOKEN_PATH = Path("google_token.pickle")


def get_google_credentials():
    creds = None

    # Try to load existing token
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # If no creds or expired, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Build InstalledAppFlow from secrets directly (no file needed)
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": GOOGLE_SECRETS["client_id"],
                        "project_id": GOOGLE_SECRETS["project_id"],
                        "auth_uri": GOOGLE_SECRETS["auth_uri"],
                        "token_uri": GOOGLE_SECRETS["token_uri"],
                        "auth_provider_x509_cert_url": GOOGLE_SECRETS[
                            "auth_provider_x509_cert_url"
                        ],
                        "client_secret": GOOGLE_SECRETS["client_secret"],
                        "redirect_uris": GOOGLE_SECRETS["redirect_uris"],
                    }
                },
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        # Save token locally (may not persist on Streamlit Cloud between sessions)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return creds
