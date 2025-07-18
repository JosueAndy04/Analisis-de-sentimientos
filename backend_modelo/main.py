from dotenv import load_dotenv
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import pandas as pd
import re
from collections import Counter
import os

load_dotenv()

HUGGINGFACE_MODEL_ID = os.getenv("HUGGINGFACE_MODEL_ID")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HUGGINGFACE_MODEL_ID or not HF_TOKEN:
    raise RuntimeError(
        "Las variables de entorno HUGGINGFACE_MODEL_ID y HF_TOKEN deben estar definidas."
    )

tokenizer = BertTokenizer.from_pretrained(HUGGINGFACE_MODEL_ID)
model = BertForSequenceClassification.from_pretrained(HUGGINGFACE_MODEL_ID)


app = FastAPI()


class TextInput(BaseModel):
    text: str


MAX_TEXT_LENGTH = 512

LABELS = {0: "negativo", 1: "neutro", 2: "positivo"}


def predict_label(text: str) -> str:
    """
    Realiza la inferencia de sentimiento sobre un texto dado.

    Parámetros:
        text (str): Texto a analizar.

    Retorna:
        str: Etiqueta predicha ('negativo', 'neutro', 'positivo' o 'desconocido').
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
    return LABELS.get(int(predicted_class), "desconocido")


@app.post("/predict")
def predict(input: TextInput):
    """
    Endpoint para predecir el sentimiento de un texto recibido en formato JSON.

    Parámetros:
        input (TextInput): Objeto con el campo 'text' (str).

    Retorna:
        dict: Diccionario con la predicción ('prediction').
    """
    if not input.text or len(input.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")
    if len(input.text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"El texto no puede exceder {MAX_TEXT_LENGTH} caracteres.",
        )
    try:
        label = predict_label(input.text)
        return {"prediction": label}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/read-file/")
async def read_file(file: UploadFile = File(...)):
    """
    Endpoint para leer un archivo CSV o Excel y devolver sus columnas.

    Parámetros:
        file (UploadFile): Archivo subido por el usuario (.csv, .xls, .xlsx).

    Retorna:
        dict: Diccionario con la lista de columnas ('columns').
    """
    try:
        if file.filename and file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename and file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file.file)
        else:
            raise HTTPException(
                status_code=400, detail="Formato de archivo no soportado."
            )
        columns = df.columns.tolist()
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-file/")
async def predict_file(file: UploadFile = File(...)):
    """
    Analiza el archivo, predice sentimientos y prepara datos para gráficas.
    """
    contents = await file.read()
    try:
        if file.filename and file.filename.endswith(".csv"):
            df = pd.read_csv(
                io.BytesIO(contents), keep_default_na=False, na_filter=False
            )
        elif file.filename and file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(
                status_code=400, detail="Formato de archivo no soportado."
            )

        # Limpia los nombres de las columnas
        df.columns = df.columns.str.strip()
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo leer el archivo.")

    # Conversión de tipos de columnas
    int_columns = [
        "Retweets",
        "Likes",
        "Comments",
        "Views",
        "Institucionales",
        "Medios de Comunicación ",
        "General",
        "Bots",
        "Interacciones",
        "Interacciones y Audiencia",
    ]
    str_columns = [
        "Name",
        "Handle",
        "Media URL",
        "Tweet URL",
        "Profile Link",
        "Post Body",
        "Cuenta Verificada",
        "Periodo",
    ]
    date_columns = ["Date", "Timestamp"]

    for col in int_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    for col in str_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Reemplazar valores vacíos en columnas específicas
    for col in ["Institucionales", "Medios de Comunicación", "General", "Bots"]:
        if col in df.columns:
            df[col] = df[col].replace("", 0).fillna(0)

    # Predecir sentimientos
    if "Post Body" not in df.columns:
        raise HTTPException(
            status_code=400, detail="El archivo no contiene la columna 'Post Body'."
        )
    textos = df["Post Body"].tolist()
    results = []
    for text in textos:
        if isinstance(text, str) and text.strip():
            label = predict_label(text)
        else:
            label = "desconocido"
        results.append(label)
    df["Sentimiento"] = results

    # Prepara datos para gráficas
    columns = df.columns.tolist()
    data = {}

    # 1. Top 10 usuarios con mayor Interacciones y Audiencia
    if all(
        col in df.columns for col in ["Name", "Handle", "Interacciones y Audiencia"]
    ):
        top_users = (
            df.groupby(["Name", "Handle"])["Interacciones y Audiencia"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        data["top_users"] = top_users.to_dict(orient="records")

    # 2. Lineplot de conteo de sentimientos por mes y año
    if "Sentimiento" in df.columns and "Date" in df.columns:
        df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
        sentiment_month = (
            df.groupby(["YearMonth", "Sentimiento"]).size().reset_index(name="Conteo")
        )
        data["sentiment_month"] = sentiment_month.to_dict(orient="records")

    # 3. Conteo de sentimientos para gráfico de pastel
    if "Sentimiento" in df.columns:
        sentiment_counts = df["Sentimiento"].value_counts()
        data["sentiment_counts"] = sentiment_counts.to_dict()

    # Estadísticas generales
    data["total_retweets"] = (
        int(df["Retweets"].sum()) if "Retweets" in df.columns else 0
    )
    data["total_likes"] = int(df["Likes"].sum()) if "Likes" in df.columns else 0
    data["total_views"] = int(df["Views"].sum()) if "Views" in df.columns else 0
    data["total_comments"] = (
        int(df["Comments"].sum()) if "Comments" in df.columns else 0
    )

    # Post con más Interacciones y Audiencia (solo los campos solicitados)
    if "Interacciones y Audiencia" in df.columns:
        idx_max = df["Interacciones y Audiencia"].idxmax()
        post_max = df.loc[idx_max].to_dict()
        campos = [
            "Name",
            "Handle",
            "Retweets",
            "Likes",
            "Comments",
            "Views",
            "Post Body",
            "Timestamp",
            "Sentimiento",
        ]
        post_filtrado = {}
        for campo in campos:
            if campo in post_max:
                if campo == "Timestamp" and pd.notna(post_max[campo]):
                    try:
                        fecha = pd.to_datetime(post_max[campo])
                        post_filtrado[campo] = fecha.strftime("%d/%m/%Y")
                    except Exception:
                        post_filtrado[campo] = str(post_max[campo])
                else:
                    post_filtrado[campo] = post_max[campo]
        data["post_max_interacciones"] = post_filtrado

    # Quita la zona horaria de todas las columnas datetime64
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)

    df = df.replace([float("inf"), float("-inf")], float("nan"))
    df = df.fillna("")

    if "post_max_interacciones" in data:
        for k, v in data["post_max_interacciones"].items():
            if pd.isna(v) or v in [float("inf"), float("-inf")]:
                data["post_max_interacciones"][k] = ""

    # Conteo total de cada tipo de cuenta
    conteo_tipo_cuenta = {}
    for col in ["Institucionales", "Medios de Comunicación", "General", "Bots"]:
        if col in df.columns:
            conteo_tipo_cuenta[col] = int(df[col].sum())
    data["conteo_tipo_cuenta"] = conteo_tipo_cuenta

    # Sentimiento por tipo de cuenta (estructura para stacked bar chart)
    tipos = ["Institucionales", "Medios de Comunicación", "General", "Bots"]
    sentimientos = ["positivo", "negativo", "neutro"]
    sentimiento_tipo_cuenta = {}

    for tipo in tipos:
        if tipo in df.columns:
            cuenta = {}
            for sent in sentimientos:
                cuenta[sent] = int(
                    df[(df[tipo] > 0) & (df["Sentimiento"] == sent)].shape[0]
                )
            sentimiento_tipo_cuenta[tipo] = cuenta

    data["sentimiento_tipo_cuenta"] = sentimiento_tipo_cuenta

    # Palabras más frecuentes en "Post Body"
    if "Post Body" in df.columns:
        # Une todos los textos en uno solo
        all_text = " ".join(df["Post Body"].dropna().astype(str)).lower()
        # Elimina signos de puntuación y separa por palabras
        words = re.findall(r"\b\w+\b", all_text)
        # Puedes excluir stopwords si lo deseas
        stopwords = set(
            [
                "de",
                "la",
                "que",
                "el",
                "en",
                "y",
                "a",
                "los",
                "del",
                "se",
                "las",
                "por",
                "un",
                "para",
                "con",
                "no",
                "una",
                "su",
                "al",
                "es",
                "lo",
                "como",
                "más",
                "pero",
                "sus",
                "le",
                "ya",
                "o",
                "este",
                "sí",
                "porque",
                "esta",
                "entre",
                "cuando",
                "muy",
                "sin",
                "sobre",
                "también",
                "me",
                "hasta",
                "hay",
                "donde",
                "quien",
                "desde",
                "todo",
                "nos",
                "durante",
                "todos",
                "uno",
                "les",
                "ni",
                "contra",
                "otros",
                "ese",
                "eso",
                "ante",
                "ellos",
                "e",
                "esto",
                "mí",
                "antes",
                "algunos",
                "qué",
                "unos",
                "yo",
                "otro",
                "otras",
                "otra",
                "él",
                "tanto",
                "esa",
                "estos",
                "mucho",
                "quienes",
                "nada",
                "muchos",
                "cual",
                "poco",
                "ella",
                "estar",
                "estas",
                "algunas",
                "algo",
                "nosotros",
                "mi",
                "mis",
                "tú",
                "te",
                "ti",
                "tu",
                "tus",
                "ellas",
                "nosotras",
                "vosotros",
                "vosotras",
                "os",
                "mío",
                "mía",
                "míos",
                "mías",
                "tuyo",
                "tuya",
                "tuyos",
                "tuyas",
                "suyo",
                "suya",
                "suyos",
                "suyas",
                "nuestro",
                "nuestra",
                "nuestros",
                "nuestras",
                "vuestro",
                "vuestra",
                "vuestros",
                "vuestras",
                "esos",
                "esas",
                "estoy",
                "estás",
                "está",
                "estamos",
                "estáis",
                "están",
                "esté",
                "estés",
                "estemos",
                "estéis",
                "estén",
                "estaré",
                "estarás",
                "estará",
                "estaremos",
                "estaréis",
                "estarán",
                "estaría",
                "estarías",
                "estaríamos",
                "estaríais",
                "estarían",
                "estaba",
                "estabas",
                "estábamos",
                "estabais",
                "estaban",
                "estuve",
                "estuviste",
                "estuvo",
                "estuvimos",
                "estuvisteis",
                "estuvieron",
                "estuviera",
                "estuvieras",
                "estuviéramos",
                "estuvierais",
                "estuvieran",
                "estuviese",
                "estuvieses",
                "estuviésemos",
                "estuvieseis",
                "estuviesen",
                "estando",
                "estado",
                "estada",
                "estados",
                "estadas",
                "estad",
                "http",
                "https",
                "www",
                "com",
                "co",
                "org",
                "net",
                "es",
                "bin",
                "bit",
                "cada",
                "asi",
                "así",
                "solo",
                "sólo",
                "si",
                "tras",
            ]
        )
        filtered_words = [w for w in words if w not in stopwords and len(w) > 2]
        word_counts = Counter(filtered_words).most_common(20)  # Top 20
        data["top_words"] = word_counts

    return {
        "predicciones": df["Sentimiento"].tolist(),
        "data": data,
        "columns": columns,
    }
