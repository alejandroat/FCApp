import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Gestion de Jugadores", page_icon="⚽", layout="wide")

API_URL = "http://localhost:8000"

if 'usuario_logueado' not in st.session_state:
    st.session_state.usuario_logueado = None
if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = None
if 'pagina' not in st.session_state:
    st.session_state.pagina = "jugadores"
    
# ============== FUNCIONES ===========================#

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def login(nombre, contrasena):
    """Función para iniciar sesión del usuario"""
    try:
        data = {"nombre": nombre, "contrasena": contrasena}
        response = requests.post(f"{API_URL}/usuarios/login", json=data)
        print("=" * 50)
        print("DEBUG - login:")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta del backend: {response.text}")
        print("=" * 50)
        if response.status_code == 200:
            return response.json()  # Devuelve token, usuario_id y nombre
        return None
    except:
        return None
    
def obtener_usuario_id(nombre):
    try:
        response = requests.get(f"{API_URL}/usuarios/")
        if response.status_code == 200:
            usuarios = response.json()
            for usuario in usuarios:
                if usuario["nombre"] == nombre:
                    return usuario["id"]
        return None
    except:
        return None

def crear_usuario(nombre, contrasena):
    """Crea un nuevo usuario"""
    try:
        data = {"nombre": nombre, "contrasena": contrasena}
        response = requests.post(f"{API_URL}/usuarios/", json=data)
        return response.status_code == 200
    except:
        return False
    
def obtener_jugadores_usuario(filtros=None, ordenar_por="valoracion", orden="DESC", limite=10, offset=0):
    """Obtiene SOLO los jugadores del usuario autenticado (usa el token)"""
    try:
        if filtros is None:
            filtros = {}
        params = {
            **filtros,
            "ordenar_por": ordenar_por,
            "orden": orden,
            "limite": limite,
            "offset": offset
        }
        response = requests.get(f"{API_URL}/jugadores/mis-jugadores", params=params, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []
    
def crear_jugador(datos_jugador):
    """Crea un nuevo jugador (el backend usa el token para saber el usuario_id)"""
    try:
        # Preparar los datos
        datos = {
            "nombre": datos_jugador.get("nombre"),
            "valoracion": int(datos_jugador.get("valoracion", 50)),
            "posicion_principal": datos_jugador.get("posicion_principal"),
            "pais": datos_jugador.get("pais"),
            "equipo": datos_jugador.get("equipo"),
            "posicion_secundaria": ",".join(datos_jugador.get("posicion_secundaria", [])) if datos_jugador.get("posicion_secundaria") else None,
            "dorsal": int(datos_jugador.get("dorsal")) if datos_jugador.get("dorsal") else None,
            "equipacion": datos_jugador.get("equipacion") if datos_jugador.get("equipacion") else None,
            "rango": int(datos_jugador.get("rango", 3)),
            "habilitado": bool(datos_jugador.get("habilitado", True)),
            "programa": datos_jugador.get("programa") if datos_jugador.get("programa") else None,
            "imagen_url": datos_jugador.get("imagen_url") if datos_jugador.get("imagen_url") else None
        }
        
        print("=" * 50)
        print("DEBUG - crear_jugador:")
        print(f"Token en session_state: {st.session_state.token}")
        print(f"Headers que se enviarán: {get_headers()}")
        print(f"Datos a enviar: {datos}")
        print("=" * 50)
        
        response = requests.post(f"{API_URL}/jugadores/", json=datos, headers=get_headers())
        
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta del backend: {response.text}")
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error del backend: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error en crear_jugador: {e}")
        return False
    
def eliminar_jugador(jugador_id):
    """Elimina un jugador"""
    try:
        response = requests.delete(f"{API_URL}/jugadores/{jugador_id}", headers=get_headers())
        return response.status_code == 200
    except:
        return False
    
def actualizar_jugador(jugador_id, datos_jugador):
    """Actualiza un jugador enviando los datos como JSON"""
    try:
        # Unir la lista de posiciones secundarias en un string separado por comas
        if 'posicion_secundaria' in datos_jugador and datos_jugador['posicion_secundaria']:
            datos_jugador['posicion_secundaria'] = ",".join(datos_jugador['posicion_secundaria'])
        else:
            datos_jugador['posicion_secundaria'] = None
            
        # Filtrar campos vacíos para no enviarlos en el PUT
        datos_limpios = {k: v for k, v in datos_jugador.items() if v is not None and v != ""}
        
        # Enviar como JSON con el token
        response = requests.put(f"{API_URL}/jugadores/{jugador_id}", json=datos_limpios, headers=get_headers())
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error al actualizar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Excepción al actualizar jugador: {e}")
        return False
    
def buscar_imagen_jugador(nombre_jugador: str) -> str | None:
    """Busca la imagen de un jugador desde el backend"""
    try:
        response = requests.get(f"{API_URL}/jugadores/buscar-imagen/{nombre_jugador}")
        if response.status_code == 200:
            data = response.json()
            return data.get("imagen_url")
        return None
    except Exception as e:
        print(f"Error buscando imagen: {e}")
        return None
    
#=================== LOGIN =========================#

if st.session_state.usuario_logueado is None:
    st.title("Login de Usuarios")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab1:
        st.subheader("Iniciar Sesión")
        nombre_login = st.text_input("Nombre de usuario", key="login_nombre")
        contrasena_login = st.text_input("Contraseña", type="password", key="login_contrasena")
        
        if st.button("Entrar", type="primary"):
            if nombre_login and contrasena_login:
               resultado = login(nombre_login, contrasena_login)
               if resultado:
                     # 🔑 Guardar el token y los datos del usuario
                     st.session_state.token = resultado["access_token"]
                     st.session_state.usuario_logueado = resultado["nombre"]
                     st.session_state.usuario_id = resultado["usuario_id"]
                     st.success(f"Bienvenido, {nombre_login}!")
                     st.rerun()
               else:
                     st.error("Nombre de usuario o contraseña incorrectos.")
            else:
                st.warning("Por favor, completa todos los campos.")
                
    with tab2:
        st.subheader("Registrarse")
        nombre_registro = st.text_input("Nombre de usuario", key="registro_nombre")
        contrasena_registro = st.text_input("Contraseña", type="password", key="registro_contrasena")
        
        if st.button("Registrarse", type="primary"):
            if nombre_registro and contrasena_registro:
                if crear_usuario(nombre_registro, contrasena_registro):
                    st.success("Usuario creado exitosamente. Ahora puedes iniciar sesión.")
                else:
                    st.error("Error al crear el usuario (¿El nombre ya está en uso?).")
            else:
                st.warning("Por favor, completa todos los campos.")

#=================== APP PRINCIPAL =========================#
else:
    with st.sidebar:
        st.title(f"⚽ {st.session_state.usuario_logueado}")
        st.write("Gestiona tus jugadores de fútbol aquí.")
        st.divider()
        
        if st.button("📋 Ver mis jugadores"):
            st.session_state.pagina = "jugadores"
        if st.button("➕ Agregar jugador"):
            st.session_state.pagina = "agregar"
        if st.button("Estadisticas"):
            st.session_state.pagina = "estadisticas"
        st.divider()
        if st.button("🚪 Cerrar sesión"):
            st.session_state.usuario_logueado = None
            st.session_state.usuario_id = None
            st.session_state.pagina = "jugadores"
            st.rerun()
            
    # 1. VISTA DE LISTA DE JUGADORES
    if st.session_state.pagina == "jugadores":
        st.title("Mis Jugadores")
        
        if 'jugador_a_eliminar_id' in st.session_state:
            st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar a **{st.session_state.jugador_a_eliminar_nombre}**? Esta acción no se puede deshacer.")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("✅ Sí, eliminar definitivamente", type="primary"):
                    if eliminar_jugador(st.session_state.jugador_a_eliminar_id):
                        st.success("Jugador eliminado correctamente.")
                        del st.session_state.jugador_a_eliminar_id
                        del st.session_state.jugador_a_eliminar_nombre
                        st.rerun()
                    else:
                        st.error("Error al eliminar.")
            with col_c2:
                if st.button("❌ Cancelar"):
                    del st.session_state.jugador_a_eliminar_id
                    del st.session_state.jugador_a_eliminar_nombre
                    st.rerun()
            st.divider()
        with st.container(border=True):
            # st.subheader("Filtros de Búsqueda")
            col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 2])
            
            with col_f1:
                filtro_nombre = st.text_input("🔍 Nombre", placeholder="Ej: Messi", key="filtro_nombre")
            with col_f2:
                POSICIONES_FILTRO = ["TODAS", "POR", "LD", "LI", "DFC", "MCD", "MC", "MD", "MI", "MCO", "ED", "EI", "DEL"]
                filtro_posicion = st.selectbox("⚽ Posición", POSICIONES_FILTRO, key="filtro_posicion")
            with col_f3:
                filtro_ordenar = st.selectbox("📊 Ordenar por", ["Valoración", "Nombre", "Rango", "Dorsal"], key="filtro_ordenar")
                filtro_direccion = st.selectbox("Dirección", ["Descendente", "Ascendente"], key="filtro_direccion")
            with col_f4:
                if st.button("🗑️ Limpiar Filtros", use_container_width=True):
                    keys_a_borrar = ["filtro_nombre", "filtro_posicion", "filtro_ordenar", "filtro_direccion", "filtro_valoracion", "filtro_estado"]
                    for key in keys_a_borrar:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        filtros = {}
        if st.session_state.get("filtro_nombre"): filtros["nombre"] = st.session_state.filtro_nombre
        if st.session_state.get("filtro_posicion") != "TODAS": filtros["posicion"] = st.session_state.filtro_posicion
        
        ordenar_por_map = {"Valoración": "valoracion", "Nombre": "nombre", "Rango": "rango", "Dorsal": "dorsal"}
        orden_por = ordenar_por_map.get(st.session_state.get("filtro_ordenar", "Valoración"), "valoracion")
        orden_dir = "DESC" if st.session_state.get("filtro_direccion", "Descendente") == "Descendente" else "ASC"
        
        LIMITE_POR_PAGINA = 10
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
            
        offset = (st.session_state.pagina_actual - 1) * LIMITE_POR_PAGINA
        
        nombre_val = st.session_state.get("filtro_nombre", "")
        pais_val = st.session_state.get("filtro_pais", "")
        posicion_val = st.session_state.get("filtro_posicion", "TODAS")
        estado_val = st.session_state.get("filtro_estado", "TODOS")
        valoracion_val = st.session_state.get("filtro_valoracion", (0, 130))
        
        jugadores = obtener_jugadores_usuario(
            filtros=filtros, 
            ordenar_por=orden_por, 
            orden=orden_dir, 
            limite=LIMITE_POR_PAGINA, 
            offset=offset
        )
        
        if jugadores:
            st.caption(f"Se encontraron **{len(jugadores)}** jugadores con los filtros aplicados.")
            st.divider()
            
            for jugador in jugadores:
                estado_color = "" if jugador.get("habilitado", 1) == 1 else ""
                estado_texto = "Activo" if jugador.get("habilitado", 1) == 1 else "Inactivo"
                
                with st.container(border=True):
                    col_img, col1, col2, col3, col4 = st.columns([1, 3, 3, 2, 1])
                    
                    # Columna de imagen
                    with col_img:
                        imagen_url = jugador.get('imagen_url')
                        if imagen_url:
                            st.image(imagen_url, width=80)
                        else:
                            st.write("📷")
                    
                    with col1:
                        st.subheader(f"{jugador['nombre']} #{jugador.get('dorsal', '-')}")
                        st.caption(f"{jugador.get('equipo', 'Sin equipo')} | {jugador['pais']}")
                        st.write(f"**Programa:** {jugador.get('programa', 'N/A')}")
                    with col2:
                        st.write(f"**Pos. Principal:** {jugador['posicion_principal']}")
                        sec = jugador.get('posicion_secundaria')
                        if sec: st.write(f"**Secundaria(s):** {sec}")
                        st.write(f"**Equipación:** {jugador.get('equipacion', 'N/A')}")
                    with col3:
                        st.metric("Valoración", jugador['valoracion'])
                        st.metric("Rango", f"{jugador['rango']}/5")
                        st.write(f"{estado_color} {estado_texto}")
                    with col4:
                        if st.button("🗑️", key=f"del_{jugador['id']}"):
                            st.session_state.jugador_a_eliminar_id = jugador['id']
                            st.session_state.jugador_a_eliminar_nombre = jugador['nombre']
                            st.rerun()
                            
                        if st.button("✏️", key=f"edit_{jugador['id']}"):
                            st.session_state.editar_jugador = jugador
                            st.session_state.pagina = "editar"
                            st.rerun()
        else:
            st.warning("No se encontraron jugadores con estos filtros.")
            if st.button("Limpiar filtros y mostrar todos"):
                keys_a_borrar = ["filtro_nombre", "filtro_pais", "filtro_posicion", "filtro_estado", "filtro_valoracion"]
                for key in keys_a_borrar:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
                
        st.divider()
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        
        with col_pag1:
            if st.button("⬅️ Anterior", disabled=(st.session_state.pagina_actual == 1), use_container_width=True):
                st.session_state.pagina_actual -= 1
                st.rerun()
        
        with col_pag2:
            st.write(f"**Página {st.session_state.pagina_actual}**")
            
        with col_pag3:
            es_ultima_pagina = len(jugadores) < LIMITE_POR_PAGINA
            if st.button("Siguiente ➡️", disabled=es_ultima_pagina, use_container_width=True):
                st.session_state.pagina_actual += 1
                st.rerun()
            
    # 2. VISTA DE AGREGAR JUGADOR
    elif st.session_state.pagina == "agregar":
        st.title("➕ Agregar Nuevo Jugador")
        POSICIONES = ["POR", "LD", "LI", "DFC", "MCD", "MC", "MD", "MI", "MCO", "ED", "EI", "DEL"]
        
        with st.form("form_jugador"):
            col1, col2, col3 = st.columns(3)
            with col1:
                nombre = st.text_input("Nombre del jugador*")
                dorsal = st.number_input("Dorsal", min_value=1, max_value=99, step=1, value=1)
                equipacion = st.text_input("Equipación (Ej: Manchester City)*")
            with col2:
                posicion_principal = st.selectbox("Posición Principal*", POSICIONES)
                posicion_secundaria = st.multiselect("Posición Secundaria", POSICIONES)
                pais = st.text_input("País*")
            with col3:
                equipo = st.text_input("Equipo*")
                programa = st.text_input("Programa*")
                habilitado = st.checkbox("Habilitado", value=True)
                
            st.divider()
            
            # SECCIÓN DE IMAGEN
            st.subheader("️ Imagen del Jugador")
            col_img1, col_img2 = st.columns([3, 1])
            
            with col_img1:
                imagen_url_manual = st.text_input("URL de imagen (opcional)", 
                                                  placeholder="Pega una URL o usa el buscador automático")
            
            with col_img2:
                buscar_auto = st.form_submit_button("🔍 Buscar Auto", use_container_width=True)
            
            # Si presiona buscar automático
            imagen_url_final = imagen_url_manual
            if buscar_auto and nombre:
                with st.spinner(f"Buscando imagen de {nombre}..."):
                    imagen_encontrada = buscar_imagen_jugador(nombre)
                    if imagen_encontrada:
                        imagen_url_final = imagen_encontrada
                        st.success("¡Imagen encontrada!")
                    else:
                        st.warning("No se encontró imagen. Puedes pegar una URL manualmente.")
            
            # Mostrar preview de la imagen
            if imagen_url_final:
                st.image(imagen_url_final, caption=f"Vista previa: {nombre}", width=200)
            
            st.divider()
            col4, col5 = st.columns(2)
            with col4: valoracion = st.slider("Valoración*", 50, 130, 75)
            with col5: rango = st.slider("Rango*", 0, 5, 3)
            
            submit = st.form_submit_button("Agregar Jugador", type="primary")
            if submit:
                if nombre and posicion_principal and pais and equipo:
                    datos = {
                        "nombre": nombre, "valoracion": valoracion, "posicion_principal": posicion_principal,
                        "posicion_secundaria": posicion_secundaria, "pais": pais, "equipo": equipo,
                        "dorsal": dorsal, "equipacion": equipacion, "rango": rango,
                        "habilitado": habilitado, "programa": programa,
                        "imagen_url": imagen_url_final
                    }
                    print(f"Token actual: {st.session_state.token}")
                    print(f"Headers que se enviarán: {get_headers()}")
                    if crear_jugador(datos):
                        st.success("¡Jugador agregado exitosamente!")
                        st.session_state.pagina = "jugadores"
                        st.rerun()
                    else:
                        st.error("Error al agregar. Revisa la consola.")
                else:
                    st.warning("Completa todos los campos obligatorios (*)")
                    
        if st.button("← Volver a la lista"):
            st.session_state.pagina = "jugadores"
            st.rerun()

    # 3. VISTA DE EDITAR JUGADOR
    elif st.session_state.pagina == "editar" and 'editar_jugador' in st.session_state:
        jugador = st.session_state.editar_jugador
        
        if 'imagen_url_editar' not in st.session_state:
            st.session_state.imagen_url_editar = jugador.get('imagen_url') or ''
        st.title("️ Editar Jugador")
        
        POSICIONES = ["POR", "LD", "LI", "DFC", "MCD", "MC", "MD", "MI", "MCO", "ED", "EI", "DEL"]
        
        # Preparar posiciones secundarias de forma segura (de string a lista)
        pos_sec_str = jugador.get('posicion_secundaria')
        if pos_sec_str and isinstance(pos_sec_str, str):
            pos_sec_lista = [p.strip() for p in pos_sec_str.split(',') if p.strip() in POSICIONES]
        else:
            pos_sec_lista = []

        with st.form("form_editar"):
            col1, col2, col3 = st.columns(3)
            with col1:
                nombre = st.text_input("Nombre", value=jugador.get('nombre', ''))
                dorsal_val = jugador.get('dorsal')
                dorsal_default = int(dorsal_val) if dorsal_val not in [None, ''] else 1
                dorsal = st.number_input("Dorsal", min_value=1, max_value=99, value=dorsal_default)
                equipacion = st.text_input("Equipación", value=str(jugador.get('equipacion') or ''))
                
            with col2:
                pos_principal_val = jugador.get('posicion_principal')
                pos_principal_idx = POSICIONES.index(pos_principal_val) if pos_principal_val in POSICIONES else 0
                
                posicion_principal = st.selectbox("Posición Principal", POSICIONES, index=pos_principal_idx)
                posicion_secundaria = st.multiselect("Posición Secundaria", POSICIONES, default=pos_sec_lista)
                pais = st.text_input("País", value=jugador.get('pais', ''))
                
            with col3:
                equipo = st.text_input("Equipo", value=jugador.get('equipo', ''))
                programa = st.text_input("Programa", value=str(jugador.get('programa') or ''))
                habilitado = st.checkbox("Habilitado", value=bool(jugador.get('habilitado', 1)))

            st.divider()
            
            # SECCIÓN DE IMAGEN (NUEVA)
            st.subheader("️ Imagen del Jugador")
            
            if st.session_state.imagen_url_editar:
                st.image(st.session_state.imagen_url_editar, caption="Imagen actual" , width=200)
                
            col_img1, col_img2, col_img3 = st.columns([2, 1, 1])
            
            with col_img1:
                # Campo para URL manual
                url_manual = st.text_input("URL personalizada (opcional)", 
                                          value="", 
                                          placeholder="Pega una URL aquí",
                                          key="edit_url_manual")
            
            with col_img2:
                # Botón buscar automático
                if st.form_submit_button("🔍 Buscar Auto", use_container_width=True):
                    nombre_busqueda = st.session_state.get("edit_nombre", jugador.get('nombre', ''))
                    
                    with st.spinner(f"Buscando imagen de {nombre_busqueda}..."):
                        try:
                            response = requests.get(f"{API_URL}/jugadores/buscar-imagen/{nombre_busqueda}")
                            if response.status_code == 200:
                                data = response.json()
                                nueva_url = data.get("imagen_url")
                                if nueva_url:
                                    st.session_state.imagen_url_editar = nueva_url
                                    st.success("¡Imagen encontrada y guardada!")
                                    st.rerun()
                            else:
                                st.warning("No se encontró imagen.")
                        except Exception as e:
                            st.error(f"Error al buscar: {e}")
            
            with col_img3:
                # Botón usar URL manual
                if url_manual and st.form_submit_button("💾 Usar URL", use_container_width=True):
                    st.session_state.imagen_url_editar = url_manual
                    st.success("URL guardada")
                    st.rerun()
            
            # Mostrar preview si hay imagen encontrada
            if st.session_state.imagen_url_editar:
                st.caption("✅ Esta imagen se guardará al actualizar")
            
            st.divider()
            col4, col5 = st.columns(2)
            with col4: 
                valoracion = st.slider("Valoración", 50, 130, int(jugador.get('valoracion', 75)), key="edit_valoracion")
            with col5: 
                rango = st.slider("Rango", 0, 5, int(jugador.get('rango', 3)), key="edit_rango")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1: 
                submit = st.form_submit_button("💾 Actualizar Jugador", type="primary")
            with col_btn2: 
                cancel = st.form_submit_button("❌ Cancelar")
            
            if cancel:
                if 'editar_jugador' in st.session_state: 
                    del st.session_state.editar_jugador
                if 'imagen_url_editar' in st.session_state:
                    del st.session_state.imagen_url_editar
                st.session_state.pagina = "jugadores"
                st.rerun()
            
            if submit:
                datos = {
                    "nombre": st.session_state.get("edit_nombre"),
                    "valoracion": st.session_state.get("edit_valoracion"),
                    "posicion_principal": st.session_state.get("edit_pos_principal"),
                    "posicion_secundaria": st.session_state.get("edit_pos_secundaria"),
                    "pais": st.session_state.get("edit_pais"),
                    "equipo": st.session_state.get("edit_equipo"),
                    "dorsal": st.session_state.get("edit_dorsal"),
                    "equipacion": st.session_state.get("edit_equipacion"),
                    "rango": st.session_state.get("edit_rango"),
                    "habilitado": st.session_state.get("edit_habilitado"),
                    "programa": st.session_state.get("edit_programa"),
                    "imagen_url": st.session_state.imagen_url_editar
                }
                
                if actualizar_jugador(jugador['id'], datos):
                    st.success("¡Jugador actualizado exitosamente!")
                    if 'editar_jugador' in st.session_state: 
                        del st.session_state.editar_jugador
                    if 'imagen_url_editar' in st.session_state:
                        del st.session_state.imagen_url_editar
                    st.session_state.pagina = "jugadores"
                    st.rerun()
                else:
                    st.error("Error al actualizar. Revisa la consola.")
                    
        # 4. VISTA DE ESTADÍSTICAS (DASHBOARD)
    elif st.session_state.pagina == "estadisticas":
        st.title("📊 Dashboard de Estadísticas")
        
        # Obtenemos TODOS los jugadores (sin filtros de búsqueda) para el análisis global
        jugadores = obtener_jugadores_usuario()
        
        if not jugadores:
            st.info("Aún no tienes jugadores registrados. Agrega algunos para ver las estadísticas.")
        else:
                        
            # Convertimos la lista de diccionarios a un DataFrame de Pandas (tabla)
            df = pd.DataFrame(jugadores)
            
            # --- SECCIÓN 1: KPIs (Indicadores Clave) ---
            st.subheader("Resumen General")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Jugadores", len(df))
            with col2:
                avg_val = df['valoracion'].mean()
                st.metric("Promedio Valoración", f"{avg_val:.1f}")
            with col3:
                # Jugador mejor valorado
                top_player = df.loc[df['valoracion'].idxmax()]
                st.metric("Mejor Jugador", f"{top_player['nombre']} ({top_player['valoracion']})")
            with col4:
                # Jugador con mayor rango (1-5)
                top_rank = df.loc[df['rango'].idxmax()]
                st.metric("Mayor Rango", f"{top_rank['nombre']} (Rango {top_rank['rango']})")
                
            st.divider()
            
            # --- SECCIÓN 2: GRÁFICOS ---
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.subheader("Jugadores por Posición Principal")
                # Contamos cuántos jugadores hay por posición
                conteo_pos = df['posicion_principal'].value_counts().reset_index()
                conteo_pos.columns = ['Posición', 'Cantidad']
                
                fig_bar = px.bar(conteo_pos, x='Posición', y='Cantidad', 
                                 color='Cantidad', 
                                 color_continuous_scale='Viridis',
                                 title='Distribución por Posición')
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with col_graf2:
                st.subheader("Distribución de Valoraciones")
                # Histograma para ver cuántos jugadores tienen cierta valoración
                fig_hist = px.histogram(df, x='valoracion', nbins=10,
                                        title='Frecuencia de Valoraciones',
                                        color_discrete_sequence=['#636EFA'])
                
                fig_hist.update_xaxes(
                    dtick= 1,
                    tickformat = 'd',
                )
                fig_hist.update_yaxes(
                    dtick= 1,
                    tickformat = 'd'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
                
            st.divider()
            
            col_graf3, col_graf4 = st.columns(2)
            
            with col_graf3:
                st.subheader("Top 5 Países")
                # Gráfico de pastel con los 5 países con más jugadores
                conteo_pais = df['pais'].value_counts().head(5).reset_index()
                conteo_pais.columns = ['País', 'Cantidad']
                
                fig_pie = px.pie(conteo_pais, values='Cantidad', names='País', 
                                 title='Top 5 Países de Origen',
                                 hole=0.4) # hole=0.4 lo hace tipo "dona"
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_graf4:
                st.subheader("Valoración vs Rango")
                # Gráfico de dispersión para ver correlación
                fig_scatter = px.scatter(df, x='rango', y='valoracion', 
                                         color='posicion_principal',
                                         size='valoracion',
                                         hover_data=['nombre', 'equipo'],
                                         title='Relación Rango vs Valoración')
                
                fig_scatter.update_xaxes(
                    dtick= 1,
                    tickformat = 'd',
                    range=[-0.5, 5.5]
                )
                fig_scatter.update_yaxes(
                    dtick= 1,
                    tickformat = 'd',
                )
                st.plotly_chart(fig_scatter, use_container_width=True)