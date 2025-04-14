#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Funções auxiliares para o servidor MCP.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)

def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Lê um arquivo JSON e retorna seu conteúdo.
    
    Args:
        file_path: Caminho para o arquivo JSON
        
    Returns:
        Conteúdo do arquivo JSON
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
        json.JSONDecodeError: Se o arquivo não for um JSON válido
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON do arquivo {file_path}: {e}")
        raise

def write_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """
    Escreve dados em um arquivo JSON.
    
    Args:
        file_path: Caminho para o arquivo JSON
        data: Dados a serem escritos
    """
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao escrever no arquivo {file_path}: {e}")
        raise

def filter_dict(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
    """
    Filtra um dicionário para manter apenas as chaves permitidas.
    
    Args:
        data: Dicionário a ser filtrado
        allowed_keys: Lista de chaves permitidas
        
    Returns:
        Dicionário filtrado
    """
    return {k: v for k, v in data.items() if k in allowed_keys}

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mescla dois dicionários, com o segundo tendo precedência.
    
    Args:
        dict1: Primeiro dicionário
        dict2: Segundo dicionário (tem precedência)
        
    Returns:
        Dicionário mesclado
    """
    result = dict1.copy()
    result.update(dict2)
    return result

def normalize_meta_ads_status(status: Union[str, List[str]]) -> List[str]:
    """
    Normaliza o status do Meta Ads para o formato esperado pela API.
    
    Args:
        status: Status a ser normalizado (string ou lista)
        
    Returns:
        Lista de status normalizada
    """
    # Mapeamento de status simples para status da API
    status_map = {
        "active": "ACTIVE",
        "paused": "PAUSED",
        "deleted": "DELETED",
        "archived": "ARCHIVED"
    }
    
    if isinstance(status, str):
        status = [status]
    
    # Normalizar cada status
    normalized = []
    for s in status:
        s_lower = s.lower()
        if s_lower in status_map:
            normalized.append(status_map[s_lower])
        else:
            normalized.append(s.upper())
    
    return normalized

def format_meta_ads_insights(insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Formata insights do Meta Ads para um formato mais amigável.
    
    Args:
        insights: Lista de insights brutos
        
    Returns:
        Lista de insights formatados
    """
    formatted_insights = []
    
    for insight in insights:
        formatted = {
            "date_start": insight.get("date_start"),
            "date_stop": insight.get("date_stop"),
            "impressions": insight.get("impressions", 0),
            "clicks": insight.get("clicks", 0),
            "spend": insight.get("spend", 0),
            "ctr": insight.get("ctr", 0),
            "cpc": insight.get("cpc", 0),
            "reach": insight.get("reach", 0),
        }
        
        # Processar ações
        actions = insight.get("actions", [])
        if actions:
            for action in actions:
                action_type = action.get("action_type", "").lower().replace("_", "")
                action_value = action.get("value", 0)
                formatted[f"action_{action_type}"] = action_value
        
        # Processar custo por tipo de ação
        cost_per_action = insight.get("cost_per_action_type", [])
        if cost_per_action:
            for cost in cost_per_action:
                action_type = cost.get("action_type", "").lower().replace("_", "")
                cost_value = cost.get("value", 0)
                formatted[f"cost_per_{action_type}"] = cost_value
        
        formatted_insights.append(formatted)
    
    return formatted_insights