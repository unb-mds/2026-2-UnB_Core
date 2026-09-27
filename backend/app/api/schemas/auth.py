from pydantic import BaseModel, EmailStr, Field


class CadastroRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=1, max_length=128)


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: str
    ativo: bool


class CadastroResponse(BaseModel):
    usuario: UsuarioResponse


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse