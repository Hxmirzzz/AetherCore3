from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable
from src.domain.entities.existencias import ArchivoExistenciasOrigen, PlanoExistenciasNacional

class IExistenciasAggregator(ABC):
    @abstractmethod
    def build_nacional(self, archivos: Iterable[ArchivoExistenciasOrigen]) -> PlanoExistenciasNacional:
        ...