from __future__ import annotations
from pathlib import Path

from src.application.interfaces.i_existencias_output import IExistenciasOutput
from src.domain.entities.existencias import PlanoExistenciasNacional
from src.infrastructure.file_system.existencias_txt_writer import ExistenciasTxtWriter

class ExistenciasOutputService(IExistenciasOutput):
    """
    Servicio de aplicación que se encarga de:
    - Llamar al writer para generar el nacional.
    - Devolver la ruta final generada.
    """
    def __init__(self, txt_writer: ExistenciasTxtWriter | None = None):
        self._writer = txt_writer or ExistenciasTxtWriter()

    def generar_nacional(self, plano: PlanoExistenciasNacional) -> Path:
        """
        Genera el TXT nacional (y gestiona versiones/copias).
        """
        return self._writer.write_nacional(plano)