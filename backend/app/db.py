from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

_database_url = settings.effective_database_url
_is_sqlite = _database_url.startswith("sqlite")

if _is_sqlite:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    _database_url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)

if _is_sqlite:

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, connection_record) -> None:
        # WAL deja leer mientras alguien escribe (en vez de bloquear el fichero
        # entero); busy_timeout hace que una escritura concurrente espere en vez
        # de fallar al instante con "database is locked" — puede pasar ya con el
        # worker de refresco corriendo a la vez que alguien usa la app.
        # Solo aplica a SQLite — en Postgres (Neon) esto no hace falta.
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
