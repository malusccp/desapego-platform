from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


from app.db.database import get_db
from app.schemas import UserCreate, UserRead, Token, LoginRequest
from app.services.user_service import criar_usuario, autenticar_usuario
from app.core.security import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(dados: UserCreate, db: Session = Depends(get_db)):
    return criar_usuario(db, dados)


@router.post("/login", response_model=Token)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, dados.email, dados.senha)
    token = create_access_token(usuario.id)
    return Token(access_token=token)