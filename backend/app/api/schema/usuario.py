from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from passlib.context import CryptContext
from sqlmodel import SQLModel, Field
from fastapi import HTTPException,Depends, APIRouter,FastAPI
from sqlmodel import SQLModel, Field, Session,select, col


from backend.app.api.security import criar_access_token, obter_usuario_token
from backend.app.api.schemas.auth import LoginResponse, UsuarioResponse
#session
from backend.app.db import get_session

#senhas hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
class UsuarioBase(SQLModel):

    email : EmailStr = Field(unique=True, index=True)
    nome : str
    #perfil : str  movi para a classe Usuario
    status : str #troquei o literal pois SQLModel não aceita literal
    ativo : bool = Field(default = False)
    @field_validator("status")
    def validate_status(cls,v):
        permitido = ["Online","Offline","Aparecer Offline","Ausente"]
        if v not in permitido:
            raise ValueError(f"deve ser um dos status a sequir {permitido}")
        return v

    

class Usuario(UsuarioBase,table = True):
    id: int | None = Field(default=None,
                           primary_key=True)
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)
    perfil : str = Field(default= "usuario")
    senha : str

    @field_validator("perfil")
    def validate_perfil(cls,v):
            permitido = ["usuario","moderador","administrador"]
            if v not in permitido:
                raise ValueError(f"Perfil de usuario não valido {v}")
            return v

class UsuarioCreate(UsuarioBase):
    senha : str 
    

class UsuarioLogin(SQLModel):
    email : EmailStr
    senha : str 

class get_current_user(BaseModel):
    email: EmailStr
    nome: str
    status: str
    ativo: bool
    id : int
    perfil : str

#pesquisa no database e retorna usuario
def get_usuario(
    payload: dict = Depends(obter_usuario_token),
    session: Session = Depends(get_session),
):
    usuario = session.get(Usuario, int(payload["sub"]))

    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=401,
            detail="Usuário inválido ou inativo",
        )

    return usuario

#router
router_usuario = APIRouter(prefix="/usuario")

#nome autoexplicatorio
def verificar_admin_moderador(usuario : get_current_user,session : get_session):
    if usuario.perfil == "administrador" or usuario.perfil == "moderador":
        return usuario
    
    raise HTTPException(status_code=403,
                        detail=f"{usuario.nome} não tem permição para acessar essa pagina")


@router_usuario.post("/login")
def get_login_usuario(dadosLogin : UsuarioLogin, session : Session = Depends(get_session)):
    procurar_usuario = select(Usuario).where(Usuario.email == dadosLogin.email)
    usuario = session.exec(procurar_usuario).first()
    if usuario:
            senha_valida = verificar_senha(dadosLogin.senha,usuario.senha)
            if not senha_valida:
                raise HTTPException(status_code=400, detail="E-mail ou senha incorretos")
    else:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    token = criar_access_token(
        usuario_id=usuario.id,
        perfil=usuario.perfil,
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        usuario=UsuarioResponse.model_validate(usuario),
    )

@router_usuario.post("/cadastro", response_model=get_current_user)
def criar_usuario(usuario : UsuarioCreate, session : Session = Depends(get_session)):
    procurar_usuario = select(Usuario).where(Usuario.email == usuario.email)
    usuarioExistente = session.exec(procurar_usuario).first()
    if usuarioExistente:
        raise HTTPException(
            status_code= 409,
            detail = "Ja existe usuario com esse e-mail cadastrado"
        )

    dados = usuario.model_dump()
    dados["senha"] = hash_senha(dados["senha"])

    db_usuario = Usuario.model_validate(dados)
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)

    return get_current_user.model_validate(db_usuario)


@router_usuario.get("/me", response_model=get_current_user)
def usuario_atual(usuario: Usuario = Depends(get_usuario)):
    return get_current_user.model_validate(usuario)

