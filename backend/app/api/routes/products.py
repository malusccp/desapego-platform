from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.models import User, ProductCategory
from app.schemas import ProductRead, ProductCreate, Page
from app.api.deps import get_current_user
from app.db.database import get_db
from app.services.product_service import criar_produto, listar_produtos, procurar_anuncio_id

router = APIRouter(prefix="/products", tags=["products"])


# TODO: POST   /products        -> ProductRead (201)  (privada)
# TODO: PATCH  /products/{id}   -> ProductRead        (privada: somente o owner)
# TODO: DELETE /products/{id}   -> 204                (privada: somente o owner)

@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def criar(
    dados: ProductCreate,
    usuario: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return criar_produto(db, dados, usuario.id)


@router.get("", response_model=Page[ProductRead])
def listar(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db), categoria: ProductCategory | None = None, q: str | None = None
):
    itens, total = listar_produtos(db, page, size, categoria, q)
    return Page[ProductRead].build(itens, total, page, size)


@router.get("/{product_id}", response_model=ProductRead)
def buscar(product_id: int, db: Session = Depends(get_db)):
    anuncio = procurar_anuncio_id(db, product_id)
    return anuncio

    