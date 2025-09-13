from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def auth_sign_up(payload: dict) -> dict:
    """
    Register a new user in Supabase.
    Always returns a Python dict, never a JSONResponse object.
    """
    response = supabase.auth.sign_up(payload)
    return response if isinstance(response, dict) else response.__dict__


def auth_sign_in(payload: dict) -> dict:
    """
    Authenticate user with email and password.
    Always returns a Python dict, never a JSONResponse object.
    """
    response = supabase.auth.sign_in_with_password(payload)
    return response if isinstance(response, dict) else response.__dict__
