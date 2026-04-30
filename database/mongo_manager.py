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










