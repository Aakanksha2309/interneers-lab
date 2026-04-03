from django.core.management.base import BaseCommand
from ...models.product_category import ProductCategory
from ...models.product import Product
from decimal import Decimal
from datetime import datetime, timedelta, timezone


class Command(BaseCommand):
    help = 'Seeds initial products into MongoDB'

    def handle(self, *args, **kwargs):
        # Fetch Categories (Prerequisite: seed_categories must have run)
        electronics = ProductCategory.objects(title="Electronics").first()
        groceries = ProductCategory.objects(title="Groceries").first()
        apparel = ProductCategory.objects(title="Apparel").first()

        if not (electronics and groceries and apparel):
            self.stdout.write(
                self.style.ERROR("Categories not found. Run seed_categories first!")
            )
            return

        # Define Core Test Scenarios
        CORE_PRODUCTS = [
            # --- ELECTRONICS ---
            {
                "name": "iPhone 15",
                "brand": "Apple",
                "category": electronics,
                "warehouse_quantity": 50,
                "selling_price": Decimal("999.00"),
                "cost_price": Decimal("600.00"),
                "is_perishable": False,
            },
            {
                "name": "Galaxy S23",  # SCENARIO: LOW STOCK (Threshold 10)
                "brand": "Samsung",
                "category": electronics,
                "warehouse_quantity": 5,
                "low_stock_threshold": 10,
                "selling_price": Decimal("850.00"),
                "is_perishable": False,
            },
            {
                "name": "Broken Charger",  # SCENARIO: OUT OF STOCK
                "brand": "Generic",
                "category": electronics,
                "warehouse_quantity": 0,
                "selling_price": Decimal("10.00"),
                "is_perishable": False,
            },

            # --- GROCERIES ---
            {
                "name": "Organic Milk",  # SCENARIO: PERISHABLE (Valid)
                "brand": "DairyFarm",
                "category": groceries,
                "warehouse_quantity": 20,
                "selling_price": Decimal("4.50"),
                "is_perishable": True,
                "expiry_date": datetime.now(timezone.utc) + timedelta(days=5),
            },

            # --- APPAREL ---
            {
                "name": "Cotton T-Shirt",
                "brand": "FashionCo",
                "category": apparel,
                "warehouse_quantity": 100,
                "selling_price": Decimal("19.99"),
                "is_perishable": False,
            },
            {
                "name": "Blue Jeans",  # Same brand for brand-filtering tests
                "brand": "FashionCo",
                "category": apparel,
                "warehouse_quantity": 60,
                "selling_price": Decimal("49.99"),
                "is_perishable": False,
            },
        ]

        self.stdout.write("Seeding core products...")

        for p_data in CORE_PRODUCTS:
            exists = Product.objects(name=p_data["name"]).first()
            if not exists:
                Product(**p_data).save()
                self.stdout.write(
                    self.style.SUCCESS(f"Created: {p_data['name']}")
                )

        # BULK DATA
        # Create 15 generic items in Electronics so as to have multiple pages
        self.stdout.write("Seeding bulk products for pagination testing...")
        for i in range(1, 16):
            name = f"Electronic Accessory {i}"
            if not Product.objects(name=name).first():
                Product(
                    name=name,
                    brand="GenericTech",
                    category=electronics,
                    warehouse_quantity=20,
                    selling_price=Decimal(f"{10 + i}.99"),
                    is_perishable=False,
                ).save()

        self.stdout.write(self.style.SUCCESS("Product Database Seeded successfully!"))
