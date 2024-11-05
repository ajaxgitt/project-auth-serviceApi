from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class Grupos_ids(BaseModel):
    id: int
    
    
    
# Modelos Pydantic
class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    group_ids: Optional[List[Grupos_ids]] = None 