#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classe base para conectores de API no servidor MCP.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

class BaseConnector(ABC):
    """
    Classe base abstrata para todos os conectores de API.
    
    Todos os conectores específicos devem herdar desta classe e implementar
    os métodos abstratos.
    """
    
    def __init__(self):
        """Inicializa o conector base."""
        pass
    
    @abstractmethod
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Conecta à API externa usando as credenciais fornecidas.
        
        Args:
            credentials: Dicionário com as credenciais necessárias
            
        Returns:
            bool: Verdadeiro se a conexão for bem-sucedida, falso caso contrário
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Desconecta da API externa.
        
        Returns:
            bool: Verdadeiro se desconectado com sucesso
        """
        pass