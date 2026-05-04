"""

Aplicacion de consola para gestion de inventario y ventas de salmon.
"""

import sys
import os
from getpass import getpass

# Asegurar que los modulos del proyecto son importables
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.mongo_manager import db_manager
from services.auth_service import AuthService, AuthenticationError
from services.inventory_service import InventoryService
from utils.validators import InputValidator, ValidationError
from utils.security import LoginAttemptTracker
from views.admin_menu import AdminMenu
from views.seller_menu import SellerMenu


def initialize_system() -> bool:
    """
    Inicializa conexion a DB y datos por defecto.
    Returns: True si todo OK, False si falla criticamente.
    """
    print("ACME SMOKED FISH - Sistema de Gestion")
    print("=" * 50)
    print("Conectando a base de datos...")
    
    if not db_manager.connect():
        print("Error critico: No se pudo conectar a MongoDB")
        print("Verifique que MongoDB este ejecutandose:")
        print("  $ mongod --dbpath /ruta/a/datos")
        return False
    
    print("Conexion establecida")
    
    try:
        AuthService.initialize_default_users()
        InventoryService.initialize_inventory()
    except Exception as e:
        print(f"Advertencia en inicializacion: {e}")
        return False
    def login_screen()-> tuple:
        """ Pantalla con validaciones de seguridad"""
        print("\n"+"="*50)
        print("INICIO DE SESION")
        print("="*50)
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            try:
                username = input("Usuario:").strip()
                try:
                    username = InputValidator.validate_username(username)
                except ValidationError as e:
                    print(f"Error:{e}")
                    attempts += 1
                    continue
                if LoginAttemptTracker.is_blocked(username):
                    print("Cuenta bloquada temporalmente por intentos fallidos")
                    print("Espere 5 minutos o contacte al administrador")
                    continue
                password = getpass("Contraseña:")
                user, session = AuthService.authenticate(username, password)
                return user, session
            except ArithmeticError as e:
                print(f"Error:{e}")
                attempts += 1
                if attempts > max_attempts:
                    print(f"Intentos restantes: {max_attempts -attempts}")
            except KeyboardInterrupt:
                print("\nSaliendo del sistema...")
                sys.exit(0)
                print("\nDemasiados intentos fallidos. Saliendo...")
                sys.exit(1)
                def main()-> None:
                    """ Punto de entrada principal."""
                    try:
                        if not initialize_system():
                            sys.exit(1)
                            user,session = login_screen()
                            print(f"\nBievenido,{user.username}! ")
                            print(f"Rol:{user.role.upper()}")
                            if user.role == "administrador":
                                menu = AdminMenu()
                            elif user.role == "vendedor":
                                menu = SellerMenu()
                            else:
                                print(f"Rol desconocido:{user.role}")
                                sys.exit(1)
                            menu.run()
                    except KeyboardInterrupt:
                        print("\nInterrupcion detectada")
                    finally:
                        print("\nCerrando conexiones...")
                        db_manager.close()
                        print("Sistema finalizado")
                        if __name__ == "__main__":
                            main()
                            


                    
                    











    