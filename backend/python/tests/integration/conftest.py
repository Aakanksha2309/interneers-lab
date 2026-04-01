import pytest
from django.core.management import call_command
from mongoengine import connect, disconnect

from django_app.products.models.product import Product
from django_app.products.models.product_category import ProductCategory
from rest_framework.test import APIClient


# DB SETUP (RUNS ONCE)
@pytest.fixture(scope="session", autouse=True)
def setup_local_mongodb():
    disconnect()

    connect(
        db='test_intern_db',
        host='mongodb://localhost:27017',
        alias='default'
    )

    yield

    disconnect()



# CLEAN DB (RUNS BEFORE EACH TEST)
@pytest.fixture(autouse=True)
def clean_db():
    yield
    Product.objects.delete()
    ProductCategory.objects.delete()


# OPTIONAL SEEDING 
@pytest.fixture
def seeded_data():
    try:
        call_command('seed_categories')
        call_command('seed_products')
    except Exception as e:
        pytest.fail(f"Seeding failed: {e}")

@pytest.fixture
def api_client():
    """
    Simulates a client (like Postman or a Frontend) making HTTP requests.
    """
    return APIClient()