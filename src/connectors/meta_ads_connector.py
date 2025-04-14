#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Conector para a API do Meta Ads.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad

from .base_connector import BaseConnector

logger = logging.getLogger(__name__)

class MetaAdsConnector(BaseConnector):
    """Conector para interagir com a API do Meta Ads (Facebook Ads)."""
    
    def __init__(self):
        """Inicializa o conector Meta Ads."""
        super().__init__()
        self._api = None
        self._account_id = None
    
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Conecta à API do Meta Ads usando as credenciais fornecidas.
        
        Args:
            credentials: Dicionário contendo app_id, app_secret, access_token e account_id
            
        Returns:
            bool: Verdadeiro se a conexão for bem-sucedida, falso caso contrário
        """
        try:
            app_id = credentials.get('app_id') or os.getenv('META_APP_ID')
            app_secret = credentials.get('app_secret') or os.getenv('META_APP_SECRET')
            access_token = credentials.get('access_token') or os.getenv('META_ACCESS_TOKEN')
            self._account_id = credentials.get('account_id') or os.getenv('META_ACCOUNT_ID')
            
            if not all([app_id, app_secret, access_token, self._account_id]):
                logger.error("Credenciais de API incompletas")
                return False
            
            # Inicializar a API
            self._api = FacebookAdsApi.init(app_id, app_secret, access_token)
            
            # Verificar se podemos acessar a conta
            account = AdAccount(f'act_{self._account_id}')
            account.api_get(fields=['name', 'account_status'])
            
            logger.info(f"Conectado à conta Meta Ads: {self._account_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar à API do Meta Ads: {e}", exc_info=True)
            return False
    
    async def get_campaigns(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Obtém campanhas da conta.
        
        Args:
            params: Parâmetros para filtragem (status, limit, etc.)
            
        Returns:
            Lista de campanhas
        """
        if not self._api:
            raise ValueError("Não conectado à API do Meta Ads")
        
        try:
            account = AdAccount(f'act_{self._account_id}')
            fields = ['id', 'name', 'objective', 'status', 'created_time', 'updated_time', 'daily_budget', 'lifetime_budget']
            params_dict = {}
            
            # Aplicar filtros se fornecidos
            if 'status' in params:
                params_dict['effective_status'] = params['status']
            if 'limit' in params:
                params_dict['limit'] = params['limit']
            
            campaigns = account.get_campaigns(
                fields=fields,
                params=params_dict
            )
            
            return [campaign.export_all_data() for campaign in campaigns]
            
        except Exception as e:
            logger.error(f"Erro ao obter campanhas: {e}", exc_info=True)
            raise
    
    async def get_ad_sets(self, campaign_id: Optional[str] = None, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Obtém conjuntos de anúncios.
        
        Args:
            campaign_id: ID da campanha (opcional)
            params: Parâmetros adicionais
            
        Returns:
            Lista de conjuntos de anúncios
        """
        if not self._api:
            raise ValueError("Não conectado à API do Meta Ads")
        
        try:
            account = AdAccount(f'act_{self._account_id}')
            fields = ['id', 'name', 'campaign_id', 'status', 'targeting', 'daily_budget', 'lifetime_budget', 'start_time', 'end_time']
            params_dict = {}
            
            if params:
                if 'status' in params:
                    params_dict['effective_status'] = params['status']
                if 'limit' in params:
                    params_dict['limit'] = params['limit']
            
            if campaign_id:
                # Filtrar por campanha específica
                params_dict['campaign_id'] = campaign_id
            
            ad_sets = account.get_ad_sets(
                fields=fields,
                params=params_dict
            )
            
            return [ad_set.export_all_data() for ad_set in ad_sets]
            
        except Exception as e:
            logger.error(f"Erro ao obter conjuntos de anúncios: {e}", exc_info=True)
            raise
    
    async def create_campaign(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova campanha.
        
        Args:
            data: Dados da campanha a ser criada
            
        Returns:
            Detalhes da campanha criada
        """
        if not self._api:
            raise ValueError("Não conectado à API do Meta Ads")
        
        try:
            account = AdAccount(f'act_{self._account_id}')
            
            # Configurar campos necessários
            required_fields = ['name', 'objective', 'status']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Campo obrigatório ausente: {field}")
            
            # Criar campanha
            campaign = account.create_campaign(
                params={
                    'name': data['name'],
                    'objective': data['objective'],
                    'status': data['status'],
                    'special_ad_categories': data.get('special_ad_categories', []),
                }
            )
            
            # Buscar detalhes da campanha criada
            campaign_id = campaign['id']
            result = Campaign(campaign_id).api_get(
                fields=['id', 'name', 'objective', 'status', 'created_time']
            )
            
            return result.export_all_data()
            
        except Exception as e:
            logger.error(f"Erro ao criar campanha: {e}", exc_info=True)
            raise
    
    async def get_insights(self, object_id: str, object_type: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Obtém insights de performance para um objeto específico.
        
        Args:
            object_id: ID do objeto (campanha, conjunto de anúncios, anúncio)
            object_type: Tipo do objeto ('campaign', 'adset', 'ad')
            params: Parâmetros para filtragem e configuração
            
        Returns:
            Lista de insights
        """
        if not self._api:
            raise ValueError("Não conectado à API do Meta Ads")
        
        try:
            # Mapear tipo de objeto para a classe correta
            obj_map = {
                'campaign': Campaign,
                'adset': AdSet,
                'ad': Ad
            }
            
            if object_type not in obj_map:
                raise ValueError(f"Tipo de objeto inválido: {object_type}")
            
            # Obter a classe apropriada
            obj_class = obj_map[object_type]
            obj = obj_class(object_id)
            
            # Configurar campos e parâmetros padrão
            fields = params.get('fields', [
                'impressions', 'clicks', 'spend', 'cpc', 'ctr', 'reach',
                'actions', 'cost_per_action_type'
            ])
            
            params_dict = {
                'time_range': params.get('time_range', {'since': '7d', 'until': 'today'}),
                'time_increment': params.get('time_increment', 1)
            }
            
            # Obter insights
            insights = obj.get_insights(
                fields=fields,
                params=params_dict
            )
            
            return [insight.export_all_data() for insight in insights]
            
        except Exception as e:
            logger.error(f"Erro ao obter insights: {e}", exc_info=True)
            raise
            
    async def disconnect(self) -> bool:
        """
        Desconecta da API do Meta Ads.
        
        Returns:
            bool: Verdadeiro se desconectado com sucesso
        """
        if self._api:
            # Não há um método explícito de desconexão na biblioteca
            # Simplesmente redefinimos o objeto API
            self._api = None
            self._account_id = None
            logger.info("Desconectado da API do Meta Ads")
            return True
        return False