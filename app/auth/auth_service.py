import bcrypt

# HASH PASSWORD
def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure bcrypt hash.
    """

    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )
    return hashed_password.decode("utf-8")

# VERIFY PASSWORD
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Check whether the entered password matches
    the stored bcrypt hash.
    """

    password_bytes = plain_password.encode("utf-8")

    hashed_password_bytes = (
        hashed_password.encode("utf-8")
    )

    return bcrypt.checkpw(
        password_bytes,
        hashed_password_bytes
    )