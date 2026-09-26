from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel, Field


class DenunciaBase(SQLModel):
    autor_id: int
    publicacao_id: int | None = None
    conteudo_id: int | None = None
    tipo: str
    descricao: str
    estado: str = "aberta"

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor: str) -> str:
        estados_permitidos = [
            "aberta",
            "em_analise",
            "resolvida",
            "descartada",
        ]

        if valor not in estados_permitidos:
            raise ValueError(
                f"estado deve ser um dos seguintes: {estados_permitidos}"
            )

        return valor


class Denuncia(DenunciaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    criada_em: datetime = Field(default_factory=datetime.now)
    atualizada_em: datetime = Field(default_factory=datetime.now

class DenunciaCreate(DenunciaBase):
    pass
