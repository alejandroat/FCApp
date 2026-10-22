from pydantic import BaseModel, EmailStr

# Datos que llegan al crear un usuario
class UsuarioCreate(BaseModel):
    nombre: str
    contrasena: str

# Datos que se devuelven al cliente
class UsuarioResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True
