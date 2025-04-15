#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Testes para o servidor MCP principal.
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Importação condicional para evitar erros circulares
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import app


@pytest.fixture
def client():
    """Fixture que fornece um cliente de teste."""
    return TestClient(app)


@pytest.fixture
def mock_token():
    """Fixture para simular um token válido."""
    with patch("src.middleware.authentication.verify_token", return_value="test_token"):
        yield "test_token"


class TestServer:
    """Testes para o servidor MCP."""

    def test_health_check(self, client):
        """Testa o endpoint de verificação de saúde."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "message": "MCP Server está funcionando"}

    @patch("src.handlers.meta_ads_handler.MetaAdsHandler.handle")
    def test_meta_ads_request(self, mock_handle, client, mock_token):
        """Testa o endpoint de solicitação para Meta Ads."""
        # Configurar o mock para retornar um resultado simulado
        mock_result = {"campaigns": [{"id": "123", "name": "Test Campaign"}]}
        mock_handle.return_value = mock_result

        # Enviar solicitação
        response = client.post(
            "/api/v1/meta-ads",
            headers={"Authorization": f"Bearer {mock_token}"},
            json={
                "operation": "get_campaigns",
                "parameters": {"limit": 10},
                "context": None
            }
        )

        # Verificar resposta
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["status"] == "success"
        assert json_response["data"] == mock_result
        
        # Verificar se o manipulador foi chamado com os parâmetros corretos
        mock_handle.assert_called_once_with("get_campaigns", {"limit": 10}, None)

    def test_meta_ads_request_invalid(self, client, mock_token):
        """Testa o endpoint de solicitação para Meta Ads com dados inválidos."""
        # Enviar solicitação inválida (sem operação)
        response = client.post(
            "/api/v1/meta-ads",
            headers={"Authorization": f"Bearer {mock_token}"},
            json={
                "parameters": {"limit": 10},
                "context": None
            }
        )

        # Verificar se a validação falhou
        assert response.status_code == 422  # Unprocessable Entity

    @patch("src.handlers.meta_ads_handler.MetaAdsHandler.handle")
    def test_meta_ads_request_error(self, mock_handle, client, mock_token):
        """Testa o tratamento de erros no endpoint de Meta Ads."""
        # Configurar o mock para lançar uma exceção
        mock_handle.side_effect = ValueError("Operação inválida")

        # Enviar solicitação
        response = client.post(
            "/api/v1/meta-ads",
            headers={"Authorization": f"Bearer {mock_token}"},
            json={
                "operation": "invalid_operation",
                "parameters": {},
                "context": None
            }
        )

        # Verificar resposta de erro
        assert response.status_code == 400  # Bad Request
        json_response = response.json()
        assert "detail" in json_response
        assert json_response["detail"] == "Operação inválida"

    def test_unauthorized_request(self, client):
        """Testa solicitação sem token de autenticação."""
        # Enviar solicitação sem cabeçalho de autorização
        response = client.post(
            "/api/v1/meta-ads",
            json={
                "operation": "get_campaigns",
                "parameters": {},
                "context": None
            }
        )

        # Verificar resposta de não autorizado
        assert response.status_code == 401  # Unauthorized