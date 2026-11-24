from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.app.domain import PerfilUsuario


class UsuarioAdminCriacao(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    perfil: PerfilUsuario = PerfilUsuario.USUARIO


class UsuarioAdminAtualizacao(BaseModel):
    perfil: PerfilUsuario | None = None
    ativo: bool | None = None


class UsuarioAdminPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    # Resposta: o e-mail já foi validado na entrada. Revalidar aqui derrubaria a lista
    # inteira de usuários por causa de um único cadastro fora do padrão.
    email: str
    perfil: PerfilUsuario
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
