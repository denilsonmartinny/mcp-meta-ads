#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Manipulador para solicitações relacionadas ao Meta Ads.
"""

import logging
from typing import Dict, Any, List, Optional

from .base_handler import BaseHandler
from ..connectors.meta_ads_connector import MetaAdsConnector

logger = logging.getLogger(__name__)

class MetaAdsHandler(BaseHandler):
    """
    Manipulador para processar solicitações relacionadas ao Meta Ads.
    """
    
    def __init__(self):
        """Inicializa o manipulador Meta Ads."""
        super().__init__()
        self.connector = MetaAdsConnector()
    
    async def handle(self, operation: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Manipula uma operação Meta Ads.
        
        Args:
            operation: Nome da operação a ser executada
            parameters: Parâmetros da operação
            context: Contexto adicional (opcional)
            
        Returns:
            Resultado da operação
        """
        # Verificar se é necessário conectar primeiro
        if operation != "connect" and not self._is_test_mode(context):
            await self._ensure_connected(parameters, context)
        
        # Mapear operação para método
        operation_map = {
            "connect": self._handle_connect,
            "disconnect": self._handle_disconnect,
            "get_campaigns": self._handle_get_campaigns,
            "get_ad_sets": self._handle_get_ad_sets,
            "get_ads": self._handle_get_ads,
            "create_campaign": self._handle_create_campaign,
            "update_campaign": self._handle_update_campaign,
            "get_insights": self._handle_get_insights,
        }
        
        if operation not in operation_map:
            raise ValueError(f"Operação não suportada: {operation}")
        
        handler_method = operation_map[operation]
        return await handler_method(parameters, context)
    
    async def _ensure_connected(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> None:
        """
        Garante que o conector esteja conectado antes de executar operações.
        
        Args:
            parameters: Parâmetros da operação
            context: Contexto adicional (opcional)
        """
        credentials = {}
        
        # Obter credenciais do contexto, se disponível
        if context and "credentials" in context:
            credentials = context["credentials"]
        
        # Se não houver credenciais no contexto, usar credenciais de ambiente
        connected = await self.connector.connect(credentials)
        
        if not connected:
            raise ValueError("Falha ao conectar à API do Meta Ads. Verifique as credenciais.")
    
    def _is_test_mode(self, context: Optional[Dict[str, Any]]) -> bool:
        """
        Verifica se estamos em modo de teste.
        
        Args:
            context: Contexto adicional
            
        Returns:
            bool: Verdadeiro se estiver em modo de teste
        """
        return context and context.get("test_mode", False)
    
    async def _handle_connect(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manipula a operação de conexão.
        
        Args:
            parameters: Credenciais para conexão
            context: Contexto adicional (opcional)
            
        Returns:
            Status da conexão
        """
        credentials = parameters.get("credentials", {})
        success = await self.connector.connect(credentials)
        
        return {
            "connected": success,
            "message": "Conectado com sucesso" if success else "Falha na conexão"
        }
    
    async def _handle_disconnect(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manipula a operação de desconexão.
        
        Args:
            parameters: Parâmetros (não utilizados)
            context: Contexto adicional (opcional)
            
        Returns:
            Status da desconexão
        """
        success = await self.connector.disconnect()
        
        return {
            "disconnected": success,
            "message": "Desconectado com sucesso" if success else "Falha na desconexão"
        }
    
    async def _handle_get_campaigns(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manipula a operação de obtenção de campanhas.
        
        Args:
            parameters: Parâmetros para filtragem
            context: Contexto adicional (opcional)
            
        Returns:
            Lista de campanhas e metadados
        """
        campaigns = await self.connector.get_campaigns(parameters)
        
        return {
            "campaigns": campaigns,
            "count": len(campaigns),
            "parameters": parameters
        }
    
    async def _handle_get_ad_sets(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manipula a operação de obtenção de conjuntos de anúncios.
        
        Args:
            parameters: Parâmetros para filtragem
            context: Contexto adicional (opcional)
            
        Returns:
            Lista de conjuntos de anúncios e metadados
        """
        campaign_id = parameters.get("campaign_id")
        ad_sets = await self.connector.get_ad_sets(campaign_id, parameters)
        
        return {
            "ad_sets": ad_sets,
            "count": len(ad_sets),
            "campaign_id": campaign_id,
            "parameters": parameters
        }
    
    async def _handle_get_ads(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manipula a operação de obtenção de anúncios.
        
        Args:
            parameters: Parâmetros para filtragem
            context: Contexto adicional (opcional)
            
        Returns:
            Lista de anúncios e metadados
        """
        # Implementação futura
        raise NotImplementedError("Operação get_ads ainda não implementada")
    
    async def _handle_create_campaign(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manipula a operação de criação de campanha.
        
        Args:
            parameters: Dados da campanha
            context: Contexto adicional (opcional)
            
        Returns:
            Detalhes da campanha criada
        """
        result = await self.connector.create_campaign(parameters)
        
        return {
            "campaign": result,
            "success": True,
            "message": "Campanha criada com sucesso"
        }
    
    async def _handle_update_campaign(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manipula a operação de atualização de campanha.
        
        Args:
            parameters: Dados da campanha
            context: Contexto adicional (opcional)
            
        Returns:
            Detalhes da campanha atualizada
        """
        # Implementação futura
        raise NotImplementedError("Operação update_campaign ainda não implementada")
    
    async def _handle_get_insights(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manipula a operação de obtenção de insights.