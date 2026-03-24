"""
This file handles all the database work for Product Categories.
"""
from ..models.product_category import ProductCategory
from mongoengine.errors import OperationError


class CategoryRepository:
    # Find one category using its unique ID
    def get_by_id(self, category_id):
        return ProductCategory.objects(id=category_id).first()

    #Finds a category by its title
    def get_by_title(self, title):
        return ProductCategory.objects(title=title).first()

    # Get a list of every category
    def get_all(self):
        return ProductCategory.objects()

    #Create a category
    def create(self,data):
        category=ProductCategory(**data)
        category.save()
        return category

    #Update category details
    def update(self, category_id, data):
        category = self.get_by_id(category_id)
        if not category:
            return None
        for key, value in data.items():
            setattr(category, key, value)
        category.save()
        return category
    #Delete category which don't have any product under it 
    def delete(self, category_id):
        category = self.get_by_id(category_id)
        if not category:
            return False
        try:
            category.delete()
            return True
        except OperationError:
            return None
    