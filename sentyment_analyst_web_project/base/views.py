from django.shortcuts import render
from django.http import JsonResponse
import requests
import os
import time
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

        # 🔍 Debug del archivo recibido
        print("📂 Archivo recibido en Django:")
        print(f"   Nombre: {file.name}")
        print(f"   Tipo: {file.content_type}")
        print(f"   Tamaño: {file.size} bytes")
        print(f"{BACKEND_URL}/predict-file/")

        # 🔄 Reiniciar puntero por si se leyó antes
        file.seek(0)

        try:
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/predict-file/",
                files={"file": (file.name, file.read(), file.content_type)},
                timeout=60,  # ⏳ baja a 60s para ver si hay timeouts más claros
            )
            duration = time.time() - start_time

            # 🔍 Debug de la respuesta
            print("🔗 URL llamada:", response.url)
            print(f"⏱️ Tiempo de respuesta: {duration:.2f}s")
            print("📡 Status Code:", response.status_code)

            try:
                print("📨 Respuesta JSON:", response.json())
            except Exception:
                print("📨 Respuesta cruda:", response.text[:500])  # solo primeros 500 chars

            if response.status_code == 200:
                data = response.json()
                context["data"] = data.get("data")
                context["predicciones"] = data.get("predicciones")
                context["file_name"] = file.name
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

        except requests.exceptions.Timeout:
            print("⏳ ERROR: El backend no respondió en el tiempo límite (timeout)")
            return JsonResponse(
                {"error": "El backend tardó demasiado en responder (timeout)"},
                status=504,
            )
        except requests.exceptions.RequestException as e:
            print("❌ ERROR de conexión con el backend:", str(e))
            return JsonResponse(
                {"error": f"Error al conectar al backend: {str(e)}"}, status=500
            )

    # Renderiza el template solo en GET
    context["error"] = error
    return render(request, "base/upload.html", context)
