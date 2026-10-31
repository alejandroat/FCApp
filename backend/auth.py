import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_connection

SECRET_KEY = "FCMOBILEantesFIFAMOBILE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_byte_enc)

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Obtener el 'sub' y asegurar que sea string, luego convertirlo a entero para la BD
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        user_id = int(user_id_str)
        
    except Exception as e:
        # Capturamos CUALQUIER error de JWT (incluyendo JWTClaimsError) de forma segura
        print(f"❌ ERROR JWT al decodificar: {e}")
        raise credentials_exception
    
    try:
        conn = get_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,)).fetchone()
        conn.close()
        
        if user is None:
            print("❌ ERROR: Usuario no encontrado en la base de datos")
            raise credentials_exception
            
        return dict(user)
    except Exception as e:
        print(f"❌ ERROR en consulta DB: {e}")
        raise credentials_exception