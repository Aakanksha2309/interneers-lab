"""
This file handles business logic for Categories. 
It raises specific exceptions.
"""
from ..exceptions import CategoryNotFoundError,BusinessValidationError
from ..repositories.product_category_repository import CategoryRepository
from mongoengine.errors import NotUniqueError
from bson import ObjectId


class CategoryService:
    def __init__(self):
        self.repository = CategoryRepository()
        
    # Create a new category 
    def create_category(self,data):
        try:
            title = data.get("title", "").strip()
            existing = self.repository.get_by_title_case_insensitive(title)
            if existing:
                raise BusinessValidationError(f"Category '{title}' already exists.")
            return self.repository.create(data)
        except NotUniqueError:
            raise BusinessValidationError(f"Category '{data.get('title')}' already exists.")
    
    # Get a list of every category
    def get_all_categories(self):
        return self.repository.get_all()
    
    # Find one category by id 
    def get_category_by_id(self,category_id):
        if not ObjectId.is_valid(category_id):
            raise CategoryNotFoundError(f"Invalid ID format: '{category_id}'")
        category=self.repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError("Category not found!")
        return category
    
    # Update category info
    def update_category(self, category_id, data):
        #Category id is valid or not 
        if not ObjectId.is_valid(category_id):              
            raise CategoryNotFoundError(f"Invalid ID format: '{category_id}'")
  
        title = data.get("title")
        payload = {}
        if title is not None:
            title = title.strip()
            existing = self.repository.get_by_title_case_insensitive(title)
            if existing and str(existing.id) != category_id:
                raise BusinessValidationError(f"Category '{title}' already exists.")
            payload["title"] = title

        updated = self.repository.update(category_id, payload)
        if updated is None:
            raise CategoryNotFoundError("Category not found!")
        return updated
    
    # Delete category only if it is not being used by any products
    def delete_category(self, category_id):
        #Checking if category id is a valid id or not 
        if not ObjectId.is_valid(category_id):
            raise CategoryNotFoundError(f"Invalid ID format: '{category_id}'")
        result = self.repository.delete(category_id)
        if result is None:
            raise BusinessValidationError("Cannot delete category: Products are still assigned to it.")
        if not result:
            raise CategoryNotFoundError("Category not found!")
        return True