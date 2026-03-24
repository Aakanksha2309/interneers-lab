"""
This file handles all product logic, including filtering, 
category assignments, and CSV bulk uploads.
"""

from ..repositories.product_repository import ProductRepository
from ..exceptions import ProductNotFoundError, BusinessValidationError,BulkValidationError,CategoryNotFoundError
from ..repositories.product_category_repository import CategoryRepository
import io,csv,math,datetime
from bson import ObjectId
from datetime import datetime,UTC
from ..serializers.product_serializer import ProductSerializer


class ProductService:
    def __init__(self):
        self.repository = ProductRepository()
        self.category_repository = CategoryRepository()
  
    #Converts a Category ID string into a Database Object
    def _merge_category_into_payload(self, data):
        payload = data.copy()

        if "category_id" not in payload:
            return payload 

        category_id = payload.pop("category_id") 
        if not ObjectId.is_valid(category_id):  #Extract the ID and verify it is a valid MongoDB format
            raise CategoryNotFoundError(f"Invalid ID format: '{category_id}'")
        
        category = self.category_repository.get_by_id(category_id)    
        if not category:
            raise CategoryNotFoundError("Invalid category ID")
        
        payload["category"] = category # Swap the ID string for the real Object
        
        return payload
    
    #Search and Filter:Converts user inputs into a MongoDB-compatible query
    def get_catalog(self, page, limit, active_filters):
        mongo_query = {}
        raw_query = {}

        # Brand Filter 
        if "brand" in active_filters:
            mongo_query["brand__iexact"] = active_filters["brand"]
        #Name filter 
        if "search" in active_filters and active_filters["search"]:
            mongo_query["name__icontains"] = active_filters["search"]
        # Category Filter 
        if "category_ids" in active_filters and active_filters["category_ids"]:
            try:
                #Converts a comma-separated string of IDs into a list of Objects
                cids = active_filters["category_ids"].split(",")
                mongo_query["category__in"] = [ObjectId(cid.strip()) for cid in cids if cid.strip()]
            except Exception:
                 raise ValueError("Invalid category_ids format")

       #Handles Price ranges and Expiry dates
        if "is_perishable" in active_filters:
            mongo_query["is_perishable"] = active_filters["is_perishable"]

        if "min_price" in active_filters:
            mongo_query["selling_price__gte"] = active_filters["min_price"]
        
        if "max_price" in active_filters:
            mongo_query["selling_price__lte"] = active_filters["max_price"]

        if "expires_before" in active_filters:
            mongo_query["expiry_date__lte"] = active_filters["expires_before"]

        #Compares warehouse quantity and threshold quantity
        if active_filters.get("low_stock") is True:
            raw_query["$expr"] = {
                "$lte": ["$warehouse_quantity", "$low_stock_threshold"]
            }

       
        skip = (page - 1) * limit
        products, total_count = self.repository.get_paginated(
            mongo_query=mongo_query,
            raw_query=raw_query,
            skip=skip,
            limit=limit
        )
        total_pages = math.ceil(total_count / limit) if limit > 0 else 1

        return {
            "products": products,
            "metadata": {
                "total_items": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "limit": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    # Standard CRUD operations
    #Create product
    def create_product(self, data):
        payload = self._merge_category_into_payload(data)
        return self.repository.create(payload)
    
    #Get product by ID
    def get_product(self, product_id):
        product = self.repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found.")
        return product
    
    #Update product details
    def update_product(self, product_id, data):

        self.get_product(product_id)       
        payload = self._merge_category_into_payload(data)
        updated = self.repository.update(product_id, payload)
        if updated is None:
            raise ProductNotFoundError(f"Product with ID {product_id} not found.")
        return updated
    
    #Delete product
    def delete_product(self, product_id):
        if not self.repository.delete(product_id):
            raise ProductNotFoundError(f"Could not delete: Product {product_id} missing.")
        return True

    # Category Management logic
    #Fetch producst from a prticulr category
    def fetch_products_for_category(self, category_id):
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError("Category not found!")
        return self.repository.get_products_by_category_id(category.id)

    #Assign category to a product
    def add_product_to_category(self, category_id, product_id):
        product = self.get_product(product_id)
        category = self.category_repository.get_category_by_id(category_id)
        if not category:
            raise CategoryNotFoundError("Given category not found!")
        return self.repository.assign_category(product, category)

    #Remove product from a category
    def remove_product_from_category(self, category_id, product_id):
        product = self.get_product(product_id)
        category = self.category_repository.get_category_by_id(category_id)
        if not category:
            raise CategoryNotFoundError("Given category not found!")
        return self.repository.remove_category(product, category)

    #Bulk upload data using csv files 
    def bulk_create_from_csv(self, file_obj):
        if not file_obj.name.endswith('.csv'):
            raise BulkValidationError(details="File must be in .csv format")
        
        # 1. Setup counters and storage
        decoded_file = file_obj.read().decode('utf-8')
        reader = list(csv.DictReader(io.StringIO(decoded_file))) # Convert to list to get length
        total_rows = len(reader)
        
        valid_payloads = []
        errors_list = []
        batch_time = datetime.now(UTC)

        # 2. Process rows
        for index, row in enumerate(reader):
            row_num = index + 2 # Header is row 1, first data is row 2
            
            clean_row = {k: v.strip() for k, v in row.items() if v and v.strip() != ""}
            
            if 'category' in clean_row:
                clean_row['category_id'] = clean_row.pop('category')
            
            if 'is_perishable' in clean_row:
                clean_row['is_perishable'] = clean_row['is_perishable'].lower() == 'true'

            serializer = ProductSerializer(data=clean_row)
            
            if serializer.is_valid():
                data = dict(serializer.validated_data)
                try:
                    data = self._merge_category_into_payload(data)
                    data['created_at'] = batch_time
                    data['updated_at'] = batch_time
                    valid_payloads.append(data)
                except CategoryNotFoundError as e:
                    errors_list.append({"row": row_num, "error": str(e)})
            else:
                # Format serializer errors to be more readable in your 'errors' list
                readable_errors = ", ".join([f"{k}: {v[0]}" for k, v in serializer.errors.items()])
                errors_list.append({"row": row_num, "error": readable_errors})

        # 3. Execution Phase
        if valid_payloads:
            self.repository.bulk_create(valid_payloads)

        # 4. Construct your custom Response Object
        return {
            "total": total_rows,
            "success": len(valid_payloads),
            "failed": len(errors_list),
            "errors": errors_list
        }