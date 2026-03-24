from django.core.management.base import BaseCommand
from django_app.products.models.product import Product
from django_app.products.models.product_category import ProductCategory
from mongoengine.queryset.visitor import Q


class Command(BaseCommand):
    """
    Custom management command to clean up legacy product data.
    It ensures every Product document is linked to a ProductCategory.
    """

    help = "Assign default category to products that don't have one"
    def handle(self, *args, **kwargs):

        """
        Main execution logic for the migration command.
        1. Ensures a 'Uncategorized' category exists.
        2. Queries for Products missing the 'category' field.
        3. Performs a bulk update using MongoEngine's atomic operators.
        """

        self.stdout.write("Checking for products without categories...")

        try:
           #look for 'Uncategorized' to use for legacy items
            default_category = ProductCategory.objects(title="Uncategorized").first()
            
            if not default_category:
                default_category = ProductCategory(
                    title="Uncategorized",
                    description="Default category for old products"
                ).save()
                self.stdout.write(self.style.SUCCESS("Created 'Uncategorized' category"))
            else:
                self.stdout.write(f"Using existing category: {default_category.title}")

            # Update products where category is missing or null
            query = Product.objects(Q(category=None) | Q(category__exists=False))
            count_to_update = query.count()

            if count_to_update == 0:
                self.stdout.write(self.style.WARNING("No products found needing a category update."))
                return

            # Perform the bulk update
            updated_count = query.update(set__category=default_category)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated {updated_count} products")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during migration: {e}"))
    





   