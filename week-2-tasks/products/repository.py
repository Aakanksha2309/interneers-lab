#This code acts as the repository layer for the app

from .models import Product

class ProductRepository:
  #Creating a new product entry
  def create(self,validated_data):
    return Product.objects.create(**validated_data)

#Get all items 
def get_all(self):
  return Product.objects.all()

#Get items via id 
def get_by_ID(self,product_id): 
  try:
    return Product.objects.get(id=product_id)
  except Product.DoesNotExist:
    return None

#Update entry
def update(self,product,validated_data):
  for attr,value in validated_data.items():
    setattr(product,attr,value)
  product.save()
  return product

#Delete an entry
def delete(self,product):
  product.delete()

  
