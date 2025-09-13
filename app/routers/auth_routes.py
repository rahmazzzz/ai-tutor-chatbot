# app/routes/auth_routes.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user_schema import UserCreate, UserOut
from app.schemas.auth import LoginRequest, AuthResponse
from app.deps import get_current_user
from app.container.core_container import AuthContainer

# Configure logger
logger = logging.getLogger("auth_routes")
logger.setLevel(logging.INFO)

# Optional: add console handler if not configured globally
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Set the prefix here to avoid double "/auth" when including in main.py
router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_container = AuthContainer()


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    """
    Register a new user.
    """
    logger.info(f"Attempting to register user: {user.email}")
    try:
        result = await auth_container.service.register(
            email=user.email,
            password=user.password,
            username=user.username
        )
        logger.info(f"User registered successfully: {user.email}")
        return result
    except Exception as e:
        logger.error(f"Error registering user {user.email}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login and get JWT token.
    """
    logger.info(f"Login attempt for user: {request.email}")
    try:
        result = await auth_container.service.login(
            email=request.email,
            password=request.password
        )
        logger.info(f"User logged in successfully: {request.email}")
        return result
    except Exception as e:
        logger.error(f"Login failed for user {request.email}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: UserOut = Depends(get_current_user)):
    """
    Get the current logged-in user.
    """
    logger.info(f"Fetching current user info: {current_user.email}")
    return current_user
