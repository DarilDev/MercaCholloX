from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_path: Path = BASE_DIR / "data" / "mercachollo.db"

    mercadona_base_url: str = "https://tienda.mercadona.es/api"
    mercadona_default_wh: str = "mad1"  # almacén/código postal por defecto (Madrid)

    overpass_url: str = "https://overpass-api.de/api/interpreter"
    osrm_url: str = "https://router.project-osrm.org"

    default_vehicle_consumption_l_per_100km: float = 6.5
    default_fuel_type: str = "gasoleo_a"  # coincide con las categorías del MITECO
    default_hourly_value_eur: float = 8.0
    worth_it_threshold_eur: float = 0.5

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
