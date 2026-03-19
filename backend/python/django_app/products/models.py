from django.db import models
import datetime
from mongoengine import Document,IntField,FloatField,StringField,DateTimeField,signals,DecimalField
class Product(Document):
    name = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    category = StringField(required=True, choices=['Electronics', 'Apparel', 'Home', 'Groceries'])
    brand = StringField(required=True)
    price = DecimalField(required=True, precision=2, min_value=0.01)
    warehouse_quantity = IntField(required=True, min_value=0)

    #Audit columns 
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    meta={'collection':'products'}
    
    #update the updated_at field before saving the document 
    @classmethod
    def pre_save(cls,sender,document,**kwargs):
        document.updated_at = datetime.datetime.utcnow()

#Link the signal 
signals.pre_save.connect(Product.pre_save, sender=Product)
