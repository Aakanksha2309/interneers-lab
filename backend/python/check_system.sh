#!/bin/bash

# This line tells the script to STOP if any test fails. 

set -e

echo "STEP 1: Running Unit Tests"
pytest tests/unit/ -v

echo "STEP 2: Running Integration Tests (API & Database)"
pytest tests/integration/ -v

echo "SUCCESS: Everything is working. No regressions found!"