from django.shortcuts import render
from django.http import JsonResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL", "https://sentiment-api-production-addd.up.railway.app"
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
                f'{BACKEND_URL}/predict-file/',
                files={"file": (file.name, file.read(), file.content_type)},
                timeout=600,
            )
            print("🔗 URL:", response.url)
            if response.status_code == 200:
                context["data"] = response.json()["data"]
                context["predicciones"] = response.json()["predicciones"]
                context["file_name"] = file.name
                # Devuelve solo el contexto como JSON
                return JsonResponse(context)
            else:
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"detail": response.text}
                return JsonResponse(
                    {
                        "error": f"Error en backend ({response.status_code}): {error_data}"
                    },
                    status=response.status_code,
                )
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"error": f"Error al conectar al backend: {str(e)}"}, status=500
            )


    # Renderiza el template solo en GET
    context["error"] = error
    return render(request, "base/upload.html", context)
