from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


    
    

class Miembros(BaseModel):
    user_id:int
    grupo_id:int
    
    
class FotoUpdate(BaseModel):
    profile_photo: Optional[str] = None
    
class NotificationRequest(BaseModel):
    usernames: List[str]
    message: str
    name_group:str
    grupo_id :int
    
    
class UserCreate(BaseModel):
    username:str
    password:str
    email:Optional[str] = None
    
class UserResponse(BaseModel):
    id:int
    username:str
    profile_photo:Optional[str] = None
    email:str
    exp:int
    
class UsersWithTokenResponse(BaseModel):
    id_token: int
    users: List[UserResponse]
    
    
class LoginData(BaseModel):
    username: str
    password: str





class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    occupation: Optional[str] = None
    phone_number: Optional[str] = None

    


    
    
class ListRespose(BaseModel):
    id : int
    
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class GrupoCreate(BaseModel):
    name_group: str
    

class Red_Miembros(BaseModel):
    id:int
    username:str
    profile_photo:Optional[str] = None
    
    
class Red_Miembros_group(BaseModel):
    id:int
    username:str
    profile_photo:Optional[str] = None
    exp:int
    level:str


    
# class Grupo_respose(BaseModel):
#     id:int
#     miembros : List[Red_Miembros]
    

class Grupo_respose(BaseModel):
    id:int
    name_group:str
    usuarios : List[Red_Miembros_group]
