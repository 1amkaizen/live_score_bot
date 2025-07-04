from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    bot_token: str
    chat_id: int  # <- tambahkan ini

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
