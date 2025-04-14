#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classe base para manipuladores de solicitações no servidor MCP.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseHandler(ABC):
    """
    Classe base abstrata para todos os manipuladores de solicitações.
    
    Todos os manipuladores específicos devem herdar desta classe e implementar
    os métodos abstratos.
    """
    
    def __init__(self):
        """Inicializa o manipulador base."""
        pass
    
    @abstractmethod
    async def handle(self, operation: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Manipula uma operação solicitada.
        
        Args:
            operation: Nome da operação a ser executada
            parameters: Parâmetros da operação
            context: Contexto adicional (opcional)
            
        Returns:
            Resultado da operação
        """
        pass