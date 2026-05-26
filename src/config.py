"""Configuración del proyecto cargada desde .env."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Postgres
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")
    # Mongo
    MONGO_URL: str = os.getenv("MONGO_URL", "")
    # Cassandra (Astra)
    ASTRA_BUNDLE_PATH: str = os.getenv("ASTRA_BUNDLE_PATH", "")
    ASTRA_CLIENT_ID: str = os.getenv("ASTRA_CLIENT_ID", "")
    ASTRA_CLIENT_SECRET: str = os.getenv("ASTRA_CLIENT_SECRET", "")
    ASTRA_TOKEN: str = os.getenv("ASTRA_TOKEN", "")
    ASTRA_KEYSPACE: str = os.getenv("ASTRA_KEYSPACE", "uber_tp")
    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()


def validate() -> None:
    """Verifica que las credenciales criticas esten presentes. Lanza RuntimeError si falta alguna."""
    required = [
        "POSTGRES_URL", "MONGO_URL",
        "ASTRA_BUNDLE_PATH", "ASTRA_CLIENT_ID", "ASTRA_CLIENT_SECRET",
        "NEO4J_URI", "NEO4J_PASSWORD",
        "REDIS_HOST", "REDIS_PASSWORD",
    ]
    missing = [f for f in required if not getattr(settings, f)]
    if missing:
        raise RuntimeError(f"Variables de entorno faltantes en .env: {missing}")
