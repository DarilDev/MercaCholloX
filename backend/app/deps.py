from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User


def get_current_user(
    x_device_id: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> User:
    """Resuelve (o crea) el usuario a partir del header X-Device-Id que manda
    el móvil. Identidad anónima por dispositivo, no login real — ver
    models.User y docs/DECISIONS.md. Nunca aceptar un id de usuario que venga
    de la URL/body: "de quién son estos datos" se resuelve siempre aquí,
    en servidor, a partir de lo que manda el cliente como identidad propia."""
    if not x_device_id:
        raise HTTPException(status_code=400, detail="Falta el header X-Device-Id")

    user = db.query(User).filter(User.device_uuid == x_device_id).first()
    if user is None:
        user = User(device_uuid=x_device_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
