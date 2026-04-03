"""
Category Integration Tests
--------------------------
These tests ensure that the API, business logic, and database all work together correctly. They exercise the integrated flow from URL request down to MongoDB.
"""

import pytest

# =========================================================
#                   CREATE CATEGORY TESTS
# =========================================================

@pytest.mark.django_db
def test_create_category(api_client):
    """Test successful category creation."""
    payload = {"title": "Electronics"}
    res = api_client.post("/api/categories/", payload, format="json")
    assert res.status_code == 201
    assert "id" in res.data
    assert res.data["message"] == "Category created successfully"


@pytest.mark.django_db
def test_create_category_whitespace_title(api_client):
    """Test validation logic for title with only whitespace."""
    res = api_client.post("/api/categories/", {"title": "   "}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
@pytest.mark.parametrize(
    "title1, title2, expected_msg",
    [
        ("Electronics", "Electronics", "already exists"),
        ("Electronics", "electronics", "already exists"),
    ]
)
def test_create_duplicate_category_variants(api_client, title1, title2, expected_msg):
    """Test validation when creating duplicate categories."""
    api_client.post("/api/categories/", {"title": title1}, format="json")
    res = api_client.post("/api/categories/", {"title": title2}, format="json")
    assert res.status_code == 400
    assert expected_msg in res.data["error"]


@pytest.mark.django_db
def test_create_category_empty_title(api_client):
    """Test validation when category title is empty."""
    res = api_client.post("/api/categories/", {"title": ""}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_create_category_missing_title(api_client):
    """Test validation when category title is missing."""
    res = api_client.post("/api/categories/", {}, format="json")
    assert res.status_code == 400


# =========================================================
#                     GET CATEGORY TESTS
# =========================================================

@pytest.mark.django_db
def test_get_all_categories(api_client, seeded_data):
    """Test fetching all categories."""
    res = api_client.get("/api/categories/")
    assert res.status_code == 400
    assert isinstance(res.data, list)
    assert len(res.data) > 0

@pytest.mark.django_db
def test_get_category_invalid_id_format(api_client):
    """Test fetching a category with invalid ID format."""
    res = api_client.get("/api/categories/invalid-id/")
    assert res.status_code == 404
    assert "error" in res.data

@pytest.mark.django_db
def test_get_category_by_id(api_client):
    """Test fetching a category by valid ID."""
    create_res = api_client.post("/api/categories/", {"title": "Books"}, format="json")
    category_id = create_res.data["id"]
    get_res = api_client.get(f"/api/categories/{category_id}/")
    assert get_res.status_code == 200
    assert get_res.data["title"] == "Books"

@pytest.mark.django_db
def test_get_category_not_found(api_client):
    """Test fetching a non-existent category (valid ID format)."""
    fake_id = "64b8f8f8f8f8f8f8f8f8f8f8"
    res = api_client.get(f"/api/categories/{fake_id}/")
    assert res.status_code == 404
    assert "error" in res.data


# =========================================================
#                    UPDATE CATEGORY TESTS
# =========================================================

@pytest.mark.django_db
def test_update_category(api_client):
    """Test successful category update."""
    create_res = api_client.post("/api/categories/", {"title": "Old"}, format="json")
    category_id = create_res.data["id"]
    update_res = api_client.patch(
        f"/api/categories/{category_id}/",
        {"title": "New"},
        format="json"
    )
    assert update_res.status_code == 200
    assert update_res.data["message"] == "Updated successfully"
    assert update_res.data["category"]["title"] == "New"

@pytest.mark.django_db
def test_update_category_invalid_id_format(api_client):
    """Test updating with an invalid category ID format."""
    res = api_client.patch("/api/categories/invalid-id/", {"title": "New"}, format="json")
    assert res.status_code == 404
    assert "error" in res.data

@pytest.mark.django_db
def test_update_category_empty_payload(api_client):
    """Test updating with an empty payload."""
    create_res = api_client.post("/api/categories/", {"title": "Test"}, format="json")
    category_id = create_res.data["id"]
    res = api_client.patch(f"/api/categories/{category_id}/", {}, format="json")
    assert res.status_code == 200

@pytest.mark.django_db
def test_update_category_duplicate_name(api_client):
    """
    Prevent renaming a category to a title 
    that is already being used by another category.
    """
    cat1_id = api_client.post("/api/categories/", {"title": "A"}, format="json").data["id"]
    cat2_id = api_client.post("/api/categories/", {"title": "B"}, format="json").data["id"]
    res = api_client.patch(
        f"/api/categories/{cat2_id}/",
        {"title": "A"},
        format="json"
    )
    assert res.status_code == 400
    assert "already exists" in res.data["error"]

@pytest.mark.django_db
def test_update_category_same_title(api_client):
    """Updating a category with its current title should succeed."""
    cat_id = api_client.post("/api/categories/", {"title": "Same"}, format="json").data["id"]
    res = api_client.patch(
        f"/api/categories/{cat_id}/",
        {"title": "Same"},
        format="json"
    )
    assert res.status_code == 200

@pytest.mark.django_db
def test_update_category_not_found(api_client):
    """Test updating a non-existent category."""
    fake_id = "64b8f8f8f8f8f8f8f8f8f8f8"
    res = api_client.patch(f"/api/categories/{fake_id}/", {"title": "New"}, format="json")
    assert res.status_code == 404
    assert "error" in res.data

# =========================================================
#                   DELETE CATEGORY TESTS
# =========================================================

@pytest.mark.django_db
def test_delete_category_success(api_client):
    """Test successful category deletion."""
    create_res = api_client.post("/api/categories/", {"title": "Temp"}, format="json")
    category_id = create_res.data["id"]

    delete_res = api_client.delete(f"/api/categories/{category_id}/")
    assert delete_res.status_code == 200
    assert delete_res.data["status"] == "success"

@pytest.mark.django_db
def test_delete_category_invalid_id_format(api_client):
    """Test deleting with invalid category ID format."""
    res = api_client.delete("/api/categories/invalid-id/")
    assert res.status_code == 404
    assert "error" in res.data

@pytest.mark.django_db
def test_delete_category_not_found(api_client):
    """Test deleting a non-existent category."""
    fake_id = "64b8f8f8f8f8f8f8f8f8f8f8"
    res = api_client.delete(f"/api/categories/{fake_id}/")
    assert res.status_code == 404
    assert "error" in res.data

@pytest.mark.django_db
def test_delete_category_twice(api_client):
    """Test deleting the same category twice."""
    create_res = api_client.post("/api/categories/", {"title": "Temp"}, format="json")
    category_id = create_res.data["id"]

    api_client.delete(f"/api/categories/{category_id}/")
    res = api_client.delete(f"/api/categories/{category_id}/")
    assert res.status_code == 404

@pytest.mark.django_db
def test_delete_category_in_use(api_client):
    """Test deleting a category that still has products linked to it."""
    create_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = create_res.data["id"]

    api_client.post(
        "/api/products/",
        {
            "name": "Phone",
            "brand": "Apple",
            "selling_price": 500,
            "warehouse_quantity": 10,
            "category_id": category_id,
            "is_perishable": False
        },
        format="json"
    )

    res = api_client.get(f"/api/products/category/{category_id}/")
    assert res.status_code == 200
    assert len(res.data) == 1

    delete_res = api_client.delete(f"/api/categories/{category_id}/")
    assert delete_res.status_code == 400
    assert "error" in delete_res.data
    assert "Cannot delete category" in delete_res.data["error"]

@pytest.mark.django_db
def test_category_empty_id(api_client):
    """Test fetching a category with an empty string as ID."""
    res = api_client.get("/api/categories//")
    assert res.status_code in [400, 404]

@pytest.mark.django_db
def test_category_numeric_id(api_client):
    """Test fetching a category with a numeric ID."""
    res = api_client.get("/api/categories/123/")
    assert res.status_code in [400, 404]

@pytest.mark.django_db
def test_category_none_id_behavior(api_client):
    """Test fetching a category with 'None' as ID."""
    res = api_client.get("/api/categories/None/")
    assert res.status_code in [400, 404]

@pytest.mark.django_db
def test_category_random_string_id(api_client):
    """Test fetching a category with a malformed string ID."""
    res = api_client.get("/api/categories/abcxyz/")
    assert res.status_code in [400, 404]
