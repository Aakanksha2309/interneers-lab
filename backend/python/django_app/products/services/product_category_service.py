"""
This file handles business logic for Categories. 
It raises specific exceptions.
"""
from ..exceptions import CategoryNotFoundError
from ..repositories.product_category_repository import CategoryRepository
from mongoengine.errors import NotUniqueError

class CategoryService:
    def __init__(self):
        self.repository = CategoryRepository()
        
    # Create a new category 
    def create_category(self,data):
        try:
            return self.repository.create(data)
        except NotUniqueError:
            raise ValueError(f"Category '{data.get('title')}' already exists.")
    
    # Get a list of every category
    def get_all_categories(self):
        return self.repository.get_all()
    
    # Find one category by id 
    def get_category_by_id(self,category_id):
        category=self.repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError("Category not found!")
        return category
    
    # Update category info
    def update_category(self, category_id, data):
        updated = self.repository.update(category_id, data)
        if updated is None:
            raise CategoryNotFoundError("Category not found!")
        return updated
    
    # Delete category only if it is not being used by any products
    def delete_category(self, category_id):
        result = self.repository.delete(category_id)
        if result == "IN_USE":
            raise ValueError("Cannot delete category: Products are still assigned to it.")
        if not result:
            raise CategoryNotFoundError("Category not found!")
        return True