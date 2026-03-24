"""
This file is for storing our Products.
It tracks the name,brand,warehouse quantity and other details for every product
"""
from datetime import datetime, timezone
from mongoengine import Document,IntField,FloatField,StringField,DateTimeField,signals,DecimalField,ValidationError,ReferenceField,BooleanField,DENY
from .product_category import ProductCategory
class Product(Document):
    # Basic item details
    name = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    brand = StringField(required=True,default="Unknown")
    # Link this product to a category and can't delete a category with products in it
    category = ReferenceField(ProductCategory,reverse_delete_rule=DENY) 
    # Inventory tracking details 
    warehouse_quantity = IntField(required=True, min_value=0)
    low_stock_threshold = IntField(default=10)
    #fields for perishable items 
    is_perishable = BooleanField(default=False)
    expiry_date = DateTimeField()
    #pricing
    cost_price = DecimalField(min_value=0.0,precision=2)
    selling_price = DecimalField(required=True, min_value=0.01,precision=2)
    #Audit columns 
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    meta={'collection':'products',
          'indexes': [
            'category', 
            'brand', 
            ('category', 'name')
        ]}
    
    #update the updated_at field before saving the document 
    @classmethod
    def pre_save(cls,sender,document,**kwargs):
        document.updated_at = datetime.now(timezone.utc)
    def clean(self):
        if self.is_perishable and not self.expiry_date:
            raise ValidationError("Expiry date required")

#Link the signal 
signals.pre_save.connect(Product.pre_save, sender=Product)
