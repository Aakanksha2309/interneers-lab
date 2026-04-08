"""
This file defines how we store Product Categories in MongoDB.
It handles the category name, a short description, and automatically 
tracks when a category is created or updated.
"""
from datetime import datetime, timezone
from mongoengine import DateTimeField, Document, StringField, signals


class ProductCategory(Document):
    title = StringField(required=True, unique=True)
    description = StringField(max_length=500)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        "collection": "product_categories",
        "indexes": ["title", "-created_at"],
    }
    # To automatically update the time upon editing a category 
    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.now(timezone.utc)


signals.pre_save.connect(ProductCategory.pre_save, sender=ProductCategory)