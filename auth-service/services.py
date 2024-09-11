from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from . models import User
from .schemas import UserCreate
from decouple import config



oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

 


def get_user_by_id(db:Session, id:int):
    return db.query(User).filter(User.id == id).first()


def get_user_by_email(db:Session, email:str):
    return db.query(User).filter(User.email == email).first()


def create_user(db:Session, user:UserCreate):
    password = pwd_context.hash(user.password)
    # db_user = User(username = user.username, email = user.email, hashed_password = hashed_password) solo para pruebas
    db_user = User(username = user.username, password = password)
    db.add(db_user)
    db.commit()
    return "user created with success "



def authenticate_user(username:str, password:str, db:Session):
    """
    funcion para authebtificar el username y password """
    user = db.query(User).filter(User.username==username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False  
    return user

def create_access_token(data:dict, expires_delta:timedelta | None = None):
    """
    funcion para crear el token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow()+expires_delta
    else:
        expire = datetime.utcnow()+timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encode_jwt = jwt.encode(to_encode, config("SECRET_KEY"), algorithm=config('ALGORITHM'))
    return encode_jwt




def verify_token(token:str =Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="token is invalid or expired")
