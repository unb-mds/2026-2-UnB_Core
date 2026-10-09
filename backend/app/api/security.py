from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.app.settings.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuario/login")


def criar_access_token(usuario_id: int, perfil: str) -> str:
    agora = datetime.now(timezone.utc)
    expiracao = agora + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(usuario_id),
        "perfil": perfil,
        "iat": agora,
        "exp": expiracao,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def obter_usuario_token(
    token: str = Depends(oauth2_scheme),
) -> dict:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError:
        raise credenciais_invalidas

    if not payload.get("sub"):
        raise credenciais_invalidas

    return payload