import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = ""
    WANDB_API_KEY: Optional[str] = None
    WANDB_PROJECT: str = "docintel"
    
    # Models - Updated to current available models
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Vector DB
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    COLLECTION_NAME: str = "documents"
    
    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Retrieval
    TOP_K: int = 5
    
    # Paths
    DATA_DIR: str = "./data/raw"
    PROCESSED_DIR: str = "./data/processed"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
