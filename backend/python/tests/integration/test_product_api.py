import pytest
from io import BytesIO
from django_app.products.models.product import Product
from django.core.files.uploadedfile import SimpleUploadedFile


# -----------------------------------
# CREATE PRODUCT
# -----------------------------------
@pytest.mark.django_db
def test_create_product(api_client):
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    res = api_client.post(
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

    assert res.status_code == 201
    assert "id" in res.data
    assert res.data["status"] == "Created"
    assert Product.objects(name="Phone").count() > 0


#ERROR: invalid category
@pytest.mark.django_db
def test_create_product_invalid_category(api_client):
    res = api_client.post(
        "/api/products/",
        {
             "name": "Phone",
        "brand": "Apple",
        "selling_price": 500,
        "warehouse_quantity": 10,
        "is_perishable": False,
        "category_id":"invalid"
        },
        format="json"
    )

    assert res.status_code == 404
    assert "error" in res.data


# -----------------------------------
# GET PRODUCT
# -----------------------------------
@pytest.mark.django_db
def test_get_product(api_client):
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        { "name": "Phone",
        "brand": "Apple",
        "selling_price": 500,
        "warehouse_quantity": 10,
        "category_id": category_id,
        "is_perishable": False},
        format="json"
    )

    product_id = prod_res.data["id"]

    res = api_client.get(f"/api/products/{product_id}/")

    assert res.status_code == 200
    assert res.data["name"] == "Phone"


#ERROR
@pytest.mark.django_db
def test_get_product_not_found(api_client):
    res = api_client.get("/api/products/64b8f8f8f8f8f8f8f8f8f8f8/")

    assert res.status_code == 404


# -----------------------------------
# UPDATE PRODUCT
# -----------------------------------
@pytest.mark.django_db
def test_update_product(api_client):
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        { "name": "Phone",
        "brand": "Apple",
        "selling_price": 500,
        "warehouse_quantity": 10,
        "category_id": category_id,
        "is_perishable": False},
        format="json"
    )

    product_id = prod_res.data["id"]

    res = api_client.patch(
        f"/api/products/{product_id}/",
        {"selling_price": 600},
        format="json"
    )

    assert res.status_code == 200
    assert res.data["product"]["selling_price"] == "600.00"

    #  DB check
    product = Product.objects.get(id=product_id)
    assert res.data["product"]["selling_price"] == "600.00"


# -----------------------------------
# DELETE PRODUCT
# -----------------------------------
@pytest.mark.django_db
def test_delete_product(api_client):
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        { "name": "Phone",
        "brand": "Apple",
        "selling_price": 500,
        "warehouse_quantity": 10,
        "category_id": category_id,
        "is_perishable": False},
        format="json"
    )

    product_id = prod_res.data["id"]

    res = api_client.delete(f"/api/products/{product_id}/")

    assert res.status_code == 200

    # DB check
    assert Product.objects(id=product_id).count() == 0


# -----------------------------------
# LIST PRODUCTS (FILTER + PAGINATION)
# -----------------------------------
@pytest.mark.django_db
def test_get_products_with_filter(api_client):
    res = api_client.get("/api/products/?page=1&limit=5")

    assert res.status_code == 200
    assert "data" in res.data
    assert "pagination" in res.data


# ERROR: invalid pagination
@pytest.mark.django_db
def test_invalid_pagination(api_client):
    res = api_client.get("/api/products/?page=0&limit=0")

    assert res.status_code == 400


# -----------------------------------
# BULK CSV UPLOAD
# -----------------------------------
@pytest.mark.django_db
def test_bulk_upload_products(api_client):
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]
    csv_content =f"""name,brand,category,warehouse_quantity,selling_price,cost_price,is_perishable,description
    Office Chair,Steelcase,{category_id},12,499.00,300.00,false,Ergonomic with lumbar support"""
    file = SimpleUploadedFile(
    "products.csv",
    csv_content.encode("utf-8"),
    content_type="text/csv"
    )


    res = api_client.post(
        "/api/products/bulk-upload/",
        {"file": file},
        format="multipart"
    )

    assert res.status_code in [201, 207]
    assert Product.objects.count() >= 1


# ERROR: wrong file type
@pytest.mark.django_db
def test_bulk_upload_invalid_file(api_client):
    file = BytesIO(b"invalid")
    file.name = "test.txt"

    res = api_client.post(
        "/api/products/bulk-upload/",
        {"file": file},
        format="multipart"
    )

    assert res.status_code == 400