from django.contrib import admin
from django.urls import path
from django.http import HttpResponse,JsonResponse
from .views import greet_view,farewell_view

def home(request):
    return JsonResponse({"message": "Welcome! Use /greet/ or /farewell/ endpoints."})

urlpatterns = [
    path('', home), 
    path('admin/', admin.site.urls),
    path('greet/', greet_view),
    path('farewell/', farewell_view)
]
