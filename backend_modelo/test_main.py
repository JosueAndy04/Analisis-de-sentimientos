from fastapi.testclient import TestClient
from main import app
import io
import pandas as pd

client = TestClient(app)

def test_predict_ok():
    response = client.post("/predict", json={"text": "Este es un texto de prueba."})
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_predict_empty_text():
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "El texto no puede estar vacío."

def test_predict_long_text():
    long_text = "a" * 600
    response = client.post("/predict", json={"text": long_text})
    assert response.status_code == 400
    assert "no puede exceder" in response.json()["detail"]

def test_read_file_csv_columns():
    # Crear un CSV en memoria
    csv_content = "Post Body,OtraColumna\nTexto de prueba,123\n"
    file = io.BytesIO(csv_content.encode("utf-8"))
    response = client.post(
        "/read-file/",
        files={"file": ("test.csv", file, "text/csv")},
    )
    assert response.status_code == 200
    assert "columns" in response.json()
    assert "Post Body" in response.json()["columns"]

def test_read_file_xlsx_columns():
    # Crear un Excel en memoria
    df = pd.DataFrame({"Post Body": ["Texto"], "OtraColumna": [1]})
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    response = client.post(
        "/read-file/",
        files={"file": ("test.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    assert "columns" in response.json()
    assert "Post Body" in response.json()["columns"]

def test_predict_file_csv():
    csv_content = "Post Body\nTexto positivo\nTexto negativo\n\n"
    file = io.BytesIO(csv_content.encode("utf-8"))
    response = client.post(
        "/predict-file/",
        files={"file": ("test.csv", file, "text/csv")},
    )
    assert response.status_code == 200
    assert "predicciones" in response.json()
    assert len(response.json()["predicciones"]) == 2

def test_predict_file_no_post_body():
    csv_content = "OtraColumna\nTexto\n"
    file = io.BytesIO(csv_content.encode("utf-8"))
    response = client.post(
        "/predict-file/",
        files={"file": ("test.csv", file, "text/csv")},
    )
    assert response.status_code == 400
    assert "no contiene la columna" in response.json()["detail"]