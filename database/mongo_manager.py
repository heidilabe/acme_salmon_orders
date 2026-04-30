"""
Gestor de conexion MongoDB con patron Singleton.
Impementa:Pool de conexiones, manejo de excepciones, logging de operaciones"""

from typing import Optional, Dict, Any, List
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure,DuplicateKeyError
from pymongo.collection import Collection
from contextlib import contextmanager
import logging
from datetime import datetime
from config.settings import DB_CONFIG
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s -%(name)s - %(levelname)s - %(message)s'    
)
logging = logging.getLogger(__name__)
class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    _client: Optional[MongoClient] = None
    _db = None
    def __new__(cls)-> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            return cls._instance
    def connect(self)-> bool:
        try:
            self._client = MongoClient(
                DB_CONFIG.connection_string,
                serverSelectionTimeousMS = 5000,
                maxPoolSize = 10,
                minPoolsize = 1,
            )
            self._client.admin.command('ping')
            self._db = self._client[DB_CONFIG.DB_NAME]
            self.create_indexes()
            logging.info("conexion a MongoDB establecida exitosamente")
            return True
        except ConnectionFailure as e:
            logging.error(f"Fallo de conexion a MongoDB: {e}")
            return False
        except Exception as e:
            logging.error(f"Error inesperado en conexion: {e}")
            return False
    def _create_indexes(self)-> None:
        self._db.users.create_index("username", unique = True)
        self._db.sales.create_index([("salmon_type",ASCENDING),("date",DESCENDING)])
        self._db.products.create_index("salmon_type",unique = True)
    @property
    def db(self):
        if self._db is None:
            raise RuntimeError("No hay conexion activa a la base de datos")
        return self._db
    @property
    def users(self)-> Collection:
        return self.db.users
    @property
    def products(self)-> Collection:
        return self.db.products
    @property
    def sales(self)-> Collection:
        return self.db.sales
    def close(self)-> None:
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logging.info("Conexion a MongoDB cerrada")
    def __del__(self):
        self.close()
db_manager = DatabaseManager()

        
                           

        











