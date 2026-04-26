"""
This file handles all product logic, including filtering, 
category assignments, and CSV bulk uploads.
"""

from ..repositories.product_repository import ProductRepository
from ..exceptions import ProductNotFoundError, BusinessValidationError,BulkValidationError,CategoryNotFoundError
from ..repositories.product_category_repository import CategoryRepository
import io,csv,math
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
        category_id = payload.get("category_id")

        if not category_id:
            # User provided NO ID, so find the "Uncategorized" default
            category = self.category_repository.get_by_title_case_insensitive("Uncategorized")
            
            # If "Uncategorized" doesn't even exist in DB, create it now
            if not category:
                category = self.category_repository.create({
                    "title": "Uncategorized",
                    "description": "Default category for products"
                })

        else:
            #Extract the ID and verify it is a valid MongoDB format
            if not ObjectId.is_valid(category_id):
                raise CategoryNotFoundError(f"Invalid ID format: '{category_id}'")
            
            category = self.category_repository.get_by_id(category_id)    
            if not category:
                raise CategoryNotFoundError("Invalid category ID")
        
        # Remove the string ID and attach the actual Category Object
        payload.pop("category_id", None) 
        payload["category"] = category
        
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
            cids = [cid.strip() for cid in active_filters["category_ids"].split(",") if cid.strip()]
            valid_oids = []
            
            for cid in cids:
                if ObjectId.is_valid(cid):
                    valid_oids.append(ObjectId(cid))
                else:
                    raise BusinessValidationError(f"Invalid category ID format: '{cid}'")
            
            if valid_oids:
                mongo_query["category__in"] = valid_oids
            else:
                # If they provided a key but no valid IDs, 
                # force an empty result by searching for a non-existent ID
                mongo_query["category"] = ObjectId("000000000000000000000000")
           
       #Handles Price ranges and Expiry dates
        if "is_perishable" in active_filters:
            mongo_query["is_perishable"] = active_filters["is_perishable"]

        if "min_price" in active_filters:
            mongo_query["selling_price__gte"] = active_filters["min_price"]
        
        if "max_price" in active_filters:
            mongo_query["selling_price__lte"] = active_filters["max_price"]

        if "expires_before" in active_filters:
            mongo_query["is_perishable"] = True
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
        global_total_value = self.repository.get_global_total_value()

        return {
            "products": products,
            "metadata": {
                "total_items": total_count,
                "total_pages": total_pages,
                "total_inventory_value":global_total_value,
                "current_page": page,
                "limit": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    # Standard CRUD operations
    #Create product
    def create_product(self, data):
        name = data.get('name')
        brand = data.get('brand')
        existing = self.repository.get_by_name_and_brand(name, brand)
        if existing:
           # Product with given name and brand already exists 
            raise BusinessValidationError(f"Conflict: {name} by {brand} is already in the system.")
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

        payload = data.copy()
        new_name=payload.get("name")
        new_brand=payload.get("brand")

        if new_name or new_brand:
            current=self.repository.get_by_id(product_id)
            if not current:
                raise ProductNotFoundError(f"Product with ID {product_id} not found.")
            check_name=new_name or current.name
            check_brand=new_brand or current.brand

            duplicate=self.repository.get_by_name_and_brand_excluding(check_name,check_brand,product_id)
            if duplicate:
                raise BusinessValidationError(f"Conflict:{check_name} by {check_brand} already exists")
        if "category_id" in payload:
            payload = self._merge_category_into_payload(payload)
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
    #Fetch products from a particular category
    def fetch_products_for_category(self, category_id):
        if not ObjectId.is_valid(category_id):
            raise CategoryNotFoundError(f"Invalid ID format: '{category_id}'")
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError("Category not found!")
        return self.repository.get_products_by_category_id(category.id)

    #Assign category to selected products 
    def bulk_add_products_to_category(self, product_ids,category_id):
        if not product_ids:
            raise BusinessValidationError("product_ids must be a non-empty list")

        if not isinstance(product_ids, list):
            raise BusinessValidationError(
                f"product_ids must be a list, got {type(product_ids).__name__}"
            )

        if not ObjectId.is_valid(category_id):
            raise CategoryNotFoundError(f"Invalid category ID format:'{category_id}'")

        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError("Given category not found!")
        
        updated=[]
        errors=[]

        for pid in product_ids:
            try:
                product = self.get_product(pid)
                updated_product=self.repository.assign_category(product,category)
                updated.append(updated_product)
            except ProductNotFoundError as e:
                errors.append({"product_id": pid, "error": str(e)})
            except CategoryNotFoundError as e:
                raise CategoryNotFoundError(
                f"Target category '{category_id}' not found or invalid. "
                f"Bulk move aborted. {len(updated)} products were moved before this failure."
                )
            except BusinessValidationError as e:
                errors.append({"product_id": pid, "error": str(e)})

        return updated, errors

    # Remove products from a category( assigning uncategorised category to such products )
    def bulk_remove_products_from_category(self,product_ids):
        valid_object_ids=[]
        for p_id in product_ids:
            if not ObjectId.is_valid(p_id):
                raise BusinessValidationError(f"Invalid Product ID format: {p_id}")
            valid_object_ids.append(ObjectId(p_id))

        existing_products = self.repository.get_existing_ids(valid_object_ids)
    
        if len(existing_products) != len(valid_object_ids):
            # Find which ones are missing 
            missing = set(valid_object_ids) - set(existing_products)
            raise ProductNotFoundError(f"Action failed. Products not found: {list(missing)}")

        default_cat = self.category_repository.get_by_title_case_insensitive("Uncategorized") 
        # Create category if it doesn't exist
        if not default_cat:
            default_cat = self.category_repository.create({
                "title": "Uncategorized",
                "description": "Default category for products"
            })
        return self.repository.bulk_remove_category(product_ids, default_cat)

    # Delete bulk products from a category
    def bulk_delete_products(self, product_ids):
        valid_ids = [ObjectId(p_id) for p_id in product_ids if ObjectId.is_valid(p_id)]
        
        if len(valid_ids) != len(product_ids):
            raise BusinessValidationError("One or more Product IDs are invalid.")

        # Check if products exist
        existing_ids = self.repository.get_existing_ids(valid_ids)
        if len(existing_ids) != len(valid_ids):
            raise ProductNotFoundError("Some products selected for deletion were not found.")
        success = self.repository.bulk_delete(valid_ids)
    
        if not success:
            raise BusinessValidationError("Database failed to delete the selected products.")
        return True

    #Bulk upload data using csv files 
    def bulk_create_from_csv(self, file_obj):
        if not file_obj.name.endswith('.csv'):
            raise BulkValidationError(details="File must be in .csv format")
        
        # Setup counters and storage
        decoded_file = file_obj.read().decode('utf-8')
        reader = list(csv.DictReader(io.StringIO(decoded_file))) # Convert to list to get length
        total_rows = len(reader)
        
        valid_payloads = []
        errors_list = []
        batch_time = datetime.now(UTC)
        seen_in_this_csv = set()

        # Process rows
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
                name_key = str(data.get('name', '')).strip().lower()
                brand_key = str(data.get('brand', '')).strip().lower()
                unique_key = (name_key, brand_key)
                if unique_key in seen_in_this_csv:
                    errors_list.append({
                        "row": row_num, 
                        "error": f"Duplicate entry within this CSV: {data['name']} ({data['brand']})"
                    })
                    continue
                existing = self.repository.get_by_name_and_brand(data['name'], data['brand'])
                if existing:
                    errors_list.append({
                        "row": row_num, 
                        "error": f"Duplicate found: {data['name']} by {data['brand']} already exists."
                    })
                    continue
                try:
                    data = self._merge_category_into_payload(data)
                    data['created_at'] = batch_time
                    data['updated_at'] = batch_time
                    valid_payloads.append(data)
                    seen_in_this_csv.add(unique_key)
                except CategoryNotFoundError as e:
                    errors_list.append({"row": row_num, "error": str(e)})
            else:
                # Format serializer errors to be more readable
                readable_errors = ", ".join([f"{k}: {v[0]}" for k, v in serializer.errors.items()])
                errors_list.append({"row": row_num, "error": readable_errors})

        if valid_payloads:
            self.repository.bulk_create(valid_payloads)

        return {
            "total": total_rows,
            "success": len(valid_payloads),
            "failed": len(errors_list),
            "errors": errors_list
        }