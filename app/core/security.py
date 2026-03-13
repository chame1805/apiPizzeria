import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_segura_cambiala_en_produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _decode(token: str) -> dict:
    """Decodifica el token y lanza 401 si es inválido."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Dependencia básica: solo verifica que el token sea válido y retorna el user_id."""
    payload = _decode(token)
    user_id: int = payload.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def get_current_rol(token: str = Depends(oauth2_scheme)) -> str:
    """Dependencia que retorna el rol del usuario autenticado."""
    payload = _decode(token)
    rol: str = payload.get("rol", "MESERO")
    return rol


def require_rol(*roles_permitidos: str):
    """
    Fábrica de dependencias para proteger endpoints por rol.

    Uso:
        @router.post("/", dependencies=[Depends(require_rol("ADMIN"))])
        @router.post("/", dependencies=[Depends(require_rol("ADMIN", "COCINERO"))])
    """
    def _check(token: str = Depends(oauth2_scheme)) -> str:
        payload = _decode(token)
        rol: str = payload.get("rol", "MESERO")
        if rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {' o '.join(roles_permitidos)}",
            )
        return rol
    return _check


def decode_token_ws(token: str) -> Optional[int]:
    """
    Variante para WebSocket (sin Depends). Retorna user_id o None si falla.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("id")
    except JWTError:
        return None


def decode_token_ws_payload(token: str) -> Optional[dict]:
    """
    Variante para WebSocket que retorna payload completo o None si falla.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
