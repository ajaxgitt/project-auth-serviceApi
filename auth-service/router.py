
from fastapi import  Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .services import ( UserCreate, get_user_by_username, get_user_by_id,create_access_token , get_user_by_email,
                        authenticate_user , verify_token, create_user)

from fastapi import Depends
from . database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from decouple import config
from . models import User
from .schemas import LoginData, UserUpdate,UserResponse,FotoUpdate
from typing import List

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

 

user = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





@user.post("/api/user/register" ,tags=['crear'])
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
  
    created_user = create_user(db=db, user=user)
    return {"id": created_user.id, "username": created_user.username, "email": created_user.email}
  
    # return create_user(db=db, user=user)






@user.get('/api/users', response_model=list[UserResponse] ,tags=['optener'])
def get_users(db:Session = Depends(get_db)):
    """funcion para llamar a 100 usuario ususarios"""
    users = db.query(User).all()
    return users




@user.get('/api/users/lists', response_model=list[UserResponse] ,tags=['optener'])
def get_users(db:Session = Depends(get_db)):
    """funcion para llamar a usuario prueba"""
    users = db.query(User).all()
    return users



@user.get('/api/get_user/{id}',tags=['optener'])
def get_user_id(id:int, db:Session = Depends(get_db)):
    """funciona para llamar a aun user por su id"""
    user  = get_user_by_id(db=db, id=id)
    if user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    return user
        





@user.post("/api/user/token",tags=['crear'])
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
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@user.get("/api/user/verify-token/{token}",tags=['optener'])
async def verify_user_token(token: str):
    """verifica si el token es autentico"""
    verify_token(token=token)    
    return {"message":"token is valid"}


@user.get("/api/user/perfil/{token}",tags=['optener'])
def get_peril_user(token:str, db: Session = Depends(get_db)):
    """funcion para obtener el usuario por el token"""
    user = verify_token(token=token)   
    db_user = get_user_by_id(db=db, id=user['sub']) 
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    return db_user
    
    
    
@user.get("/api/user_id/{token}",tags=['optener'])
def get_peril_user(token:str, db: Session = Depends(get_db)):
    """funcion para obtener el id del usuario por el token"""
    user = verify_token(token=token)    
    db_user = get_user_by_id(db=db, id=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    return db_user.id



@user.get("/api/get_id/{token}",tags=['optener'])
def get_id(token:str):
    """funcion para obtener el id del usuario usando el token sin db"""
    id_user = verify_token(token=token)
    return int(id_user['sub'])
    
    
  



@user.put('/api/user/update/{token}',tags=['editar'])
def update_user(token: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """servicio para editar la informacion del user"""
    # Buscar el usuario en la base de datos
    user = verify_token(token=token)    
    db_user = get_user_by_id(db=db, id=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    
    if user_update.bio is not None:
        db_user.bio = user_update.bio
    if user_update.occupation is not None:
        db_user.occupation = user_update.occupation
    
    
    db.commit()
    
    return {"message": "User updated successfully", "user": db_user}

  
@user.put('/api/foto/update/{token}',tags=['editar'])
def update_foto(token: str, foto_update: FotoUpdate, db: Session = Depends(get_db)):
    """servicio para editar la foto del user"""
    # Buscar el usuario en la base de datos
    user = verify_token(token=token)    
    db_user = get_user_by_id(db=db, id=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    
    if foto_update.profile_photo is not None:
        db_user.profile_photo = foto_update.profile_photo
    
    
    db.commit()
    
    return {"message": "User updated successfully", "user": db_user}

  




