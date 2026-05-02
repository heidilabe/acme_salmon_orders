"""
Servisio de autenticacion con gestion de sesiones
"""
from typing import Optional,Tuple
from datetime import datetime
from database.mongo_manager import db_manager
from models.user import User, Administrator,Seller
from utils.validators import InputValidator, ValidationError
from utils.security import LoginAttemptTracker, Session, AuditLogger

class AuthenticationError(Exception):
    """
    Error de autenticacion 
    """
pass

class AutheService:
    """ 
    Servicio de autentificacion y gestion de sesiones
    """
    _current_sesion: Optional[Session]= None
    @classmethod
    def initialize_default_users(cls)-> None:
        """
        Crea usuarios por defecto si no existen.
        """
        users_colletion = db_manager.users
        if users_colletion.count_documents({})> 0:
            return
        admin = Administrator(
            username="admin",
            password_hash=User.hash_password("Admin@2024!")


        )
        seller = Seller(
            username="vendedor",
            password_hash=User.hash_password("Vendedor@2024!")


        )
        users_colletion.insert_many([
            {
                "username": admin.username,
                "password_hash": admin.password_hash,
                "role": admin.role,
                "is active":admin.is_active,
                "created_at": admin.created_at


            },
            {
                "username":seller.username,
                "password_hash": seller.password_hash,
                "role": seller.role,
                "is_active": seller.is_active,
                "created_at": seller.created_at


            }
        ])
        print("Usuarios por defecto creados:")
        print("Admin: admin / Admin@2024!")
        print("Vendedor: vendedor / Vendedor@2024!")
    @classmethod
    def authenticate(cls, username: str, password: str)-> Tuple[User, Session]:
        """
        Autentica usuario y crea sesion.
        """
        try:
            username = InputValidator.validate_username(username)
        except ValidationError as e:
            raise AuthenticationError(str(e)) 
        if LoginAttemptTracker.is_blocked(username):
            raise AuthenticationError(
            "Cuenta temporalmente bloqueada por intentos fallidos, espere 5 minutos"

            )
        user_data = db_manager.users.find_one({"username": username})
        if not user_data:
            LoginAttemptTracker.record_attempt(username)
            raise AuthenticationError("Credenciales invalidas")
        user = cls._create_user_instance(user_data)
        if not user.verify_password(password):
            is_blocked = LoginAttemptTracker.record_attempt(username)
            if is_blocked:
                raise AuthenticationError(
                    "cuenta bloqueada tras 3 intentos fallidos. Espere 5 minutos."


                )
            raise AuthenticationError("credenciales invalidas")
        LoginAttemptTracker.reset(username)
        user.update_last_login()
        db_manager.users.update_one(
            {"username": username},
            {"$set":{"last_login": user.last_login}}

        )
        Session = Session(
            username=user.username,
            role=user.role

        )
        cls._current_session = Session
        AuditLogger.log_action(username,"LOGIN", "Autenticacion exitosa")
        return user, Session
    @classmethod
    def _create_user_instance(cls,data: dict)-> User:
        """ Factory para instanciar el tipo correcto de usuario."""
        if data["role"] == "administrador":
            return Administrator(data["username"], data["password_hash"])
        return Seller(data["username"], data["password_hash"])
    @classmethod
    def get_current_session(cls)-> Optional[Session]:
        """
        Obtiene session activa.
        """
        if cls._current_session and cls._current_session.is_expired():
            cls.logout()
            return None
        return cls._current_session
    @classmethod
    def logout(cls)-> None:
        """Cierra sesion actual."""
        if cls._current_sesion:
            AuditLogger.log_action(
                cls._current_sesion.username,
                "LOGOUT", "Cierre de sesion"



            )
            cls._current_sesion = None
    @classmethod
    def require_auth(cls,required_role: Optional[str] = None)-> Session:
        ssesion = cls._get_current_session()
        if not ssesion:
            raise AuthenticationError("Sesion no iniciada o expirada")
        if required_role and Session.role != required_role:
            AuditLogger.log_action(
                ssesion.username,
                "ACCESS_DENIED",
                f"Requiere:{required_role}"


            )
            raise AuthenticationError("Permisos insuficientes")
        ssesion.update_activity()
        return ssesion
        

        

        





