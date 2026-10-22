from pydantic import BaseModel, Field
from typing import Optional

class JugadorCreate(BaseModel):
    nombre: str
    valoracion: int
    posicion_principal: str
    pais: str
    equipo: str
    posicion_secundaria: Optional[str] = None
    dorsal: Optional[int] = None
    equipacion: Optional[str] = None
    rango: int = Field(default=0, ge=0, le=5)
    habilitado: bool = True
    programa: Optional[str] = None
    imagen_url: Optional[str] = None

class JugadorResponse(BaseModel):
    id: int
    nombre: str
    valoracion: int
    posicion_principal: str
    pais: str
    equipo: str
    usuario_id: int
    posicion_secundaria: Optional[str] = None
    dorsal: Optional[int] = None
    equipacion: Optional[str] = None
    rango: int
    habilitado: bool
    programa: Optional[str] = None
    imagen_url: Optional[str] = None

class Config:
    from_attributes = True
    
class JugadorUpdate(BaseModel):
    nombre: Optional[str] = None
    valoracion: Optional[int] = None
    posicion_principal: Optional[str] = None
    posicion_secundaria: Optional[str] = None
    pais: Optional[str] = None
    equipo: Optional[str] = None
    dorsal: Optional[int] = None
    equipacion: Optional[str] = None
    rango: Optional[int] = None
    habilitado: Optional[bool] = None
    programa: Optional[str] = None
    imagen_url: Optional[str] = None