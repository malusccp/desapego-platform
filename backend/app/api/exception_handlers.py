from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.user_service import EmailJaCadastradoError, CredenciaisInvalidasError
from app.services.product_service import AnuncioNaoEncontradoError
from app.core.security import TokenInvalidoError


async def email_ja_cadastrado_handler(request: Request, exc: EmailJaCadastradoError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "E-mail já cadastrado."})


async def credenciais_invalidas_handler(request: Request, exc: CredenciaisInvalidasError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "E-mail ou senha inválidos."})


async def token_invalido_handler(request: Request, exc: TokenInvalidoError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Token inválido ou expirado."})

async def anuncio_nao_encontrado_handler(request: Request, exc: AnuncioNaoEncontradoError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Anúncio não encontrado"})

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(EmailJaCadastradoError, email_ja_cadastrado_handler)
    app.add_exception_handler(CredenciaisInvalidasError, credenciais_invalidas_handler)
    app.add_exception_handler(TokenInvalidoError, token_invalido_handler)
    app.add_exception_handler(AnuncioNaoEncontradoError, anuncio_nao_encontrado_handler)