from pydantic import BaseModel
from typing import Optional


class FotoUpdate(BaseModel):
    profile_photo: Optional[str] = None
    
    
    
class UserCreate(BaseModel):
    username:str
    password:str
    email:Optional[str] = None
    
class UserResponse(BaseModel):
    id:int
    username:str
    profile_photo:Optional[str] = None
    email:str
    
class LoginData(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    bio: Optional[str] = None
    occupation: Optional[str] = None



    
    
class ListRespose(BaseModel):
    id : int