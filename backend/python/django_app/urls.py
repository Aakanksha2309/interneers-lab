from django.contrib import admin
from django.urls import path
from django.http import HttpResponse,JsonResponse

def hello_world(request):
    return HttpResponse("Hello, world! This is our interneers-lab.")

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('hello/', hello_world),
    
# ]

# django_app/urls.py

def hello_name(request):
    """
    A simple view that returns 'Hello, {name}' in JSON format.
    Uses a query parameter named 'name'.
    """
    # Get 'name' from the query string, default to 'World' if missing
    name = request.GET.get("name", "World")
    return JsonResponse({"message": f"Hello, {name}!"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', hello_name)
]
