from sqlalchemy.orm import Session
from app.domain.models.models import Usuario
from typing import Optional

class UsuarioRepository:
    
    @staticmethod
    def crear_usuario(db: Session, email: str, nombre: str, password_hash: str) -> Usuario:
        """Crea un nuevo usuario en la base de datos"""
        usuario = Usuario(
            email=email,
            nombre=nombre,
            password_hash=password_hash
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    
    @staticmethod
    def obtener_por_email(db: Session, email: str) -> Optional[Usuario]:
        """Busca un usuario por su email"""
        return db.query(Usuario).filter(Usuario.email == email).first()
    
    @staticmethod
    def obtener_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
        """Busca un usuario por su ID"""
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()
