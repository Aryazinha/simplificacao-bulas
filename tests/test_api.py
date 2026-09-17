import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.main import app

@pytest.fixture
def client():
    # É fundamental usar o TestClient dentro de um bloco 'with' 
    # para acionar os eventos de lifespan (startup/shutdown) do FastAPI,
    # que é onde inicializamos o EasyOCR.
    with patch("easyocr.Reader") as mock_reader:
        mock_instance = MagicMock()
        mock_reader.return_value = mock_instance
        with TestClient(app) as c:
            yield c

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    dados = response.json()
    assert dados["status"] == "ok"
    assert "ocr_loaded" in dados
    assert dados["ocr_loaded"] is True

def test_extrair_texto_sem_arquivo(client):
    # Tentar enviar requisição sem o campo de arquivo
    response = client.post("/api/v1/bula/extrair")
    assert response.status_code == 422

def test_extrair_texto_arquivo_invalido(client):
    # Envia um arquivo txt no lugar de uma imagem
    files = {"file": ("teste.txt", b"conteudo fake", "text/plain")}
    response = client.post("/api/v1/bula/extrair", files=files)
    assert response.status_code == 415
    assert "image" in response.json()["detail"].lower()

@patch("src.api.routers.bula.extrair_texto_da_imagem")
def test_extrair_texto_sucesso(mock_extrair, client):
    mock_extrair.return_value = "Texto simulado do OCR."
    
    # Envia uma imagem fake
    files = {"file": ("bula.jpg", b"fake_image_bytes", "image/jpeg")}
    response = client.post("/api/v1/bula/extrair", files=files)
    
    assert response.status_code == 200
    assert response.json() == {"texto": "Texto simulado do OCR."}

@patch("src.api.routers.bula.extrair_texto_da_imagem")
@patch("src.api.routers.bula.simplificar_texto")
def test_simplificar_bula_sucesso(mock_simplificar, mock_extrair, client):
    # Simulamos o OCR retornando um texto grande
    mock_extrair.return_value = "Texto longo simulado da bula para passar na validacao do tamanho minimo de 50 caracteres."
    
    # Simulamos o LLM retornando um dicionário no formato correto esperado pelo BulaSimplificadaResponse
    mock_bula_json = {
        "medicamento": "Aspirina",
        "para_que_serve": "Dor de cabeça",
        "como_usar": "1 comprimido via oral",
        "contraindicacoes": "Alergia ao ácido acetilsalicílico",
        "efeitos_colaterais": "Náusea, gastrite",
        "disclaimer_medico": "Procure um médico."
    }
    mock_simplificar.return_value = mock_bula_json
    
    files = {"file": ("bula.jpg", b"fake_image_bytes", "image/jpeg")}
    response = client.post("/api/v1/bula/simplificar", files=files)
    
    assert response.status_code == 200
    dados = response.json()
    assert dados["para_que_serve"] == "Dor de cabeça"
    assert "disclaimer_medico" in dados
