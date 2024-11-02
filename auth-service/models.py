from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Table, BigInteger, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .database import Base
from .database import engine


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    user = relationship("User", back_populates="notifications")

grupos_users = Table('grupos_users', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('grupo_id', Integer, ForeignKey('grupos.id'))
)

class User(Base):
    __tablename__ = "users"  
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    name = Column(String(50), nullable=True)
    
    email = Column(String(255), unique=True, index=True, nullable=False)  
    password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    is_online = Column(Boolean, default=False)
    virtual_coins = Column(Integer, default=50)
    exp = Column(BigInteger, default=0)
    bio = Column(String(255), nullable=True)
    occupation = Column(String(255), nullable=True)
    profile_photo = Column(String(255), nullable=True)
    level = Column(String(50), default="Novato")
    
    # datos extra
    phone_number = Column(String(15), nullable=True)
    
    grupos = relationship('Grupo', secondary=grupos_users, back_populates='usuarios')  
    notifications = relationship("Notification", back_populates="user")


class Grupo(Base):
    __tablename__ = "grupos"
    
    id = Column(Integer, primary_key=True, index=True)
    name_group = Column(String(50), unique=True, index=True)
    
    usuarios = relationship('User', secondary=grupos_users, back_populates='grupos')  



Base.metadata.create_all(bind=engine)







# Novato: 🟢
# Explorador: 🔵
# Veterano: 🟠
# Maestro: 🔴
# Gran Maestro: 🟣
# Sabio: ⚫
# Leyenda: 🏅
