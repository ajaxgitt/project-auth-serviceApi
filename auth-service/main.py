from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from . router import user



app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")


origins = [
    "http://127.0.0.1:8000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puedes agregar más dominios si es necesario
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

app.include_router(user)