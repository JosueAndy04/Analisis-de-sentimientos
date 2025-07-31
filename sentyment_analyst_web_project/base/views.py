from django.shortcuts import render
from django.http import JsonResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL", "https://analisis-de-sentimientos-tcpb.onrender.com/"
)


def home(request):
    return upload_file(request)


def upload_file(request):
    error = None
    context = {}
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        try:
            response = requests.post(
                BACKEND_URL + "/predict-file/",
                files={"file": (file.name, file.read(), file.content_type)},
                timeout=60,
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
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"error": f"Error al conectar al backend: {str(e)}"}, status=500
            )
    # Renderiza el template solo en GET
    context["error"] = error
    return render(request, "base/upload.html", context)
