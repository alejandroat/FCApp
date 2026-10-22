import requests

def buscar_imagen_jugador(nombre_jugador: str) -> str | None:
    """
    Busca la imagen de un jugador.
    Estrategia 1: Wikipedia (Muy estable, gratis, sin bloqueos)
    Estrategia 2: TheSportsDB (Fallback por si Wikipedia falla)
    """
    try:
        print(f"🔍 Buscando imagen para: '{nombre_jugador}'")
        
        # Formatear nombre para URL (ej: "Josko Gvardiol" -> "Josko_Gvardiol")
        nombre_formateado = nombre_jugador.replace(" ", "_")
        
        # ==========================================
        # ESTRATEGIA 1: WIKIPEDIA (Recomendada)
        # ==========================================
        url_wiki = f"https://en.wikipedia.org/api/rest_v1/page/summary/{nombre_formateado}"
        
        # Wikipedia exige un User-Agent descriptivo para no bloquear
        headers_wiki = {
            'User-Agent': 'FCApp/1.0 (proyecto_personal_de_futbol)'
        }
        
        response_wiki = requests.get(url_wiki, headers=headers_wiki, timeout=5)
        
        if response_wiki.status_code == 200:
            data_wiki = response_wiki.json()
            # Wikipedia devuelve la imagen en la clave 'thumbnail' -> 'source'
            if 'thumbnail' in data_wiki and 'source' in data_wiki['thumbnail']:
                imagen_url = data_wiki['thumbnail']['source']
                print(f"✅ Imagen encontrada en Wikipedia: {imagen_url}")
                return imagen_url
            else:
                print("️ Página de Wikipedia encontrada, pero no tiene imagen destacada.")
        else:
            print(f"⚠️ Wikipedia no encontró al jugador (Status {response_wiki.status_code}).")

        # ==========================================
        # ESTRATEGIA 2: THESPORTSDB (Fallback)
        # ==========================================
        print("🔄 Intentando fallback con TheSportsDB...")
        url_sportsdb = f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p={nombre_jugador}"
        
        headers_sportsdb = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response_sportsdb = requests.get(url_sportsdb, headers=headers_sportsdb, timeout=5)
        
        if response_sportsdb.status_code == 200:
            data_sportsdb = response_sportsdb.json()
            if data_sportsdb.get('player') and len(data_sportsdb['player']) > 0:
                imagen_url = data_sportsdb['player'][0].get('strThumb')
                if imagen_url and imagen_url != '':
                    print(f"✅ Imagen encontrada en TheSportsDB: {imagen_url}")
                    return imagen_url
                    
        print(f"❌ No se encontró imagen en ninguna fuente para: {nombre_jugador}")
        return None
        
    except Exception as e:
        print(f"❌ Error general buscando imagen: {e}")
        return None