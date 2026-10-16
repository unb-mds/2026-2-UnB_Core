from datetime import datetime
from pydantic import HttpUrl, field_validator
from sqlmodel import SQLModel, Field, AutoString
from fastapi import APIRouter

from SubmissaoBase import SubmissaoBase,Submissao

class ConteudoAcademicoBase(SubmissaoBase):
    pass    



class ConteudoAcademico(Submissao,ConteudoAcademicoBase,table = True):
    corpo_ou_url : str
    pass

class ConteudoAcademicoCreate(ConteudoAcademicoBase):
    corpo_ou_url : HttpUrl =  Field(unique=True, index=True, sa_type=AutoString)
    
CounteudoAcademico_router = APIRouter()

