from .repository import ProductRepository
from .exceptions import ProductNotFoundError, BusinessValidationError

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()
        
    #Create product
    def create_product(self, data):
        return self.repository.create(data)
    
    #Get all products in sorted order of creation with pagiantion 
    def get_catalog(self, page=1, limit=10):
        items = self.repository.get_paginated(page, limit)
        total_items = self.repository.count_total()
        total_pages = (total_items + limit - 1) // limit 
        return {
            "products": items,
            "metadata": {
                "current_page": page,
                "limit": limit,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
    
    #Get product by ID
    def get_product(self, product_id):
        product = self.repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found.")
        return product
    
    #Update product details
    def update_product(self, product_id, data):

        self.get_product(product_id)       
        return self.repository.update(product_id, data)
    
    #Delete product
    def delete_product(self, product_id):
        if not self.repository.delete(product_id):
            raise ProductNotFoundError(f"Could not delete: Product {product_id} missing.")
        return True