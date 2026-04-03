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
<<<<<<< HEAD
from django_app.products.exceptions import CategoryNotFoundError,BusinessValidationError
=======
from django_app.products.exceptions import CategoryNotFoundError
>>>>>>> 5155439 (test: add unit,integration suites and regression script)
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
<<<<<<< HEAD
        ("507f1f77bcf86cd799439011", None, CategoryNotFoundError,),
=======
        ("507f1f77bcf86cd799439011", None, CategoryNotFoundError),
        ("invalid-id", None, CategoryNotFoundError),
>>>>>>> 5155439 (test: add unit,integration suites and regression script)
    ]
)
def test_get_category_by_id(service, category_id, repo_return, expected_exception):
    """
    Validates the following:
    1. Success: Returns the category object if the ID exists.
    2. Raises CategoryNotFoundError if the Category ID isn't in the DB.
<<<<<<< HEAD
    """
    
    service.repository.get_by_id.return_value = repo_return
=======
    3. Invalid: Rejects the request immediately if category ID format is wrong.
    """
    if ObjectId.is_valid(category_id):
        service.repository.get_by_id.return_value = repo_return
>>>>>>> 5155439 (test: add unit,integration suites and regression script)

    if expected_exception:
        with pytest.raises(expected_exception):
            service.get_category_by_id(category_id)
    else:
        result = service.get_category_by_id(category_id)
        assert result == repo_return
<<<<<<< HEAD

    service.repository.get_by_id.assert_called_once_with(category_id)
    
def test_get_category_by_id_invalid(service):
    with pytest.raises(CategoryNotFoundError):
        service.get_category_by_id("invalid-id")
    service.repository.get_by_id.assert_not_called()
=======
        service.repository.get_by_id.assert_called_once_with(category_id)

>>>>>>> 5155439 (test: add unit,integration suites and regression script)

# ------------------ DELETE CATEGORY ------------------


@pytest.mark.parametrize(
    "category_id, repo_return, expected_exception",
    [
        ("507f1f77bcf86cd799439011", True, None),
<<<<<<< HEAD
        ("507f1f77bcf86cd799439011", None, BusinessValidationError),  # in use
        ("507f1f77bcf86cd799439011", False, CategoryNotFoundError),
=======
        ("507f1f77bcf86cd799439011", None, ValueError),  # in use
        ("507f1f77bcf86cd799439011", False, CategoryNotFoundError),
        ("invalid-id", None, CategoryNotFoundError),
>>>>>>> 5155439 (test: add unit,integration suites and regression script)
    ]
)
def test_delete_category(service, category_id, repo_return, expected_exception):
    """
    Tests the following cases for deleting categories:
    1. Category is removed successfully.
    2. Category in use (products exist in the particular category).
    3. Fails if the category doesn't exist in the DB.
<<<<<<< HEAD
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
=======
    4. Raises error for invalid Category ID.
    """
    if ObjectId.is_valid(category_id):
        service.repository.delete.return_value = repo_return
    else:
        service.repository.delete.return_value = None

    if expected_exception:
        with pytest.raises(expected_exception):
            service.delete_category(category_id)
    else:
        result = service.delete_category(category_id)
        assert result is True
        service.repository.delete.assert_called_once_with(category_id)


# ------------------ UPDATE CATEGORY ------------------


@pytest.mark.parametrize(
    "category_id, update_return, existing_category, expected_exception",
    [
        ("507f1f77bcf86cd799439011", {"id": "1"}, None, None),
        ("507f1f77bcf86cd799439011", None, None, CategoryNotFoundError),
        ("invalid-id", None, None, CategoryNotFoundError),
        ("507f1f77bcf86cd799439011", {"id": "1"}, MagicMock(id="507f1f77bcf86cd799439012"), ValueError),
        ("507f1f77bcf86cd799439011", {"id": "1"}, MagicMock(id="507f1f77bcf86cd799439011"), None),
    ]
)
def test_update_category(
    service, category_id, update_return, existing_category, expected_exception
):
    """
    Tests the following updation scenarios:
    1. SUCCESS CASE: Valid category ID with no duplicate 
    2. CATEGORY NOT FOUND: Repository returns None (category does not exist)
    3. INVALID CATEGORY ID:Category ID format is invalid
    4. DUPLICATE CATEGORY TITLE: Another category already exists with same title
    """
    if ObjectId.is_valid(category_id):
        service.repository.update.return_value = update_return
        service.repository.get_by_title_case_insensitive.return_value = existing_category
    else:
        service.repository.get_by_title_case_insensitive.return_value = None
        service.repository.get_by_id.return_value = None

    if expected_exception:
        with pytest.raises(expected_exception):
            service.update_category(category_id, {"title": "New"})
    else:
        result = service.update_category(category_id, {"title": "New"})
        assert result == update_return
>>>>>>> 5155439 (test: add unit,integration suites and regression script)
        service.repository.update.assert_called_once_with(
            category_id,
            {"title": "New"}
        )
<<<<<<< HEAD
   

def test_update_category_invalid(service):
    with pytest.raises(CategoryNotFoundError):
        service.update_category("invalid-id",{"title":"New"})
    service.repository.update.assert_not_called()
=======
        if ObjectId.is_valid(category_id):
            service.repository.get_by_title_case_insensitive.assert_called_once()
        else:
            service.repository.get_by_title_case_insensitive.assert_not_called()
>>>>>>> 5155439 (test: add unit,integration suites and regression script)
