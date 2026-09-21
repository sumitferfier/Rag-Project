# Responsibility:
#   Define the structure of data coming into and going out
#   of our FastAPI endpoints.

from pydantic import BaseModel

class AskRequest(BaseModel):

    # User's question
    question: str