from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.infrastructure.config.settings_existencias import get_existencias_settings
from src.domain.value_objects.fecha_contable import FechaContable
from src.domain.value_objects.tipo_valor import TipoValor

@dataclass
class ExistenciasPathManager:
    """
    Administra rutas para:
    - Origen (PLANOS y gestionados)
    - Nacional (por fecha contable y tipo de valor)
    - Copias de versiones anteriores del nacional
    """
    origen_planos: Path
    origen_nacional: Path

    @classmethod
    def from_settings(cls) -> "ExistenciasPathManager":
        cfg = get_existencias_settings()
        return cls(
            origen_planos=cfg.paths.origen_planos,
            nacional_base=cfg.paths.nacional_base,
        )

    @property
    def origen_gestionados(self) -> Path:
        """
        Carpeta donde moveremos los TXT origen ya procesados
        """
        return self.origen_planos / "gestionados"

    # ---------- Rutas NACIONAL ----------

    def nacional_folder_for_date(self, fecha: FechaContable) -> Path:
        """
        Carpeta de salida para una fecha contable
        """
        sub = fecha.to_yymmdd()
        return self.nacional_base / sub

    def nacional_copias_folder_for_date(self, fecha: FechaContable) -> Path:
        """
        Carpeta de copias para esa fecha
        """
        return self.nacional_folder_for_date(fecha) / "COPIAS"

    def nacional_filename(self, fecha: FechaContable, tipo_valor: TipoValor) -> Path:
        """
        Nombre del archivo nacional:

        VYBUBOG<YYMMDD><HHMI><TV>.TXT

        - Siempre ciudad BOG (centralizado).
        - YYMMDD tomado de la fecha contable.
        - HHMI de la hora de generación (ahora).
        - TV = abreviatura (CU, EU, etc.).
        """
        hoy_hora = datetime.now().strftime("%H%M")
        yymmdd = fecha.to_yymmdd()
        tv = tipo_valor.abreviatura
        return f"VYBUBOG{yymmdd}{hoy_hora}{tv}.TXT"

    def nacional_main_path(self, fecha: FechaContable, tipo_valor: TipoValor) -> Path:
        """
        Ruta principal del archivo nacional
        """
        folder = self.nacional_folder_for_date(fecha)
        filename = self.nacional_filename(fecha, tipo_valor)
        return folder / filename

    def nacional_backup_name(self, original_name: str) -> str:
        """
        Cuando ya existe un nacional y lo vamos a reemplazar,
        renombramos el anterior con timestamp de generación:

        VYBUBOG2510162359EU.TXT -> VYBUBOG2510162359EU_20251119T0930.TXT
        """
        p = Path(original_name)
        stem = p.stem
        suffix = p.suffix or ".TXT"
        ts = datetime.now().strftime("%Y%m%dT%H%M")
        return f"{stem}_{ts}{suffix}"