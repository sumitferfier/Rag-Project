# LLM SERVICE
# Responsibility:
#   Create and provide the Gemini Chat LLM.
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings

class LlmService:

    # INITIALIZE LLM
    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_llm_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.2
        )

    # GET LLM
    def get_llm(self):
        return self.llm