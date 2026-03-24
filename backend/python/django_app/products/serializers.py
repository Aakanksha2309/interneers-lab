
from rest_framework import serializers

class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000, required=False)
    category = serializers.ChoiceField(choices=['Electronics', 'Apparel', 'Home', 'Groceries'])
    brand = serializers.CharField()
    #Validation for price to be positive
    price = serializers.FloatField(min_value=0.01,error_messages={"min_value": "Price must be a positive value greater than zero.","invalid": "Please enter a valid decimal number for the price."})
    #Validation for quantity cannot be negative 
    warehouse_quantity = serializers.IntegerField(min_value=0,error_messages={
            "min_value": "Inventory cannot be negative."})
    # Audit fields 
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

   