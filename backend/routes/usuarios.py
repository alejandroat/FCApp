from fastapi import APIRouter, HTTPException
from database import get_connection
from schemas.usuario import UsuarioCreate, UsuarioResponse
from auth import get_password_hash, verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=dict)
def agregar_usuario(usuario: UsuarioCreate):
    conn = get_connection()
    
    # ⚠️ Nota el %s en lugar de ?
    usuario_existente = conn.execute(
        "SELECT id FROM usuarios WHERE nombre = %s", 
        (usuario.nombre,)
    ).fetchone()
    
    if usuario_existente:
        conn.close()
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    
    hashed_password = get_password_hash(usuario.contrasena)
    
    conn.execute(
        "INSERT INTO usuarios (nombre, contrasena) VALUES (%s, %s)", 
        (usuario.nombre, hashed_password)
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario creado exitosamente"}

@router.post("/login")
def login_usuario(usuario: UsuarioCreate):
    conn = get_connection()
    
    db_user = conn.execute(
        "SELECT * FROM usuarios WHERE nombre = %s", 
        (usuario.nombre,)
    ).fetchone()
    conn.close()
    
    if not db_user or not verify_password(usuario.contrasena, db_user['contrasena']):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": str(db_user['id'])}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": db_user['id'],
        "nombre": db_user['nombre']
    }