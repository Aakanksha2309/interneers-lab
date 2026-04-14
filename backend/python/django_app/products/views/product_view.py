"""
This file handles all Product-related HTTP requests.
It manages catalog filtering, individual product CRUD, and CSV bulk uploads.
"""
from ..serializers.product_serializer import ProductSerializer
from ..services.product_service import ProductService
from ..exceptions import CategoryNotFoundError, ProductNotFoundError,BulkValidationError,BusinessValidationError
from datetime import datetime  
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser


class ProductView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductService()
    # List products with filtering and pagination 
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))

            if page < 1 or limit < 1:
                return Response({"error": "Page and limit must be positive integers"}, status=400)

            try:
                min_price_raw = request.GET.get("min_price")
                max_price_raw = request.GET.get("max_price")
                min_price = float(min_price_raw) if min_price_raw else None
                max_price = float(max_price_raw) if max_price_raw else None
            except ValueError:
                return Response({"error": "Invalid price values"}, status=400)

            expires_before = request.GET.get("expires_before")
            if expires_before:
                try:
                    expires_before = datetime.fromisoformat(expires_before)
                except ValueError:
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

            def get_bool(param):
                val = request.GET.get(param)
                if val is None: return None
                return val.lower() == "true"

            filters = {
                "search": request.GET.get("search"),
                "category_ids": request.GET.get("category_ids"),
                "brand": request.GET.get("brand"),
                "min_price": min_price,
                "max_price": max_price,
                "is_perishable": get_bool("is_perishable"), # Only filters if present
                "expires_before": expires_before,
                "low_stock": get_bool("low_stock"), # Only filters if present
            }

            active_filters = {k: v for k, v in filters.items() if v is not None}

            result = self.service.get_catalog(page, limit, active_filters)
            serializer = ProductSerializer(result['products'], many=True)

            return Response({
                "status": "success",
                "data": serializer.data,
                "pagination": result['metadata']
            })

        except ValueError:
            return Response({"error": "Invalid pagination parameters"}, status=400)
        except BusinessValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create a new product 
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = self.service.create_product(serializer.validated_data)
        except CategoryNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except BusinessValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"id": str(product.id), "status": "Created"},
            status=status.HTTP_201_CREATED,
        )


class ProductDetailView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductService()
    # Get a single product by ID
    def get(self, request, product_id):
        try:
            product = self.service.get_product(product_id)
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        except ProductNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # Update product
    def patch(self, request, product_id):
        try:
            serializer = ProductSerializer(
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)

            updated_product = self.service.update_product(
            product_id, 
            serializer.validated_data
            )
            return Response({
                "message": "Updated successfully",
                "product": ProductSerializer(updated_product).data
            }, status=status.HTTP_200_OK)
            
        except ProductNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except CategoryNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # Delete product 
    def delete(self, request, product_id):
        try:
            self.service.delete_product(product_id)
            return Response({
            "status": "success",
            "message": f"Product with ID {product_id} was successfully deleted.",
            }, status=status.HTTP_200_OK)
        except ProductNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    #PRODUCT OPERATIONS BASED ON CATEGORY 
class ProductCategoryView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductService()
    # Fetch product by category
    def get(self,request,category_id):
        try:
            products=self.service.fetch_products_for_category(category_id)
            serializer=ProductSerializer(products,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except CategoryNotFoundError as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)
      

    # Link a product to a category
    def post(self,request,category_id,product_id):
        try:
            product=self.service.add_product_to_category(category_id,product_id)
            serializer=ProductSerializer(product)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except CategoryNotFoundError as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)
        except ProductNotFoundError as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)
    
    # Unlink a product from a category
    def delete(self,request,category_id,product_id):
        try:
            product=self.service.remove_product_from_category(category_id,product_id)
            serializer=ProductSerializer(product)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except CategoryNotFoundError as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)
        except ProductNotFoundError as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)
        except BusinessValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductBulkUploadView(APIView):
    parser_classes = [MultiPartParser]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductService()
    # Handle CSV File Uploads
    def post(self,request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = self.service.bulk_create_from_csv(file_obj)
            if result['success'] > 0 and result['failed'] > 0:
                status_code = 207  # Multi-Status
            elif result['success'] > 0:
                status_code = 201  # Created
            else:
                status_code = 400  # Bad Request
                
            return Response(result, status=status_code)
        except BulkValidationError as e:
            return Response({
                "message": "CSV data is invalid",
                "details": e.details
            }, status=status.HTTP_400_BAD_REQUEST)
