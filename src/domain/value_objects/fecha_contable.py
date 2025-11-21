from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class FechaContable:
    value: date

    @staticmethod
    def from_ddmmyyyy(s: str) -> "FechaContable":
        """
        Parsea fecha en formato dd/mm/yyyy
        Ejemplo: "21/11/2025" → date(2025, 11, 21)
        """
        dt = datetime.strptime(s.strip(), "%d/%m/%Y").date()
        return FechaContable(value=dt)

    @staticmethod
    def from_yymmdd(s: str) -> "FechaContable":
        """
        Parsea fecha en formato yymmdd
        Ejemplo: "251121" → date(2025, 11, 21)
        """
        dt = datetime.strptime(s.strip(), "%y%m%d").date()
        return FechaContable(value=dt)

    def to_ddmmyyyy(self) -> str:
        """Retorna: dd/mm/yyyy (con barras) para archivo nacional"""
        return self.value.strftime("%d/%m/%Y")

    def to_yymmdd(self) -> str:
        """Retorna: yymmdd (sin barras) para carpetas"""
        return self.value.strftime("%y%m%d")

    @staticmethod
    def from_filename(nombre: str) -> "FechaContable":
        """
        Extrae fecha desde nombre de archivo.
        Formato esperado: VYBUCTG<yymmdd>HHMITV.TXT
        Posiciones: 7-12 (6 caracteres para yymmdd)
        
        Ejemplo: VYBUCTG2511210601EU.TXT → 251121 → 2025-11-21
        """
        try:
            stem = Path(nombre).stem.upper()
            fecha_str = stem[7:13]
            return FechaContable.from_yymmdd(fecha_str)
        except Exception:
            logger.warning("No se pudo extraer fecha desde nombre de archivo: %s", nombre)
            raise