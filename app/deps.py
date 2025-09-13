# app/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.clients.supabase_api_client import supabase
import logging

logger = logging.getLogger("deps")
security = HTTPBearer()

def get_current_user(credentials=Depends(security)):
    """
    Extracts the current user from the Authorization header.
    Returns a dictionary with 'sub', 'email', and 'token'.
    Raises HTTPException if the token is invalid or Supabase user not found.
    """
    token = credentials.credentials
    logger.info(f"Token received: {token}")

    try:
        response = supabase.auth.get_user(token)
        user = response.user
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Supabase token",
            )
        # Return current user info including the JWT token
        return {
            "sub": user.id,
            "email": user.email,
            "token": token
        }
    except Exception as e:
        logger.error(f"Supabase auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Supabase authentication failed: {str(e)}"
        )


def admin_required(current_user=Depends(get_current_user)):
    """
    Dependency to ensure the user has an 'admin' role.
    Raises HTTPException if not an admin.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
