""""""
import os
from typing import NoReturn
from datetime import datetime, date, timedelta

from services.auth_service import AuthService
from services.inventory_service import InventoryService
from utils.validators import InputValidator, ValidationError
from utils.security import AuditLogger
from database.mongo_manager import db_manager
class SellerMenu:
    """Interfaz de consola para perfil Vendedor."""
    
    def __init__(self):
        self.session = AuthService.get_current_session()
        self.username = self.session.username if self.session else "unknown"
        self.cart = []
    def display_header(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("  ACME SMOKED FISH - PUNTO DE VENTA")
        print(f"  Usuario: {self.username} | Rol: Vendedor")
        print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
    def display_menu(self) -> None:
        print("\nMENU DE VENTAS:")
        print("1. Nueva Venta")
        print("2. Ver Inventario Disponible")
        print("3. Mis Ventas del Dia")
        print("4. Cerrar Sesion")
        print("-" * 40)
    def run(self) -> NoReturn:
        """Bucle principal."""
        while True:
            try:
                self.display_header()
                self.display_menu()
                option = input("\nSeleccione opcion: ").strip()
                try:
                    option_num = InputValidator.validate_menu_option(option, range(1, 5))
                except ValidationError as e:
                    print(f"Error: {e}")
                    input("Presione Enter para continuar...")
                    continue
                if option_num == 1:
                    self.new_sale()
                elif option_num == 2:
                    self.view_inventory()
                elif option_num == 3:
                    self.view_my_sales()
                elif option_num == 4:
                    self.logout()
                    break
            except KeyboardInterrupt:
                print("\n\nOperacion cancelada")
                continue
            except Exception as e:
                print(f"\nError: {e}")
                input("Presione Enter para continuar...")
    def view_inventory(self) -> None:
        """Muestra inventario disponible para venta."""
        self.display_header()
        print("\nINVENTARIO DISPONIBLE")
        print("-" * 50)
        products = InventoryService.get_all_products()
        print(f"{'Tipo':<15} {'Precio/kg':>12} {'Stock':>10} {'Disponible':>12}")
        print("-" * 50)
        for product in products:
            available = max(0, product.stock_kg - product.min_stock)
            status = "OK" if available > 5 else "BAJO" if available > 0 else "SIN STOCK"
            print(f"{product.name:<15} ${product.sale_price:>10,.0f} "
                  f"{product.stock_kg:>9.2f}kg {status:>10}")
        input("\nPresione Enter para continuar...")
    def new_sale(self) -> None:
        """Proceso de venta interactivo."""
        self.cart = []
        while True:
            self.display_header()
            print("\nNUEVA VENTA")
            if self.cart:
                print("\nItems en carrito:")
                total = 0
                for i, item in enumerate(self.cart, 1):
                    subtotal = item["quantity_kg"] * item["unit_price"]
                    total += subtotal
                    print(f"  {i}. {item['name']}: {item['quantity_kg']}kg "
                          f"@ ${item['unit_price']:,.0f}/kg = ${subtotal:,.0f}")
                print(f"\n  TOTAL: ${total:,.0f}")
            print("-" * 40)
            print("\nSeleccione tipo de salmon (0 para finalizar):")
            products = InventoryService.get_all_products()
            for i, product in enumerate(products, 1):
                available = max(0, product.stock_kg - product.min_stock)
                print(f"{i}. {product.name} - ${product.sale_price:,.0f}/kg "
                      f"(Disp: {available:.2f}kg)")
            print("0. Finalizar venta")
            print("C. Cancelar venta")
            choice = input("\nOpcion: ").strip().upper()
            if choice == "C":
                print("Venta cancelada")
                self.cart = []
                input("Presione Enter...")
                return
            if choice =="0":
                if not self.cart:
                    print("carrito vacio")
                    input("Presione Enter....")
                    return
                self._finalize_sale()
                return
            try:
                idx = int(choice) - 1
                if idx < 0 or idx > len(products):
                    raise ValueError
            except ValueError:
                print("Opcion invalida")
                input("Presione Enter...")
                continue
            selected = products[idx]
            available = max(0, selected.stock_kg - selected.min_stock)
            if available <=0:
                print(f"{selected.name} sin stock disponible")
                input("Presione Enter...")
                continue
            try:
                kg_str = input(f"Cantidad en kg (max{available:.2f}):").strip()
                kg = InputValidator.validate_kg_amount(kg_str)
                if kg > available:
                    print(f"Maximo disponible:{available:.2f}kg")
                    input("presione Enter...")
                    continue
                existing = next((item for item in self.cart if item["salmon_type"] == selected.salmon_type),None)
                if existing:
                    if existing["quantity_kg"]+ kg > available:
                        print("total en carrito excederia disponible")
                        input("Presione enter...")
                        continue
                    existing["quantity_kg"] += kg
                else:
                    self.cart.append({
                        "salmon_type": selected.salmon_type,
                        "name": selected.name,
                        "quantity_kg": kg,
                        "unit_price": selected.sale_price
                    })
                    print(f"{kg}kg de {selected.name} agregado")
            except ValidationError as e:
                print(f"Error: {e}")
                input("Presione Enter...")
    def _finalize_sale(self) -> None:
        """Finaliza la venta y persistencia."""
        self.display_header()
        print("\nRESUMEN DE VENTA")
        print("-" * 50)
        total = sum(item["quantity_kg"] * item["unit_price"] for item in self.cart)
        for item in self.cart:
            subtotal = item["quantity_kg"] * item["unit_price"]
            print(f"{item['name']:<20} {item['quantity_kg']:>6.2f}kg "
                  f"${item['unit_price']:>10,.0f} ${subtotal:>10,.0f}")
        print("-" * 50)
        print(f"{'TOTAL':<20} ${total:>28,.0f}")
        customer = input("\nNombre cliente (opcional): ").strip()
        notes = input("Notas (opcional): ").strip()
        confirm = input("\nConfirmar venta? (S/N): ").strip().upper()
        if confirm != "S":
            print("Venta cancelada")
            self.cart = []
            input("Presione Enter...")
            return
        try:
            items_data = [
                {
                    "salmon_type": item["salmon_type"],
                    "quantity_kg": item["quantity_kg"]
                }
                for item in self.cart
            ]
            
            sale = InventoryService.register_sale(
                seller_username=self.username,
                items_data=items_data,
                customer_name=customer,
                notes=notes
            )
            print(f"\nVENTA REGISTRADA EXITOSAMENTE")
            print(f"   Numero: {sale.sale_id}")
            print(f"   Total: ${sale.total_amount:,.0f}")
            print(f"   Ganancia neta: ${sale.total_profit:,.0f}")
            
            self.cart = []
            AuditLogger.log_action(self.username, "SALE_COMPLETED", 
                                 f"ID: {sale.sale_id}, Total: ${sale.total_amount}")
        except Exception as e:
            print(f"\nError al registrar venta: {e}")
        
        input("\nPresione Enter para continuar...")
    def view_my_sales(self) -> None:
        """Muestra ventas del vendedor actual."""
        self.display_header()
        print(f"\nMIS VENTAS - {self.username}")
        print("-" * 60)
        today = date.today()
        tomorrow = today + timedelta(days=1)
        cursor = db_manager.sales.find({
            "seller_username": self.username,
            "date": {
                "$gte": datetime.combine(today, datetime.min.time()),
                "$lt": datetime.combine(tomorrow, datetime.min.time())
            }
        }).sort("date", -1)
        sales = list(cursor)
        
        if not sales:
            print("No hay ventas registradas hoy")
        else:
            total_day = 0
            print(f"{'Hora':<10} {'ID':<20} {'Total':>12} {'Items':>20}")
            print("-" * 65)
            for doc in sales:
                sale_time = doc["date"].strftime("%H:%M")if  isinstance(doc["date"],datetime) else "N/A"
                items_summary = ", ".join([
                    f"{item['salmon_type'][:3]}:{item['quantity_kg']}kg"
                    for item in doc["items"]
                ])
                print(f"{sale_time:<10} {str(doc['_id']):<20} "
                f"${doc['total_amount']:>10,.0f} {items_summary:>20}")
                total_day += doc["total_amount"]
            print("-" * 65)
            print(f"{'TOTAL DIA':<20} ${total_day:>42,.0f}")
        input("\nPresione Enter para continuar...")
    
    def logout(self) -> None:
        """Cierra sesion."""
        print(f"\nHasta pronto, {self.username}")
        AuthService.logout()

                    
                

            



                  
            
         
           
   

    
        
        
            
                    
