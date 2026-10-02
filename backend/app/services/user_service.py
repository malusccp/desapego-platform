from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas import UserCreate


class EmailJaCadastradoError(Exception):
    """Levantada quando já existe um usuário com o e-mail informado."""

class CredenciaisInvalidasError(Exception):
    """Levantada quando não existe um usuário com aquele email ou senha não confere"""

def criar_usuario(db: Session, dados: UserCreate) -> User:

    existente = db.scalar(select(User).where(User.email == dados.email))
    if existente:
        raise EmailJaCadastradoError()


    usuario = User(
        nome=dados.nome,
        email=dados.email,
        telefone=dados.telefone,
        senha_hash=hash_password(dados.senha),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar_usuario(db: Session, email: str, senha: str) -> User:
    usuario = db.scalar(select(User).where(User.email == email))

    if usuario is None or not verify_password(senha, usuario.senha_hash):
       raise CredenciaisInvalidasError()

    return usuario
