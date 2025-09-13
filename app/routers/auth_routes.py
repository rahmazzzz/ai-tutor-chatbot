# app/routers/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_schema import UserCreate, UserOut
from app.schemas.auth import LoginRequest, AuthResponse
from app.services.auth_service import AuthService
from app.deps import get_current_user
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()
logger = logging.getLogger("auth_routes")
logging.basicConfig(level=logging.INFO)


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    logger.info(f"Register request received for email: {user.email}, username: {user.username}")
    try:
        result = await auth_service.register(
            email=user.email,
            password=user.password,
            username=user.username
        )
        logger.info(f"User registered successfully: {getattr(result, 'email', None)}")
        return result
    except Exception as e:
        logger.error(f"Unexpected error during registration for {user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    logger.info(f"Login request received for email: {request.email}")
    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password
        )

        # Use getattr to avoid crashes if user/email is missing
        user_email = getattr(result.user, "email", "unknown")
        logger.info(f"User logged in successfully: {user_email}")

        return result
    except Exception as e:
        logger.error(f"Login failed for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: UserOut = Depends(get_current_user)):
    return current_user
