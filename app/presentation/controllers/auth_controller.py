from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.data.sources.database import get_db
from app.domain.schemas.auth_schemas import (
    UsuarioRegister, 
    UsuarioLogin, 
    TokenResponse, 
    UsuarioResponse
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    datos: UsuarioRegister,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en el sistema.
    
    - **email**: Email único del usuario
    - **nombre**: Nombre completo del usuario
    - **password**: Contraseña (se almacenará hasheada)
    """
    try:
        # Registrar el usuario
        usuario = AuthService.registrar_usuario(db, datos)
        
        # Generar token
        access_token = AuthService.crear_access_token(
            data={"sub": usuario.email, "id": usuario.id}
        )
        
        # Preparar respuesta
        usuario_response = UsuarioResponse(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            fecha_registro=usuario.fecha_registro
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            usuario=usuario_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
def login(
    datos: UsuarioLogin,
    db: Session = Depends(get_db)
):
    """
    Inicia sesión con email y contraseña.
    
    - **email**: Email del usuario
    - **password**: Contraseña del usuario
    
    Retorna un token JWT para autenticación.
    """
    try:
        # Autenticar usuario
        usuario, access_token = AuthService.autenticar_usuario(db, datos)
        
        # Preparar respuesta
        usuario_response = UsuarioResponse(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            fecha_registro=usuario.fecha_registro
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            usuario=usuario_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar sesión: {str(e)}"
        )
