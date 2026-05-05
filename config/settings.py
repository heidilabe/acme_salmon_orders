"""Configuracion centralizada de la aplicacion 
"""
import os
from dataclasses import dataclass
from typing import Final

@dataclass(frozen=True)
class DatabaseConfig:
    """Configuracion inmutable de la base de datos
    """
    HOST: str = os.getenv("MONGO_HOST", "localhost")
    PORT: int = int(os.getenv("MONGO_PORT","27017"))
    DB_NAME: str = os.getenv("MONGO_DB","acme_salmon_db")
    USER: str = os.getenv("MONGO_USER","")
    PASSWORD: str = os.getenv("MONGO_PASSWORD","")
    @property
    def connection_string(self) -> str:
        """Genera la cadena de conexion a MongoDB corregida"""
        if self.USER and self.PASSWORD:
            return f"mongodb://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB_NAME}"
        return f"mongodb://{self.HOST}:{self.PORT}/{self.DB_NAME}"
@dataclass(frozen=True)
class AppConfig:
        """
        Configuracion de la aplicacion.
        """
        SALMON_TYPES: Final[tuple] = (
            {
                "id":"atlantico","nombre":"Salmon Atlantico","precio_venta": 12000,"costo": 8000
            
            },
            {
                "id":"nordico","nombre":"Salmon Nordico","precio_venta": 15000,"costo": 10000
            },
            {
                "id": "pacifico","nombre": "Salmon Pacifico","precio_venta": 7000,"costo": 5000
            }
        )
        INITIAL_STOCK_KG:float = 10.0
        MAX_LOGIN_ATTEMPTS: int = 3
        SESSION_TIMEOUT_MINUTES: int = 30

        ROLE_ADMIN: str = "administrador"
        ROLE_SELLER: str = "vendedor"

DB_CONFIG = DatabaseConfig()
APP_CONFIG = AppConfig()

    
    
       
            
        

        

        


