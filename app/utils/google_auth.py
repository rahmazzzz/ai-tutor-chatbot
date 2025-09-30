# app/utils/google_auth.py
import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import streamlit as st

# Load secrets from Streamlit
secrets = st.secrets
SCOPES = secrets["GOOGLE_CALENDAR_SCOPES"].split(",")
CREDS_JSON = secrets["GOOGLE_CLIENT_SECRET_JSON"]

def get_google_credentials():
    creds = None

    # Load token from Streamlit secrets if available
    if "GOOGLE_CALENDAR_TOKEN" in st.secrets:
        token_bytes = st.secrets["GOOGLE_CALENDAR_TOKEN"].encode()
        creds = pickle.loads(token_bytes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Write client secret JSON to temp file
            with open("temp_credentials.json", "w") as f:
                json.dump(json.loads(CREDS_JSON), f)

            flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

            os.remove("temp_credentials.json")  # cleanup

            # Optional: show token to save back to Streamlit secrets
            st.write("⚠️ Copy this token to your Streamlit secrets as 'GOOGLE_CALENDAR_TOKEN'")
            token_bytes = pickle.dumps(creds)
            st.write(token_bytes.decode("latin1"))

    return creds
