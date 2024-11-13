from fastapi import   HTTPException, status, APIRouter,WebSocket, WebSocketDisconnect, Depends , File ,UploadFile
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .services import ( UserCreate, get_user_by_username, get_user_by_id,create_access_token , get_user_by_email,
                        authenticate_user , verify_token, create_user,ConnectionManager )

from . database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime
from decouple import config
from . models import User, Grupo,Notification,grupos_users
from .schemas import LoginData, UserUpdate,UserResponse,FotoUpdate,GrupoCreate,Red_Miembros,NotificationRequest,Miembros,UsersWithTokenResponse,Grupo_respose
from typing import List ,Dict

from sqlalchemy import delete



import cloudinary # type:ignore
import cloudinary.uploader #type:ignore
from fastapi.responses import JSONResponse




oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

 

user = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


manager = ConnectionManager()


# WebSocket

@user.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)  
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Mensaje recibido de {user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"Error en el WebSocket: {e}")
        await websocket.close()





#notificaciones
@user.post("/send_notification/{username}/",tags=['notificacaiones'])
async def send_notification(username: str, message: str, db: Session = Depends(get_db)):
    """Endpoint para enviar notificaciones a un usuario específico"""
    user_id = db.query(User).filter(User.username == username).first()
    if user_id:
        user = db.query(User).filter(User.id == user_id.id).first()
        if user:
            await manager.send_message(message, user_id.id)
        
        return {"message": f"Notificación enviada a {user.username}!"}
    return {"error": "Usuario no encontrado!"}







@user.post("/send_notifications/",tags=['notificacaiones'])
async def send_notifications(request: NotificationRequest, db: Session = Depends(get_db)):
    usernames = request.usernames
    message = request.message
    grupo_id = request.grupo_id
    name_group = request.name_group
    
    not_found_users = []

    for username in usernames:
        user = db.query(User).filter(User.username == username).first()
        if user:
            new_notification = Notification(
                user_id=user.id,
                message=message,
                name_group =name_group,
                grupo_id =grupo_id,
                created_at=datetime.utcnow(),
                is_read=False
            )
            db.add(new_notification)
            await manager.send_message(message, user.id)
        else:
            not_found_users.append(username)

    db.commit()
    
    if not_found_users:
        return {
            "message": "Notificaciones enviadas, pero algunos usuarios no fueron encontrados.",
            "not_found_users": not_found_users
        }
    
    return {"message": "Notificaciones enviadas a todos los usuarios y guardadas en la base de datos!"}



@user.get('/get_notificaciones/{user_id}/',tags=['notificacaiones'])
def get_notificaciones(user_id: int , db:Session =Depends(get_db)):
    """Endpoint para enviar leer todas las notificaciones"""
    notificaciones_user = db.query(Notification).filter(Notification.user_id == user_id).all()
    if notificaciones_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
        
    return notificaciones_user 

@user.get('/get_contador/{id_user}',tags=['notificacaiones'])
def get_contador(id_user:int, db:Session = Depends(get_db)):
    """funcion que devuelve elk contador de notificaciones"""
    db_user = db.query(User).filter(User.id == id_user).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    notificacionesdb_user = db.query(Notification).filter(Notification.user_id==db_user.id).all()
    if notificacionesdb_user is None:
        raise HTTPException(status_code=404, detail="No se ninguna notificacion para  el usuario")
    
    return {"notificaiones": len(notificacionesdb_user)} 




    




@user.delete('/notification/{notification_id}' ,tags=['notificacaiones'] )
async def delete_notification(notification_id:int,db:Session=Depends(get_db)):
    """"funcion para leiminar una notificacion"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="No se encontró dicha notificacion")
    db.delete(notification)
    db.commit()
    return {"message": "notificacion eliminada exitosamente"}
        







        
# Usuarios

@user.post("/api/user/register" ,tags=['crear'])
def register_user(user:UserCreate, db:Session = Depends(get_db)):
    """
    funcion para registrar un nuevo usuario
    """
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Este nombre de usuario ya existe")
    
    db_email = get_user_by_email(db, email=user.email)
    
    if db_email:
        raise HTTPException(status_code=400, detail="Correo electrónico ya registrado")
  
    created_user = create_user(db=db, user=user)
    return {"id": created_user.id, "username": created_user.username, "email": created_user.email}
  




@user.get('/api/users', response_model=list[UserResponse] ,tags=['optener'])
def get_users(db:Session = Depends(get_db)):
    """funcion para llamar a 100 usuario ususarios"""
    users = db.query(User).all()
    return users



@user.get('/api/users/lists/{token}', response_model=UsersWithTokenResponse, tags=['prueba'])
def get_users(token: str, db: Session = Depends(get_db)):
    """Función para obtener usuarios con el id_token"""
    
    id_user = verify_token(token=token)
    id_token = int(id_user['sub'])
    
    users = db.query(User).all()

    user_list = [
        UserResponse(
            id=user.id,
            username=user.username,
            profile_photo=user.profile_photo,
            email=user.email,
            exp=user.exp  
        ) for user in users
    ]
    
    return {'id_token': id_token, 'users': user_list}


@user.get('/api/get_user/{id}',tags=['optener'])
def get_user_id(id:int, db:Session = Depends(get_db)):
    """funciona para llamar a aun user por su id"""
    user  = get_user_by_id(db=db, id=id)
    if user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    return {"data_user":user, "grupos":user.grupos}

        

@user.get('/api/get_user/grupos/{token}',tags=['optener'])
def get_user_id_grupos_list(token:str, db:Session = Depends(get_db)):
    """funciona para llamar a aun user por su token y ver sus grupos"""
    
    user = verify_token(token=token)   
    db_user = get_user_by_id(db=db, id=user['sub']) 
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")

    return {"grupos":db_user.grupos}
  




@user.post("/api/user/token",tags=['crear'])
def login_for_access_token(login_data: LoginData, db: Session = Depends(get_db)):
    """funcion para logeaarnos en la pagina con una respuesta jwt"""
    user = authenticate_user(login_data.username, login_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=int(config("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@user.get("/api/user/verify-token/{token}",tags=['optener'])
async def verify_user_token(token: str):
    """verifica si el token es autentico"""
    verify_token(token=token)    
    return {"message":"token is valid"}


@user.get("/api/user/perfil/{token}",tags=['optener'])
def get_peril_user(token:str, db: Session = Depends(get_db)):
    """funcion para obtener el usuario por el token"""
    user = verify_token(token=token)   
    db_user = get_user_by_id(db=db, id=user['sub']) 
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    
    return {"data_user":db_user, "grupos":db_user.grupos}

    
    
    
@user.get("/api/user_id/{token}",tags=['optener'])
def get_peril_user(token:str, db: Session = Depends(get_db)):
    """funcion para obtener el id del usuario por el token"""
    user = verify_token(token=token)    
    db_user = get_user_by_id(db=db, id=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    return db_user.id



@user.get("/api/get_id/{token}",tags=['optener'])
def get_id(token:str):
    """funcion para obtener el id del usuario usando el token sin db"""
    id_user = verify_token(token=token)
    return int(id_user['sub'])
    
    
  
cloudinary.config(
    cloud_name='digvece58',  
    api_key='689978857773482', 
    api_secret='GmiUXiABsY3r-ot9mxPgcivF_wU'   
)



@user.put("/users/{token}/profile_photo/")
async def update_profile_photo(token: str, file: UploadFile = File(...), db:Session=Depends(get_db)):
    
    try:
        usuario = verify_token(token=token)    
        user_id = get_user_by_id(db=db, id=usuario['sub'])
    
        response = cloudinary.uploader.upload(file.file)
        image_url = response['secure_url']  

        user = db.query(User).filter(User.id == user_id.id).first()
        user.profile_photo = image_url
        db.commit()

        return {"url": image_url}  
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    


@user.put('/api/user/update/{token}',tags=['editar'])
def update_user(token: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """servicio para editar la informacion del user"""
    user = verify_token(token=token)    
    db_user = get_user_by_id(db=db, id=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    
    if user_update.bio is not None:
        db_user.bio = user_update.bio
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.phone_number is not None:
        db_user.phone_number = user_update.phone_number
        
    if user_update.occupation is not None:
        db_user.occupation = user_update.occupation
    
    db.commit()
    
    return {"message": "User updated successfully", "user": db_user}




  
@user.put('/api/foto/update/{token}',tags=['editar'])
def update_foto(token: str, foto_update: FotoUpdate, db: Session = Depends(get_db)):
    """servicio para editar la foto del user"""
    user = verify_token(token=token)    
    db_user = get_user_by_id(db=db, id=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    
    if foto_update.profile_photo is not None:
        db_user.profile_photo = foto_update.profile_photo
    db.commit()
    
    return {"message": "User updated successfully", "user": db_user}


@user.put('/api/exp_update/{token}/{exp}', tags=['exp'])
def update_exp(token:str,exp:int, db:Session = Depends(get_db)):
    

    """funcion para acatualisar la exp de puntos del user"""
    
    user = verify_token(token=token)    
    user_id = get_user_by_id(db=db, id=user['sub'])
    
    
    db_user = db.query(User).filter(User.id==user_id.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario")
    
    db_user.exp += exp
    
    db.commit()
    if db_user.exp >= 500:
        db_user.level = 'Explorador'
        db.commit()    
        
        
    return {"message": "EXP del usuario actualizada", "user_id": user_id, "new_exp": db_user.exp}









  
#   grupos

@user.post("/grupos/{token}", response_model=GrupoCreate,tags=['grupos'])
def create_grupo(grupo: GrupoCreate,token: str, db: Session = Depends(get_db)):
    """funcion para crear un nuevo grupo"""
    user = verify_token(token=token)    
    db_user = get_user_by_id(db=db, id=user['sub'])
     
    if db.query(Grupo).filter(Grupo.name_group == grupo.name_group).first():
        raise HTTPException(status_code=400, detail="Este nombre  ya existe")
    if len(grupo.name_group) >= 12:
        raise HTTPException(status_code=400, detail="Este nombre  es muy largo")
    else:
        db_grupo = Grupo(
            name_group=grupo.name_group,
            )
        db.add(db_grupo)
        db.commit()
        db.refresh(db_grupo)
        db_user.grupos.append(db_grupo)
        db.commit()
        return db_grupo




@user.delete('/api/{user_id}/{grupo_id}/', tags=['grupos'])
def remove_member(user_id: int, grupo_id: int, db: Session = Depends(get_db)):
    """Función para eliminar o salir de un grupo"""
    
    # Verificar que el grupo existe
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if grupo is None:
        raise HTTPException(status_code=400, detail="Grupo no encontrado")

    # Verificar si el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Eliminar la relación en la tabla de asociación 'grupos_users'
    stmt = delete(grupos_users).where(
        grupos_users.c.user_id == user_id,
        grupos_users.c.grupo_id == grupo_id
    )
    result = db.execute(stmt)

    # Si no se eliminó ninguna fila, el usuario no estaba en el grupo
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="El usuario no es miembro del grupo")

    db.commit()
    
    return {"message": "Usuario eliminado del grupo correctamente"}




@user.post("/users/{user_id}/grupos/{grupo_id}/{notification_id}",tags=['grupos'] )
def add_user_to_grupo(notification_id:int, user_id: int, grupo_id: int, db: Session = Depends(get_db)):
    """funcion para agregar un nuevo miembro algrupo"""
    db_user = db.query(User).filter(User.id == user_id).first()
    db_grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()

    if not db_user or not db_grupo:
        raise HTTPException(status_code=404, detail="User or Grupo not found")

    db_user.grupos.append(db_grupo)
    db.commit()
    
    # eliminar la notificacion
    
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="No se encontró dicha notificacion")
    db.delete(notification)
    db.commit()
    
    return {"message": "User added to grupo"}



@user.get("/users/{user_id}/grupos",tags=['grupos'])
def get_user_grupos(user_id: int, db: Session = Depends(get_db)):
    """funcion para obter todos los grupos por el id del user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db_user.grupos

@user.get("/grupos/{grupo_id}/users", response_model=List[Red_Miembros],tags=['grupos'])
def get_grupo_users(grupo_id: int, db: Session = Depends(get_db)):
    """Función para obtener todos los integrantes del grupo por el id del grupo."""
    
    db_grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not db_grupo:
        raise HTTPException(status_code=404, detail="Grupo not found")
    
    # Devuelve la lista de usuarios del grupo
    return db_grupo.usuarios

@user.get("/grupos_get/{grupo_id}/users", response_model=Grupo_respose ,tags=['grupos'])
def get_grupo_users(grupo_id: int, db: Session = Depends(get_db)):
    """Función para obtener todos los integrantes del grupo por el id del grupo."""
    db_grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not db_grupo:
        raise HTTPException(status_code=404, detail="Grupo not found")
    return db_grupo



@user.post("/grupos/{grupo_id}/users",tags=['grupos'])
def add_users_to_grupo(grupo_id: int, user_ids: List[int], db: Session = Depends(get_db)):
    """funcion para agregar a los users  al nuevo grupo"""
    
    db_grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not db_grupo:
        raise HTTPException(status_code=404, detail="Grupo not found")

    for user_id in user_ids:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db_grupo.usuarios.append(db_user)
        else:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    db.commit()
    return {"message": "Users added to grupo"}

