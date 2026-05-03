"""
Servicio de gestion, de inventario y ventas. Transacciones seguras.

"""
from typing import List, Optional, Dict
from datetime import datetime
from database.mongo_manager import db_manager, transaction_scope
from models.product import SalmonProduct
from models.sale import Sale
from config.settings import APP_CONFIG
from utils.validators import InputValidator, ValidationError
from utils.security import AuditLogger

class InventoryError(Exception):
    """Error en operacion de inventario."""
    pass

class InventoryService:
    """Servicio de inventario con operaciones automaticas.
    Responsabilidad unica: gestionar stock y ventas.
    """

    @classmethod
    def initialize_inventory(cls) -> None:
        """ inicializa stock si esta vacio."""
        products_collection = db_manager.products
        if products_collection.count_documents({}) > 0:
            return
        initial_products = []
        for salmon_id, name, sale_price, purchase_price in APP_CONFIG.SALMON_TYPES:
            product = SalmonProduct(
            salmon_type=salmon_id,
            name=name,
            sale_price=sale_price,
            purchase_price=purchase_price,
            stock_kg=APP_CONFIG.INITIAL_STOCK_KG
            )
            initial_products.append(product.to_dict())
        products_collection.insert_many(initial_products)
        print("Inventario inicializado con 10kg por tipo salmon")
    @classmethod
    def get_all_products(cls) -> List[SalmonProduct]:
        """Obtiene todos los productos activos."""
        cursor = db_manager.products.find({"is_active": True})
        return [SalmonProduct.from_dict(doc) for doc in cursor]
    @classmethod
    def get_product(cls,salmon_type: str) ->Optional[SalmonProduct]:
        """Obtiene producto por tipo."""
        doc = db_manager.products.find_one({" salmon_type": salmon_type,"is_active":True})
        return SalmonProduct.from_dict(doc)if doc else None
    @classmethod
    def update_stock(cls,salmon_type: str, amount_kg: float,
        is_addition: bool, admin_username: str)-> SalmonProduct:
        """ Actualiza stock(agregar o quitar).
        Atomicidad: operacion de una sola escritura en MongoDB."""
        InputValidator.validate_kg_amount(str(abs(amount_kg)))
        with transaction_scope():
            product = cls.get_product(salmon_type)
            if not product:
                raise InventoryError("Producto no encontrado")
            if is_addition:
                product.increase_stock(amount_kg, admin_username)
            else:
                if product.stock_kg -amount_kg < product.min_stock:
                    raise InventoryError(
                    f"Operacion invalida.stock quedaria en "
                    f"{product.stock_kg - amount_kg}kg (minimo:{product.min_stock}kg)"       
                    )
                product.stock_kg-=amount_kg
                product.updated_at = datetime.now()
                product.updated_by = admin_username

            db_manager.products.update_one(
                {"salmon_type": salmon_type},
                {"$set":{
                "stock_kg":product.stock_kg,
                "updated_at": product.updated_at,
                "updated_by": product.updated_by
                }}
                )
            action = "STOCK_ADD" if is_addition else "STOCK_REMOVE"
            AuditLogger.log_action(
            admin_username,
            action,
            f"{salmon_type}:{'+' if is_addition else '-'}{amount_kg}kg"
                )
            return product
    @classmethod
    def update_prices(cls,salmon_type: str, new_sale: float, new_purchase: float, admin_username: str)-> SalmonProduct:
                """ Actualiza precios de producto"""
                product = cls.get_product(salmon_type)
                if not product:
                    raise InventoryError("Producto no encontrado")
                product.update_prices(new_sale, new_purchase,admin_username)
                db_manager.products.update_one(
                    {"salmon_type":salmon_type},
                    {"$set":{
                        "sale_price":product.sale_price,
                        "purchase_price": product.purchase_price,
                        "updated_at": product.updated_at,
                        "updated_by": product.updated_by,
                    }}
                )
                AuditLogger.log_action(
                    admin_username,
                    "PRICE_UPDATE",
                    f"{salmon_type}: venta=${new_sale}, compra=${new_purchase}"
 )
                return product
@classmethod
def register_sale(cls, seller_username: str, items_data: List[Dict],
                customer_name: Optional[str] = None,
                notes:Optional[str] = None )->Sale:
    """  Registra venta con atomicidad en stock.
        items_data: [{"salmon_type": "atlantico","quantity_kg": 2.5},...]"""
    sale = Sale(
        seller_username=seller_username,
        customer_name=InputValidator.sanitize_string(customer_name or ""),
        notes=InputValidator.sanitize_string(notes or "")
    )
    with transaction_scope():
        for item in items_data:
            salmon_type = InputValidator.validate_salmon_type(
            item["salmon_type"], APP_CONFIG.SALMON_TYPES
                )
            quantity = InputValidator.validate_kg_amount(str(item["quantity_kg"]))
            product= cls.get_product(salmon_type)
            if not product:
                raise InventoryError(f"producto no encontrado: {salmon_type}")
            if not product.has_stock(quantity):
                available = max(0, product.stock_kg - product.min_stock)
                raise InventoryError(
                    f"Stock insuficiente para {product.name}."
                    f"Solicitado : {quantity}kg, Disponible:{available}kg"
                    )
            sale.add_item(
                salmon_type=salmon_type,
                quantity_kg=quantity,
                unit_price= product.sale_price,
                purchase_price= product.purchase_price

            )
            sale.validate_sale()

            result = db_manager.sales.insert_one(sale.to_dict())
            sale.sale_id = str(result.inserted_id)
            for item in sale.items:
                db_manager.products.update_one(
                  {"salmon_type":item.salmon_type}, 
                 {"$inc":{
                     "$set":{
                         "updated_at": datetime.now(),
                         "updated_by": seller_username
                     }
                 }}       
                ) 
                AuditLogger.log_action(
                seller_username,
                "SALE",
                f"Venta #{sale.sale_id} por ${sale.total_amount:,.0f}"
                )
                return sale
            @classmethod
            def get_sales_history(cls,limit: int = 50, salmon_type:Optional[str]= None)->List[Sale]:
                """ Obtiene historial de ventas"""
                query = {}
                if salmon_type:
                    query["items.salmon_type"]= salmon_type
                cursor = db_manager.sales.find(query).sort("date",-1).limit(limit)
                return [Sale.from_dict(doc) for doc in cursor]
                

                                                   
                                                 




        