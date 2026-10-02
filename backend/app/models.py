import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ProductStatus(str, enum.Enum):
    ATIVO = "ativo"
    VENDIDO = "vendido"


class ProductCategory(str, enum.Enum):
    ELETRONICOS = "eletronicos"
    MOVEIS = "moveis"
    ROUPAS = "roupas"
    LIVROS = "livros"
    ESPORTES = "esportes"
    CASA = "casa"
    VEICULOS = "veiculos"
    BRINQUEDOS = "brinquedos"
    OUTROS = "outros"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(20))
    senha_hash: Mapped[str] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    products: Mapped[list["Product"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    titulo: Mapped[str] = mapped_column(String(120))
    descricao: Mapped[str] = mapped_column(Text)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    # native_enum=False grava como VARCHAR + CHECK: portátil entre SQLite e PostgreSQL
    # e evita ALTER TYPE ao adicionar novas categorias.
    categoria: Mapped[ProductCategory] = mapped_column(
        Enum(ProductCategory, native_enum=False, length=30, values_callable=lambda e: [m.value for m in e])
    )
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]),
        default=ProductStatus.ATIVO,
        server_default=ProductStatus.ATIVO.value,
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped[User] = relationship(back_populates="products")

    __table_args__ = (
        # Atende a listagem pública: WHERE status = 'ativo' [AND categoria = ?] ORDER BY criado_em DESC
        Index("ix_products_status_categoria_criado_em", "status", "categoria", "criado_em"),
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} titulo={self.titulo!r} status={self.status.value if self.status is not None else None }   >"
