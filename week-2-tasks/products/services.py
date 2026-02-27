# This is the service layer 

from .repository import ProductRepository

class ProductService:
    def __init__(self):
        self.repository=ProductRepository()

    def create_product(self,validated_data):
        if validated_data.get("price",0)<0:
            raise ValueError("Price cannot be negative")
        if validated_data.get("quantity",0)<0:
            raise ValueError("Quantity cannot be negative")
        
        return self.repository.create(validated_data)
    
    def list_products(self):
        return self.repository.get_all()
    
    def get_product(self,product_id):
        return self.repository.get_by_ID(product_id)
    
    def update_product(self,product_id,validated_data):
        product=self.repository.get_by_ID(product_id)
        if not product:
            return None
        return self.repository.update(product,validated_data)
    
    def delete_product(self,product_id):
        product=self.repository.get_by_ID(product_id)
        if not product:
            return None
        return self.repository.delete(product)
