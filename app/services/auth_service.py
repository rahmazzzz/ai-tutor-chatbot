# app/services/auth_service.py
from app.clients.supabase_api_client import supabase
from app.schemas.auth import AuthResponse, UserResponse
from app.exceptions.base_exceptions import ValidationError
from app.exceptions.decorators import handle_exceptions


class AuthService:

    @handle_exceptions
    async def register(self, email: str, password: str, username: str = None) -> UserResponse:
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"username": username} if username else {}}
            })

            user = response.user
            if not user:
                raise ValidationError("No user returned from Supabase")

        except Exception as e:
            raise ValidationError(f"Supabase signup error: {str(e)}")

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.user_metadata.get("username") if user.user_metadata else None
        )

    @handle_exceptions
    async def login(self, email: str, password: str) -> AuthResponse:
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            user = response.user
            session = response.session
            if not user or not session:
                raise ValidationError("Invalid login response from Supabase")

        except Exception as e:
            raise ValidationError(f"Supabase login error: {str(e)}")

        user_model = UserResponse(
            id=user.id,
            email=user.email,
            username=user.user_metadata.get("username") if user.user_metadata else None
        )

        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            user=user_model
        )
    async def get_profile(self, user_id: str):
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if not response.data:
            return None
        return response.data[0]