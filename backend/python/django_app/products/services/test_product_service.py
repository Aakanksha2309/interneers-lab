"""
Product Service Unit Tests
--------------------------
This file contains the "Business Logic" tests. Instead of using a real
database, we use 'Mocks' to simulate repository behavior.
"""

import pytest
from unittest.mock import MagicMock, patch, ANY
from bson import ObjectId

from django_app.products.services.product_service import ProductService
from django_app.products.exceptions import (
    ProductNotFoundError,
    CategoryNotFoundError,
    BulkValidationError,
    BusinessValidationError,
)

# ================================
# SETUP & FIXTURES
# ================================

@pytest.fixture
def service():
    """Initializes the service and swaps the real database repositories"""
    service = ProductService()
    service.repository = MagicMock()
    service.category_repository = MagicMock()
    return service

# ================================
# CRUD OPERATIONS
# ================================

# --- PRODUCT CREATION ---

@pytest.mark.parametrize(
    "data, category_exists, default_exists, expected_exception",
    [
        (
            {"name": "Milk", "brand": "Dairy", "category_id": "507f1f77bcf86cd799439011"},
            True, True, None
        ),
        (
            {"name": "Bread", "brand": "Bakery", "category_id": "507f1f77bcf86cd799439011"},
            False, True, CategoryNotFoundError
        ),
        (
            {"name": "Eggs", "brand": "Farm", "category_id": "invalid-id"},
            True, True, CategoryNotFoundError
        ),
        (
            {"name": "Apple", "brand": "Orchard"},
            True, True, None
        ),
        (
            {"name": "Banana", "brand": "Tropical"},
            True, False, None
        ),
    ]
)
def test_create_product(service, data, category_exists, default_exists, expected_exception):
    """
    Validates product creation across 5 scenarios:
      1. Valid category ID exists in DB.
      2. ID provided but it doesn't exist: should fail.
      3. Invalid MongoDB ObjectId provided: should fail.
      4. No ID provided; finds existing 'Uncategorized' default.
      5. No ID and no default exists; service creates 'Uncategorized' during execution.
    """
    service.repository.get_by_name_and_brand.return_value = None
    # Mock category lookup
    if "category_id" in data and ObjectId.is_valid(data["category_id"]):
        service.category_repository.get_by_id.return_value = (
            MagicMock() if category_exists else None
        )
    # Mock default category logic
    if not data.get("category_id"):
        if default_exists:
            service.category_repository.get_by_title_case_insensitive.return_value = MagicMock()
        else:
            service.category_repository.get_by_title_case_insensitive.return_value = None
            service.category_repository.create.return_value = MagicMock()

    service.repository.create.return_value = {"name": "Laptop"}

    if expected_exception:
        with pytest.raises(expected_exception):
            service.create_product(data)
    else:
        result = service.create_product(data)
        assert result == {"name": "Laptop"}
        args = service.repository.create.call_args[0][0]
        assert "category" in args
        assert args["category"] is not None

# --- GET PRODUCT ---

@pytest.mark.parametrize(
    "repo_return, should_raise",
    [
        ({"id": "507f1f77bcf86cd799439012"}, False),
        (None, True),
    ]
)
def test_get_product(service, repo_return, should_raise):
    """
    1. Success: Returns the product dict if the repository finds it.
    2. Not Found: Raises ProductNotFoundError if None is returned.
    """
    service.repository.get_by_id.return_value = repo_return

    if should_raise:
        with pytest.raises(ProductNotFoundError):
            service.get_product("507f1f77bcf86cd799439012")
    else:
        result = service.get_product("507f1f77bcf86cd799439012")
        assert result == {"id": "507f1f77bcf86cd799439012"}

    service.repository.get_by_id.assert_called_once_with("507f1f77bcf86cd799439012")

# --- UPDATE PRODUCT ---

@pytest.mark.parametrize(
    "data, category_exists, default_exists, repo_return, expected_exception",
    [
        ({"category_id": "507f1f77bcf86cd799439011"}, True,  None,  {"id": "1"}, None),
        ({"category_id": "invalid-id"},               None,  None,  None,        CategoryNotFoundError),
        ({"category_id": "507f1f77bcf86cd799439011"}, False, None,  None,        CategoryNotFoundError),
        ({},                                         None,  True,  {"id": "1"}, None),
        ({},                                         None,  False, {"id": "1"}, None),
        ({"category_id": "507f1f77bcf86cd799439011"}, True,  None,  None,        ProductNotFoundError),
    ]
)
def test_update_product(
    service, data, category_exists, default_exists, repo_return, expected_exception
):
    """
    Tests the update logic across 6 scenarios:
      1. Update to valid existing category
      2. Rejects invalid category IDs
      3. Rejects if requested category doesn't exist
      4. No category provided; finds default 'Uncategorized'
      5. No category; creates 'Uncategorized' during execution
      6. Fails if product does not exist
    """
    product_id = "507f1f77bcf86cd799439012"

    # Mock category lookup
    if "category_id" in data and ObjectId.is_valid(data["category_id"]):
        if category_exists is True:
            service.category_repository.get_by_id.return_value = MagicMock()
        elif category_exists is False:
            service.category_repository.get_by_id.return_value = None
    
    # Mock default category
    if "category_id" not in data:
        if default_exists is True:
            service.category_repository.get_by_title_case_insensitive.return_value = MagicMock()
        elif default_exists is False:
            service.category_repository.get_by_title_case_insensitive.return_value = None
            service.category_repository.create.return_value = MagicMock()

    service.repository.update.return_value = repo_return

    if expected_exception:
        with pytest.raises(expected_exception):
            service.update_product(product_id, data)
    else:
        result = service.update_product(product_id, data)
        assert result == repo_return
        service.repository.update.assert_called_once_with(product_id, ANY)

# --- DELETE PRODUCT ---

@pytest.mark.parametrize(
    "repo_return, should_raise",
    [
        (True, False),
        (False, True),
    ]
)
def test_delete_product(service, repo_return, should_raise):
    """
    1. Success: Returns True if removed.
    2. Not Found: Raises ProductNotFoundError for invalid ID/not found.
    """
    service.repository.delete.return_value = repo_return

    if should_raise:
        with pytest.raises(ProductNotFoundError):
            service.delete_product("507f1f77bcf86cd799439012")
    else:
        assert service.delete_product("507f1f77bcf86cd799439012") is True

    service.repository.delete.assert_called_once_with("507f1f77bcf86cd799439012")

# ================================================================
# Product-Category Relationship
# ================================================================

# --- FETCH PRODUCTS BY CATEGORY ---

@pytest.mark.parametrize(
    "category_id, category_exists, expected_exception",
    [
        ("507f1f77bcf86cd799439011", True, None),
        ("507f1f77bcf86cd799439011", False, CategoryNotFoundError),
        ("invalid-id", True, CategoryNotFoundError),
    ]
)
def test_fetch_products_for_category(service, category_id, category_exists, expected_exception):
    """
    1. Success: Finds valid category and returns associated products.
    2. Missing: Valid ID format, category doesn't exist.
    3. Invalid Format: ID not a valid ObjectId.
    """
    mock_category = MagicMock()
    mock_category.id = category_id

    if ObjectId.is_valid(category_id):
        service.category_repository.get_by_id.return_value = (
            mock_category if category_exists else None
        )
    else:
        service.category_repository.get_by_id.return_value = None

    service.repository.get_products_by_category_id.return_value = ["p1", "p2"]

    if expected_exception:
        with pytest.raises(expected_exception):
            service.fetch_products_for_category(category_id)
        service.repository.get_products_by_category_id.assert_not_called()
    else:
        result = service.fetch_products_for_category(category_id)
        assert result == ["p1", "p2"]
        service.repository.get_products_by_category_id.assert_called_once_with(mock_category.id)

# --- ADD PRODUCT TO CATEGORY ---

@pytest.mark.parametrize(
    "product_exists, category_id_valid, same_category, category_exists, expected_exception",
    [
        (True,  True,  False, True,  None),
        (False, True,  False, True,  ProductNotFoundError),
        (True,  False, False, True,  CategoryNotFoundError),
        (True,  True,  False, False, CategoryNotFoundError),
        (True,  True,  True,  True,  None),
    ]
)
def test_add_product_to_category(
    service, product_exists, category_id_valid, same_category, category_exists, expected_exception
):
    """
    1. Successful assignment to new valid category.
    2. Fails if product ID doesn't exist.
    3. Invalid category ID: rejects before DB.
    4. Valid but non-existent category.
    5. Already in that category: early return.
    """
    valid_oid = "507f1f77bcf86cd799439011"
    category_id = valid_oid if category_id_valid else "invalid-id"
    product_id = "prod_123"

    # Mock product
    if product_exists:
        mock_product = MagicMock()
        if same_category and category_id_valid:
            mock_product.category = MagicMock()
            mock_product.category.id = valid_oid
        else:
            mock_product.category = None if not same_category else MagicMock()
            if mock_product.category:
                mock_product.category.id = ObjectId()  # different category
        service.get_product = MagicMock(return_value=mock_product)
    else:
        service.get_product = MagicMock(side_effect=ProductNotFoundError)

    # Mock category repo
    service.category_repository.get_by_id.return_value = MagicMock() if category_exists else None
    service.repository.assign_category = MagicMock(return_value="assigned")

    if expected_exception:
        with pytest.raises(expected_exception):
            service.add_product_to_category(category_id, product_id)
        service.repository.assign_category.assert_not_called()
    else:
        result = service.add_product_to_category(category_id, product_id)
        if same_category and category_id_valid:
            assert result == mock_product
            service.repository.assign_category.assert_not_called()
        else:
            assert result == "assigned"
            service.repository.assign_category.assert_called_once_with(
                mock_product,
                service.category_repository.get_by_id.return_value,
            )

# --- REMOVE PRODUCT FROM CATEGORY ---

@pytest.mark.parametrize(
    "product_exists, category_id_valid, product_in_correct_cat, default_exists, expected_exception",
    [
        (True,  True,  True,  True,  None),
        (False, True,  True,  True,  ProductNotFoundError),
        (True,  False, True,  True,  CategoryNotFoundError),
        (True,  True,  False, True,  BusinessValidationError),
        (True,  True,  True,  False, None),
    ]
)
def test_remove_product_from_category(
    service, product_exists, category_id_valid, product_in_correct_cat, default_exists, expected_exception
):
    """
    1. Moves from target category to 'Uncategorized' (success).
    2. Product missing: fail.
    3. Invalid category ID rejected.
    4. Fails if not actually in the category.
    5. 'Uncategorized' created if missing.
    """
    valid_oid = "507f1f77bcf86cd799439011"
    category_id = valid_oid if category_id_valid else "invalid-id"
    product_id = "prod_123"
    mock_product = MagicMock()
    mock_product.category = MagicMock()

    if product_exists:
        if product_in_correct_cat and category_id_valid:
            mock_product.category.id = ObjectId(valid_oid)
        else:
            mock_product.category.id = ObjectId()  # different ID
        service.get_product = MagicMock(return_value=mock_product)
    else:
        service.get_product = MagicMock(side_effect=ProductNotFoundError)

    if default_exists:
        mock_default = MagicMock()
        service.category_repository.get_by_title_case_insensitive = MagicMock(return_value=mock_default)
    else:
        service.category_repository.get_by_title_case_insensitive = MagicMock(return_value=None)
        service.category_repository.create = MagicMock(return_value=MagicMock())

    service.repository.remove_category = MagicMock(return_value="removed_successfully")

    if expected_exception:
        with pytest.raises(expected_exception):
            service.remove_product_from_category(category_id, product_id)
        service.repository.remove_category.assert_not_called()
    else:
        result = service.remove_product_from_category(category_id, product_id)
        assert result == "removed_successfully"
        service.get_product.assert_called_once_with(product_id)
        called_args = service.repository.remove_category.call_args[0]
        assert called_args[0] == mock_product
        assert called_args[1] is not None
        # Check default category logic
        service.category_repository.get_by_title_case_insensitive.assert_called_once_with("Uncategorized")
        if not default_exists:
            service.category_repository.create.assert_called_once()

# ================================
# BULK CREATE FROM CSV
# ================================

@patch("django_app.products.services.product_service.ProductSerializer")
@pytest.mark.parametrize(
    "file_name, should_raise",
    [
        ("data.txt", True),
        ("data.csv", False),
    ]
)
def test_bulk_file_validation(mock_serializer, service, file_name, should_raise):
    """
    1. Rejects non-CSV files.
    2. Parses valid .csv file and performs bulk DB write.
    """
    file = MagicMock()
    file.name = file_name

    if should_raise:
        with pytest.raises(BulkValidationError):
            service.bulk_create_from_csv(file)
    else:
        file.read.return_value = b"name,brand,price\nproduct1,Brand1,100"
        # Configure the Mock Serializer to mimic a successful validation cycle
        mock_instance = MagicMock()
        mock_instance.is_valid.return_value = True
        mock_instance.validated_data = {"name": "product1","brand": "Brand1", "price": 100}
        mock_serializer.return_value = mock_instance
        # DB returns None i.e. product doesn't exists 
        service.repository.get_by_name_and_brand.return_value = None
        service._merge_category_into_payload = MagicMock(side_effect=lambda x: x)
        service.repository.bulk_create = MagicMock()
        result = service.bulk_create_from_csv(file)
        assert result["total"] == 1
        assert result["success"] == 1
        assert result["failed"] == 0
        service.repository.bulk_create.assert_called_once()


@patch("django_app.products.services.product_service.ProductSerializer")
@pytest.mark.parametrize(
    "csv_content, repo_return, expected_success, expected_failed",
    [
        ("name,brand\nProductA,BrandA", None, 1, 0),
        ("name,brand\nProductA,BrandA", MagicMock(), 0, 1),
        ("name,brand\nProductA,BrandA\nproducta,branda", None, 1, 1),
    ]
)
def test_bulk_create_logic(mock_serializer_class, service, csv_content, repo_return, expected_success, expected_failed):
    """
    Tests the follwoing data scenarios:
    
    1. New Products: Validates that unique rows are successfully prepared for creation.
    2. Database Conflicts: Ensures rows that already exist in the database are marked as failures.
    3. CSV Duplication: Ensures that if the same product appears twice in one file, 
       only the first is processed and the second is flagged as a duplicate.
    """
    file = MagicMock()
    file.name = "data.csv"
    file.read.return_value = csv_content.encode('utf-8')

   #Dynamic Serializer Mocking
    def side_effect(data=None, **kwargs):
        mock_inst = MagicMock()
        mock_inst.is_valid.return_value = True
        mock_inst.validated_data = data  # This is the key!
        return mock_inst

    mock_serializer_class.side_effect = side_effect

    #Mock Repository
    service.repository.get_by_name_and_brand = MagicMock(return_value=repo_return)
    service.repository.bulk_create = MagicMock()
    service._merge_category_into_payload = MagicMock(side_effect=lambda x: x)

    result = service.bulk_create_from_csv(file)

    assert result["success"] == expected_success
    assert result["failed"] == expected_failed

# --- GET CATALOG WITHOUT FILTER ---

def test_get_catalog_no_filters(service):
    """
    When no search terms, requests paginated list with empty query.
    """
    service.repository.get_paginated.return_value = (["p1"], 1)
    result = service.get_catalog(page=1, limit=10, active_filters={})
    assert result["products"] == ["p1"]
    assert result["metadata"]["total_items"] == 1
    assert result["metadata"]["current_page"] == 1
    assert result["metadata"]["limit"] == 10
    service.repository.get_paginated.assert_called_once_with(
        mongo_query={},
        raw_query={},
        skip=0,
        limit=10,
    )

# --- GET CATALOG WITH FILTER ---

@pytest.mark.parametrize(
    "filters, expected_mongo",
    [
        ({"brand": "Nike"},                {"brand__iexact":      "Nike"}),
        ({"search": "shoe"},               {"name__icontains":    "shoe"}),
        ({"min_price": 50},                {"selling_price__gte": 50}),
        ({"max_price": 150},               {"selling_price__lte": 150}),
        ({"is_perishable": True},          {"is_perishable":      True}),
        ({"expires_before": "2026-01-01"}, {"expiry_date__lte":   "2026-01-01", "is_perishable": True}),
    ]
)
def test_get_catalog_filter_mapping(service, filters, expected_mongo):
    """
    Checks that input filters are mapped to MongoDB queries correctly.
    """
    service.repository.get_paginated.return_value = ([], 0)
    service.get_catalog(page=1, limit=10, active_filters=filters)
    args = service.repository.get_paginated.call_args.kwargs
    assert args["mongo_query"] == expected_mongo

# --- COMPLEX FILTER ---

def test_get_catalog_complex_filters(service):
    """
    The 'low_stock' flag produces a complex comparison query.
    """
    service.repository.get_paginated.return_value = ([], 0)
    service.get_catalog(page=1, limit=10, active_filters={"low_stock": True})
    args = service.repository.get_paginated.call_args.kwargs
    assert args["raw_query"]["$expr"] == {
        "$lte": ["$warehouse_quantity", "$low_stock_threshold"]
    }

# --- CATEGORY FILTER ---

@pytest.mark.parametrize(
    "category_string, should_raise",
    [
        ("507f1f77bcf86cd799439011,507f1f77bcf86cd799439012", False),
        ("473662681726fd871", True),
        ("507f1f77bcf86cd799439011, invalid_id", True),
        (" , , ", False),
    ]
)
def test_get_catalog_category_id_validation(service, category_string, should_raise):
    """
    Test validation and mapping for category_id(s) filter on catalog queries.
    """
    filters = {"category_ids": category_string}
    service.repository.get_paginated.return_value = ([], 0)

    if should_raise:
        with pytest.raises(BusinessValidationError):
            service.get_catalog(page=1, limit=10, active_filters=filters)
    else:
        service.get_catalog(page=1, limit=10, active_filters=filters)
        args = service.repository.get_paginated.call_args.kwargs
        cleaned_ids = [cid.strip() for cid in category_string.split(",") if cid.strip()]
        if cleaned_ids:
            assert "category__in" in args["mongo_query"]
            assert isinstance(args["mongo_query"]["category__in"][0], ObjectId)
        else:
            assert "category" in args["mongo_query"]

# --- TESTING PAGINATION ---

@pytest.mark.parametrize(
    "page, limit, expected_skip",
    [
        (1,  10,  0),
        (2,  10, 10),
        (3,  20, 40),
    ]
)
def test_get_catalog_pagination_logic(service, page, limit, expected_skip):
    """
    Correct skip value based on page and limit.
    """
    service.repository.get_paginated.return_value = ([], 0)
    service.get_catalog(page=page, limit=limit, active_filters={})
    args = service.repository.get_paginated.call_args.kwargs
    assert args["skip"] == expected_skip
    assert args["limit"] == limit

def test_get_catalog_metadata_flags(service):
    """
    Validate extra metadata fields and pagination logic.
    """
    service.repository.get_paginated.return_value = (["p1"], 25)
    result = service.get_catalog(page=2, limit=10, active_filters={})
    meta = result["metadata"]
    assert result["products"] == ["p1"]
    assert meta["total_items"] == 25
    assert meta["total_pages"] == 3
    assert meta["current_page"] == 2
    assert meta["has_next"] is True
    assert meta["has_prev"] is True
    assert meta["limit"] == 10

# --- Empty search ignored ---

def test_get_catalog_empty_search_ignored(service):
    """
    Should ignore and not apply an empty search string filter.
    """
    service.repository.get_paginated.return_value = ([], 0)
    service.get_catalog(page=1, limit=10, active_filters={"search": ""})
    args = service.repository.get_paginated.call_args.kwargs
    assert args["mongo_query"] == {}
