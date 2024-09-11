from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from datetime import datetime
from .database import Base
from .database import engine

class User(Base):
    __tablename__ = "users"  
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password = Column(String(255))
    #para saber si el usuario es administrador
    is_admin = Column(Boolean, default=False)
    #cuando se creo la cuenta
    created_at = Column(DateTime, default=datetime.utcnow)
    # ultima conexion
    last_active_at = Column(DateTime, default=datetime.utcnow)
    # 'en linea?
    is_online = Column(Boolean, default=False)
    # monedas
    virtual_coins = Column(Integer, default=0)
    #racha actual
    current_streak = Column(Integer, default=0)
    # Historial de rachas
    streak_history = Column(JSON, default=[])
    bio = Column(String(255), nullable=True)
    occupation = Column(String(255), nullable=True)
    profile_photo = Column(String(255), nullable=True)
    level = Column(String(50), default="Novato")


User.metadata.create_all(bind=engine)




# Novato: 🟢
# Explorador: 🔵
# Veterano: 🟠
# Maestro: 🔴
# Gran Maestro: 🟣
# Sabio: ⚫
# Leyenda: 🏅
