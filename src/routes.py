#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definições de rotas para o servidor MCP.
"""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field

from .middleware.authentication import verify_token
from .handlers.meta_ads_handler import MetaAdsHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

# Modelos de dados
class MCPRequest(BaseModel):
    """Modelo para solicitações MCP."""
    operation: str = Field(..., description="Operação a ser realizada")
    parameters: Dict[str, Any] = Field(default={}, description="Parâmetros da operação")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexto adicional")

class MCPResponse(BaseModel):
    """Modelo para respostas MCP."""
    status: str = Field(..., description="Status da operação")
    data: Optional[Any] = Field(default=None, description="Dados retornados")
    message: Optional[str] = Field(default=None, description="Mensagem adicional")

# Rotas Meta Ads
@router.post("/meta-ads", response_model=MCPResponse)
async def handle_meta_ads_request(
    request: MCPRequest = Body(...),
    token: str = Depends(verify_token)
):
    """
    Manipula solicitações relacionadas ao Meta Ads.
    
    Operações suportadas:
    - get_campaigns: Obter campanhas
    - get_ad_sets: Obter conjuntos de anúncios
    - get_ads: Obter anúncios
    - create_campaign: Criar uma campanha
    - update_campaign: Atualizar uma campanha
    - get_insights: Obter insights de performance
    """
    try:
        handler = MetaAdsHandler()
        result = await handler.handle(request.operation, request.parameters, request.context)
        
        return MCPResponse(
            status="success",
            data=result,
            message="Operação realizada com sucesso"
        )
    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao processar solicitação Meta Ads: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar solicitação"
        )