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


