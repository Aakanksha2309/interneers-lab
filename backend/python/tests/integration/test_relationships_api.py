<<<<<<< HEAD
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
# ADDING PRODUCT TO A CATEGORY
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
        f"/api/products/category/{cat_b}/{prod}/", format="json"
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
        f"/api/products/category/{category_id}/{product_id}/", format="json"
    )
    assert res1.status_code in (200, 204)

    res2 = api_client.post(
        f"/api/products/category/{category_id}/{product_id}/", format="json"
    )
    assert res2.status_code in (200, 204)

    get_res = api_client.get(f"/api/products/{product_id}/")
    assert get_res.status_code == 200
    assert get_res.data["category_id"] == category_id


# -------------------------------------------------
# REMOVING PRODUCT FROM A PARTICULAR CATEGORY
# -------------------------------------------------


@pytest.mark.django_db
def test_remove_product_from_category(api_client):
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

    res = api_client.delete(
        f"/api/products/category/{category_id}/{product_id}/", format="json"
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
def test_remove_product_wrong_category(api_client):
    """
    Test Removing product from wrong category
    """
    cat1 = api_client.post("/api/categories/", {"title": "A"}, format="json").data["id"]
    cat2 = api_client.post("/api/categories/", {"title": "B"}, format="json").data["id"]

    prod = api_client.post(
        "/api/products/",
        {
            "name": "Item",
            "brand": "Test",
            "selling_price": 100,
            "warehouse_quantity": 5,
            "category_id": cat1,
            "is_perishable": False,
        },
        format="json",
    ).data["id"]

    res = api_client.delete(f"/api/products/category/{cat2}/{prod}/")
    assert res.status_code == 400

    get_res = api_client.get(f"/api/products/{prod}/")
    assert get_res.status_code == 200
    assert get_res.data["category_id"] == cat1


@pytest.mark.django_db
def test_delete_product_nonexistent_category(api_client):
    """
    Test removing product from invalid category
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

    invalid_category_id = "507f1f77bcf86cd799439999"

    res = api_client.delete(f"/api/products/category/{invalid_category_id}/{prod}/")
    assert res.status_code in (400, 404)


@pytest.mark.django_db
def test_remove_product_invalid_product_id(api_client):
    """
    Try deleting a product using a valid category but invalid product id.
    """
    cat_res = api_client.post("/api/categories/", {"title": "A"}, format="json")
    category_id = cat_res.data["id"]

    invalid_product_id = "507f1f77bcf86cd799439999"
    res = api_client.delete(
        f"/api/products/category/{category_id}/{invalid_product_id}/"
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

    api_client.delete(f"/api/products/category/{cat}/{prod}/")

    res = api_client.delete(f"/api/categories/{cat}/")

    assert res.status_code == 200
<<<<<<< HEAD
=======
=======
import pytest


# ---------------------------------------------------------
# 1. CATEGORY → PRODUCT E2E FLOW
# ---------------------------------------------------------
@pytest.mark.django_db
def test_category_product_e2e_flow(api_client):

    cat_res = api_client.post("/api/categories/", {
        "title": "Electronics"
    })

    assert cat_res.status_code in [200, 201]
    category_id = cat_res.data["id"]

    prod_res = api_client.post("/api/products/", {
        "name": "Laptop",
        "brand": "Dell",
        "category_id": category_id,
        "warehouse_quantity": 10,
        "selling_price": 75000,
        "cost_price": 55000,
        "is_perishable": False,
        "description": "Gaming laptop"
    })

    assert prod_res.status_code in [200, 201]
    product_id = prod_res.data["id"]

    res = api_client.get(f"/api/products/{product_id}/")

    assert res.status_code == 200
    assert res.data.get("category_id") == category_id


# ---------------------------------------------------------
# 2. FETCH PRODUCTS BY CATEGORY
# ---------------------------------------------------------
@pytest.mark.django_db
def test_get_products_by_category(api_client):

    cat_res = api_client.post("/api/categories/", {
        "title": "Furniture"
    })

    assert cat_res.status_code in [200, 201]
    category_id = cat_res.data["id"]

    for i in range(3):
        api_client.post("/api/products/", {
            "name": f"Chair-{i}",
            "brand": "Ikea",
            "category_id": category_id,
            "warehouse_quantity": 5,
            "selling_price": 2000,
            "cost_price": 1500,
            "is_perishable": False,
            "description": "Wooden chair"
        })

    res = api_client.get(f"/api/products/category/{category_id}/")

    assert res.status_code == 200
    assert len(res.data) >= 3


# ---------------------------------------------------------
# 3. NESTED RELATIONSHIP ENDPOINT
# ---------------------------------------------------------
@pytest.mark.django_db
def test_nested_category_product_endpoint(api_client):

    cat_res = api_client.post("/api/categories/", {
        "title": "Appliances"
    })

    assert cat_res.status_code in [200, 201]
    category_id = cat_res.data["id"]

    prod_res = api_client.post("/api/products/", {
        "name": "Fridge",
        "brand": "LG",
        "category_id": category_id,
        "warehouse_quantity": 2,
        "selling_price": 30000,
        "cost_price": 25000,
        "is_perishable": False,
        "description": "Double door fridge"
    })

    assert prod_res.status_code in [200, 201]
    product_id = prod_res.data["id"]

    res = api_client.get(
        f"/api/products/category/{category_id}/"
    )

    assert res.status_code == 200
    for product in res.data:
        assert product["category_id"] == category_id
    assert len(res.data) == 1


# ---------------------------------------------------------
# 4. ADD / UPDATE PRODUCT CATEGORY
# ---------------------------------------------------------
@pytest.mark.django_db
def test_add_or_update_product_category(api_client):

    cat_res = api_client.post("/api/categories/", {
        "title": "Mobiles"
    })

    assert cat_res.status_code in [200, 201]
    category_id = cat_res.data["id"]
    print("category created")
    prod_res = api_client.post("/api/products/", {
        "name": "Phone",
        "brand": "Apple",
        "warehouse_quantity": 5,
        "selling_price": 90000,
        "cost_price": 70000,
        "is_perishable": False,
        "description": "iPhone",
        "category_id": category_id
    },format="json")

    assert prod_res.status_code in [200, 201]
    product_id = prod_res.data["id"]
    print("product created")

    res = api_client.post(
        f"/api/products/category/{category_id}/{product_id}/",
        format="json"
    )

    assert res.status_code in [200, 204]

    get_res = api_client.get(f"/api/products/{product_id}/")
    assert get_res.status_code == 200
    assert get_res.data.get("category_id") == category_id


# ---------------------------------------------------------
# 5. REMOVE PRODUCT FROM CATEGORY
# ---------------------------------------------------------
@pytest.mark.django_db
def test_remove_product_from_category(api_client):

    cat_res = api_client.post("/api/categories/", {
        "title": "Stationery"
    })

    assert cat_res.status_code in [200, 201]
    category_id = cat_res.data["id"]

    prod_res = api_client.post("/api/products/", {
        "name": "Notebook",
        "brand": "Classmate",
        "category_id": category_id,
        "warehouse_quantity": 20,
        "selling_price": 50,
        "cost_price": 30,
        "is_perishable": False,
        "description": "Ruled notebook"
    })

    assert prod_res.status_code in [200, 201]
    product_id = prod_res.data["id"]

    # remove category
    res = api_client.delete(
        f"/api/products/category/{category_id}/{product_id}/",
        format="json"
    )

    assert res.status_code in [200, 204]

    get_res = api_client.get(f"/api/products/{product_id}/")
    assert get_res.status_code == 200
    assert "category_id" not in get_res.data


# ---------------------------------------------------------
# 6. ERROR: INVALID CATEGORY ASSIGNMENT
# ---------------------------------------------------------
@pytest.mark.django_db
def test_invalid_category_assignment(api_client):

    prod_res = api_client.post("/api/products/", {
        "name": "Tablet",
        "brand": "Samsung",
        "category_id": "invalid-id",
        "warehouse_quantity": 3,
        "selling_price": 30000,
        "cost_price": 20000,
        "is_perishable": False,
        "description": "Galaxy Tab"
    })

    assert prod_res.status_code in [400, 404, 500]

    product_id = prod_res.data.get("id")

    if product_id:
        res = api_client.patch(
            f"/api/products/{product_id}/",
            {"category_id": "invalid-id"},
            format="json"
        )

        assert res.status_code in [400, 404, 500]


# ---------------------------------------------------------
# 7. ERROR: INVALID CATEGORY FETCH
# ---------------------------------------------------------
@pytest.mark.django_db
def test_fetch_products_invalid_category(api_client):
    category_id="64b8f8f8f8f8f8f8f8f8f8f8"
    res = api_client.get(f"/api/products/category/{category_id}/")

    assert res.status_code in [400, 404]

>>>>>>> f41cf44 (WEEK-5 initial work)
>>>>>>> c29911f (WEEK-5 initial work)
