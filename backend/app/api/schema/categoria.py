from sqlmodel import SQLModel, Field


class CategoriaBase(SQLModel):
    nome: str = Field(min_length=1, max_length=100, index=True)
    descricao: str | None = Field(default=None, max_length=255)


class Categoria(CategoriaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id: int

