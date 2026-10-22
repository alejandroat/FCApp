from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from schemas.usuario import UsuarioCreate, UsuarioResponse
from auth import get_password_hash, verify_password, create_access_token
from schemas.jugador import JugadorCreate, JugadorResponse
from datetime import timedelta

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios():
    conn = get_connection()
    usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return [dict(u) for u in usuarios]

@router.post("/", response_model=dict)
def agregar_usuario(usuario: UsuarioCreate):
    conn = get_connection()
    
    usuario_existente = conn.execute(
        "SELECT id FROM usuarios WHERE nombre = ?",
        (usuario.nombre,)
    ).fetchone()
    
    if usuario_existente:
        conn.close()
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    
    hashed_password = get_password_hash(usuario.contrasena)
    conn.execute(
        "INSERT INTO usuarios (nombre, contrasena) VALUES (?, ?)",
        (usuario.nombre, hashed_password))
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario agregado"}

@router.post("/login")
def login_usuario(usuario: UsuarioCreate):
    conn = get_connection()
    db_user = conn.execute(
        "SELECT * FROM usuarios WHERE nombre = ?",
        (usuario.nombre,)
    ).fetchone()
    conn.close()
    
    if not db_user or not verify_password(usuario.contrasena, db_user["contrasena"]):
        raise HTTPException(status_code=401, detail="Nombre de usuario o contraseña incorrectos")
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": str(db_user["id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "usuario_id": db_user["id"], "nombre": db_user["nombre"]}

@router.get("/search/")
def buscar_usuarios(nombre: str):
    conn = get_connection()
    usuarios = conn.execute(
        "SELECT * FROM usuarios WHERE nombre LIKE ?",
        (f"%{nombre}%",)
    ).fetchall()
    conn.close()
    return [dict(u) for u in usuarios]

@router.get("/count/")
def contar_usuarios(): 
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) as total FROM usuarios").fetchone()["total"]
    conn.close()
    return {"total_usuarios": count}

@router.get("/{usuario_id}/jugadores", response_model=list[JugadorResponse])
def obtener_jugadores_de_usuario(usuario_id: int):
    conn = get_connection()
    
    # Verificar que el usuario existe
    usuario = conn.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    if not usuario:
        conn.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    jugadores = conn.execute(
        "SELECT * FROM jugadores WHERE usuario_id = ?",
        (usuario_id,)
    ).fetchall()
    conn.close()
    return [dict(j) for j in jugadores]

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int):
    conn = get_connection()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE id = ?",
        (usuario_id,)
    ).fetchone()
    conn.close()
    if usuario:
        return dict(usuario)
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: int, nombre: str = None, contrasena: str = None):
    conn = get_connection()
    if nombre:
        conn.execute("UPDATE usuarios SET nombre = ? WHERE id = ?", (nombre, usuario_id))
    if contrasena:
        conn.execute("UPDATE usuarios SET contrasena = ? WHERE id = ?", (contrasena, usuario_id))
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario actualizado"}
    
@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario eliminado"}