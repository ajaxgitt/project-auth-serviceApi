
from fastapi import  Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . services import UserCreate, get_user_by_username, create_access_token , authenticate_user , verify_token, create_user
from fastapi import Depends
from . database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from decouple import config
from . models import User
from .schemas import LoginData

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
        raise HTTPException(status_code=400, detail="username already registered")
    
    # db_email = get_user_by_email(db, email= user.email)
    # if db_email:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@user.put('/api/user/update/{id}')
def update_user(user:UserCreate, id):
    pass



@user.get('/api/users', response_model=list[UserCreate])
def get_users(skip:int = 0, limit:int=100, db:Session = Depends(get_db)):
    """funcion para llamar a todos los ususarios"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users




@user.post("/api/user/token")
def login_for_access_token(login_data: LoginData, db: Session = Depends(get_db)):
    """funcion para logeaarnos en la pagina con una respuesta jwt"""
    user = authenticate_user(login_data.username, login_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
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


