from fastapi import   HTTPException, APIRouter, Depends 
from sqlalchemy.orm import Session
from . database import SessionLocal

from .models import *
from .schemas_event import *




evento = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        




@evento.post("/events/" , tags=['eventos'])
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Endpoint para crear eventos"""
    new_event_db = Event(  
        name=event.name,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time
    )
    db.add(new_event_db)
    db.commit()
    db.refresh(new_event_db)  

    # Asociar grupos al evento
    if event.group_ids: 
        for group_id in event.group_ids:
            group = db.query(Grupo).filter(Grupo.id == group_id).first()
            if group:
                new_event_db.groups.append(group)  

    db.commit() 
    return new_event_db  



@evento.post("/events/{event_id}/register_group/{group_id}", tags=['eventos'])
def register_group_for_event(event_id: int, group_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first() 
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    
    group = db.query(Grupo).filter(Grupo.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado.")
    
    # Comprobar si el grupo ya está registrado
    if group not in event.groups:
        event.groups.append(group)
        db.commit()
        return {"message": "Grupo registrado en el evento con éxito."}
    else:
        return {"message": "El grupo ya está registrado en este evento."}


@evento.get('/event/{id_event}/',tags=['eventos'])
def get_event_by_id(id_event:int,db:Session=Depends(get_db)):
    evento_db = db.query(Event).filter(Event.id == id_event).first()
    if evento_db is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    return {"data_event":evento_db, "grupos_event":evento_db.groups}