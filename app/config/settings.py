from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # Gemini API key used for generating RAG answers
    gemini_api_key: str

    # Gemini model used for final answer generation
    gemini_llm_model: str = "gemini-3.5-flash-lite"


    # JINA EMBEDDINGS
    # Jina API key used for document/query embeddings
    jina_api_key: str

    # Jina embedding model
    jina_embedding_model: str = "jina-embeddings-v5-text-nano"


    # CHROMA
    # ChromaDB storage directory
    chroma_persist_directory: str = "./vector_db"

    # Uploaded PDF storage directory
    pdf_directory: str = "./data/pdfs"

    # JWT
    # Secret used to sign JWT tokens
    jwt_secret: str

    # token lifetime in minutes
    jwt_expiration_minutes: int = 60

    # PYDANTIC SETTINGS
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

# Create settings object
settings = Settings()