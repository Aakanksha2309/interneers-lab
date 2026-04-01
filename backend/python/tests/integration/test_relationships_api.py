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

