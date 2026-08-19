from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

settings.database_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{settings.database_path}", connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, connection_record) -> None:
    # WAL deja leer mientras alguien escribe (en vez de bloquear el fichero
    # entero); busy_timeout hace que una escritura concurrente espere en vez
    # de fallar al instante con "database is locked" — puede pasar ya con el
    # worker de refresco corriendo a la vez que alguien usa la app.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from app import models  # noqa: F401 — registra los modelos en Base.metadata

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
