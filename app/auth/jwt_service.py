from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config.settings import settings

# JWT CONFIGURATION
# Algorithm used to sign the JWT
ALGORITHM = "HS256"

# CREATE ACCESS TOKEN
def create_access_token(
    user_id: int,
    email: str
) -> str:
    """
    Create a JWT access token for the authenticated user.
    """

    # Token expiration time
    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.jwt_expiration_minutes
        )
    )

    # Data stored inside the JWT
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }

    # Create and sign JWT
    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=ALGORITHM
    )
    return token