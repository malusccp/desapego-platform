from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

class TokenInvalidoError(Exception):
    """Levantada quando o token é inválido"""

def hash_password(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")      
    sal = bcrypt.gensalt()                    
    hash_bytes = bcrypt.hashpw(senha_bytes, sal)   
    return hash_bytes.decode("utf-8")      


def verify_password(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))   


def create_access_token(user_id: int) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expira_em}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        raise TokenInvalidoError()

    return int(payload.get("sub"))