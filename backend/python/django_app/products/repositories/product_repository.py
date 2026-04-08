"""
This file handles all the database work for Products.
It manages creating, finding, updating, and deleting product records in MongoDB.    
It also manages fetching products from category, adding product to category, removing product from category and bulk create 
"""
from ..models.product import Product
from mongoengine.errors import DoesNotExist, ValidationError


class ProductRepository:
    
    #Handles all direct interactions with MongoDB using MongoEngine.
    
    # Create a new product
    def create(self, validated_data):
        product = Product(**validated_data)
        return product.save()
 
    # Handles searching and pagination
    def get_paginated(self, mongo_query, raw_query, skip, limit=10):
        queryset = Product.objects(**mongo_query)
        if raw_query:
            queryset = queryset.filter(__raw__=raw_query)
        total_count = queryset.count()
        products = queryset.skip(skip).limit(limit)
        return products, total_count


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
        if not product:
            return None
        for key, value in validated_data.items():
            setattr(product, key, value)
        product.save()
        return product

    #Deleting a document 
    def delete(self, product_id):
        product = self.get_by_id(product_id)
        if product:
            product.delete()
            return True
        return False
    
    # Get all products that belong to a specific category
    def get_products_by_category_id(self,cat_id):
        return Product.objects(category=cat_id).select_related()
    
    # Link a product to a specific category
    def assign_category(self,product,category):
        if product.category == category:
            return product
        product.category=category
        product.save()
        return product

    # Unlink a product from its category and assigning it in uncategorised section
    def remove_category(self,product,default_category):
        product.category = default_category
        product.save()
        return product

    # Create many products at once
    def bulk_create(self, data_list):
       
        product_instances = [Product(**item) for item in data_list]
        created_docs = Product.objects.insert(product_instances)
        return {
            "count": len(created_docs),
            "ids": [str(p.id) for p in created_docs]
        }






