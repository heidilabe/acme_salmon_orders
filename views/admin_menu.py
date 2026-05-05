"""
Menú interactivo para Administrador.
UI desacoplada de lógica de negocio.
"""

from typing import NoReturn
import os

from services.auth_service import AuthService
from services.inventory_service import InventoryService
from services.report_service import ReportService
from utils.validators import InputValidator, ValidationError
from utils.security import AuditLogger
from config.settings import APP_CONFIG


class AdminMenu:
    """Interfaz de consola para perfil Administrador."""
    
    def __init__(self):
        self.session = AuthService.get_current_session()
        self.username = self.session.username if self.session else "unknown"
    
    def display_header(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("  🐟 ACME SMOKED FISH - PANEL DE ADMINISTRACIÓN")
        print(f"  Usuario: {self.username} | Rol: Administrador")
        print("=" * 60)
    
    def display_menu(self) -> None:
        print("\n📋 MENÚ PRINCIPAL:")
        print("1. 📦 Gestión de Inventario")
        print("2. 💰 Actualizar Precios")
        print("3. 📊 Ver Historial de Ventas")
        print("4. 📈 Reportes y Estadísticas")
        print("5. 🔒 Cerrar Sesión")
        print("-" * 40)
    
    def run(self) -> NoReturn:
        """Bucle principal del menú."""
        while True:
            try:
                self.display_header()
                self.display_menu()
                
                option = input("\nSeleccione opción: ").strip()
                
                try:
                    option_num = InputValidator.validate_menu_option(option, range(1, 6))
                except ValidationError as e:
                    print(f"❌ {e}")
                    input("Presione Enter para continuar...")
                    continue
                
                if option_num == 1:
                    self.manage_inventory()
                elif option_num == 2:
                    self.update_prices()
                elif option_num == 3:
                    self.view_sales_history()
                elif option_num == 4:
                    self.generate_reports()
                elif option_num == 5:
                    self.logout()
                    break
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Operación cancelada por usuario")
                continue
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                AuditLogger.log_action(self.username, "ERROR", str(e))
                input("Presione Enter para continuar...")
    
    def manage_inventory(self) -> None:
        """Submenú de gestión de inventario."""
        while True:
            self.display_header()
            print("\n📦 GESTIÓN DE INVENTARIO")
            print("-" * 40)
            
            # Mostrar estado actual
            products = InventoryService.get_all_products()
            for i, product in enumerate(products, 1):
                status = "🟢" if product.stock_kg > 5 else "🟡" if product.stock_kg > 1 else "🔴"
                print(f"{i}. {status} {product.name}")
                print(f"   Stock: {product.stock_kg}kg | Precio: ${product.sale_price:,.0f}")
                print()
            
            print("Opciones:")
            print("1. Agregar stock")
            print("2. Quitar stock")
            print("3. Volver al menú principal")
            
            try:
                opt = input("\nOpción: ").strip()
                opt_num = InputValidator.validate_menu_option(opt, range(1, 4))
                
                if opt_num == 3:
                    break
                
                # Seleccionar producto
                print("\nSeleccione tipo de salmón:")
                for i, (tid, name, _, _) in enumerate(APP_CONFIG.SALMON_TYPES, 1):
                    print(f"{i}. {name}")
                
                prod_opt = input("Tipo: ").strip()
                prod_idx = InputValidator.validate_menu_option(prod_opt, range(1, 4)) - 1
                salmon_type = APP_CONFIG.SALMON_TYPES[prod_idx][0]
                
                amount_str = input("Cantidad en kg (ej: 5.5): ").strip()
                amount = InputValidator.validate_kg_amount(amount_str)
                
                if opt_num == 1:
                    InventoryService.update_stock(salmon_type, amount, True, self.username)
                    print(f"✅ Stock actualizado: +{amount}kg")
                else:
                    InventoryService.update_stock(salmon_type, amount, False, self.username)
                    print(f"✅ Stock actualizado: -{amount}kg")
                
                AuditLogger.log_action(self.username, "INVENTORY_UPDATE", 
                                     f"{salmon_type}: {'+' if opt_num == 1 else '-'}{amount}kg")
                
            except ValidationError as e:
                print(f"❌ {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            input("\nPresione Enter para continuar...")
    
    def update_prices(self) -> None:
        """Actualización de precios de compra/venta."""
        self.display_header()
        print("\n💰 ACTUALIZAR PRECIOS")
        print("-" * 40)
        
        products = InventoryService.get_all_products()
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name}")
            print(f"   Precio Venta: ${product.sale_price:,.0f}")
            print(f"   Precio Compra: ${product.purchase_price:,.0f}")
            print(f"   Margen: {product.margin_percentage:.1f}%")
            print()
        
        try:
            print("Seleccione tipo de salmón:")
            for i, (tid, name, _, _) in enumerate(APP_CONFIG.SALMON_TYPES, 1):
                print(f"{i}. {name}")
            
            prod_opt = input("Tipo: ").strip()
            prod_idx = InputValidator.validate_menu_option(prod_opt, range(1, 4)) - 1
            salmon_type = APP_CONFIG.SALMON_TYPES[prod_idx][0]
            
            sale_price_str = input("Nuevo precio de VENTA (COP/kg): ").strip()
            sale_price = InputValidator.validate_positive_amount(sale_price_str, "Precio venta")
            
            purchase_price_str = input("Nuevo precio de COMPRA (COP/kg): ").strip()
            purchase_price = InputValidator.validate_positive_amount(purchase_price_str, "Precio compra")
            
            if sale_price <= purchase_price:
                print("❌ El precio de venta debe ser mayor al de compra")
                input("Presione Enter...")
                return
            
            InventoryService.update_prices(salmon_type, sale_price, purchase_price, self.username)
            print(f"✅ Precios actualizados para {APP_CONFIG.SALMON_TYPES[prod_idx][1]}")
            
        except ValidationError as e:
            print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def view_sales_history(self) -> None:
        """Visualización de historial de ventas."""
        self.display_header()
        print("\n📊 HISTORIAL DE VENTAS")
        print("-" * 60)
        
        try:
            limit_str = input("Cantidad de registros a mostrar (default 20): ").strip()
            limit = int(limit_str) if limit_str else 20
            if limit > 100:
                limit = 100
        except ValueError:
            limit = 20
        
        sales = InventoryService.get_sales_history(limit=limit)
        
        if not sales:
            print("No hay ventas registradas")
        else:
            print(f"{'ID':<24} {'Fecha':<20} {'Vendedor':<15} {'Total':>12} {'Ganancia':>12}")
            print("-" * 85)
            
            for sale in sales:
                date_str = sale.date.strftime("%Y-%m-%d %H:%M") if sale.date else "N/A"
                print(f"{str(sale.sale_id):<24} {date_str:<20} "
                      f"{sale.seller_username:<15} ${sale.total_amount:>10,.0f} "
                      f"${sale.total_profit:>10,.0f}")
                
                # Detalle de items
                for item in sale.items:
                    print(f"  └─ {item.salmon_type}: {item.quantity_kg}kg @ ${item.unit_price:,.0f}/kg")
        
        input("\nPresione Enter para continuar...")
    
    def generate_reports(self) -> None:
        """Submenú de reportes."""
        while True:
            self.display_header()
            print("\n📈 REPORTES Y ESTADÍSTICAS")
            print("-" * 40)
            print("1. Relación Coste-Ganancia por Tipo")
            print("2. Salmón más Vendido (últimos 5 pedidos)")
            print("3. Estado Actual del Inventario")
            print("4. Resumen de Ventas (30 días)")
            print("5. Volver")
            
            try:
                opt = input("\nOpción: ").strip()
                opt_num = InputValidator.validate_menu_option(opt, range(1, 6))
                
                if opt_num == 5:
                    break
                elif opt_num == 1:
                    self._report_cost_profit()
                elif opt_num == 2:
                    self._report_top_salmon()
                elif opt_num == 3:
                    self._report_inventory()
                elif opt_num == 4:
                    self._report_summary()
                
            except ValidationError as e:
                print(f"❌ {e}")
            
            input("\nPresione Enter para continuar...")
    
    def _report_cost_profit(self) -> None:
        """Reporte de coste vs ganancia."""
        print("\n📊 RELACIÓN COSTE-GANANCIA")
        print("=" * 70)
        
        report = ReportService.get_cost_profit_relation()
        
        if not report:
            print("No hay datos suficientes")
            return
        
        print(f"{'Tipo':<15} {'Kg Vendidos':<12} {'Costo':>12} {'Ingreso':>12} "
              f"{'Ganancia':>12} {'Margen %':>10}")
        print("-" * 75)
        
        for item in report:
            print(f"{item['name']:<15} {item['total_kg_sold']:<12.2f} "
                  f"${item['total_cost']:>10,.0f} ${item['total_revenue']:>10,.0f} "
                  f"${item['net_profit']:>10,.0f} {item['margin_percentage']:>9.1f}%")
    
    def _report_top_salmon(self) -> None:
        """Reporte de salmón más vendido."""
        print("\n🏆 SALMÓN MÁS VENDIDO - ÚLTIMOS 5 PEDIDOS")
        print("=" * 50)
        
        report = ReportService.get_top_salmon_last_orders(5)
        
        if not report:
            print("No hay pedidos recientes")
            return
        
        print(f"Tipo: {report['name']} ({report['salmon_type']})")
        print(f"Kg vendidos: {report['total_kg_in_last_n_orders']}kg")
        print(f"Apariciones: {report['appearances_in_orders']} de {report['orders_analyzed']} pedidos")
        print(f"Período: {report['period']}")
    
    def _report_inventory(self) -> None:
        """Reporte de inventario actual."""
        print("\n📦 ESTADO DEL INVENTARIO")
        print("=" * 60)
        
        report = ReportService.get_inventory_status()
        
        print(f"{'Tipo':<15} {'Stock':<10} {'Estado':<10} {'P.Venta':>10} {'P.Compra':>10}")
        print("-" * 60)
        
        for item in report:
            status_emoji = {"OK": "🟢", "LOW": "🟡", "CRITICAL": "🔴"}.get(item['status'], "⚪")
            print(f"{item['name']:<15} {item['stock_kg']:<10.2f} "
                  f"{status_emoji} {item['status']:<8} "
                  f"${item['sale_price']:>9,.0f} ${item['purchase_price']:>9,.0f}")
    
    def _report_summary(self) -> None:
        """Resumen de ventas."""
        print("\n📈 RESUMEN DE VENTAS (ÚLTIMOS 30 DÍAS)")
        print("=" * 40)
        
        summary = ReportService.get_sales_summary(30)
        
        print(f"Período: {summary['period_days']} días")
        print(f"Total ventas: {summary['total_sales']}")
        print(f"Ingresos totales: ${summary['total_revenue']:,.0f}")
        print(f"Ganancia neta: ${summary['total_profit']:,.0f}")
        print(f"Promedio por venta: ${summary['avg_sale']:,.0f}")
    
    def logout(self) -> None:
        """Cierra sesión."""
        print(f"\n👋 Hasta pronto, {self.username}")
        AuthService.logout()
