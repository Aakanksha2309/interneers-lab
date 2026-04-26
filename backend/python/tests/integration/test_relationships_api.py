"""
Product-Category Relationship Tests
------------------------------------------
These tests focus on the "handshake" between products and their categories.
We're making sure that when you link an item to a category, it stays linked,
and that our safety rules (like not deleting a category that still has
products) are working as intended.
"""

import pytest


@pytest.mark.django_db
def test_category_product_e2e_flow(api_client):
    """
    Testing the full loop: Create category -> Create product inside it -> Fetch product
    """
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"})
    assert cat_res.status_code in (200, 201)
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        {
            "name": "Laptop",
            "brand": "Dell",
            "category_id": category_id,
            "warehouse_quantity": 10,
            "selling_price": 75000,
            "cost_price": 55000,
            "is_perishable": False,
            "description": "Gaming laptop",
        },
    )
    assert prod_res.status_code in (200, 201)
    product_id = prod_res.data["id"]

    res = api_client.get(f"/api/products/{product_id}/")
    assert res.status_code == 200
    assert "category_id" in res.data
    assert res.data["category_id"] == category_id
    assert res.data["id"] == product_id


@pytest.mark.django_db
def test_get_products_by_category(api_client):
    """
    Test: Fetch products by category
    """
    cat_res = api_client.post("/api/categories/", {"title": "Furniture"})
    assert cat_res.status_code in (200, 201)
    category_id = cat_res.data["id"]

    for i in range(3):
        api_client.post(
            "/api/products/",
            {
                "name": f"Chair-{i}",
                "brand": "Ikea",
                "category_id": category_id,
                "warehouse_quantity": 5,
                "selling_price": 2000,
                "cost_price": 1500,
                "is_perishable": False,
                "description": "Wooden chair",
            },
        )

    res = api_client.get(f"/api/products/category/{category_id}/")
    assert res.status_code == 200
    assert len(res.data) == 3


@pytest.mark.django_db
def test_get_products_empty_category(api_client):
    """
    Ensure fetching products from a valid category with no products returns an empty list.
    """
    cat_res = api_client.post("/api/categories/", {"title": "EmptyCat"})
    assert cat_res.status_code in (200, 201)
    category_id = cat_res.data["id"]

    res = api_client.get(f"/api/products/category/{category_id}/")
    assert res.status_code == 200
    assert res.data == []


@pytest.mark.django_db
def test_get_products_invalid_category(api_client):
    """
    Test: Fetching products from incorrect category id
    """
    invalid_category_id = "507f1f77bcf86cd799439999"  # valid format but non-existent
    res = api_client.get(f"/api/products/category/{invalid_category_id}/")
    assert res.status_code in (400, 404)


# ------------------------------------
# BULK MOVE PRODUCTS TO A CATEGORY
# ------------------------------------
@pytest.mark.django_db
def test_update_product_category_change(api_client):
    """
    Testing the logic for moving a product from Category A to Category B
    """
    cat_a = api_client.post("/api/categories/", {"title": "A"}, format="json").data["id"]
    cat_b = api_client.post("/api/categories/", {"title": "B"}, format="json").data["id"]

    prod = api_client.post(
        "/api/products/",
        {
            "name": "Item",
            "brand": "Test",
            "selling_price": 100,
            "warehouse_quantity": 5,
            "category_id": cat_a,
            "is_perishable": False,
        },
        format="json",
    ).data["id"]

    res = api_client.post(
        "/api/products/category/bulk-move/",
        {"product_ids": [prod], "category_id": cat_b},
        format="json",
    )
    assert res.status_code in (200, 204)

    get_res = api_client.get(f"/api/products/{prod}/")
    assert get_res.data["category_id"] == cat_b


@pytest.mark.django_db
def test_product_category_assignment_idempotent(api_client):
    """
    Integration test: assigning the same category multiple times should not break anything.
    """
    cat_res = api_client.post("/api/categories/", {"title": "Mobiles"}, format="json")
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        {
            "name": "Phone",
            "brand": "Apple",
            "warehouse_quantity": 5,
            "selling_price": 90000,
            "cost_price": 70000,
            "is_perishable": False,
            "description": "iPhone",
            "category_id": category_id,
        },
        format="json",
    )
    product_id = prod_res.data["id"]

    res1 = api_client.post(
        "/api/products/category/bulk-move/",
        {"product_ids": [product_id], "category_id": category_id},
        format="json",
    )
    assert res1.status_code in (200, 204)

    res2 = api_client.post(
        "/api/products/category/bulk-move/",
        {"product_ids": [product_id], "category_id": category_id},
        format="json",
    )
    assert res2.status_code in (200, 204)

    get_res = api_client.get(f"/api/products/{product_id}/")
    assert get_res.status_code == 200
    assert get_res.data["category_id"] == category_id


# -------------------------------------------------
# BULK REMOVE PRODUCTS FROM A PARTICULAR CATEGORY
# -------------------------------------------------


@pytest.mark.django_db
def test_remove_products_from_category(api_client):
    """
    Test: If we remove a product from a category, it should fall back to "Uncategorized"
    """
    cat_res = api_client.post("/api/categories/", {"title": "Stationery"})
    assert cat_res.status_code in (200, 201)
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        {
            "name": "Notebook",
            "brand": "Classmate",
            "category_id": category_id,
            "warehouse_quantity": 20,
            "selling_price": 50,
            "cost_price": 30,
            "is_perishable": False,
            "description": "Ruled notebook",
        },
    )
    assert prod_res.status_code in (200, 201)
    product_id = prod_res.data["id"]

    res = api_client.post(
        "/api/products/category/bulk-remove/",
        {"product_ids": [product_id]},
        format="json",
    )
    assert res.status_code in [200, 204]

    cats_res = api_client.get("/api/categories/")
    assert cats_res.status_code == 200
    cats = cats_res.data
    uncat = next((c for c in cats if c["title"].lower() == "uncategorized"), None)
    assert uncat is not None, "Uncategorized category not found"

    UNCATEGORISED_ID = uncat["id"]
    get_res = api_client.get(f"/api/products/{product_id}/")
    assert get_res.data["category_id"] == UNCATEGORISED_ID


@pytest.mark.django_db
def test_remove_products_invalid_product_id(api_client):
    """
    Try deleting products using invalid product id.
    """
    cat = api_client.post("/api/categories/", {"title": "A"}, format="json").data["id"]
    prod = api_client.post(
        "/api/products/",
        {
            "name": "Item",
            "brand": "Test",
            "selling_price": 100,
            "warehouse_quantity": 5,
            "category_id": cat,
            "is_perishable": False,
        },
        format="json",
    ).data["id"]

    api_client.delete(f"/api/products/{prod}/")

    res = api_client.post(
        "/api/products/category/bulk-remove/",
        {"product_ids": [prod]},
        format="json",
    )
    assert res.status_code in (400, 404)


@pytest.mark.django_db
def test_delete_category_after_removing_products(api_client):
    """
    Test: Deleting category after removing product
    """
    cat = api_client.post("/api/categories/", {"title": "Temp"}, format="json").data["id"]

    prod = api_client.post(
        "/api/products/",
        {
            "name": "Test",
            "brand": "Test",
            "selling_price": 100,
            "warehouse_quantity": 10,
            "category_id": cat,
            "is_perishable": False,
        },
        format="json",
    ).data["id"]

    remove_res = api_client.post(
        "/api/products/category/bulk-remove/",
        {"product_ids": [prod]},
        format="json",
    )

    assert remove_res.status_code == 200

    res = api_client.delete(f"/api/categories/{cat}/")
    assert res.status_code == 200

# --------------------------------
# BULK DELETE PRODUCTS
# --------------------------------

@pytest.mark.django_db
def test_bulk_delete_products(api_client):
    """Test: Bulk deleting multiple products"""
    cat = api_client.post("/api/categories/", {"title": "BulkDeleteCat"}, format="json").data["id"]

    prod1 = api_client.post(
        "/api/products/",
        {"name": "BulkDeleteP1", "brand": "BrandBD1", "selling_price": 100,
         "warehouse_quantity": 5, "category_id": cat, "is_perishable": False},
        format="json",
    ).data["id"]

    prod2 = api_client.post(
        "/api/products/",
        {"name": "BulkDeleteP2", "brand": "BrandBD2", "selling_price": 100,
         "warehouse_quantity": 5, "category_id": cat, "is_perishable": False},
        format="json",
    ).data["id"]

    res = api_client.post(
        "/api/products/bulk-delete/",
        {"product_ids": [prod1, prod2]},
        format="json",
    )
    assert res.status_code == 200

    assert api_client.get(f"/api/products/{prod1}/").status_code == 404
    assert api_client.get(f"/api/products/{prod2}/").status_code == 404


@pytest.mark.django_db
def test_bulk_delete_nonexistent_products(api_client):
    """Test: Bulk deleting a product that no longer exists"""
    cat = api_client.post("/api/categories/", {"title": "BulkDeleteNonExistCat"}, format="json").data["id"]
    prod = api_client.post(
        "/api/products/",
        {"name": "BulkDeleteGone", "brand": "BrandBDG", "selling_price": 100,
         "warehouse_quantity": 5, "category_id": cat, "is_perishable": False},
        format="json",
    ).data["id"]

    api_client.delete(f"/api/products/{prod}/")

    res = api_client.post(
        "/api/products/bulk-delete/",
        {"product_ids": [prod]},
        format="json",
    )
    assert res.status_code in (400, 404)


@pytest.mark.django_db
def test_bulk_delete_empty_list(api_client):
    """Test: Bulk delete with empty list should fail"""
    res = api_client.post(
        "/api/products/bulk-delete/",
        {"product_ids": []},
        format="json",
    )
    assert res.status_code == 400


# --------------------------------
# BULK MOVE EDGE CASES
# --------------------------------

@pytest.mark.django_db
def test_bulk_move_multiple_products(api_client):
    """Test: Moving multiple products to a new category at once"""
    cat_a = api_client.post("/api/categories/", {"title": "BulkMoveSource"}, format="json").data["id"]
    cat_b = api_client.post("/api/categories/", {"title": "BulkMoveDest"}, format="json").data["id"]

    prod1 = api_client.post(
        "/api/products/",
        {"name": "BulkMoveP1", "brand": "BrandBM1", "selling_price": 100,
         "warehouse_quantity": 5, "category_id": cat_a, "is_perishable": False},
        format="json",
    ).data["id"]

    prod2 = api_client.post(
        "/api/products/",
        {"name": "BulkMoveP2", "brand": "BrandBM2", "selling_price": 100,
         "warehouse_quantity": 5, "category_id": cat_a, "is_perishable": False},
        format="json",
    ).data["id"]

    res = api_client.post(
        "/api/products/category/bulk-move/",
        {"product_ids": [prod1, prod2], "category_id": cat_b},
        format="json",
    )
    assert res.status_code == 200

    assert api_client.get(f"/api/products/{prod1}/").data["category_id"] == cat_b
    assert api_client.get(f"/api/products/{prod2}/").data["category_id"] == cat_b


@pytest.mark.django_db
def test_bulk_move_nonexistent_category(api_client):
    """Test: Moving products to a category that doesn't exist"""
    cat = api_client.post("/api/categories/", {"title": "BulkMoveNonExistCat"}, format="json").data["id"]
    prod = api_client.post(
        "/api/products/",
        {"name": "BulkMoveNonExist", "brand": "BrandBMNE", "selling_price": 100,
         "warehouse_quantity": 5, "category_id": cat, "is_perishable": False},
        format="json",
    ).data["id"]

    fake_category_id = "507f1f77bcf86cd799439099"
    res = api_client.post(
        "/api/products/category/bulk-move/",
        {"product_ids": [prod], "category_id": fake_category_id},
        format="json",
    )
    assert res.status_code in (400, 404)


@pytest.mark.django_db
def test_bulk_move_empty_product_list(api_client):
    """Test: Bulk move with empty product list should fail"""
    cat = api_client.post("/api/categories/", {"title": "BulkMoveEmptyCat"}, format="json").data["id"]

    res = api_client.post(
        "/api/products/category/bulk-move/",
        {"product_ids": [], "category_id": cat},
        format="json",
    )
    assert res.status_code == 400