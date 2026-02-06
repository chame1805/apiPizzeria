from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
import os

from app.data.repositories.usuario_repository import UsuarioRepository
from app.domain.schemas.auth_schemas import UsuarioRegister, UsuarioLogin
from app.domain.models.models import Usuario

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT - Desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_segura_cambiala_en_produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))  # 7 días por defecto

class AuthService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea la contraseña"""
        # Bcrypt tiene un límite de 72 bytes, truncamos de manera segura
        if len(password) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    
    @staticmethod
    def verificar_password(password_plano: str, password_hash: str) -> bool:
        """Verifica que la contraseña coincida con el hash"""
        return pwd_context.verify(password_plano, password_hash)
    
    @staticmethod
    def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crea un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def registrar_usuario(db: Session, datos: UsuarioRegister) -> Usuario:
        """Registra un nuevo usuario"""
        # Verificar si el email ya existe
        usuario_existente = UsuarioRepository.obtener_por_email(db, datos.email)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Hashear la contraseña
        password_hash = AuthService.hash_password(datos.password)
        
        # Crear el usuario
        usuario = UsuarioRepository.crear_usuario(
            db=db,
            email=datos.email,
            nombre=datos.nombre,
            password_hash=password_hash
        )
        
        return usuario
    
    @staticmethod
    def autenticar_usuario(db: Session, datos: UsuarioLogin) -> tuple[Usuario, str]:
        """Autentica un usuario y devuelve el usuario y el token"""
        # Buscar el usuario por email
        usuario = UsuarioRepository.obtener_por_email(db, datos.email)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar la contraseña
        if not AuthService.verificar_password(datos.password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear el token
        access_token = AuthService.crear_access_token(
            data={"sub": usuario.email, "id": usuario.id}
        )
        
        return usuario, access_token
