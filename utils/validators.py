"""
Utilidades de validacion y sanitizacion de entrada.
Previene:Inyeccion, desbordamiento, tipos incorrectos, valores negativos.
"""
import re
from typing import Optional
class ValidationError(Exception):
    pass
class InputValidator:
    _USERNAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]{3,19}$')
    _PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    @staticmethod
    def validate_username(username: str) -> str:
        if not isinstance(username, str):
            raise ValidationError("Username debe ser texto")
        
   

        

    

    