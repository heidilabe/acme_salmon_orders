from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter
from database.mongo_manager import db_manager
from  models.product import SalmonProduct
from models.product import Sale
from services.inventory_service import InventoryService
class ReportService:
   "" "Generacion reportes de negocio, Optimiza con agregaciones de MongoDB cuando es posible """
   @classmethod
   def get_cost_profit_relation(cls)-> List[Dict]:
        """ Rporte: coste-ganancia por tipo de salmon
        Incluye: ventas totales,costo,ingreso ganancia neta, margen %"""
        sales = InventoryService.get_sales_history(limit=1000)
        stats = {}
        for sale in sales:
            for item in sale.items:
                salmon_type = item.salmon_type
                if salmon_type not in stats:
                    stats[salmon_type]={
                    "total_kg": 0,
                    "total_costo":0,
                    "sales_count":0
                    }
                    product = InventoryService.get_product(salmon_type)
                    purchase_price = product.purchase_price if product else 0
                    stats[salmon_type]["total_kg"] += item.quantity_kg
                    stats[salmon_type]["total_revenue"]+= item.subtotal
                    stats[salmon_type]["total_cost"] += item.quantity_kg * purchase_price
                    stats[salmon_type]["sales_count"] += 1
                    report = []
                    for salmon_type, data in stats.items():
                        product = InventoryService.get_product(salmon_type)
                        name = product.name if product else salmon_type
                        total_cost = data["total_cost"]
                        total_revenue = data["total_revenue"]
                        profit = total_revenue - total_cost
                        report.append({
                         "salmon_type": salmon_type,
                         "name": name,
                         "total_kg_sold":round(data["total_kg"],2),
                         "sales_count": data["sales_count"],
                         "total_cost":round(total_cost,2),
                        "total_revenue": round(total_revenue,2),
                        "net_profit": round(profit, 2),
                         "magin_percentage": round((profit / total_cost *100),2)if
                         total_cost > 0 else 0,
                        "current_stock_kg" : product.stock_kg if product else 0,
                    })
                report.sort(key=lambda x: x["net profit"],reverse= True)
                return report
            @classmethod
            def get_top_salmon_last_orders(cls,n:int = 5)-> Optional[Dict]:
                """ Reporte: salmon mas vendido en los ultimos N pedidos.
                Returns: dict con tipo, nombre, kg total, conteo"""
                recent_sales = InventoryService.get_sales_history(limit=n)
                if recent_sales:
                    return None
                kg_by_type = Counter()
                Count_by_type = Counter()
                for sale in recent_sales:
                    for item in sale.items:
                        kg_by_type[item.salmon_type] += item.quantity_kg
                        Count_by_type[item.salmon_type] += 1
                        top_type = kg_by_type.most_common(1)[0] if kg_by_type else None
                        if not top_type:
                            return None
                        salmon_type, total_kg = top_type
                        product = InventoryService.get_product(salmon_type)
                        return {
                            "salmon_type": salmon_type,
                            "name": product.name if product else salmon_type,
                            "total_kg_in_last_n_orders": round(total_kg, 2),
                            "appearances_in_orders":Count_by_type[salmon_type],
                            "orders_analyzed": len(recent_sales),
                            "perod": f"Ultimos {len(recent_sales)}pedidos"
                             
        }
                        









        


   
    


