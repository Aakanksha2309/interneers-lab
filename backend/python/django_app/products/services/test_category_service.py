"""
Product Category Service Tests
------------------------------
Verifies business logic for category management, including
uniqueness constraints, safe deletion, and ID validation.
"""

import pytest
from unittest.mock import MagicMock
from mongoengine.errors import NotUniqueError
from bson import ObjectId
from django_app.products.exceptions import CategoryNotFoundError,BusinessValidationError
from django_app.products.services.product_category_service import CategoryService

# ------------------ FIXTURES ------------------


@pytest.fixture
def service():
    """
    Initializes the service and swaps out the real database repositories with mocks.
    """
    service = CategoryService()
    service.repository = MagicMock()
    return service


# ------------------ CREATE CATEGORY ------------------


@pytest.mark.parametrize(
    "repo_behavior, expected_exception",
    [
        ("success", None),
        ("duplicate", BusinessValidationError),
    ]
)
def test_create_category(service, repo_behavior, expected_exception):
    """
    1. New Category: Successfully creates a category with a unique title.
    2. Duplicate Title: Catches MongoDB's NotUniqueError.
    """
    data = {"title": "Electronics"}

    if repo_behavior == "success":
        service.repository.create.return_value = data
        service.repository.get_by_title_case_insensitive.return_value = None
    else:
        service.repository.create.side_effect = NotUniqueError()

    if expected_exception:
        with pytest.raises(expected_exception) as exc:
            service.create_category(data)
        assert "already exists" in str(exc.value)
    else:
        result = service.create_category(data)
        assert result == data
        service.repository.create.assert_called_once_with(data)


# ------------------ GET ALL CATEGORIES ------------------


def test_get_all_categories(service):
    service.repository.get_all.return_value = ["cat1", "cat2"]

    result = service.get_all_categories()

    assert result == ["cat1", "cat2"]


# ------------------ GET CATEGORY BY ID ------------------


@pytest.mark.parametrize(
    "category_id, repo_return, expected_exception",
    [
        ("507f1f77bcf86cd799439011", {"id": "1"}, None),
        ("507f1f77bcf86cd799439011", None, CategoryNotFoundError,),
    ]
)
def test_get_category_by_id(service, category_id, repo_return, expected_exception):
    """
    Validates the following:
    1. Success: Returns the category object if the ID exists.
    2. Raises CategoryNotFoundError if the Category ID isn't in the DB.
    """
    
    service.repository.get_by_id.return_value = repo_return

    if expected_exception:
        with pytest.raises(expected_exception):
            service.get_category_by_id(category_id)
    else:
        result = service.get_category_by_id(category_id)
        assert result == repo_return

    service.repository.get_by_id.assert_called_once_with(category_id)
    
def test_get_category_by_id_invalid(service):
    with pytest.raises(CategoryNotFoundError):
        service.get_category_by_id("invalid-id")
    service.repository.get_by_id.assert_not_called()

# ------------------ DELETE CATEGORY ------------------


@pytest.mark.parametrize(
    "category_id, repo_return, expected_exception",
    [
        ("507f1f77bcf86cd799439011", True, None),
        ("507f1f77bcf86cd799439011", None, BusinessValidationError),  # in use
        ("507f1f77bcf86cd799439011", False, CategoryNotFoundError),
    ]
)
def test_delete_category(service, category_id, repo_return, expected_exception):
    """
    Tests the following cases for deleting categories:
    1. Category is removed successfully.
    2. Category in use (products exist in the particular category).
    3. Fails if the category doesn't exist in the DB.
    """
    
    service.repository.delete.return_value = repo_return
    
    if expected_exception:
        with pytest.raises(expected_exception):
            service.delete_category(category_id)
    else:
        result = service.delete_category(category_id)
        assert result is True

    service.repository.delete.assert_called_once_with(category_id)
    
def test_delete_category_invalid(service):
    with pytest.raises(CategoryNotFoundError):
        service.delete_category("invalid-id")
    service.repository.delete.assert_not_called()


# ------------------ UPDATE CATEGORY ------------------


@pytest.mark.parametrize(
    "category_id, update_return, existing_category, expected_exception, call_update",
    [
        ("507f1f77bcf86cd799439011", {"id": "1"}, None, None,True),
        ("507f1f77bcf86cd799439011", None, None, CategoryNotFoundError,True),
        ("507f1f77bcf86cd799439011", {"id": "1"}, MagicMock(id="507f1f77bcf86cd799439012"), BusinessValidationError,False),
        ("507f1f77bcf86cd799439011", {"id": "1"}, MagicMock(id="507f1f77bcf86cd799439011"), None,True),
    ]
)
def test_update_category(
    service, category_id, update_return, existing_category, expected_exception,call_update
):
    """
    Tests the following updation scenarios:
    1. SUCCESS CASE: Valid category ID with no duplicate 
    2. CATEGORY NOT FOUND: Repository returns None (category does not exist)
    3. DUPLICATE CATEGORY TITLE: Another category already exists with same title
    """
    
    service.repository.update.return_value = update_return
    service.repository.get_by_title_case_insensitive.return_value = existing_category

    if expected_exception:
        with pytest.raises(expected_exception):
            service.update_category(category_id, {"title": "New"})
    else:
        result = service.update_category(category_id, {"title": "New"})
        assert result == update_return
    

    if not call_update:
        service.repository.update.assert_not_called()
    else:
        service.repository.update.assert_called_once_with(
            category_id,
            {"title": "New"}
        )
   

def test_update_category_invalid(service):
    with pytest.raises(CategoryNotFoundError):
        service.update_category("invalid-id",{"title":"New"})
    service.repository.update.assert_not_called()