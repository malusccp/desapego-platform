from fastapi import APIRouter, Depends
from app.models import User
from app.schemas import UserRead
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def me(usuario: User = Depends(get_current_user)):
    return usuario


# TODO: GET /users/me/products -> Page[ProductRead]   (privada: anúncios do usuário logado)
