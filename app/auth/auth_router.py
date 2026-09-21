from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.database import get_db
from app.auth.models import User

from app.auth.auth_service import (
    hash_password,
    verify_password
)

from app.auth.jwt_service import (
    create_access_token
)

from app.schemas.auth_schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse
)

# AUTH ROUTER
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# REGISTER
@router.post(
    "/register",
    response_model=RegisterResponse
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = hash_password(
        request.password
    )

    # Create new user
    user = User(
        email=request.email,
        password=hashed_password
    )

    # Save user to database
    db.add(user)
    db.commit()
    db.refresh(user)

    # Return response
    return RegisterResponse(
        message="User registered successfully",
        email=user.email
    )

# LOGIN
@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    # Find user by email
    user = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    # User not found
    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    password_valid = verify_password(
        request.password,
        user.password
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT access token
    access_token = create_access_token(
        user_id=user.id,
        email=user.email
    )

    # Return JWT token
    return LoginResponse(
        access_token=access_token,
        token_type="bearer"
    )