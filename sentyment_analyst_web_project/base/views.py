from django.shortcuts import render
from django.http import JsonResponse
import requests

def home(request):
    return upload_file(request)

def upload_file(request):
    error = None
    context = {}
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        response = requests.post(
            "http://localhost:8000/predict-file/",
            files={"file": (file.name, file.read(), file.content_type)},
        )
        if response.status_code == 200:
            context["data"] = response.json()["data"]
            context["predicciones"] = response.json()["predicciones"]
            context["file_name"] = file.name
            # Devuelve solo el contexto como JSON
            return JsonResponse(context)
        else:
            error = response.json()["detail"]
            return JsonResponse({"error": error}, status=400)
    # Renderiza el template solo en GET
    context["error"] = error
    return render(request, "base/upload.html", context)
