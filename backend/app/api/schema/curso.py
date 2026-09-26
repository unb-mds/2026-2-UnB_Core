from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from typing import List

class CursoBase(SQLModel):
    nome: str
    sigla: str
    ativo: bool = True


class Curso(CursoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    disciplina_id: List[int] = Field(default_factory=list, sa_column=Column(JSON))



class CursoCreate(CursoBase):

    pass

class CursoGet(CursoBase):
    disciplina_id: List[int] = Field(default_factory=list, sa_column=Column(JSON))



