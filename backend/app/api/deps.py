from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import TokenInvalidoError, decode_access_token
from app.db.database import get_db
from app.models import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials)                       # passo 2: leia o token (dica: credentials.credentials)
    usuario = db.get(User, user_id)      # passo 3
    if not usuario:                              # passo 4
        raise TokenInvalidoError()
    return usuario                       # passo 5