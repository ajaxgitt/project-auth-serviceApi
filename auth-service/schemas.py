from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username:str
    hashed_password:str
    email:Optional[str] = None
    
class LoginData(BaseModel):
    username: str
    password: str
    
    
