from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.domain.models.models import Usuario
from app.domain.models.order_models import WaiterProfile


class WaiterRepository:

    @staticmethod
    def get_usuario(db: Session, user_id: int) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.id == user_id).first()

    @staticmethod
    def get_profile(db: Session, user_id: int) -> Optional[WaiterProfile]:
        return (
            db.query(WaiterProfile)
            .filter(WaiterProfile.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_full(db: Session, user_id: int) -> Optional[Tuple[Usuario, WaiterProfile]]:
        """Devuelve (usuario, perfil) o None si el usuario no existe."""
        usuario = WaiterRepository.get_usuario(db, user_id)
        if not usuario:
            return None
        profile = WaiterRepository.get_profile(db, user_id)
        # Si todavía no tiene perfil extendido, creamos uno vacío persistido
        if not profile:
            profile = WaiterProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return usuario, profile

    @staticmethod
    def update_name_phone(
        db: Session,
        user_id: int,
        name: Optional[str],
        phone: Optional[str],
    ) -> Optional[Tuple[Usuario, WaiterProfile]]:
        """Actualiza nombre en usuarios y/o teléfono en waiter_profiles."""
        result = WaiterRepository.get_full(db, user_id)
        if not result:
            return None
        usuario, profile = result

        if name is not None:
            usuario.nombre = name

        if phone is not None:
            profile.phone = phone

        db.commit()
        db.refresh(usuario)
        db.refresh(profile)
        return usuario, profile

    @staticmethod
    def update_photo(db: Session, user_id: int, photo_url: str) -> Optional[WaiterProfile]:
        """Actualiza la URL de la foto del mesero."""
        result = WaiterRepository.get_full(db, user_id)
        if not result:
            return None
        _, profile = result
        profile.photo_url = photo_url
        db.commit()
        db.refresh(profile)
        return profile
