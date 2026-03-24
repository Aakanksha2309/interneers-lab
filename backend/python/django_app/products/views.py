from .services import ProductService
from .exceptions import ProductNotFoundError, BusinessValidationError
from .serializers import ProductSerializer  
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ProductView(APIView):
    service = ProductService()

    #Get all products with pagination 
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            result = self.service.get_catalog(page=page, limit=limit)
            serialized_products = ProductSerializer(result['products'],many=True)

            return Response({
                "data": serialized_products.data,
                "pagination": result['metadata']
            }, status=200)
            
        except ValueError:
            return Response({"error": "Page and limit must be integers"}, status=status.HTTP_400_BAD_REQUEST)
    #Create product  
    def post(self, request):
        serializer=ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = self.service.create_product(request.data)
            return Response({"id": str(product.id), "status": "Created"}, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    service = ProductService()
    #Get product by ID
    def get(self, request, product_id):
        try:
            product = self.service.get_product(product_id)
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        except ProductNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    #Update product
    def patch(self, request, product_id):
        try:
            updated_product = self.service.update_product(product_id, request.data)
            return Response({
                "message": "Updated successfully",
                "product": ProductSerializer(updated_product).data
            }, status=status.HTTP_200_OK)
            
        except ProductNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except BusinessValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #Delete a product 
    def delete(self, request, product_id):
        try:
            self.service.delete_product(product_id)
            return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProductNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)