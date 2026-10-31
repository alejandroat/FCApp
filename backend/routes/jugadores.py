from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from schemas.jugador import JugadorCreate, JugadorResponse, JugadorUpdate
from auth import get_current_user
from services.imagen_service import buscar_imagen_jugador

router = APIRouter(prefix="/jugadores", tags=["Jugadores"])

# Helper para verificar que el jugador pertenece al usuario autenticado
def verificar_propiedad(jugador_id: int, usuario_id: int):
    conn = get_connection()
    jugador = conn.execute("SELECT usuario_id FROM jugadores WHERE id = %s", (jugador_id,)).fetchone()
    conn.close()
    if not jugador or jugador['usuario_id'] != usuario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este jugador")

# GET /jugadores/mis-jugadores - Obtener SOLO mis jugadores (reemplaza /usuario/{id})
@router.get("/mis-jugadores", response_model=list[JugadorResponse])
def obtener_mis_jugadores(
    current_user: dict = Depends(get_current_user),
    nombre: str = None,
    posicion: str = None,
    pais: str = None,
    valoracion_min: int = None,
    valoracion_max: int = None,
    habilitado: bool = None,
    ordenar_por: str = "valoracion",
    orden: str = "DESC",
    limite: int = 10,
    offset: int = 0
):
    conn = get_connection()
    
    query = "SELECT * FROM jugadores WHERE usuario_id = %s"
    params = [current_user['id']]
    
    if nombre:
        query += " AND nombre LIKE %s"
        params.append(f"%{nombre}%")
    if posicion and posicion != "TODAS":
        query += " AND (posicion_principal = %s OR posicion_secundaria LIKE %s)"
        params.extend([posicion, f"%{posicion}%"])
    if pais:
        query += " AND pais LIKE %s"
        params.append(f"%{pais}%")
    if valoracion_min is not None:
        query += " AND valoracion >= %s"
        params.append(valoracion_min)
    if valoracion_max is not None:
        query += " AND valoracion <= %s"
        params.append(valoracion_max)
    if habilitado is not None:
        query += " AND habilitado = %s"
        params.append(int(habilitado))
        
    columnas_validas = ["valoracion", "nombre", "rango", "dorsal"]
    if ordenar_por not in columnas_validas:
        ordenar_por = "valoracion"
    if orden not in ["ASC", "DESC"]:
        orden = "DESC"
    
    query += f" ORDER BY {ordenar_por} {orden} LIMIT %s OFFSET %s"
    params.extend([limite, offset])
    
    jugadores = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(j) for j in jugadores]

# POST /jugadores/ - Crear jugador
@router.post("/", response_model=dict)
def agregar_jugador(jugador: JugadorCreate, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    
    # Usamos el ID del token, no el que venga en el body
    usuario_id_real = current_user['id']
    
    # Buscar imagen si no se proporcionó
    imagen_url = jugador.imagen_url
    if not imagen_url:
        imagen_url = buscar_imagen_jugador(jugador.nombre)
    
    try:
        conn.execute(
            """INSERT INTO jugadores 
               (nombre, valoracion, posicion_principal, posicion_secundaria, pais, equipo, 
                dorsal, equipacion, rango, habilitado, programa, imagen_url, usuario_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                jugador.nombre, jugador.valoracion, jugador.posicion_principal, 
                jugador.posicion_secundaria, jugador.pais, jugador.equipo,
                jugador.dorsal, jugador.equipacion, jugador.rango, 
                int(jugador.habilitado), jugador.programa, imagen_url, usuario_id_real
            )
        )
        conn.commit()
        conn.close()
        return {"mensaje": "Jugador agregado"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al agregar jugador: {str(e)}")

# DELETE /jugadores/ - Eliminar todos mis jugadores
@router.delete("/")
def eliminar_todos_mis_jugadores(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    conn.execute("DELETE FROM jugadores WHERE usuario_id = %s", (current_user['id'],))
    conn.commit()
    conn.close()
    return {"mensaje": "Todos tus jugadores han sido eliminados"}

# GET /jugadores/buscar/ - Buscar jugadores (solo los míos)
@router.get("/buscar/")
def buscar_jugadores(
    nombre: str = None, 
    posicion: str = None, 
    pais: str = None, 
    equipo: str = None,
    rango: int = None,
    habilitado: bool = None,
    current_user: dict = Depends(get_current_user)
):
    conn = get_connection()
    query = "SELECT * FROM jugadores WHERE usuario_id = %s"
    params = [current_user['id']]
    
    if nombre:
        query += " AND nombre LIKE %s"
        params.append(f"%{nombre}%")
    if posicion:
        query += " AND (posicion_principal = %s OR posicion_secundaria LIKE %s)"
        params.extend([posicion, f"%{posicion}%"])
    if pais:
        query += " AND pais = %s"
        params.append(pais)
    if equipo:
        query += " AND equipo = %s"
        params.append(equipo)
    if rango:
        query += " AND rango = %s"
        params.append(rango)
    if habilitado is not None:
        query += " AND habilitado = %s"
        params.append(int(habilitado))
    
    jugadores = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(j) for j in jugadores]

# GET /jugadores/top/ - Top jugadores (solo los míos)
@router.get("/top/")
def top_jugadores(limit: int = 11, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    jugadores = conn.execute(
        "SELECT * FROM jugadores WHERE usuario_id = %s ORDER BY valoracion DESC LIMIT %s",
        (current_user['id'], limit)
    ).fetchall()
    conn.close()
    return [dict(j) for j in jugadores]

# GET /jugadores/posiciones/ - Obtener por posición (solo los míos)
@router.get("/posiciones/")
def obtener_por_posicion(posicion: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    jugadores = conn.execute(
        "SELECT * FROM jugadores WHERE usuario_id = %s AND (posicion_principal = %s OR posicion_secundaria LIKE %s)",
        (current_user['id'], posicion, f"%{posicion}%")
    ).fetchall()
    conn.close()
    return [dict(j) for j in jugadores]

# GET /jugadores/count/ - Contar mis jugadores
@router.get("/count/")
def contar_jugadores(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) as total FROM jugadores WHERE usuario_id = %s", (current_user['id'],)).fetchone()["total"]
    conn.close()
    return {"total_jugadores": count}

# GET /jugadores/estadisticas/ - Estadísticas de mis jugadores
@router.get("/estadisticas/")
def estadisticas_jugadores(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as total FROM jugadores WHERE usuario_id = %s", (current_user['id'],)).fetchone()["total"]
    promedio_valoracion = conn.execute("SELECT AVG(valoracion) as promedio FROM jugadores WHERE usuario_id = %s", (current_user['id'],)).fetchone()["promedio"]
    conn.close()
    return {
        "total_jugadores": total,
        "promedio_valoracion": promedio_valoracion
    }

# GET /jugadores/{jugador_id} - Obtener un jugador específico
@router.get("/{jugador_id}", response_model=JugadorResponse)
def obtener_jugador(jugador_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    jugador = conn.execute(
        "SELECT * FROM jugadores WHERE id = %s AND usuario_id = %s",
        (jugador_id, current_user['id'])
    ).fetchone()
    conn.close()
    if jugador:
        return dict(jugador)
    else:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

# PUT /jugadores/{jugador_id} - Actualizar jugador
@router.put("/{jugador_id}")
def actualizar_jugador(jugador_id: int, datos: JugadorUpdate, current_user: dict = Depends(get_current_user)):
    # Verificar propiedad
    verificar_propiedad(jugador_id, current_user['id'])
    
    conn = get_connection()
    update_fields = []
    values = []
    
    campos = {
        "nombre": datos.nombre,
        "valoracion": datos.valoracion,
        "posicion_principal": datos.posicion_principal,
        "posicion_secundaria": datos.posicion_secundaria,
        "pais": datos.pais,
        "equipo": datos.equipo,
        "dorsal": datos.dorsal,
        "equipacion": datos.equipacion,
        "rango": datos.rango,
        "habilitado": int(datos.habilitado) if datos.habilitado is not None else None,
        "programa": datos.programa,
        "imagen_url": datos.imagen_url
    }
    
    for campo, valor in campos.items():
        if valor is not None:
            update_fields.append(f"{campo} = %s")
            values.append(valor)
            
    if update_fields:
        values.append(jugador_id)
        query = f"UPDATE jugadores SET {', '.join(update_fields)} WHERE id = %s"
        conn.execute(query, values)
        conn.commit()
        
    conn.close()
    return {"mensaje": "Jugador actualizado"}

# DELETE /jugadores/{jugador_id} - Eliminar un jugador específico
@router.delete("/{jugador_id}")
def eliminar_jugador(jugador_id: int, current_user: dict = Depends(get_current_user)):
    # Verificar propiedad
    verificar_propiedad(jugador_id, current_user['id'])
    
    conn = get_connection()
    conn.execute("DELETE FROM jugadores WHERE id = %s", (jugador_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Jugador eliminado"}

# GET /jugadores/buscar-imagen/{nombre} - Buscar imagen (endpoint público)
@router.get("/buscar-imagen/{nombre}")
def buscar_imagen_endpoint(nombre: str):
    """Busca imagen de un jugador solo por nombre"""
    print(f"Endpoint llamado con nombre: {nombre}")
    imagen_url = buscar_imagen_jugador(nombre)
    if imagen_url:
        return {"imagen_url": imagen_url}
    else:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontró imagen para '{nombre}'"
        )