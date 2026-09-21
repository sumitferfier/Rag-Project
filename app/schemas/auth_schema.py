from pydantic import BaseModel, EmailStr

# REGISTER REQUEST
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

# REGISTER RESPONSE
class RegisterResponse(BaseModel):

    message: str
    email: EmailStr

# LOGIN REQUEST
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# LOGIN RESPONSE
class LoginResponse(BaseModel):
    access_token: str
    token_type: str