from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.models import Product, ProductStatus, ProductCategory
from app.schemas import ProductCreate


class AnuncioNaoEncontradoError(Exception):
    """Levantada quando não existe um anúncio com o id informado."""

def criar_produto(db: Session, dados: ProductCreate, owner_id: int) -> Product:
    produto = Product(
        owner_id=owner_id,
        titulo=dados.titulo,
        descricao=dados.descricao,
        preco=dados.preco,
        categoria=dados.categoria
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def listar_produtos(db: Session, page: int, size: int, 
    categoria: ProductCategory | None = None,
    q: str | None = None) -> tuple[list[Product], int]:
    filtro = [Product.status == ProductStatus.ATIVO]

    if categoria:
        filtro.append(Product.categoria == categoria)

    if q:
       filtro.append( or_(Product.titulo.ilike(f"%{q}%"), Product.descricao.ilike(f"%{q}%")))

    total = db.scalar(select(func.count()).select_from(Product).where(*filtro))

    consulta = (
        select(Product)
        .where(*filtro)
        .order_by(Product.criado_em.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    itens = db.scalars(consulta).all()
    return itens, total


def procurar_anuncio_id(db: Session, id_produto: int ) -> Product:
    anuncio = db.get(Product, id_produto)

    if not anuncio:
        raise AnuncioNaoEncontradoError()

    return anuncio




    
