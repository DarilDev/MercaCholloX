from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_path: Path = BASE_DIR / "data" / "mercachollo.db"
    # Vacío = SQLite local (database_path). En Render/producción se define
    # MERCACHOLLO_DATABASE_URL con la cadena de conexión de Postgres (Neon) —
    # ver docs/DECISIONS.md, sección "Arquitectura para escalar".
    database_url: str = ""

    mercadona_base_url: str = "https://tienda.mercadona.es/api"
    mercadona_default_wh: str = "mad1"  # almacén/código postal por defecto (Madrid)

    overpass_url: str = "https://overpass-api.de/api/interpreter"
    osrm_url: str = "https://router.project-osrm.org"
    miteco_url: str = (
        "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes"
        "/PreciosCarburantes/EstacionesTerrestres/"
    )

    default_vehicle_consumption_l_per_100km: float = 6.5
    default_fuel_type: str = "gasoleo_a"  # coincide con las categorías del MITECO
    default_hourly_value_eur: float = 8.0
    worth_it_threshold_eur: float = 0.5

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MERCACHOLLO_")

    @property
    def effective_database_url(self) -> str:
        if not self.database_url:
            return f"sqlite:///{self.database_path}"

        url = self.database_url
        # Neon/Render dan la URL como "postgres://..." o "postgresql://...",
        # que por defecto usa el driver psycopg2 (no instalado — se instaló
        # psycopg 3). La reescribimos para no depender de que se pegue bien
        # a mano cada vez.
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()
