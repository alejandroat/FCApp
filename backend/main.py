from fastapi import FastAPI
from database import init_db
from routes import usuarios, jugadores

app = FastAPI(title="Backend Local con FastAPI y SQLite")

# Inicializa la base de datos al iniciar
init_db()

# Rutas (endpoints)
app.include_router(usuarios.router)
app.include_router(jugadores.router)
