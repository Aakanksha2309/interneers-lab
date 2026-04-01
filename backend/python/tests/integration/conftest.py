<<<<<<< HEAD
"""
Global Test Configuration
-------------------------
This file sets up everything needed to run tests smoothly.
It connects to the test database, clears data between tests,
and provides an API client to simulate real API calls.
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")
import pytest
from django.core.management import call_command
from mongoengine import connect, disconnect
=======
import pytest
from django.core.management import call_command
from mongoengine import connect, disconnect

>>>>>>> 4799cdc (WEEK-5 initial work)
from django_app.products.models.product import Product
from django_app.products.models.product_category import ProductCategory
from rest_framework.test import APIClient

<<<<<<< HEAD
# ===============================
# DATABASE SETUP
# ===============================
@pytest.fixture(scope="session", autouse=True)
def setup_local_mongodb():
    """
    Ensures connection to a dedicated test database.
    Disconnects first to avoid any hanging connections.
    """
    disconnect()
    connect(
        db="test_intern_db",
        host="mongodb://localhost:27017",
        alias="default"
    )
    yield
    disconnect()

# ===============================
# AUTOMATIC CLEANUP (Runs for every test)
# ===============================
@pytest.fixture(autouse=True)
def clean_db():
    """
    Cleans Product and ProductCategory collections after each test.
    """
=======

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
>>>>>>> 4799cdc (WEEK-5 initial work)
    yield
    Product.objects.delete()
    ProductCategory.objects.delete()

<<<<<<< HEAD
# ===============================
# Optional test data seeding
# ===============================
@pytest.fixture
def seeded_data():
    """
    Seeds test data into the database.
    """
    try:
        call_command("seed_categories")
        call_command("seed_products")
    except Exception as e:
        pytest.fail(f"Seeding failed: {e}")

# ===============================
# API CLIENT for DRF endpoints
# ===============================
@pytest.fixture
def api_client():
    """
    Simulates a client making HTTP requests.
=======

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
>>>>>>> 4799cdc (WEEK-5 initial work)
    """
    return APIClient()