""" Modelo de producto(Salmon) con control de stock teheread-safe.
Implenta: Validacion de cantidades, precios, estado del producto."""

from dataclasses import dataclass,field
from datetime import datetime
from typing import Optional
from utils.validators import InputValidator

@dataclass
class SalmonProduct:
    """Reprecenta un tipo de salmon en inventario.
    Inmutable en identidad, mutable en stock/precios."""
    salmon_type: str
    name: str
    sale_price: float
    purchase_price: float
    stock_kg: float = 0.0
    min_stock: float = 1.0
    is_active: bool = True
    updated_at: datetime = field(default_factory=datetime.now)
    updated_by: Optional[str] = None
def __post_init__(self):
    InputValidator.validate_positive_amount(self.sale_price,"Precio venta")
    InputValidator.validate_positive_amount(self.purchase_price, "Precio compra")
    InputValidator.validate_non_negative(self.stock_kg,"Stock")
    if self.sale_price <= self.purchase_price:
        raise ValueError("Precio venta debe ser mayor al precio compra")
@property
def  profit_margin(self)-> float:
    """Margen de ganancia por kg"""
    return self.sale_price - self.purchase_price
@property
def margin_percentage(self)-> float:
    """ Porcentaje de margen sobre costo."""
    return ((self.sale_price -self.purchase_price) / self.purchase_price) *100
def has_stock(self,amount_kg: float)-> bool:
        
    """Verifica disponibilidad considerado stock minimo de seguridad"""
    return (self.stock_kg - amount_kg) >= self.min_stock
def decrease_stock(self, amount_kg: float, seller_username: str)->bool:
    
        """Reduce stock de forma segura.
        Returns: True si la operacion fue exitosa"""
        InputValidator.validate_positive_amount(amount_kg,"Cantidad a vender")
        if not self.has_stok(amount_kg):
            available = max(0, self.stock_kg - self.min_stock)
            raise ValueError(f"Stock insuficiente. disponible para venta: {available}kg") 
        self.stock_kg -= amount_kg
        self.updated_at = datetime.now()
        self.updated_by = seller_username
        return True
def increase_stock(self, amount_kg: float, admin_username: str)-> None:
     """ Aumenta stock (reposicion)"""
     InputValidator.validate_positive_amount(amount_kg,"Cantidad a agregar")
     self.stock_kg += amount_kg
     self.updated_at = datetime.now()
     self.updated_by = admin_username   
def update_prices(self, new_sale: float, new_purchase: float, admin_username:str)-> None:
    """Actualiza precios de compra y venta."""
    InputValidator.validate_positive_amount(new_sale,"Nuevo precio venta")
    InputValidator.validate_positive_amount(new_purchase,"Nuevo precio compra")
    if new_sale <= new_purchase:
        raise ValueError("Precio venta debe ser mayor al precio compra")
    self.sale_price = new_sale
    self.purchase_price = new_purchase
    self.updated_at = datetime.now()
    self.updated_by = admin_username
def update_prices(self, new_sale: float, new_purchase: float, admin_username:str)-> None:
    """
    Actualiza precios con validacion"""
    InputValidator.validate_positive_amount(new_sale,"Nuevo precio venta")
    InputValidator.validate_positive_amount(new_purchase,"Nuevo precio compra")
    if new_sale <= new_purchase:
        raise ValueError("Precio venta debe ser mayor al precio compra")
    self.sale_price = new_sale
    self.purchase_price = new_purchase
    self.updated_at = datetime.now()
    self.updated_by = admin_username
def to_dict(self)-> dict:
    """
    Serializacion para MongoDB"""
    return {
        "salmon_type": self.salmon_type,
        "name": self.name,
        "sale_price": self.sale_price,
        "purchase_price": self.purchase_price,
        "stock_kg": self.stock_kg,
        "min_stock": self.min_stock,
        "is_active": self.is_active,
        "updated_at": self.updated_at,
        "updated_by": self.updated_by
    } 
@classmethod
def from_dict(cls , data: dict):
    """  Facctory method desde documento MongoDB."""
    return cls(
        salmon_type=data["salmon_type"],
        name=data["name"],
        sale_price=data["sale_price"],
        purchase_price=data["purchase_price"],
        stock_kg=data["stock_kg"],
        min_stock=data.get("min_stock",1.0),
        is_active=data.get("is_active",True),
        updated_at=data.get("updated_at",datetime.now()),
        updated_by=data.get("updated_by")
    )

    
      



    


        

        
    

