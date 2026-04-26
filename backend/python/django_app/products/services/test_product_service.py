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
        ({"name": "Milk", "brand": "Dairy"},          None,  True,  {"id": "1"}, None),         
        ({"name": "Milk", "brand": "Dairy"},          None,  True,  None,        BusinessValidationError), 
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
      7. No duplicate exists
      8. Duplicate entry exists 
    """
    product_id = "507f1f77bcf86cd799439012"

    if "name" in data or "brand" in data:
        mock_current = MagicMock()
        mock_current.name = "Milk"
        mock_current.brand = "Dairy"
        service.repository.get_by_id.return_value = mock_current
        if expected_exception == BusinessValidationError:
            # Simulate a duplicate found
            service.repository.get_by_name_and_brand_excluding.return_value = MagicMock()
        else:
            # No duplicate
            service.repository.get_by_name_and_brand_excluding.return_value = None


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

# --- BULK ADD PRODUCTS TO CATEGORY ---

@pytest.mark.parametrize(
    "product_ids, category_exists, product_found_list, expected_success, expected_errors",
    [
       
        ([str(ObjectId()), str(ObjectId())], True, [True, True], 2, 0),
        
        # 2. 
        (["pid_1", "pid_2"], True, [True, False], 1, 1),
        
        # 3. 
        ([str(ObjectId())], False, [True], 0, "raises"),
    ]
)
def test_bulk_add_products_to_category(
    service, product_ids, category_exists, product_found_list, expected_success, expected_errors
):
    """
    1. Success: Both products found and moved
    2. Partial Failure: One product missing, one succeeds
    3. Total Failure: Category itself doesn't exist
    """
    # Generating a valid MongoDB style ID
    valid_cat_id = str(ObjectId())
   # Mock Category
    service.category_repository.get_by_id.return_value = MagicMock() if category_exists else None
    
    # Mock get_product side effects based on product_found_list
    side_effects = []
    for found in product_found_list:
        side_effects.append({"name": "Product"} if found else ProductNotFoundError("Missing"))
    service.get_product = MagicMock(side_effect=side_effects)
    
    service.repository.assign_category.return_value = {"status": "updated"}

    if expected_errors == "raises":
        with pytest.raises(CategoryNotFoundError):
            service.bulk_add_products_to_category(product_ids, valid_cat_id)
    else:
        updated, errors = service.bulk_add_products_to_category(product_ids, valid_cat_id)
        assert len(updated) == expected_success
        assert len(errors) == expected_errors

# --- BULK REMOVE PRODUCTS FROM CATEGORY ---

@pytest.mark.parametrize(
    "p_ids, items_found_in_db, should_raise",
    [
        ([ObjectId()], 1, False),
        ([ObjectId(), ObjectId()], 1, True),
    ]
)
def test_remove_product_from_category(
    service, p_ids, items_found_in_db,should_raise
):
    """
    1. All products exist in DB: Success
    2. One product requested is missing from DB: Raises ProductNotFoundError
    """
   # Mock the DB check: return a list of "found" ObjectIds
    found_ids = p_ids[:items_found_in_db]
    service.repository.get_existing_ids.return_value = found_ids
    
    service.category_repository.get_by_title_case_insensitive.return_value = {"title": "Uncategorized"}
    service.repository.bulk_remove_category.return_value = True

    if should_raise:
        with pytest.raises(ProductNotFoundError):
            service.bulk_remove_products_from_category([str(p) for p in p_ids])
    else:
        result = service.bulk_remove_products_from_category([str(p) for p in p_ids])
        assert result is True

# --- BULK DELETE PRODUCTS FROM A CATGEORY---
@pytest.mark.parametrize("valid_ids, db_exists, expected_exception", [
    ([str(ObjectId())], True, None),                       
    (["invalid-id"], False, BusinessValidationError),    
    ([str(ObjectId())], False, ProductNotFoundError),    
])
def test_bulk_delete_products(service, valid_ids, db_exists, expected_exception):
    """
    1. Success
    2. Invalid format
    3. Valid format but missing in DB
    """
    # Setup existence check
    if expected_exception != BusinessValidationError:
        service.repository.get_existing_ids.return_value = [ObjectId(p) for p in valid_ids] if db_exists else []
    
    service.repository.bulk_delete.return_value = True

    if expected_exception:
        with pytest.raises(expected_exception):
            service.bulk_delete_products(valid_ids)
    else:
        assert service.bulk_delete_products(valid_ids) is True

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
