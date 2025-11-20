from __future__ import annotations
from pathlib import Path
from datetime import date
from typing import Iterable, List
import logging

from src.application.interfaces.i_existencias_output import IExistenciasOutput
from src.domain.entities.existencias import PlanoExistenciasNacional
from src.infrastructure.file_system.existencias_txt_writer import ExistenciasTxtWriter

logger = logging.getLogger(__name__)


class ExistenciasOutputService(IExistenciasOutput):
    """
    Servicio de aplicación que se encarga de:
    - Llamar al writer para generar el nacional.
    - Devolver las rutas finales generadas.
    """

    def __init__(self, txt_writer: ExistenciasTxtWriter) -> None:
        self._writer = txt_writer

    # Implementación requerida por la interfaz
    def write_nacional(self, plano: PlanoExistenciasNacional) -> Path:
        """
        Implementación concreta del método abstracto definido en IExistenciasOutput.
        """
        return self._writer.write_nacional(plano)

    # Método que el orchestrator está usando
    def generar_txt_nacionales(
        self,
        planos: Iterable[PlanoExistenciasNacional],
        fecha: date,
    ) -> List[Path]:
        """
        Genera todos los TXT nacionales para la fecha dada.
        Devuelve la lista de rutas generadas.
        """
        rutas: List[Path] = []
        for plano in planos:
            ruta = self.write_nacional(plano)
            rutas.append(ruta)

        logger.info(
            "Se generaron %d archivos nacionales para la fecha %s",
            len(rutas),
            fecha,
        )
        return rutas

    # Alias opcional, por si quieres usarlo en otro lado
    def generar_nacional(self, plano: PlanoExistenciasNacional) -> Path:
        return self.write_nacional(plano)