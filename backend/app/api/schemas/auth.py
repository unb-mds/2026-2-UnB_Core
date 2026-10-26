from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CadastroRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class UsuarioPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    perfil: str
    ativo: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioPublico
