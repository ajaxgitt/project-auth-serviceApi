from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from .router import user



app = FastAPI(
    title="servicio de login"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://127.0.0.1:8002",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(user)


