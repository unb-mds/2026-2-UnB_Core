from datetime import datetime

from pydantic import field_validator,HttpUrl
from sqlmodel import SQLModel, Field


class FonteInstitucionalBase(SQLModel):
    nome: str
    unidade_responsavel: str
    url_base: HttpUrl
    url_base : str = str(url_base)
    frequencia_verificacao: str #para que isso serve?
    estado: str | None
    ultima_verificacao: datetime | None = None #Vai sempre deixar a verificação como None

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


class FonteInstitucional(FonteInstitucionalBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class FonteInstitucionalCreate(FonteInstitucionalBase):
    pass
