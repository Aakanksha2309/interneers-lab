from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import productSerializer
from .storage import products_db,product_id_counter

#CREATE PRODUCT 
class ProductCreateView(APIView):
    def post(self,request):
        global product_id_counter #To update the id counter 
        serializer=productSerializer(data=request.data)
        if serializer.is_valid():
            product=serializer.validated_data 
            product["id"]=product_id_counter
            products_db.append(product)
            product_id_counter+=1
            return Response(product,status=status.HTTP_201_CREATED) 
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
#GET ALL PRODUCTS(including pagination)
class ProductListView(APIView):
    def get(self,request):
        # return Response(products_db,status=status.HTTP_200_OK) #without pagination 
        
        #with pagination 
        page=int(request.GET.get("page",1))
        limit=(int)(request.GET.get("limit",5))
        start=(page-1)*limit 
        end=start+limit

        paginated_data=products_db[start:end]
        return Response({
            "start page":start,
            "end page":end,
            "data":paginated_data
        })

#GET SINGLE PRODUCT 
class ProductDetailView(APIView):
    def get_product(self,pk):
        for product in products_db:
            if(pk==product["id"]):
                return product
        return None
    def get(self,request,pk):
        product=self.get_product(pk)
        if not product:
            return Response({"error":"product with given ID not found"},status=status.HTTP_404_NOT_FOUND)
        return Response(product)

#UPDATE PRODUCT


    def put(self,request,pk):
        product=self.get_product(pk)
        if not product:
            return Response({"error":"product not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=productSerializer(data=request.data)
        if serializer.is_valid():
            updated_product=serializer.validated_data
            updated_product["id"]=pk
            products_db.remove(product)
            products_db.append(updated_product)
            return Response(updated_product,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

#DELETE PRODUCT

    def delete(self,request,pk):
        product=self.get_product(pk)
        if not product:
            return Response({"error":"product not found"},status=status.HTTP_404_NOT_FOUND)
        products_db.remove(product)
        return Response({"message":"Product deleted successfully"},status=status.HTTP_204_NO_CONTENT)

