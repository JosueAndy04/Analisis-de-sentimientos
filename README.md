# 🧠 Análisis de Sentimientos con Django + FastAPI

Este proyecto implementa un **sistema de análisis de sentimientos** a partir de texto o archivos (CSV/Excel).  
Consta de dos partes principales:

1. **Frontend (Django)** → Interfaz web donde el usuario carga el archivo o texto.
2. **Backend (FastAPI + Transformers)** → Expone una API REST que procesa el texto y devuelve el análisis de sentimientos.

---

## 🚀 Tecnologías usadas

- **Frontend**: Django 5, JavaScript (fetch API).
- **Backend**: FastAPI, Transformers (HuggingFace), PyTorch.
- **Servidor**: Gunicorn + Uvicorn workers.
- **Despliegue**: Render / Railway.

---

## 📂 Estructura del proyecto
```
.
├── backend_modelo/ # Servicio FastAPI (modelo de sentimientos)
│ ├── __init__.py #
│ ├── main.py # Código principal de la API
│ ├── .env.example # Ejemplo de variables de entorno
│ 
├── sentiment_analyst/ # Proyecto Django (frontend)
│ ├── base/ # App con templates y vistas
│ └── templates/ # Templates HTML
│
│ ├── sentyment_analyst_web_project/ # App con templates y vistas
│ └── settings.py # Configuración (producción/local)
│
│ ├── static/ # Archivos estáticos (JS, CSS)
│ ├── staticfiles/ # Archivos estáticos (JS, CSS)
│ ├── manage.py # Archivo de arranque (producción/local)
│ ├── requirements.txt # Dependencias del frontend
│ ├── .env.example # Ejemplo de variables de entorno
│
├── requirements.txt # Dependencias
├── README.md
```
---

## ⚙️ Configuración local

### 1️⃣ Clonar repositorio
```
git clone https://github.com/JosueAndy04/Analisis-de-sentimientos.git
cd Analisis-de-sentimientos
```

### 2️⃣ Crear entornos virtuales
Para cada servicio (frontend y backend):

# Backend
```
cd backend_modelo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
# Frontend
```
cd ../sentiment_analyst
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3️⃣ Variables de entorno
Crear un archivo .env en la raíz del proyecto (o en cada servicio). Ejemplo:
```
.env
```
# Backend
```
HUGGINGFACE_MODEL_ID=tu-modelo-en-hf
HF_TOKEN=tu-token-hf
```
# Frontend
```
SECRET_KEY=django-secret-key
DEBUG=False
ALLOWED_HOSTS=analisis-de-sentimientos-tcpb.onrender.com
BACKEND_URL=https://sentiment-api-production-addd.up.railway.app
```
### 4️⃣ Correr backend (FastAPI)
```
cd backend_modelo
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Accede a la API docs: http://127.0.0.1:8000/docs

### 5️⃣ Correr frontend (Django)
```
cd sentiment_analyst
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```
Abre: http://127.0.0.1:8001

## ☁️ Despliegue en Producción
🔹 Backend (FastAPI en Railway)
Subir el directorio backend_modelo/.

Configurar las variables de entorno en Railway:

- HUGGINGFACE_MODEL_ID
- HF_TOKEN
- PORT (lo asigna Railway automáticamente).

Comando de arranque:

```
cd backend_modelo && gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 2 \
  --threads 2 \
  --timeout 2000 \
  --bind 0.0.0.0:$PORT
```
🔹 Frontend (Django en Render)
Subir el directorio sentiment_analyst/.

Configurar las variables de entorno:
- SECRET_KEY
- DEBUG=False
- ALLOWED_HOSTS=analisis-de-sentimientos-tcpb.onrender.com
- BACKEND_URL=https://sentiment-api-production-addd.up.railway.app

Configuración render.yaml ejemplo:

```
services:
  - type: web
    name: django-frontend
    env: python
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --noinput"
    startCommand: "gunicorn sentiment_analyst.wsgi --timeout 2400 --bind 0.0.0.0:$PORT"
```
## 📊 Endpoints del Backend
- POST /predict → recibe texto y devuelve sentimiento.
- POST /read-file/ → recibe un archivo CSV/Excel y devuelve columnas.
- POST /predict-file/ → recibe CSV/Excel y devuelve:

  - Predicciones por fila.
  - Datos agregados para gráficas.
  - Conteos de sentimientos.

---
## 🛠️ Debug y Testing

Ver logs en producción
# Railway
railway logs

# Render
render logs

---
📌 Notas importantes
- Cada worker de Gunicorn carga una copia del modelo → no excedas los recursos de tu servidor.
- Usa --workers y --threads según la RAM disponible. Ejemplo en Railway (8 GB RAM): --workers 2 --threads 2.
- collectstatic es obligatorio en producción (Django + whitenoise).
- Recuerda que el frontend y backend deben comunicarse vía HTTPS en producción.

