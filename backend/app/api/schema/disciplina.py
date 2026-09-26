import re

from fastapi import APIRouter,HTTPException,Depends
from pydantic import AfterValidator, validator
from sqlmodel import SQLModel, Field, Session, create_engine, select,select, col
from typing import  Annotated,List
from datetime import datetime

from backend.app.api.schema.curso import Curso,CursoGet
from sqlalchemy import Column, JSON

def get_session():
    with Session(engine) as session:
        yield session

def codigoDisciplina(value: str) ->str:
    upper = value.upper()
    upper = upper.replace("-", "")
    departamento = re.split(r'(\d+)', upper)[0]
    try:
        codigo = re.split(r'(\d+)', upper)[1]
    except IndexError:
        raise ValueError("falta departamento ou codigo da disciplina")
    if(departamento == "" or codigo == ''):
        raise ValueError("falta departamento ou codigo da disciplina")
    departamentos_validos = ["CIC","MAT","FCTE","FGA"] # troca isso para um database com todos os codgios de disciplina no sigaa
    if departamento not in departamentos_validos:
        raise ValueError("Departamento Não valido")

    if  0<int(codigo)<9999:
         return departamento + "-" + codigo
    else:
        raise ValueError("codigo não valido")

class DisciplinaBase(SQLModel):
    codigo: Annotated[str, AfterValidator(codigoDisciplina)]
    nome: str
    periodo: datetime
    ativo : bool



class Disciplina(DisciplinaBase,table = True):
    id: int | None = Field(default=None,
                           primary_key=True)
    curso_id : List[int] = Field(default_factory=list, sa_column=Column(JSON))
    #curso_id : list[int]  = Field(default=[], sa_column=Column(ARRAY(Integer)))  #removi temporarimente,pois usa postgresql
    #obs tambem da para colocar o curso_id como uma string,so tem que criar uma função que faz isso automaticamente

class DisciplinaCreate(DisciplinaBase):
    pass

class DisciplinaGet(DisciplinaBase):
    id : int


#router
disciplina_router = APIRouter()
crud_disciplina_router = APIRouter()

#databae
sqlite_file_name = "Disciplinas.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

@disciplina_router.get("/{curso_id}/disciplina",response_model=list[Disciplina])
async def GetListaCurso(curso_id : int,session : Session = Depends(get_session)):
    cursoProcurado =  session.get(Curso,curso_id)
    if not cursoProcurado:
        raise HTTPException(status_code=404,
                             detail=f"não foi encontrado um curso com id {curso_id} ")
    curso_procurado = CursoGet.model_validate(cursoProcurado)
    id_disciplinas = curso_procurado.disciplina_id
    if not id_disciplinas:
        return []

        # O uso correto do col()
    disciplinas = select(Disciplina).where(col(Disciplina.id).in_(id_disciplinas))

    lista_disciplina = session.exec(disciplinas).all()
    return lista_disciplina


@crud_disciplina_router.post("/criar", response_model=Disciplina)
async def post_disciplina(disciplina : DisciplinaCreate, session : Session = Depends(get_session)):
    if not disciplina:
        raise HTTPException(status_code=422,
                            detail = "Erro de entrada ou faltou parametro ou tipo errado")

    disciplina_db = Disciplina.model_validate(disciplina)
    session.add(disciplina_db)
    session.commit()
    session.refresh(disciplina_db)
    return disciplina_db

@crud_disciplina_router.get("/{id_disciplina}",response_model=DisciplinaGet)
async def get_disciplina(id_disciplina : int,session : Session = Depends(get_session)):
    disciplinaProcurar = session.get(Disciplina, id_disciplina)
    if not disciplinaProcurar:
        raise HTTPException(status_code=404,
                            detail=f"publicação com Id {id_disciplina} não existe")
    disciplina = DisciplinaGet.model_validate(disciplinaProcurar)
    return disciplina





