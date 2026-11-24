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
    # Resposta: o e-mail já foi validado na entrada. Revalidar aqui derrubaria a rota
    # inteira por causa de um único cadastro antigo ou fora do padrão.
    email: str
    perfil: str
    ativo: bool


class PerfilAtualizacao(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    senha_atual: str | None = Field(default=None, max_length=128)
    nova_senha: str | None = Field(default=None, min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioPublico
