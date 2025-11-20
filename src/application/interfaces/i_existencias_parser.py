from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from src.domain.entities.existencias import ArchivoExistenciasOrigen

class IExistenciasParser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> ArchivoExistenciasOrigen:
        """Parsea un TXT de existencias (01 + 02s) a entidad de dominio."""
        raise NotImplementedError