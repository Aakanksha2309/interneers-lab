import pytest


# -----------------------------------
# CREATE CATEGORY
# -----------------------------------
@pytest.mark.django_db
def test_create_category(api_client):
    payload = {"title": "Electronics"}

    res = api_client.post("/api/categories/", payload, format="json")

    assert res.status_code == 201
    assert "id" in res.data
    assert res.data["message"] == "Category created successfully"

#CREATING DUPLiCATE CATEGORY
@pytest.mark.django_db
def test_create_category_duplicate(api_client):
    payload = {"title": "Electronics"}

    api_client.post("/api/categories/", payload, format="json")
    res = api_client.post("/api/categories/", payload, format="json")

    assert res.status_code == 400
    assert "already exists" in res.data["error"]
# -----------------------------------
# GET ALL CATEGORIES
# -----------------------------------
@pytest.mark.django_db
def test_get_all_categories(api_client, seeded_data):
    res = api_client.get("/api/categories/")

    assert res.status_code == 200
    assert isinstance(res.data, list)
    assert len(res.data) > 0



# -----------------------------------
# GET CATEGORY BY ID
# -----------------------------------
@pytest.mark.django_db
def test_get_category_by_id(api_client):
    create_res = api_client.post("/api/categories/", {"title": "Books"}, format="json")
    category_id = create_res.data["id"]

    get_res = api_client.get(f"/api/categories/{category_id}/")

    assert get_res.status_code == 200
    assert get_res.data["title"] == "Books"

#GET CATEGORY NOT FOUND 
@pytest.mark.django_db
def test_get_category_not_found(api_client):
    fake_id = "64b8f8f8f8f8f8f8f8f8f8f8"

    res = api_client.get(f"/api/categories/{fake_id}/")

    assert res.status_code == 404
    assert "error" in res.data
# -----------------------------------
# UPDATE CATEGORY
# -----------------------------------
@pytest.mark.django_db
def test_update_category(api_client):
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

#UPDATE CATEGORY NOT FOUND
@pytest.mark.django_db
def test_update_category_not_found(api_client):
    fake_id = "64b8f8f8f8f8f8f8f8f8f8f8"

    res = api_client.patch(
        f"/api/categories/{fake_id}/",
        {"title": "New"},
        format="json"
    )

    assert res.status_code == 404
    assert "error" in res.data
# -----------------------------------
# DELETE CATEGORY (SUCCESS)
# -----------------------------------
@pytest.mark.django_db
def test_delete_category_success(api_client):
    create_res = api_client.post("/api/categories/", {"title": "Temp"}, format="json")
    category_id = create_res.data["id"]

    delete_res = api_client.delete(f"/api/categories/{category_id}/")

    # 204 → no content allowed
    assert delete_res.status_code == 200
    assert delete_res.data["status"]=="success"


# -----------------------------------
# DELETE CATEGORY NOT FOUND
# -----------------------------------
# @pytest.mark.django_db
def test_delete_category_not_found(api_client):
    fake_id = "64b8f8f8f8f8f8f8f8f8f8f8"  # valid format, non-existent

    res = api_client.delete(f"/api/categories/{fake_id}/")

    assert res.status_code == 404
    assert "error" in res.data


# -----------------------------------
# DELETE CATEGORY IN USE 
# -----------------------------------
# @pytest.mark.django_db
def test_delete_category_in_use(api_client):
    # 1. Create category
    create_res = api_client.post(
        "/api/categories/",
        {"title": "Electronics"},
        format="json"
    )
    category_id = create_res.data["id"]

    # 2. Create product linked to this category
    product_res=api_client.post(
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

    print(product_res.status_code)
    print(product_res.data)
    # 3. Verify product is actually linked 
    res = api_client.get(f"/api/products/category/{category_id}/")
    assert res.status_code == 200
    assert len(res.data) == 1

    # 4. Attempt delete (should fail)
    delete_res = api_client.delete(f"/api/categories/{category_id}/")

    assert delete_res.status_code == 400
    assert "error" in delete_res.data
    assert "Cannot delete category" in delete_res.data["error"]