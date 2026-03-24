
from django.urls import path
from .views import ProductView, ProductDetailView

urlpatterns=[
    path('products/',ProductView.as_view(),name="product_list"), 
    path('products/<str:product_id>/',ProductDetailView.as_view(),name="product_detail")
]