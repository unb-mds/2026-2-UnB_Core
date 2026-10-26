from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import field_validator, HttpUrl
from sqlmodel import SQLModel, Field, AutoString, Session
#session
from backend.app.db import get_session
from backend.app.api.schema.usuario import Usuario, verificar_admin

publicacao_router = APIRouter()
def verificar_fonte_oficial(value : HttpUrl) -> str:
    if not value or  value == "/":
        raise HTTPException(status_code=422 ,detail="Url_oficial é parametro obrigatorio")
    else :
        return str(value)




class PublicacaoInstitucionalBase(SQLModel):
    titulo: str
    resumo: str
    categoria : str
    unidade_responsavel: str
    curso_id: int | None = None
    estado: str = Field(default="ativa")
    prazo_fim: datetime | None = Field(default=None)


    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor: str | None) -> str:
        if valor is None:
            return "ativa"
        estados_permitidos = [
            "ativa",
            "inativa",
            "Sem informação"
        ]

        if valor not in estados_permitidos:
            raise ValueError(
                f"estado deve ser um dos seguintes: {estados_permitidos}"
            )

        return valor

class PublicacaoInstitucional(
    PublicacaoInstitucionalBase,
    table=True,
):
    publicacao_id: int | None = Field(default=None, primary_key=True)
    publicado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    url_oficial: str

    @property
    def id(self) -> int | None:
        return self.publicacao_id

    @id.setter
    def id(self, value: int | None) -> None:
        self.publicacao_id = value

    

class PublicacaoInstitucionalCreate(PublicacaoInstitucionalBase):
    url_oficial: HttpUrl = Field(unique=True, index=True, sa_type=AutoString)


class PublicacaoInstitucionalGet(PublicacaoInstitucionalBase):
    publicacao_id: int
    url_oficial: str | None = None
    publicado_em: datetime | None = None
    aviso: str = "Atenção os dados aqui não substituem a fonte oficial"

    @property
    def id(self) -> int:
        return self.publicacao_id


class PublicacaoInstitucionalLista(SQLModel):
    itens: list[PublicacaoInstitucionalGet]



@publicacao_router.get("/{id}", response_model=PublicacaoInstitucionalGet)
def get_publicacao(id: int, session: Session = Depends(get_session)):
    from backend.app.services.publicacao_service import detalhar_publicacao

    return detalhar_publicacao(id, session)

@publicacao_router.get("", response_model=PublicacaoInstitucionalLista)
def get_lista_publicacao(
    session: Session = Depends(get_session),
    *,
    termo: str | None = None,
    categoria: str | None = None,
    unidade: str | None = None,
    curso_id: int | None = None,
    estado: str | None = None,
    prazo_fim: str | None = None,
):
    from backend.app.services.publicacao_service import listar_publicacoes

    return {
        "itens": listar_publicacoes(
            session,
            termo=termo,
            categoria=categoria,
            unidade=unidade,
            curso_id=curso_id,
            estado=estado,
            prazo_fim=prazo_fim,
        )
    }



@publicacao_router.post("")
def post_publicacao(publicacao: PublicacaoInstitucionalCreate,session : Session = Depends(get_session),
                          admin : Usuario = Depends(verificar_admin)):
    publicacao = publicacao.model_dump()
    publicacao["url_oficial"] = str(publicacao["url_oficial"])
    if not publicacao:
        raise HTTPException(status_code=422,
                            detail="Erro de entrada, faltou parametro ou tipo errado")# colocar mais detalhes depois
    publicacao_db = PublicacaoInstitucional.model_validate(publicacao)
    session.add(publicacao_db)
    session.commit()
    session.refresh(publicacao_db)
    return publicacao_db