from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://tasks:tasks@localhost:5432/tasks"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "tasks-dev-password"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
