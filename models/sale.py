""" Auditoria completa: quien, cuando, que, cuanto"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from utils.validators import InputValidator

@dataclass
class SaleItem:
    """ Item individual dentro de una venta """
    salmon_type: str
    quantity_kg: float
    unit_price: float
    subtotal: float = 0.0
    def __post_init__(self):
        InputValidator.validate_positive_amount(self.quantity_kg, "Cantidad")
        InputValidator.validate_positive_amount(self.unit_price, "Precio unitario")
        self.subtotal = round(self.quantity_kg * self.unit_price,2)
    @dataclass
    class Sale:
        """Transaccion de venta completa  """
        sale_id: Optional[str] = None
        seller_username: str = ""
        items: list = field(default_factory=list)
        total_amount: float = 0.0
        total_profit: float = 0.0
        customer_name: Optional[str]= None
        notes: Optional[str] = None
        date: datetime = field(default_factory=datetime.now)
    def add_item(self, salmon_type: str, quantity_kg: float, unit_price: float, purchase_price: float)-> None:
            """ Agrega item y recalcula totales
            purchase_price: costo al momento de la venta para calculo de ganancia real """
            item = SaleItem(salmon_type, quantity_kg, unit_price)
            self.items.append(item)
            self.total_amount = sum(item.subtotal for item in self.items)
            item_profit = (unit_price -purchase_price) * quantity_kg
            self.total_profit += item_profit
    def validate_sale(self)-> bool:
            """ Validacion de integridad antes de persistir"""
            if not self.items:
                raise ValueError("La venta debe tener al menos un item")
            if not self.seller_username:
                raise ValueError("Venta debe tener vendedor asignado")
            calculated_total = sum(item.subtotal for item in self.items)
            if abs(calculated_total - self.total_amount) > 0.01:
                raise ValueError("Inconsistencia en  totales de ventas")
            return True
    def to_dict(self)-> dict:
            """ Serializacion para persistencia"""
            return {
                 "seller_username": self.seller_username,
                "items":[
                    {
                    "salmon_type": item.salmon_type,
                    "quantity_kg": item.quantity_kg,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal
                     }
                    for item in self.items
                ],
            "total_amount": round(self.total_amount, 2),
            "total_profit": round(self.total_profit, 2),
            "customer_name": self.customer_name,
            "notes": self.notes,
            "date": self.date
            }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Sale':
            """Recontruccion desde MongoDB"""
            sale = cls(
                sale_id=str(data.get("_id", "")),
                seller_username=data["seller_username"],
                customer_name=data.get("customer_name"),
                notes=data.get("notes"),
                date=data.get("date", datetime.now())
            )
            for item_data in data.get("items", []):
                sale.items.append(SaleItem(
                    salmon_type=item_data["salmon_type"],
                    quantity_kg=item_data["quantity kg"],
                    unit_price=item_data["unit_price"],
                    subtotal=item_data["subtotal"]

                ))
            sale.total_amount = data.get("total_amount", 0)
            sale.total_profit = data.get("total_profit", 0)
            return sale
        


    
            


       
