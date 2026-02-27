from rest_framework import serializers

class productSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    name=serializers.CharField(max_length=100)
    description=serializers.CharField(max_length=500)
    price=serializers.FloatField()
    quantity=serializers.IntegerField()
    brand=serializers.CharField(max_length=50)
    category=serializers.CharField(max_length=50)

    def validate_price(self,value):
        if(value<0):
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    def validate_quantity(self,value):
        if(value<0):
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value