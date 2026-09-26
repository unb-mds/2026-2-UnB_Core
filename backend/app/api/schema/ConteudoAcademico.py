from datetime import datetime
from pydantic import HttpUrl, field_validator
from sqlmodel import SQLModel, Field, AutoString

from SubmissaoBase import SubmissaoBase,Submissao

class ConteudoAcademicoBase(SubmissaoBase):
    corpo_ou_url : HttpUrl =  Field(unique=True, index=True, sa_type=AutoString)
    corpo_ou_url : str = str(corpo_ou_url)



class ConteudoAcademico(Submissao,ConteudoAcademicoBase,table = True):
    pass

class ConteudoAcademicoCreate(ConteudoAcademicoBase):
    pass
