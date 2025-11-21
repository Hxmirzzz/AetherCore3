from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from src.domain.entities.existencias import ArchivoExistenciasOrigen

class IExistenciasParser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> ArchivoExistenciasOrigen:
        """Parsea UN archivo TXT a entidad de dominio."""
        ...