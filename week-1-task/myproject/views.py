from django.http import JsonResponse
from application.greeting_use_case import GreetingUseCase,FarewellUseCase

def greet_view(request):
    name=request.GET.get("name")
    if not name:
        return JsonResponse({"error":"Name parameter is required"},status=400)
    use_case=GreetingUseCase()
    message=use_case.execute(name)
    return JsonResponse({"message":message})

def farewell_view(request):
    name=request.GET.get("name")
    if not name:
        return JsonResponse({"error":"Name parameter is required"},status=400)
    use_case=FarewellUseCase()
    message=use_case.execute(name)
    return JsonResponse({"message":message})
