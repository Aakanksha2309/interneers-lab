from .models import Product
from mongoengine.errors import DoesNotExist, ValidationError

class ProductRepository:
    
    #Handles all direct interactions with MongoDB using MongoEngine.
    
    #Creating a document 
    def create(self, validated_data):
        product = Product(**validated_data)
        return product.save()
 
    #Getting documents with pagination 
    def get_paginated(self, page=1, limit=10):
        offset = (page - 1) * limit
        return Product.objects.order_by('-created_at').skip(offset).limit(limit)

    #Getting total product count
    def count_total(self):
        return Product.objects.count()
    
    #Getting documents by ID
    def get_by_id(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except (DoesNotExist, ValidationError):
            return None

    #Updating a document 
    def update(self, product_id, validated_data):
        product = self.get_by_id(product_id)
        if product:
            product.update(**validated_data)
            #reload object with latest DB values
            return product.reload()
        return None

    #Deleting a document 
    def delete(self, product_id):
        product = self.get_by_id(product_id)
        if product:
            product.delete()
            return True
        return False
    







