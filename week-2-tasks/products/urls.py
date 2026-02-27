from django.urls import path
from .views import ProductCreateView,ProductListView,ProductDetailView

urlpatterns = [
    path('products/',ProductListView.as_view()),
    path('products/create/',ProductCreateView.as_view()),
    path('products/<int:pk>/',ProductDetailView.as_view())
]
