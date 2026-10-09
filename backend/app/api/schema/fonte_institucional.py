from datetime import datetime

from pydantic import field_validator, HttpUrl, AfterValidator
from sqlmodel import SQLModel, Field, AutoString


class FonteInstitucionalBase(SQLModel):
    nome: str
    unidade_responsavel: str
    url_oficial: HttpUrl  =   Field(default = None,unique=True, index=True, sa_type=AutoString)
    frequencia_verificacao: str #para que isso serve?
    estado: str | None

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor: str) -> str:
        estados_permitidos = [
            "ativa",
            "pausada",
            "indisponivel",
        ]

        if valor not in estados_permitidos:
            raise ValueError(
                f"estado deve ser um dos seguintes: {estados_permitidos}"
            )

        return valor
def verificar_fonte_oficial(value : HttpUrl) -> str:
    if not value or  value == "/":
        return "sem fonte"
    else :
        return str(value)


class FonteInstitucional(FonteInstitucionalBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ultima_verificacao : datetime | None




class FonteInstitucionalCreate(FonteInstitucionalBase):
    pass
