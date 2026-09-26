from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import field_validator, HttpUrl,AfterValidator
from sqlmodel import SQLModel, Field, AutoString,Session, create_engine,select,Relationship
from typing import Annotated

publicacao_router = APIRouter()
def verificar_fonte_oficial(value : HttpUrl) -> str:
    if not value or  value == "/":
        return "sem fonte"
    else :
        return str(value)



sqlite_file_name = "database_publicaco_institucional.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)
class PublicacaoInstitucionalBase(SQLModel):
    fonte_id: int
    titulo: str
    resumo: str
    categoria: str
    unidade_responsavel: str
    curso_id: int | None = None
    url_oficial: HttpUrl  =   Field(default = None,unique=True, index=True, sa_type=AutoString)
    publicado_em: datetime | None = None #Vai sempre deixar a verificação como None
    prazo_inicio: datetime | None = None # mesmo problema do de cima
    prazo_fim: datetime | None = None # mesmo problema
    estado: str = "nao_verificada"
    ultima_verificacao: datetime | None = None #mesmo problama

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor: str) -> str:
        estados_permitidos = [
            "ativa",
            "encerrada",
            "cancelada",
            "desatualizada",
            "nao_verificada",
            "sem_prazo",
        ]

        if valor not in estados_permitidos:
            raise ValueError(
                f"estado deve ser um dos seguintes: {estados_permitidos}"
            )

        return valor
    @field_validator("url_oficial")
    @classmethod
    def validar_url(cls,valor : HttpUrl):
        if(valor == None):
            return "/"
        return valor


def get_session():
    with Session(engine) as session:
        yield session

class PublicacaoInstitucional(
    PublicacaoInstitucionalBase,
    table=True,
):
    publicacao_id: int | None = Field(default=None, primary_key=True)
    url_oficial : Annotated[str, AfterValidator(verificar_fonte_oficial)]


class PublicacaoInstitucionalCreate(PublicacaoInstitucionalBase):
    url_oficial: Annotated[str, AfterValidator(verificar_fonte_oficial)]



class PublicacaoInstitucionalGet(PublicacaoInstitucionalBase):
    publicacao_id : int
    aviso : str = "Atenção os dados aqui não substituem a fonte oficial"




@publicacao_router.get("/{publicacao_id}",response_model=PublicacaoInstitucionalGet)
async def get_publicacao(publicacao_id: int, session : Session = Depends(get_session)):

    publicacaoProcurar = session.get(PublicacaoInstitucional,publicacao_id)
    if not publicacaoProcurar:
        raise HTTPException(status_code=404,
                                detail=f"publicação com Id {publicacao_id} não existe")
    publicacao = PublicacaoInstitucionalGet.model_validate(publicacaoProcurar)

    return publicacao

@publicacao_router.get("/",response_model=list[PublicacaoInstitucionalGet])
async def get_lista_publicacao(session : Session = Depends(get_session)):
    publicacao = select(PublicacaoInstitucional)
    lista_publicacao = session.exec(publicacao).all()
    return lista_publicacao



@publicacao_router.post("/criar")
async def post_publicacao(publicacao: PublicacaoInstitucionalCreate,session : Session = Depends(get_session)):
    if not publicacao:
        raise HTTPException(status_code=422,
                            detail="Erro de entrada, faltou parametro ou tipo errado")# colocar mais detalhes depois
    publicacao_db = PublicacaoInstitucional.model_validate(publicacao)
    session.add(publicacao_db)
    session.commit()
    session.refresh(publicacao_db)
    return publicacao_db