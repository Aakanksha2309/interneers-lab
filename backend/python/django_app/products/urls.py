
from django.urls import path
from .views.product_view import (
    ProductView,
    ProductDetailView,
    ProductCategoryView,
    ProductBulkUploadView
)
from .views.product_category_view import (
    ProductCategoryAPIView,
    ProductCategoryDetailAPIView
)

urlpatterns=[

    #  Product api
    path('products/',ProductView.as_view(),name="product_list"), 

    # Bulk Data Import
    path('products/bulk-upload/',ProductBulkUploadView.as_view(),name='product-bulk-upload'),

    # Product-Category Relationships
    path('products/category/bulk-move/', ProductCategoryView.as_view(), name='product-category-bulk-move'),
    path('products/<str:product_id>/',ProductDetailView.as_view(),name="product_detail"),
    path('products/category/<str:category_id>/',ProductCategoryView.as_view(),name='products-by-category'),
    path('products/category/<str:category_id>/<str:product_id>/',ProductCategoryView.as_view(),name='product-category-operations'),

    # Category Management
    path('categories/', ProductCategoryAPIView.as_view(), name='category-list-create'),
    path('categories/<str:category_id>/', ProductCategoryDetailAPIView.as_view(), name='category-detail')
]