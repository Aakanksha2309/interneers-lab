import pytest
from unittest.mock import MagicMock
from mongoengine.errors import NotUniqueError

from django_app.products.exceptions import CategoryNotFoundError
from django_app.products.services.product_category_service import CategoryService


@pytest.fixture
def service():
    service = CategoryService()
    service.repository = MagicMock()
    return service


# ---------------------------------------------------------
# CREATE CATEGORY
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "repo_behavior, expected_exception",
    [
        ("success", None),
        ("duplicate", ValueError),
    ]
)
def test_create_category(service, repo_behavior, expected_exception):

    if repo_behavior == "success":
        service.repository.create.return_value = {"title": "Electronics"}
    else:
        service.repository.create.side_effect = NotUniqueError()

    if expected_exception:
        with pytest.raises(expected_exception):
            service.create_category({"title": "Electronics"})
    else:
        result = service.create_category({"title": "Electronics"})
        assert result == {"title": "Electronics"}

def test_get_all_categories(service):
    service.repository.get_all.return_value = ["cat1", "cat2"]

    result = service.get_all_categories()

    assert result == ["cat1", "cat2"]
# ---------------------------------------------------------
# GET CATEGORY BY ID
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "repo_return, should_raise",
    [
        ({"id": "1"}, False),
        (None, True),
    ]
)
def test_get_category_by_id(service, repo_return, should_raise):

    service.repository.get_by_id.return_value = repo_return

    if should_raise:
        with pytest.raises(CategoryNotFoundError):
            service.get_category_by_id("1")
    else:
        result = service.get_category_by_id("1")
        assert result == repo_return


# ---------------------------------------------------------
# UPDATE CATEGORY
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "repo_return, should_raise",
    [
        ({"id": "1"}, False),
        (None, True),
    ]
)
def test_update_category(service, repo_return, should_raise):

    service.repository.update.return_value = repo_return

    if should_raise:
        with pytest.raises(CategoryNotFoundError):
            service.update_category("1", {"title": "New"})
    else:
        result = service.update_category("1", {"title": "New"})
        assert result == repo_return


# ---------------------------------------------------------
# DELETE CATEGORY
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "repo_return, expected_exception",
    [
        (True, None),
        ("IN_USE", ValueError),
        (False, CategoryNotFoundError),
    ]
)
def test_delete_category(service, repo_return, expected_exception):

    service.repository.delete.return_value = repo_return

    if expected_exception:
        with pytest.raises(expected_exception):
            service.delete_category("1")
    else:
        result = service.delete_category("1")
        assert result is True

@pytest.mark.parametrize(
    "repo_return, expected_exception",
    [
        ({"id": "1"}, None),
        (None, CategoryNotFoundError),
    ]
)
def test_update_category(service,repo_return,expected_exception):
    service.repository.update.return_value = repo_return

    if expected_exception:
         with pytest.raises(expected_exception):
            service.update_category("1", {})
    else:
        result = service.update_category("1", {"title": "New"})
        assert result == {"id": "1"}