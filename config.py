from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Tavily
    tavily_api_key: str
    
    # RAG API
    rag_api_url: str = "https://document-qna-rag.onrender.com"
    rag_namespace: str = "gibbs-2.pdf"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()