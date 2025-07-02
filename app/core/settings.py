import os

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        ".env",
    )
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV)
    project_name: str = "Tracker"

    authjwt_secret_key: str
    authjwt_algorithm: str = "HS256"

    pg_user: str
    pg_password: str
    pg_host: str
    pg_port: int
    pg_db: str
    pg_echo: bool = False

    @property
    def database_dsn(self):
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
    
    @property
    def database_dsn_not_async(self):
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


settings = Settings()

default_categories = ["Еда", "Транспорт", "Развлечение", "Услуги", "Другое"]
