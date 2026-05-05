"""
Modelos de usuarios con encapsulamiento y hash seguro de contraseñas.
Seguridad: bcript para hashing, salt automatico, validacion de fortaleza"""


from dataclasses import dataclass, field
from datetime import datetime
import bcrypt
import re

from utils.validators import InputValidator, ValidationError

@dataclass
class User:
    username: str
    password_hash: str
    role: str
    is_active: bool = True
    last_login: datetime = None
    created_at: datetime = field(default_factory=datetime.now)
    _username_pattern = re.compile(r'^[a-zA-Z0-9_]{4,20}$')
    def __post_init__(self):
     if not self._username_pattern.match(self.username):
        raise ValueError("Username debe ser alfanumerico, 4-20 caracteres")
    @classmethod
    def hash_password(cls, plain_password: str) -> str:
        InputValidator.Validate_password_strength(plain_password)
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def update_last_login(self) -> None:
        self.last_login = datetime.now()

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "role": self.role,
            "is_active": self.is_active,
            "last_login": self.last_login,
            "created_at": self.created_at
        }
class Administrator(User):
    def __init__(self, username: str, password_hash: str):
        super().__init__(username, password_hash, role='administrador')
    def can_manage_inventory(self) -> bool:
        return True
    def can_view_reports(self) -> bool:
        return True
    def can_sell(self) -> bool:
        return False
class Seller(User):
    def __init__(self, username: str, password_hash: str):
        super().__init__(username, password_hash, role='vendedor')
    def can_manage_inventory(self) -> bool:
        return False
    def can_view_reports(self) -> bool:
        return False
    def can_sell(self) -> bool:
        return True
     

        
