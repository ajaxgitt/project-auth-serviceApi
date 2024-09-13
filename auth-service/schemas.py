from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username:str
    password:str
    email:Optional[str] = None
    
class LoginData(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    bio: Optional[str] = None
    occupation: Optional[str] = None
    profile_photo: Optional[str] = None
    
    
