"""
Product Integration Tests
------------------------------
Checking how products, categories, and CSV uploads all work together.
Essentially making sure we can manage inventory without the database breaking
or losing data along the way.
"""

import pytest
from io import BytesIO
from django_app.products.models.product import Product
from django_app.products.models.product_category import ProductCategory
from django.core.files.uploadedfile import SimpleUploadedFile

# --------------------------------
# CREATE PRODUCT
# --------------------------------

@pytest.mark.django_db
def test_create_product(api_client):
    """Test: Creating a product with valid category"""
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
            "is_perishable": False,
        },
        format="json",
    )

    assert res.status_code == 201
    assert "id" in res.data
    assert res.data["status"] == "Created"
    assert Product.objects(name="Phone").count() > 0


@pytest.mark.django_db
def test_selling_less_than_cost(api_client):
    """Test: Selling price less than cost price"""
    res = api_client.post(
        "/api/products/",
        {
            "name": "Bad",
            "brand": "Test",
            "selling_price": 50,
            "cost_price": 100,
            "warehouse_quantity": 10,
            "is_perishable": False,
        },
        format="json",
    )

    assert res.status_code == 400


@pytest.mark.django_db
def test_create_product_without_category(api_client):
    """Test: Creating a product without category, should auto-assign 'Uncategorized'"""
    res = api_client.post(
        "/api/products/",
        {
            "name": "NoCatProduct",
            "brand": "Test",
            "selling_price": 100,
            "warehouse_quantity": 5,
            "is_perishable": False,
        },
        format="json",
    )
    uncat_exists = ProductCategory.objects(title__iexact="uncategorized").first()
    assert uncat_exists is not None
    assert res.status_code == 201
    assert Product.objects(name="NoCatProduct").count() == 1


@pytest.mark.django_db
def test_create_product_negative_price(api_client):
    """Test: Creating a product with negative price, should result in error"""
    res = api_client.post(
        "/api/products/",
        {
            "name": "BadProduct",
            "brand": "Test",
            "selling_price": -100,
            "warehouse_quantity": 5,
            "is_perishable": False,
        },
        format="json",
    )

    assert res.status_code == 400


@pytest.mark.django_db
def test_create_product_missing_fields(api_client):
    """Test: Product creation with missing required fields, should fail"""
    res = api_client.post(
        "/api/products/",
        {"name": "Phone"},
        format="json",
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_create_product_invalid_category(api_client):
    """Test: Product creation with invalid category id, should fail"""
    res = api_client.post(
        "/api/products/",
        {
            "name": "Phone",
            "brand": "Apple",
            "selling_price": 500,
            "warehouse_quantity": 10,
            "is_perishable": False,
            "category_id": "invalid",
        },
        format="json",
    )

    assert res.status_code == 404
    assert "error" in res.data
    if "id" in res.data:
        product_id = res.data["id"]
        get_res = api_client.get(f"/api/products/{product_id}/")
        assert get_res.status_code == 404


@pytest.mark.django_db
def test_create_duplicate_product(api_client):
    """Test: Duplicate product creation"""
    payload = {
        "name": "iPhone",
        "brand": "Apple",
        "selling_price": 1000,
        "warehouse_quantity": 10,
        "is_perishable": False,
    }

    api_client.post("/api/products/", payload, format="json")
    res = api_client.post("/api/products/", payload, format="json")

    assert res.status_code in [201, 400]


# --------------------------------
# GET PRODUCT
# --------------------------------

@pytest.mark.django_db
def test_get_product_invalid_id_format(api_client):
    """Test: Fetching product with invalid ID"""
    res = api_client.get("/api/products/invalid-id/")
    assert res.status_code == 404


@pytest.mark.django_db
def test_get_product(api_client):
    """Test: Fetching product with valid product id"""
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        {
            "name": "Phone",
            "brand": "Apple",
            "selling_price": 500,
            "warehouse_quantity": 10,
            "category_id": category_id,
            "is_perishable": False,
        },
        format="json",
    )

    product_id = prod_res.data["id"]

    res = api_client.get(f"/api/products/{product_id}/")

    assert res.status_code == 200
    assert res.data["name"] == "Phone"


@pytest.mark.django_db
def test_get_product_not_found(api_client):
    """Test: Fetching non-existent product"""
    res = api_client.get("/api/products/64b8f8f8f8f8f8f8f8f8f8f8/")
    assert res.status_code == 404


# --------------------------------
# UPDATE PRODUCT
# --------------------------------

@pytest.mark.django_db
def test_update_product(api_client):
    """Test: Updating product fields"""
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        {
            "name": "Phone",
            "brand": "Apple",
            "selling_price": 500,
            "warehouse_quantity": 10,
            "category_id": category_id,
            "is_perishable": False,
        },
        format="json",
    )

    product_id = prod_res.data["id"]

    res = api_client.patch(
        f"/api/products/{product_id}/",
        {"selling_price": 600},
        format="json",
    )

    assert res.status_code == 200
    assert res.data["product"]["selling_price"] == "600.00"
    assert res.data["message"] == "Updated successfully"

    product = Product.objects.get(id=product_id)
    assert res.data["product"]["selling_price"] == "600.00"


@pytest.mark.django_db
def test_patch_does_not_override_category(api_client):
    """Test: Update without category id"""
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        {
            "name": "Phone",
            "brand": "Apple",
            "selling_price": 500,
            "warehouse_quantity": 10,
            "category_id": category_id,
            "is_perishable": False,
        },
        format="json",
    )

    product_id = prod_res.data["id"]

    api_client.patch(
        f"/api/products/{product_id}/",
        {"selling_price": 600},
        format="json",
    )

    res = api_client.get(f"/api/products/{product_id}/")

    assert res.data["category_id"] == category_id


@pytest.mark.django_db
def test_update_product_invalid_price(api_client):
    """Test: Update invalid price"""
    res = api_client.patch(
        "/api/products/507f1f77bcf86cd799439011/",
        {"selling_price": -10},
        format="json",
    )
    assert res.status_code == 400


def test_patch_updates_category(api_client):
    """Test: Valid category updation"""
    cat1 = api_client.post("/api/categories/", {"title": "A"}, format="json").data["id"]
    cat2 = api_client.post("/api/categories/", {"title": "B"}, format="json").data["id"]

    prod = api_client.post(
        "/api/products/",
        {
            "name": "Test",
            "brand": "Test",
            "selling_price": 100,
            "warehouse_quantity": 10,
            "category_id": cat1,
            "is_perishable": False,
        },
        format="json",
    )

    product_id = prod.data["id"]

    res = api_client.patch(
        f"/api/products/{product_id}/",
        {"category_id": cat2},
        format="json",
    )

    assert res.status_code == 200

    get_res = api_client.get(f"/api/products/{product_id}/")
    assert get_res.data["category_id"] == cat2


@pytest.mark.django_db
def test_update_product_not_found(api_client):
    """Test: Updating a product that doesn't exist"""
    res = api_client.patch(
        "/api/products/507f1f77bcf86cd799439099/",
        {"selling_price": 1000},
        format="json",
    )
    assert res.status_code == 404


@pytest.mark.django_db
def test_update_product_invalid_category(api_client):
    """Test: Assigning invalid category during update"""
    res = api_client.patch(
        "/api/products/507f1f77bcf86cd799439011/",
        {"category_id": "invalid"},
        format="json",
    )
    assert res.status_code == 404


# --------------------------------
# DELETE PRODUCT
# --------------------------------

@pytest.mark.django_db
def test_delete_product(api_client):
    """Test: Deleting a product"""
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    prod_res = api_client.post(
        "/api/products/",
        {
            "name": "Phone",
            "brand": "Apple",
            "selling_price": 500,
            "warehouse_quantity": 10,
            "category_id": category_id,
            "is_perishable": False,
        },
        format="json",
    )

    product_id = prod_res.data["id"]

    res = api_client.delete(f"/api/products/{product_id}/")

    assert res.status_code == 200
    assert res.data["status"] == "success"
    assert Product.objects(id=product_id).count() == 0


@pytest.mark.django_db
def test_delete_product_invalid_id_format(api_client):
    """Test: Deleting product with invalid ID format"""
    res = api_client.delete("/api/products/invalid-id/")
    assert res.status_code == 404


@pytest.mark.django_db
def test_delete_product_not_found(api_client):
    """Test: Deleting a non-existent product"""
    res = api_client.delete("/api/products/507f1f77bcf86cd799439099/")
    assert res.status_code == 404


# --------------------------------
# FILTER AND PAGINATION
# --------------------------------

@pytest.mark.django_db
def test_get_products_with_filter(api_client):
    """Test: Product listing should support pagination"""
    res = api_client.get("/api/products/?page=1&limit=5")

    assert res.status_code == 200
    assert "data" in res.data
    assert "pagination" in res.data


@pytest.mark.django_db
def test_invalid_price_filter(api_client):
    """Test: Invalid price filter should return validation error"""
    res = api_client.get("/api/products/?min_price=abc")
    assert res.status_code == 400


@pytest.mark.django_db
def test_invalid_date_filter(api_client):
    """Test: Invalid date filter"""
    res = api_client.get("/api/products/?expires_before=not-a-date")
    assert res.status_code == 400


@pytest.mark.django_db
def test_invalid_category_ids_filter(api_client):
    """Test: Invalid category filter value"""
    res = api_client.get("/api/products/?category_ids=invalid_id")
    assert res.status_code == 400


@pytest.mark.django_db
def test_invalid_pagination(api_client):
    """Test: Invalid pagination values"""
    res = api_client.get("/api/products/?page=0&limit=0")
    assert res.status_code == 400


@pytest.mark.django_db
def test_filter_by_brand(api_client):
    """Test: Filter by brand"""
    api_client.post(
        "/api/products/",
        {
            "name": "Nike Shoe",
            "brand": "Nike",
            "selling_price": 100,
            "warehouse_quantity": 10,
            "is_perishable": False,
        },
        format="json",
    )

    res = api_client.get("/api/products/?brand=Nike")

    assert res.status_code == 200
    assert len(res.data["data"]) >= 1


@pytest.mark.django_db
def test_combined_filters(api_client):
    """Test: Filtering on the basis of price"""
    api_client.post(
        "/api/products/",
        {
            "name": "Valid",
            "brand": "Test",
            "selling_price": 50,
            "warehouse_quantity": 10,
            "is_perishable": False,
        },
        format="json",
    )

    api_client.post(
        "/api/products/",
        {
            "name": "InvalidLow",
            "brand": "Test",
            "selling_price": 5,
            "warehouse_quantity": 10,
            "is_perishable": False,
        },
        format="json",
    )

    res = api_client.get("/api/products/?min_price=10&max_price=100")

    names = [p["name"] for p in res.data["data"]]

    assert res.status_code == 200
    assert "Valid" in names
    assert "InvalidLow" not in names


@pytest.mark.django_db
def test_catalog_low_stock_filter_logic(api_client):
    """Test: Low stock filter should return only products below threshold and exclude products with sufficient stock"""
    api_client.post(
        "/api/products/",
        {
            "name": "NeedsRestock",
            "brand": "Test",
            "selling_price": 50,
            "warehouse_quantity": 5,
            "low_stock_threshold": 10,
            "is_perishable": False,
        },
        format="json",
    )

    api_client.post(
        "/api/products/",
        {
            "name": "PlentyOfStock",
            "brand": "Test",
            "selling_price": 50,
            "warehouse_quantity": 50,
            "low_stock_threshold": 10,
            "is_perishable": False,
        },
        format="json",
    )

    res = api_client.get("/api/products/?low_stock=true")

    assert res.status_code == 200
    product_names = [p["name"] for p in res.data["data"]]
    assert "NeedsRestock" in product_names
    assert "PlentyOfStock" not in product_names


@pytest.mark.django_db
def test_filter_no_results(api_client):
    """Test: Empty Filter Test"""
    res = api_client.get("/api/products/?brand=NonExistentBrand")

    assert res.status_code == 200
    assert res.data["data"] == []


@pytest.mark.django_db
def test_brand_case_insensitive(api_client):
    """Test: Checking case sensitivity while filtering"""
    api_client.post(
        "/api/products/",
        {
            "name": "Shoe",
            "brand": "Nike",
            "selling_price": 100,
            "warehouse_quantity": 10,
            "is_perishable": False,
        },
        format="json",
    )

    res = api_client.get("/api/products/?brand=nike")

    assert res.status_code == 200
    assert len(res.data["data"]) >= 1

# --------------------------------
# BULK CSV UPLOAD
# --------------------------------

@pytest.mark.django_db
def test_bulk_upload_products(api_client):
    """Test: Bulk upload should successfully process valid CSV file"""
    cat_res = api_client.post("/api/categories/", {"title": "Electronics"}, format="json")
    category_id = cat_res.data["id"]

    csv_content = (
        f"name,brand,category,warehouse_quantity,selling_price,cost_price,is_perishable,description\n"
        f"Office Chair,Steelcase,{category_id},12,499.00,300.00,false,Ergonomic with lumbar support"
    )

    file = SimpleUploadedFile(
        "products.csv",
        csv_content.encode("utf-8"),
        content_type="text/csv",
    )

    res = api_client.post(
        "/api/products/bulk-upload/",
        {"file": file},
        format="multipart",
    )

    assert res.status_code in [201, 207]
    assert Product.objects.count() >= 1
    assert "total" in res.data
    assert "success" in res.data
    assert "failed" in res.data


@pytest.mark.django_db
def test_bulk_upload_invalid_file(api_client):
    """Test: Uploading invalid file"""
    file = BytesIO(b"invalid")
    file.name = "test.txt"

    res = api_client.post("/api/products/bulk-upload/", {"file": file}, format="multipart")

    assert res.status_code == 400


@pytest.mark.django_db
def test_bulk_upload_empty_csv(api_client):
    """Test: Empty CSV file"""
    file = BytesIO(b"")
    file.name = "products.csv"

    res = api_client.post("/api/products/bulk-upload/", {"file": file}, format="multipart")

    assert res.status_code in [400, 207]


@pytest.mark.django_db
def test_bulk_upload_only_headers(api_client):
    """Test: CSV with only headers, should not create products"""
    csv_content = "name,price,brand\n"

    file = SimpleUploadedFile("products.csv", csv_content.encode("utf-8"), content_type="text/csv")

    res = api_client.post("/api/products/bulk-upload/", {"file": file}, format="multipart")

    assert res.status_code in [400, 207]


@pytest.mark.django_db
def test_bulk_upload_invalid_rows(api_client):
    """Test: Bulk upload, should handle invalid rows"""
    csv_content = (
        "name,price\n"
        ",100\n"
        "Product2,abc\n"
    )

    file = SimpleUploadedFile("products.csv", csv_content.encode("utf-8"), content_type="text/csv")

    res = api_client.post("/api/products/bulk-upload/", {"file": file}, format="multipart")

    assert res.status_code in [400, 207]
    assert "failed" in res.data


@pytest.mark.django_db
def test_bulk_upload_no_file(api_client):
    """Test: Request without file"""
    res = api_client.post("/api/products/bulk-upload/", {}, format="multipart")
    assert res.status_code == 400


@pytest.mark.django_db
def test_bulk_upload_partial_failure(api_client):
    """Test: Partial success case: some rows succeed, some fail"""
    cat_res = api_client.post("/api/categories/", {"title": "Hardware"}, format="json")
    valid_id = cat_res.data["id"]
    fake_id = "507f1f77bcf86cd799439099"  # Valid format, but doesn't exist

    csv_content = (
        "name,brand,category,warehouse_quantity,selling_price,is_perishable\n"
        f"Good Item,BrandA,{valid_id},10,100,false\n"
        f"Bad Item,BrandB,{fake_id},5,50,false"
    )
    
    file = SimpleUploadedFile("products.csv", csv_content.encode("utf-8"), content_type="text/csv")
    res = api_client.post("/api/products/bulk-upload/", {"file": file}, format="multipart")

    assert res.status_code == 207
    assert res.data["success"] == 1
    assert res.data["failed"] == 1
    assert any("category" in err["error"].lower() for err in res.data["errors"])


@pytest.mark.django_db
def test_bulk_upload_duplicate_rows(api_client):
    """Test: File with duplicate rows"""
    csv_content = (
        "name,brand,selling_price,warehouse_quantity,is_perishable\n"
        "Product1,Test,100,10,false\n"
        "Product1,Test,100,10,false\n"
    )

    file = SimpleUploadedFile("products.csv", csv_content.encode("utf-8"))

    res = api_client.post("/api/products/bulk-upload/", {"file": file}, format="multipart")

    assert res.status_code in [201, 207]