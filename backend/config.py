from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ollama_api_key: str

    # Tell Pydantic to read from a .env file
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
