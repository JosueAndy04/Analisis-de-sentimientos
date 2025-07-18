import io
import pytest
from django.urls import reverse
from unittest.mock import patch, Mock

@pytest.mark.django_db
def test_upload_file_get(client):
    """Verifica que el formulario de carga se muestre correctamente."""
    url = reverse('upload_file')
    response = client.get(url)
    assert response.status_code == 200
    assert b'<form' in response.content

@pytest.mark.django_db
@patch("base.views.requests.post")
def test_upload_file_post_success(mock_post, client):
    """Verifica que se procesen correctamente las predicciones."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"predicciones": ["positivo", "negativo"]}
    mock_post.return_value = mock_response

    file_content = b"Post Body\nTexto positivo\nTexto negativo\n"
    file = io.BytesIO(file_content)
    file.name = "test.csv"

    url = reverse('upload_file')
    response = client.post(url, {'file': file}, format='multipart')
    assert response.status_code == 200
    assert b'canvas' in response.content  # El template result.html tiene un <canvas>
    assert b'positivo' in response.content or b'negativo' in response.content

@pytest.mark.django_db
@patch("base.views.requests.post")
def test_upload_file_post_error(mock_post, client):
    """Verifica que se muestre un error si el backend responde con error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Archivo inválido"}
    mock_post.return_value = mock_response

    file_content = b"Post Body\n"
    file = io.BytesIO(file_content)
    file.name = "test.csv"

    url = reverse('upload_file')
    response = client.post(url, {'file': file}, format='multipart')
    assert response.status_code == 200
    assert b'Archivo inv' in response.content  # Busca parte del mensaje de error