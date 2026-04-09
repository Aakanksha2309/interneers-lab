#!/bin/bash

set -e

echo "STEP 1: Product Service Unit Tests"
pytest django_app/products/services/test_product_service.py -v

echo "STEP 2: Category Service Unit Tests"
pytest django_app/products/services/test_category_service.py -v

echo "STEP 3: Integration Tests"
pytest tests/integration/ -v

echo "SUCCESS: Everything is working. No regressions found!"