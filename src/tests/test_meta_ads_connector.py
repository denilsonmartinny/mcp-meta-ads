#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Testes para o conector Meta Ads.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Importação condicional para evitar erros circulares
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connectors.meta_ads_connector import MetaAdsConnector


@pytest.fixture
def connector():
    """Fixture que fornece uma instância do conector."""
    return MetaAdsConnector()


class TestMetaAdsConnector:
    """Testes para o conector Meta Ads."""

    @pytest.mark.asyncio
    @patch("facebook_business.api.FacebookAdsApi.init")
    @patch("facebook_business.adobjects.adaccount.AdAccount")
    async def test_connect_success(self, mock_adaccount, mock_api_init, connector):
        """Testa conexão bem-sucedida à API do Meta Ads."""
        # Configurar mocks
        mock_account = MagicMock()
        mock_adaccount.return_value = mock_account
        mock_api_init.return_value = MagicMock()

        # Credenciais de teste
        credentials = {
            "app_id": "test_app_id",
            "app_secret": "test_app_secret",
            "access_token": "test_access_token",
            "account_id": "test_account_id"
        }

        # Testar conexão
        result = await connector.connect(credentials)

        # Verificar resultado
        assert result is True
        
        # Verificar chamadas de mock
        mock_api_init.assert_called_once_with(
            "test_app_id", "test_app_secret", "test_access_token"
        )
        mock_adaccount.assert_called_once_with("act_test_account_id")
        mock_account.api_get.assert_called_once_with(fields=["name", "account_status"])

    @pytest.mark.asyncio
    @patch("facebook_business.api.FacebookAdsApi.init")
    async def test_connect_missing_credentials(self, mock_api_init, connector):
        """Testa conexão com credenciais incompletas."""
        # Credenciais incompletas
        credentials = {
            "app_id": "test_app_id",
            # app_secret faltando
            "access_token": "test_access_token",
            "account_id": "test_account_id"
        }

        # Testar conexão
        result = await connector.connect(credentials)

        # Verificar resultado
        assert result is False
        
        # Verificar que a API não foi inicializada
        mock_api_init.assert_not_called()

    @pytest.mark.asyncio
    @patch("facebook_business.api.FacebookAdsApi.init")
    @patch("facebook_business.adobjects.adaccount.AdAccount")
    async def test_connect_api_error(self, mock_adaccount, mock_api_init, connector):
        """Testa tratamento de erro da API durante a conexão."""
        # Configurar mocks para simular erro
        mock_account = MagicMock()
        mock_account.api_get.side_effect = Exception("API Error")
        mock_adaccount.return_value = mock_account
        mock_api_init.return_value = MagicMock()

        # Credenciais de teste
        credentials = {
            "app_id": "test_app_id",
            "app_secret": "test_app_secret",
            "access_token": "test_access_token",
            "account_id": "test_account_id"
        }

        # Testar conexão
        result = await connector.connect(credentials)

        # Verificar resultado
        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect(self, connector):
        """Testa desconexão da API."""
        # Configurar o estado do conector
        connector._api = MagicMock()
        connector._account_id = "test_account_id"

        # Testar desconexão
        result = await connector.disconnect()

        # Verificar resultado
        assert result is True
        assert connector._api is None
        assert connector._account_id is None

    @pytest.mark.asyncio
    @patch("facebook_business.adobjects.adaccount.AdAccount")
    async def test_get_campaigns(self, mock_adaccount, connector):
        """Testa obtenção de campanhas."""
        # Configurar mocks
        mock_account = MagicMock()
        mock_campaigns = [
            MagicMock(export_all_data=lambda: {"id": "123", "name": "Campaign 1"}),
            MagicMock(export_all_data=lambda: {"id": "456", "name": "Campaign 2"})
        ]
        mock_account.get_campaigns.return_value = mock_campaigns
        mock_adaccount.return_value = mock_account

        # Configurar estado do conector
        connector._api = MagicMock()
        connector._account_id = "test_account_id"

        # Testar obtenção de campanhas
        params = {"limit": 10, "status": "ACTIVE"}
        results = await connector.get_campaigns(params)

        # Verificar resultados
        assert len(results) == 2
        assert results[0]["id"] == "123"
        assert results[1]["name"] == "Campaign 2"
        
        # Verificar chamadas de mock
        mock_adaccount.assert_called_once_with("act_test_account_id")
        mock_account.get_campaigns.assert_called_once()
        # Verificar parâmetros corretos
        args, kwargs = mock_account.get_campaigns.call_args
        assert "fields" in kwargs
        assert "params" in kwargs
        assert kwargs["params"]["limit"] == 10
        assert kwargs["params"]["effective_status"] == "ACTIVE"

    @pytest.mark.asyncio
    async def test_get_campaigns_not_connected(self, connector):
        """Testa obtenção de campanhas sem conexão."""
        # Garantir que o conector não está conectado
        connector._api = None

        # Tentar obter campanhas
        with pytest.raises(ValueError) as excinfo:
            await connector.get_campaigns({})
        
        # Verificar mensagem de erro
        assert "Não conectado à API do Meta Ads" in str(excinfo.value)

    @pytest.mark.asyncio
    @patch("facebook_business.adobjects.adaccount.AdAccount")
    async def test_get_ad_sets(self, mock_adaccount, connector):
        """Testa obtenção de conjuntos de anúncios."""
        # Configurar mocks
        mock_account = MagicMock()
        mock_ad_sets = [
            MagicMock(export_all_data=lambda: {"id": "123", "name": "Ad Set 1", "campaign_id": "456"}),
            MagicMock(export_all_data=lambda: {"id": "789", "name": "Ad Set 2", "campaign_id": "456"})
        ]
        mock_account.get_ad_sets.return_value = mock_ad_sets
        mock_adaccount.return_value = mock_account

        # Configurar estado do conector
        connector._api = MagicMock()
        connector._account_id = "test_account_id"

        # Testar obtenção de conjuntos de anúncios
        campaign_id = "456"
        params = {"limit": 10}
        results = await connector.get_ad_sets(campaign_id, params)

        # Verificar resultados
        assert len(results) == 2
        assert results[0]["id"] == "123"
        assert results[1]["campaign_id"] == "456"
        
        # Verificar chamadas de mock
        mock_adaccount.assert_called_once_with("act_test_account_id")
        mock_account.get_ad_sets.assert_called_once()
        # Verificar parâmetros corretos
        args, kwargs = mock_account.get_ad_sets.call_args
        assert "fields" in kwargs
        assert "params" in kwargs
        assert kwargs["params"]["campaign_id"] == "456"
        assert kwargs["params"]["limit"] == 10

    @pytest.mark.asyncio
    @patch("facebook_business.adobjects.adaccount.AdAccount")
    async def test_create_campaign(self, mock_adaccount, connector):
        """Testa criação de campanha."""
        # Configurar mocks
        mock_account = MagicMock()
        mock_campaign = MagicMock()
        mock_campaign.export_all_data.return_value = {
            "id": "123",
            "name": "New Campaign",
            "objective": "BRAND_AWARENESS",
            "status": "PAUSED"
        }
        mock_account.create_campaign.return_value = {"id": "123"}
        mock_adaccount.return_value = mock_account

        # Mock para Campaign.api_get
        with patch("facebook_business.adobjects.campaign.Campaign") as mock_campaign_class:
            mock_campaign_instance = MagicMock()
            mock_campaign_instance.api_get.return_value = mock_campaign
            mock_campaign_class.return_value = mock_campaign_instance

            # Configurar estado do conector
            connector._api = MagicMock()
            connector._account_id = "test_account_id"

            # Dados da campanha
            campaign_data = {
                "name": "New Campaign",
                "objective": "BRAND_AWARENESS",
                "status": "PAUSED"
            }

            # Testar criação de campanha
            result = await connector.create_campaign(campaign_data)

            # Verificar resultado
            assert result["id"] == "123"
            assert result["name"] == "New Campaign"
            assert result["objective"] == "BRAND_AWARENESS"
            
            # Verificar chamadas de mock
            mock_adaccount.assert_called_once_with("act_test_account_id")
            mock_account.create_campaign.assert_called_once()
            mock_campaign_class.assert_called_once_with("123")
            mock_campaign_instance.api_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_campaign_missing_fields(self, connector):
        """Testa criação de campanha com campos obrigatórios ausentes."""
        # Configurar estado do conector
        connector._api = MagicMock()
        connector._account_id = "test_account_id"

        # Dados incompletos da campanha
        campaign_data = {
            "name": "New Campaign",
            # objective faltando
            "status": "PAUSED"
        }

        # Tentar criar campanha
        with pytest.raises(ValueError) as excinfo:
            await connector.create_campaign(campaign_data)
        
        # Verificar mensagem de erro
        assert "Campo obrigatório ausente" in str(excinfo.value)

    @pytest.mark.asyncio
    @patch("facebook_business.adobjects.campaign.Campaign")
    async def test_get_insights(self, mock_campaign, connector):
        """Testa obtenção de insights."""
        # Configurar mocks
        mock_campaign_instance = MagicMock()
        mock_insights = [
            MagicMock(export_all_data=lambda: {"impressions": 1000, "clicks": 50}),
            MagicMock(export_all_data=lambda: {"impressions": 1200, "clicks": 60})
        ]
        mock_campaign_instance.get_insights.return_value = mock_insights
        mock_campaign.return_value = mock_campaign_instance

        # Configurar estado do conector
        connector._api = MagicMock()

        # Testar obtenção de insights
        object_id = "123"
        object_type = "campaign"
        params = {
            "time_range": {"since": "2025-01-01", "until": "2025-01-31"},
            "time_increment": 1
        }
        
        results = await connector.get_insights(object_id, object_type, params)

        # Verificar resultados
        assert len(results) == 2
        assert results[0]["impressions"] == 1000
        assert results[1]["clicks"] == 60
        
        # Verificar chamadas de mock
        mock_campaign.assert_called_once_with("123")
        mock_campaign_instance.get_insights.assert_called_once()
        # Verificar parâmetros corretos
        args, kwargs = mock_campaign_instance.get_insights.call_args
        assert "fields" in kwargs
        assert "params" in kwargs
        assert kwargs["params"]["time_range"] == {"since": "2025-01-01", "until": "2025-01-31"}
        assert kwargs["params"]["time_increment"] == 1

    @pytest.mark.asyncio
    async def test_get_insights_invalid_object_type(self, connector):
        """Testa obtenção de insights com tipo de objeto inválido."""
        # Configurar estado do conector
        connector._api = MagicMock()

        # Tentar obter insights com tipo inválido
        with pytest.raises(ValueError) as excinfo:
            await connector.get_insights("123", "invalid_type", {})
        
        # Verificar mensagem de erro
        assert "Tipo de objeto inválido" in str(excinfo.value)