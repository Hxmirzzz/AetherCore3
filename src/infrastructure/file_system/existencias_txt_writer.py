from __future__ import annotations
from pathlib import Path
import os
import logging

from src.domain.entities.existencias import PlanoExistenciasNacional
from .existencias_path_manager import ExistenciasPathManager

logger = logging.getLogger(__name__)

class ExistenciasTxtWriter:
    """
    Escribe el archivo nacional en la carpeta correspondiente.
    - Si ya existe un nacional para esa fecha/tipo, mueve el viejo a COPIAS.
    """
    def __init__(self, path_manager: ExistenciasPathManager | None = None):
        self._paths = path_manager or ExistenciasPathManager.from_settings()

    def write_nacional(self, plano: PlanoExistenciasNacional) -> Path:
        """
        Escribe el plano nacional en la carpeta correspondiente.
        - Si ya existe un nacional para esa fecha/tipo, mueve el viejo a COPIAS.
        """
        fecha = plano.fecha_contable
        tipo_valor = plano.tipo_valor

        folder = self._paths.nacional_folder_for_date(fecha)
        backup_folder = self._paths.nacional_copias_folder_for_date(fecha)

        os.makedirs(folder, exist_ok=True)
        os.makedirs(backup_folder, exist_ok=True)

        main_path = self._paths.nacional_main_path(fecha, tipo_valor)

        if main_path.exists():
            backup_name = self._paths.nacional_backup_name(main_path.name)
            backup_path = backup_folder / backup_name
            logger.info("Moviendo nacional existente a COPIAS: %s -> %s", main_path, backup_path)
            os.rename(main_path, backup_path)

        lines = plano.to_lines()
        with main_path.open("w", encoding="utf-8", newline="\n") as f:
            for line in lines:
                f.write(line + "\n")

        logger.info("Archivo nacional generado: %s", main_path)
        return main_path