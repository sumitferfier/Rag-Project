from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.auth.database import get_db
from app.auth.models import User
from app.config.settings import settings


# JWT CONFIGURATION
ALGORITHM = "HS256"

# BEARER TOKEN SECURITY
security = HTTPBearer()


# GET CURRENT USER
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    # Get JWT token from Authorization header
    token = credentials.credentials

    try:

        # Decode and verify JWT
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[ALGORITHM]
        )

        # Get user ID from "sub" claim
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Find user in database
    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    # User does not exist
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    return user