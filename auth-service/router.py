
from fastapi import  Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . services import ( UserCreate, get_user_by_username, create_access_token , get_user_by_email,
                        authenticate_user , verify_token, create_user)
from fastapi import Depends
from . database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from decouple import config
from . models import User
from .schemas import LoginData, UserUpdate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

 

user = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user.post("/api/user/register")
def register_user(user:UserCreate, db:Session = Depends(get_db)):
    """
    funcion para registrar un nuevo usuario
    """
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Este nombre de usuario ya existe")
    
    db_email = get_user_by_email(db, email=user.email)
    
    if db_email:
        raise HTTPException(status_code=400, detail="Correo electrónico ya registrado")
  
    return create_user(db=db, user=user)





@user.get('/api/users', response_model=list[UserCreate])
def get_users(skip:int = 0, limit:int=100, db:Session = Depends(get_db)):
    """funcion para llamar a 100 usuario ususarios"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users




@user.post("/api/user/token")
def login_for_access_token(login_data: LoginData, db: Session = Depends(get_db)):
    """funcion para logeaarnos en la pagina con una respuesta jwt"""
    user = authenticate_user(login_data.username, login_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=int(config("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@user.get("/api/user/verify-token/{token}")
async def verify_user_token(token: str):
    """verifica si el token es autentico"""
    verify_token(token=token)    
    return {"message":"token is valid"}


@user.get("/api/user/perfil/{token}")
def get_peril_user(token:str, db: Session = Depends(get_db)):
    """funcion para obtener el usuario por el token"""
    user = verify_token(token=token)    
    db_user = get_user_by_username(db=db, username=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    return db_user
    
  



@user.put('/api/user/update/{token}')
def update_user(token: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    # Buscar el usuario en la base de datos
    user = verify_token(token=token)    
    db_user = get_user_by_username(db=db, username=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    
    if user_update.bio is not None:
        db_user.bio = user_update.bio
    if user_update.occupation is not None:
        db_user.occupation = user_update.occupation
    if user_update.profile_photo is not None:
        db_user.profile_photo = user_update.profile_photo
    
    db.commit()
    
    return {"message": "User updated successfully", "user": db_user}

@user.get("/api/user/perfil")
def get_perfil_user():
    user_data = {"id": 1, "name": "John Doe"}
    return user_data
  


