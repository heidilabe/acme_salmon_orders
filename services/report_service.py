from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter

from database.mongo_manager import db_manager
from models.sale import Sale
from models.product import SalmonProduct
from services.inventory_service import InventoryService
class ReportService:
   """Generacion reportes de negocio, Optimiza con agregaciones de MongoDB cuando es posible """
   @classmethod
   def get_cost_profit_relation(cls)-> List[Dict]:
        """ Rporte: coste-ganancia por tipo de salmon
        Incluye: ventas totales,costo,ingreso ganancia neta, margen %."""
        pipeline = [
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.salmon_type",
                    "total_kg_sold": {"$sum": "$items.quantity_kg"},
                    "total_revenue": {"$sum": "$items.subtotal"},
                    "total_profit": {"$sum": "$total_profit"},  # Simplificado, idealmente calcular por item
                    "sale_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_revenue": -1}}
        ]
        sales = InventoryService.get_sales_history(limit=1000)
        stats = {}
        for sale in sales:
            for item in sale.items:
                salmon_type = item.salmon_type
            if salmon_type not in stats:
                stats[salmon_type]= {
                "total_kg": 0,
                "total_revenue":0,
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
                    "period": f"Ultimos {len(recent_sales)}pedidos"
                             
                }  
        @classmethod
        def get_inventory_status(cls)-> List[Dict]:
                """ Reporte de estado actual del inventario"""
                products = InventoryService.get_all_products()
                report = []
                for product in products:
                    status = "OK" if product.stock_kg > product.min_stock * 2 else "LOW" if product.stock_kg > product.min_stock else "CRITICAL"
        report.append({
                "salmon_type":product.salmon_type,
                "name" : product.name,
                "stock_kg" :product.stock_kg,
                "status":stats,
                "sale_price":product.sale_price,
                "purchase_price" :  product.purchase_price,
                "margin": product.profit_margin,
                "updated_by" : product.updated_by,
                "update_at":product.updated_at    })
        return report
   @classmethod
   def get_sales_summary(cls, days: int = 30)-> Dict:
        """ Resumen de ventas del periodo."""
        since = datetime.now() - timedelta(days=days)
        pipeline = [
             {"$math":{"date":{"$gte": since}}},
            {
                "$group":{
                    "_id" : None,
                    "total_sales":{"$sum":1},
                    "total_revenue":{"$sum":"$total_amount"},
                    "total_profit":{"$sum":"$total_profit"},
                    "avg_sale":{"$avg":"$total_amoubt"}
                }
            }
        ]
        result = list(db_manager.sales.aggregate(pipeline))
        if not result:
             return{
                  "period_days":days,
                  "total_sales": 0,
                  "total_revenue":0,
                  "total_profit":0,
                  "avg_sale":0
             }
        data = result[0]
        return{
             "period_days":days,
             "total_sales":int(data["total_sales"]),
             "total_revenue":round(data["total_revenue"],2),
             "total_profit":round(data["total_profit"],2),
             "avg_sale":round(data["avg_sale"],2)
        }
   







                    
                        









        


   
    


