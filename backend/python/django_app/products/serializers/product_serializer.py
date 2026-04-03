"""
This file converts Product data between MongoDB and JSON.
It uses three types of validation:
1. Declarative (Field-level constraints like max_length)
2. Field-level (Custom brand name validator)
3. Object-level (Cross-field logic for pricing and expiry dates)
"""
from rest_framework import serializers

class ProductSerializer(serializers.Serializer):
    # Basic item info
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000, required=False,allow_blank=True)
    category_id = serializers.CharField(write_only=True,required=False)
    brand = serializers.CharField(required=True)

   #inventory tracking fields
    warehouse_quantity = serializers.IntegerField(min_value=0)
    low_stock_threshold = serializers.IntegerField(min_value=1,required=False, default=10)

    # perishable
    is_perishable = serializers.BooleanField(default=False)
    expiry_date = serializers.DateTimeField(required=False, allow_null=True)
    cost_price = serializers.DecimalField(min_value=0,max_digits=10, decimal_places=2,required=False)
    selling_price = serializers.DecimalField(min_value=0,max_digits=10, decimal_places=2)

    #audit fields
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Shows the Category ID as a string in the final output
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance is not None and getattr(instance, "category", None):
            data["category_id"] = str(instance.category.id)
        return data
        
    #Field-level Validation :- checks if product has a brand
    def validate_brand(self, value):
        brand_name = value.strip()

        if not brand_name:
            raise serializers.ValidationError("Brand name cannot be empty or just whitespace.")
        
        if len(brand_name) < 2:
            raise serializers.ValidationError("Brand name must be at least 2 characters long.")
            
        return brand_name

    # Object-level Validation 
    def validate(self, data):
        is_perishable = data.get("is_perishable")
        expiry_date = data.get("expiry_date")

        # perishable logic
        if is_perishable and not expiry_date:
            raise serializers.ValidationError(
                "Expiry date required for perishable products"
            )

        if not is_perishable and expiry_date:
            raise serializers.ValidationError(
                "Non-perishable product should not have expiry date"
            )

        # pricing logic
        cost = data.get("cost_price")
        selling = data.get("selling_price")

        if cost is not None and selling is not None and selling < cost:
            raise serializers.ValidationError(
                "Selling price cannot be less than cost price"
            )

        return data