from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    bot_token: str
    chat_ids: str  # dari .env

    @property
    def chat_id_list(self) -> list[int]:
        return [int(x.strip()) for x in self.chat_ids.split(',') if x.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
