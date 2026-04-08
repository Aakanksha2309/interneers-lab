"""
This file handles the HTTP requests (POST, GET, PATCH, DELETE).
It connects the incoming user data to the CategoryService.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..exceptions import CategoryNotFoundError
from ..serializers.product_category_serializer import ProductCategorySerializer
from ..services.product_category_service import CategoryService

 
class ProductCategoryAPIView(APIView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.category=CategoryService()

    # Create a new category
    def post(self,request):
     
        serializer=ProductCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            category = self.category.create_category(serializer.validated_data)
            return Response(
                {"id": str(category.id), "message": "Category created successfully"},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
    # List all categories
    def get(self, request):
        categories = self.category.get_all_categories()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductCategoryDetailAPIView(APIView):   
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.category=CategoryService()
    
    # Get a specific category
    def get(self,request,category_id):
        try:
            category=self.category.get_category_by_id(category_id)
            return Response(
                ProductCategorySerializer(category).data,
                status=status.HTTP_200_OK
            )
        except CategoryNotFoundError as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)
    
    # Delete category
    def delete(self, request, category_id):
        try:
            self.category.delete_category(category_id)
            return Response({
            "status": "success",
            "message": f"Category with ID {category_id} was successfully deleted.",
            }, status=status.HTTP_200_OK)
        except CategoryNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update category
    def patch(self, request, category_id):
        try:
            category_instance = self.category.get_category_by_id(category_id)
            serializer = ProductCategorySerializer(
                instance=category_instance,
                data=request.data,partial=True
            )
            serializer.is_valid(raise_exception=True)
            category = self.category.update_category(
                category_id,
                serializer.validated_data
            )
            return Response({
                "message": "Updated successfully",
                "category": ProductCategorySerializer(category).data,
            },status=status.HTTP_200_OK)

        except CategoryNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

