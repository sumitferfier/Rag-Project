from sqlalchemy import Column, Integer, String
from app.auth.database import Base
class User(Base):

    # Database table name
    __tablename__ = "users"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # User's email
    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    # Hashed password
    password = Column(
        String,
        nullable=False
    )