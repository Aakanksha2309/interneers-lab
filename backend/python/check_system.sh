#!/bin/bash

<<<<<<< HEAD
set -e

echo "STEP 1: Product Service Unit Tests"
pytest django_app/products/services/test_product_service.py -v

echo "STEP 2: Category Service Unit Tests"
pytest django_app/products/services/test_category_service.py -v

echo "STEP 3: Integration Tests"
=======
# This line tells the script to STOP if any test fails. 

set -e

echo "STEP 1: Running Unit Tests"
pytest tests/unit/ -v

echo "STEP 2: Running Integration Tests (API & Database)"
>>>>>>> f41cf44 (WEEK-5 initial work)
pytest tests/integration/ -v

echo "SUCCESS: Everything is working. No regressions found!"