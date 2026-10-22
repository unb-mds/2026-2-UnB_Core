from datetime import datetime

from pydantic import field_validator, HttpUrl, AfterValidator
from sqlmodel import SQLModel, Field, AutoString


class FonteInstitucionalBase(SQLModel):
    nome: str
    unidade_responsavel: str
    url_oficial: str = Field(unique=True, index=True)
    frequencia_verificacao: str | None = Field(default="diaria") #para que isso serve?
    estado: str | None = Field(default="ativa")

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor: str | None) -> str | None:
        if valor is None:
            return "ativa"
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


def verificar_fonte_oficial(value: str) -> str:
    if not value or value == "/":
        return "sem fonte"
    else:
        return str(value)


class FonteInstitucional(FonteInstitucionalBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ultima_verificacao: datetime | None = Field(default=None)

    @property
    def url_base(self) -> str:
        return str(self.url_oficial)


class FonteInstitucionalCreate(FonteInstitucionalBase):
    pass
