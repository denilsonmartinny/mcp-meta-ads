#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Testes para o manipulador Meta Ads.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Importação condicional para evitar erros circulares
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handlers.meta_ads_handler import MetaAdsHandler


@pytest.fixture
def handler():
    """Fixture que fornece uma instância do manipulador."""
    return MetaAdsHandler()


class TestMetaAdsHandler:
    """Testes para o manipulador Meta Ads."""

    @pytest.mark.asyncio
    async def test_handle_connect(self, handler):
        """Testa a operação de conexão."""
        # Substituir o método connect do conector por um mock
        handler.connector.connect = AsyncMock(return_value=True)

        # Chamar o método handle com a operação connect
        result = await handler.handle(
            operation="connect",
            parameters={"credentials": {"app_id": "test_app_id"}},
            context=None
        )

        # Verificar resultado
        assert result["connected"] is True
        assert "message" in result
        
        # Verificar se o mock foi chamado com os parâmetros corretos
        handler.connector.connect.assert_called_once_with({"app_id": "test_app_id"})

    @pytest.mark.asyncio
    async def test_handle_get_campaigns(self, handler):
        """Testa a operação de obtenção de campanhas."""
        # Substituir os métodos necessários por mocks
        handler.connector.connect = AsyncMock(return_value=True)
        handler.connector.get_campaigns = AsyncMock(return_value=[
            {"id": "123", "name": "Campaign 1"},
            {"id": "456", "name": "Campaign 2"}
        ])

        # Chamar o método handle com a operação get_campaigns
        result = await handler.handle(
            operation="get_campaigns",
            parameters={"limit": 10, "status": "ACTIVE"},
            context={"credentials": {"app_id": "test_app_id"}}
        )

        # Verificar resultado
        assert "campaigns" in result
        assert len(result["campaigns"]) == 2
        assert result["count"] == 2
        assert result["parameters"] == {"limit": 10, "status": "ACTIVE"}
        
        # Verificar se os mocks foram chamados corretamente
        handler.connector.connect.assert_called_once()
        handler.connector.get_campaigns.assert_called_once_with({"limit": 10, "status": "ACTIVE"})

    @pytest.mark.asyncio
    async def test_handle_get_ad_sets(self, handler):
        """Testa a operação de obtenção de conjuntos de anúncios."""
        # Substituir os métodos necessários por mocks
        handler.connector.connect = AsyncMock(return_value=True)
        handler.connector.get_ad_sets = AsyncMock(return_value=[
            {"id": "123", "name": "Ad Set 1", "campaign_id": "456"},
            {"id": "789", "name": "Ad Set 2", "campaign_id": "456"}
        ])

        # Chamar o método handle com a operação get_ad_sets
        result = await handler.handle(
            operation="get_ad_sets",
            parameters={"campaign_id": "456", "limit": 10},
            context={"credentials": {"app_id": "test_app_id"}}
        )

        # Verificar resultado
        assert "ad_sets" in result
        assert len(result["ad_sets"]) == 2
        assert result["count"] == 2
        assert result["campaign_id"] == "456"
        
        # Verificar se os mocks foram chamados corretamente
        handler.connector.connect.assert_called_once()
        handler.connector.get_ad_sets.assert_called_once_with("456", {"campaign_id": "456", "limit": 10})

    @pytest.mark.asyncio
    async def test_handle_create_campaign(self, handler):
        """Testa a operação de criação de campanha."""
        # Substituir os métodos necessários por mocks
        handler.connector.connect = AsyncMock(return_value=True)
        handler.connector.create_campaign = AsyncMock(return_value={
            "id": "123",
            "name": "New Campaign",
            "objective": "BRAND_AWARENESS",
            "status": "PAUSED"
        })

        # Dados da campanha
        campaign_data = {
            "name": "New Campaign",
            "objective": "BRAND_AWARENESS",
            "status": "PAUSED"
        }

        # Chamar o método handle com a operação create_campaign
        result = await handler.handle(
            operation="create_campaign",
            parameters=campaign_data,
            context={"credentials": {"app_id": "test_app_id"}}
        )

        # Verificar resultado
        assert "campaign" in result
        assert result["campaign"]["id"] == "123"
        assert result["campaign"]["name"] == "New Campaign"
        assert result["success"] is True
        
        # Verificar se os mocks foram chamados corretamente
        handler.connector.connect.assert_called_once()
        handler.connector.create_campaign.assert_called_once_with(campaign_data)

    @pytest.mark.asyncio
    async def test_handle_disconnect(self, handler):
        """Testa a operação de desconexão."""
        # Substituir o método disconnect do conector por um mock
        handler.connector.disconnect = AsyncMock(return_value=True)

        # Chamar o método handle com a operação disconnect
        result = await handler.handle(
            operation="disconnect",
            parameters={},
            context=None
        )

        # Verificar resultado
        assert result["disconnected"] is True
        assert "message" in result
        
        # Verificar se o mock foi chamado
        handler.connector.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_invalid_operation(self, handler):
        """Testa o tratamento de operação inválida."""
        # Chamar o método handle com uma operação inexistente
        with pytest.raises(ValueError) as excinfo:
            await handler.handle(
                operation="invalid_operation",
                parameters={},
                context=None
            )
        
        # Verificar mensagem de erro
        assert "Operação não suportada" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_connection_failure(self, handler):
        """Testa o tratamento de falha na conexão."""
        # Substituir o método connect do conector para simular falha
        handler.connector.connect = AsyncMock(return_value=False)

        # Chamar o método handle com uma operação que requer conexão
        with pytest.raises(ValueError) as excinfo:
            await handler.handle(
                operation="get_campaigns",
                parameters={},
                context={}
            )
        
        # Verificar mensagem de erro
        assert "Falha ao conectar" in str(excinfo.value)