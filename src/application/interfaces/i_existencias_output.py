from __future__ import annotations
from abc import ABC, abstractmethod
from src.domain.entities.existencias import PlanoExistenciasNacional
from pathlib import Path

class IExistenciasOutput(ABC):
    @abstractmethod
    def write_nacional(self, plano: PlanoExistenciasNacional) -> Path:
        """Genera el TXT nacional (y gestiona versiones/copias)."""
        raise NotImplementedError