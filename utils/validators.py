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
        username = username.strip().lower()
        if not InputValidator._USERNAME_PATTERN.match(username):
            raise ValidationError(
                "Username invalido. Debe iniciar con letra,4-20 caracteres alfanumericos y guione bajos"

            )
        return username
    @staticmethod
    def Validate_password_strength(password: str)-> bool:
        if not isinstance(password, str):
            raise ValidationError("Contrasena debe ser texto")
        if len(password) < 8:
            raise ValidationError("Contraseña debe tener minimo 8 caracteres")
        if not InputValidator._PASSWORD_PATTERN.match(password):
            raise ValidationError(
                "Contraseña insegura. Requiere: mayuscula, minuscula,numero y caracter especial (@$!%+?&)"
            )
        return True
    @staticmethod
    def validate_positive_amount(value, field_name: str = "Valor")-> float:
        try:
            amount = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} debe ser un número válido")
        if amount <= 0:
            raise ValidationError(f"{field_name} debe ser mayor a cero")
        if amount > 1_000_000:
            raise ValidationError(f"{field_name}excede limite maximo permitido")
        return amount
    @staticmethod
    def Validate_non_negative(value,field_name: str ="Valor")-> float:
        try:
            amount = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}debe ser un numero valido")
        if amount < 0:
            raise ValidationError(f"{field_name}no puede ser negativo")
        return amount
    @staticmethod
    def validate_salmon_type(salmon_type: str, valid_types: tuple)-> str:
        salmon_type = salmon_type.strip().lower()
        valid_ids = [t[0] for t in valid_types]
        if salmon_type not in valid_ids:
            raise ValidationError(f"Tipo de salmon invalido. Opciones:{",".join(valid_ids)}")
        return salmon_type
    @staticmethod
    def validate_kg_amount(kg: str)-> float:
        try:
            amount = round(float(kg),2)
        except (ValueError, TypeError):
            raise ValidationError("cantidad debe ser un numero (ej:1.5)")
        if amount <=0:
            raise ValidationError("cantidad debe ser mayor a 0 kg")
        if amount > 1000:
            raise ValidationError("cantidad maxima por operacion: 1000 kg")
        return amount
    @staticmethod
    def validate_menu_otion(option:str, valid_options:range)-> int:
        try:
            opt = int(option.strip())
        except (ValueError):
            raise ValidationError("opcion debe ser un numero")
        if opt not in valid_options:
            raise ValidationError("opcion fuera de rango")
        return opt
    @staticmethod
    def sanitize_string(text: str, max_length: int = 200)-> str:
        if not isinstance(text, str):
            return ""
        sanitized = "".join(char for char in text if ord (char)>= 32 or char in'\n\t')
        return sanitized[:max_length].strip()

        
        
        
            
        

        
    


                                  
        


        
        
        
   

        

    

    