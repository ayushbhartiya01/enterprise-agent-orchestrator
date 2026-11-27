from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_api_key: str
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.3-70b-versatile"
    max_agent_steps: int = Field(default=6, ge=1, le=50)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
