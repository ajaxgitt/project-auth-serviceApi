from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from datetime import datetime
from .database import Base
from .database import engine

class User(Base):
    __tablename__ = "users"  
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255))
    
    # Columna que indica si la cuenta del usuario está activa.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # 'default=datetime.utcnow' asegura que se establezca la fecha y hora actuales si no se proporciona un valor.
    last_active_at = Column(DateTime, default=datetime.utcnow)
    # 'default=False' establece el valor predeterminado como falso.
    is_online = Column(Boolean, default=False)
    # 'default=0' establece el valor predeterminado en 0 monedas.
    virtual_coins = Column(Integer, default=0)
    # Columna para almacenar el número actual de días consecutivos que el usuario ha completado ejercicios.
    # 'default=0' establece el valor predeterminado en 0 días.
    current_streak = Column(Integer, default=0)
    # Columna para almacenar el historial de transacciones de monedas del usuario.
    # Se utiliza el tipo JSON para almacenar una lista de objetos que describen cada transacción.
    # 'default=[]' establece el valor predeterminado como una lista vacía.
    transaction_history = Column(JSON, default=[])
    
    # Columna para almacenar el historial de cambios en las rachas del usuario.
    # Se utiliza el tipo JSON para almacenar una lista de objetos que describen cada cambio en la racha.
    # 'default=[]' establece el valor predeterminado como una lista vacía.
    streak_history = Column(JSON, default=[])

# Crear las tablas en la base de datos utilizando el motor de base de datos proporcionado.
User.metadata.create_all(bind=engine)
