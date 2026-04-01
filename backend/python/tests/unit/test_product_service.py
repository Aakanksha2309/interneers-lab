import pytest
from unittest.mock import MagicMock, patch

from django_app.products.services.product_service import ProductService
from django_app.products.exceptions import (
    ProductNotFoundError,
    CategoryNotFoundError,
    BulkValidationError
)


@pytest.fixture
def service():
    service = ProductService()
    service.repository = MagicMock()
    service.category_repository = MagicMock()
    return service

#create product 
@pytest.mark.parametrize(
    "category_exists, expected_exception",
    [
        (True, None),
        (False, CategoryNotFoundError),
    ]
)
def test_create_product(service, category_exists, expected_exception):
    data = {"category_id": "507f1f77bcf86cd799439011"}

    if category_exists:
        service.category_repository.get_by_id.return_value = MagicMock()
        service.repository.create.return_value = {"name": "Laptop"}

        result = service.create_product(data)
        assert result == {"name": "Laptop"}
    else:
        service.category_repository.get_by_id.return_value = None

        with pytest.raises(expected_exception):
            service.create_product(data)

#get product 
@pytest.mark.parametrize(
    "repo_return, should_raise",
    [
        ({"id": "1"}, False),
        (None, True),
    ]
)
def test_get_product(service, repo_return, should_raise):
    service.repository.get_by_id.return_value = repo_return

    if should_raise:
        with pytest.raises(ProductNotFoundError):
            service.get_product("1")
    else:
        result = service.get_product("1")
        assert result == {"id": "1"}

#update product 
@pytest.mark.parametrize(
    "repo_return, should_raise",
    [
        ({"id": "1"}, False),
        (None, True),
    ]
)

def test_update_product(service, repo_return, should_raise):
    service.repository.update.return_value = repo_return
    service.category_repository.get_by_id.return_value = MagicMock()

    if should_raise:
        with pytest.raises(ProductNotFoundError):
            service.update_product("1", {})
    else:
        data = {"category_id": "507f1f77bcf86cd799439011"}
        result = service.update_product("1", data)
        assert result == {"id": "1"}

#delete product 
@pytest.mark.parametrize(
    "repo_return, should_raise",
    [
        (True, False),
        (False, True),
    ]
)
def test_delete_product(service, repo_return, should_raise):
    service.repository.delete.return_value = repo_return

    if should_raise:
        with pytest.raises(ProductNotFoundError):
            service.delete_product("1")
    else:
        assert service.delete_product("1") is True

#fetch products by category 
@pytest.mark.parametrize(
    "category_exists, should_raise",
    [
        (True, False),
        (False, True),
    ]
)
def test_fetch_products_for_category(service, category_exists, should_raise):
    if category_exists:
        service.category_repository.get_by_id.return_value = MagicMock()
        service.repository.get_products_by_category_id.return_value = ["p1", "p2"]

        result = service.fetch_products_for_category("cat123")
        assert result == ["p1", "p2"]
    else:
        service.category_repository.get_by_id.return_value = None

        with pytest.raises(CategoryNotFoundError):
            service.fetch_products_for_category("cat123")

#add product to category 
@pytest.mark.parametrize(
    "product_exists, category_exists, expected_exception",
    [
        (True, True, None),
        (False, True, ProductNotFoundError),
        (True, False, CategoryNotFoundError),
    ]
)
def test_add_product_to_category(service, product_exists, category_exists, expected_exception):
    if product_exists:
        service.get_product = MagicMock(return_value=MagicMock())
    else:
        service.get_product = MagicMock(side_effect=ProductNotFoundError)

    if category_exists:
        service.category_repository.get_category_by_id.return_value = MagicMock()
    else:
        service.category_repository.get_category_by_id.return_value = None

    service.repository.assign_category.return_value = "assigned"

    if expected_exception:
        with pytest.raises(expected_exception):
            service.add_product_to_category("cat", "prod")
    else:
        result = service.add_product_to_category("cat", "prod")
        assert result == "assigned"

#remove product from category
@pytest.mark.parametrize(
    "product_exists, category_exists, expected_exception",
    [
        (True, True, None),
        (False, True, ProductNotFoundError),
        (True, False, CategoryNotFoundError),
    ]
)
def test_remove_product_from_category(service, product_exists, category_exists, expected_exception):
    if product_exists:
        service.get_product = MagicMock(return_value=MagicMock())
    else:
        service.get_product = MagicMock(side_effect=ProductNotFoundError)

    if category_exists:
        service.category_repository.get_category_by_id.return_value = MagicMock()
    else:
        service.category_repository.get_category_by_id.return_value = None

    service.repository.remove_category.return_value = "removed"

    if expected_exception:
        with pytest.raises(expected_exception):
            service.remove_product_from_category("cat", "prod")
    else:
        result = service.remove_product_from_category("cat", "prod")
        assert result == "removed"

#bulk create 
@pytest.mark.parametrize(
    "file_name, should_raise",
    [
        ("data.txt", True),
        ("data.csv", False),
    ]
)
def test_bulk_file_validation(service, file_name, should_raise):
    file = MagicMock()
    file.name = file_name

    if should_raise:
        with pytest.raises(BulkValidationError):
            service.bulk_create_from_csv(file)

#Get catalog
def test_get_catalog_no_filters(service):
    service.repository.get_paginated.return_value = (["p1"], 1)

    result = service.get_catalog(page=1, limit=10, active_filters={})

    assert result["products"] == ["p1"]
    assert result["metadata"]["total_items"] == 1

    service.repository.get_paginated.assert_called_once_with(
        mongo_query={},
        raw_query={},
        skip=0,
        limit=10
    )

@pytest.mark.parametrize("filters, expected_mongo_key, expected_value", [
    ({"brand": "Nike"}, "brand__iexact", "Nike"),                    # Case 1: Brand
    ({"search": "shoe"}, "name__icontains", "shoe"),                # Case 2: Search
    ({"min_price": 50}, "selling_price__gte", 50),                 # Case 3: Min Price
    ({"max_price": 150}, "selling_price__lte", 150),               # Case 4: Max Price
    ({"is_perishable": True}, "is_perishable", True),               # Case 5: Boolean
    ({"expires_before": "2026-01-01"}, "expiry_date__lte", "2026-01-01"), # Case 6: Date
])
def test_get_catalog_filter_mapping(service, filters, expected_mongo_key, expected_value):
    # Setup Mock
    service.repository.get_paginated.return_value = ([], 0)

    # Act
    service.get_catalog(page=1, limit=10, active_filters=filters)

    # Assert: Check if the Service correctly mapped the filter to the Repository call
    args = service.repository.get_paginated.call_args.kwargs
    assert args["mongo_query"][expected_mongo_key] == expected_value

@pytest.mark.parametrize("filter_data, query_type", [
    ({"low_stock": True}, "raw_query"),
])
def test_get_catalog_complex_filters(service, filter_data, query_type):
    service.repository.get_paginated.return_value = ([], 0)

    service.get_catalog(page=1, limit=10, active_filters=filter_data)
    args = service.repository.get_paginated.call_args.kwargs

    if "low_stock" in filter_data:
        assert "$expr" in args["raw_query"]


@pytest.mark.parametrize("category_string, should_raise", [
    ("507f1f77bcf86cd799439011,507f1f77bcf86cd799439012", False), # Valid IDs
    ("invalid_id_123", True),                                    # Malformed ID
    ("507f1f77bcf86cd799439011, abc", True),                     # One valid, one broken
])
def test_get_catalog_category_id_validation(service, category_string, should_raise):
    filters = {"category_ids": category_string}
    service.repository.get_paginated.return_value = ([], 0)

    if should_raise:
        with pytest.raises(ValueError): # Or your specific custom exception
            service.get_catalog(page=1, limit=10, active_filters=filters)
    else:
        service.get_catalog(page=1, limit=10, active_filters=filters)
        assert "category__in" in service.repository.get_paginated.call_args.kwargs["mongo_query"]

@pytest.mark.parametrize("page, limit, expected_skip, should_raise", [
    (1, 10, 0, False),   
    (2, 10, 10, False), 
])
def test_get_catalog_pagination_validation(service, page, limit, expected_skip, should_raise):
    service.repository.get_paginated.return_value = (["item"], 100)

    if should_raise:
        with pytest.raises((ValueError, TypeError)):
            service.get_catalog(page=page, limit=limit, active_filters={})
    else:
        result = service.get_catalog(page=page, limit=limit, active_filters={})
        args = service.repository.get_paginated.call_args.kwargs
        assert args["skip"] == expected_skip