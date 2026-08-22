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

    # Render (plan gratuito) reparte IPs de salida compartidas entre todos sus
    # clientes de la región — si otro proyecto agota la cuota de una de estas
    # APIs públicas, la IP compartida queda limitada para todos, no solo para
    # nosotros (verificado en directo, agosto 2026: /stores/nearby y /worth-it
    # devolvían vacío en Render para coordenadas con datos reales). Ninguna URL
    # individual es fiable al 100% por sí sola, así que cada servicio tiene una
    # lista con respaldo en vez de una única URL.
    overpass_urls: list[str] = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
    ]
    osrm_urls: list[str] = [
        "https://router.project-osrm.org",
        "https://routing.openstreetmap.de/routed-car",
    ]
    # Photon y Nominatim tienen formas de respuesta distintas (GeoJSON vs.
    # lista plana) — a diferencia de overpass_urls/osrm_urls no tiene sentido
    # una lista homogénea, se prueba Photon primero (pensado para
    # autocompletado) y Nominatim como respaldo.
    photon_url: str = "https://photon.komoot.io/api"
    nominatim_url: str = "https://nominatim.openstreetmap.org"
    miteco_url: str = (
        "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes"
        "/PreciosCarburantes/EstacionesTerrestres/"
    )
    # Verificado en directo: el lookup por EAN individual es fiable incluso
    # cuando la búsqueda general de OpenFoodFacts está degradada — el escáner
    # solo necesita esto, nunca busca por texto.
    openfoodfacts_url: str = "https://world.openfoodfacts.org/api/v2/product"

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
