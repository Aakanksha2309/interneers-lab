from django.core.management.base import BaseCommand
from ...models.product_category import ProductCategory


class Command(BaseCommand):
    """
    Management command to prepopulate the MongoDB collection with initial categories.
    """
    help = 'Seeds initial product categories into MongoDB'

    def handle(self, *args, **kwargs):
        """
        Main execution logic for seeding. 
        Loops through a predefined list and creates records if they don't exist.
        """
        # Define the initial data set for categories
        INITIAL_CATEGORIES = [
            {"title": "Electronics", "description": "Gadgets and tech"},
            {"title": "Groceries", "description": "Food and home essentials"},
            {"title": "Apparel", "description": "Clothing and fashion"}
        ]

        self.stdout.write("Seeding categories...")

        for cat_data in INITIAL_CATEGORIES:
            # Check if the category already exists by title to prevent duplicates
            obj = ProductCategory.objects(title=cat_data["title"]).first()
            if not obj:
                obj = ProductCategory(**cat_data)
                obj.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully created: {obj.title}"))
            else:
                self.stdout.write(f"Category already exists: {obj.title}")
                