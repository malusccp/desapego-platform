import math
import re
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Generic, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    PlainSerializer,
    field_validator,
    model_validator,
)

from app.models import ProductCategory, ProductStatus

# Pydantic v2 serializa Decimal como string no JSON; aqui o preço sai como número para o frontend.
Preco = Annotated[
    Decimal,
    Field(gt=0, max_digits=10, decimal_places=2, examples=[149.90]),
    PlainSerializer(float, return_type=float, when_used="json"),
]


def _normalizar_telefone(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor)
    if not 10 <= len(digitos) <= 13:
        raise ValueError("Telefone deve conter DDD e número (10 a 13 dígitos).")
    return digitos


# ---------------------------------------------------------------------------
# Usuários
# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    nome: str = Field(min_length=2, max_length=120, examples=["Maria Silva"])
    email: EmailStr
    telefone: str = Field(examples=["(11) 98765-4321"])

    @field_validator("nome")
    @classmethod
    def _strip_nome(cls, v: str) -> str:
        return v.strip()

    @field_validator("email")
    @classmethod
    def _lower_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("telefone")
    @classmethod
    def _validar_telefone(cls, v: str) -> str:
        return _normalizar_telefone(v)


class UserCreate(UserBase):
    senha: str = Field(min_length=8, max_length=72, examples=["senhaSegura123"])  # 72 = limite do bcrypt


class UserRead(UserBase):
    """Dados do próprio usuário autenticado (nunca inclui senha_hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime


class OwnerPublic(BaseModel):
    """Dados do vendedor exibidos no anúncio para o comprador entrar em contato."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    telefone: str


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

    @field_validator("email")
    @classmethod
    def _lower_email(cls, v: str) -> str:
        return v.lower()


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # id do usuário (o padrão JWT exige string)
    exp: int


# ---------------------------------------------------------------------------
# Anúncios
# ---------------------------------------------------------------------------
class ProductBase(BaseModel):
    titulo: str = Field(min_length=3, max_length=120, examples=["Bicicleta aro 29"])
    descricao: str = Field(min_length=10, max_length=5000)
    preco: Preco
    categoria: ProductCategory


class ProductCreate(ProductBase):
    """O status inicial é sempre 'ativo' e o owner_id vem do token, nunca do body."""


class ProductUpdate(BaseModel):
    """Atualização parcial (PATCH): apenas os campos enviados são alterados."""

    titulo: str | None = Field(default=None, min_length=3, max_length=120)
    descricao: str | None = Field(default=None, min_length=10, max_length=5000)
    preco: Preco | None = None
    categoria: ProductCategory | None = None
    status: ProductStatus | None = None

    @model_validator(mode="after")
    def _ao_menos_um_campo(self) -> "ProductUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        # Campos obrigatórios no modelo não podem ser anulados explicitamente
        nulos = [campo for campo in self.model_fields_set if getattr(self, campo) is None]
        if nulos:
            raise ValueError(f"Os campos {nulos} não podem ser nulos.")
        return self


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ProductStatus
    criado_em: datetime
    atualizado_em: datetime
    owner: OwnerPublic


# ---------------------------------------------------------------------------
# Paginação / filtros
# ---------------------------------------------------------------------------
class ProductFilters(BaseModel):
    """Query params da listagem pública (usar com `Annotated[ProductFilters, Query()]`)."""

    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    categoria: ProductCategory | None = None
    q: str | None = Field(default=None, max_length=100, description="Busca no título e na descrição")


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def build(cls, items: list[T], total: int, page: int, size: int) -> "Page[T]":
        return cls(items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0)
