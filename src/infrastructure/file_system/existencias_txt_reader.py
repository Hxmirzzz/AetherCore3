from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Iterable
import logging

from src.infrastructure.file_system.existencias_path_manager import ExistenciasPathManager
from src.domain.value_objects.fecha_contable import FechaContable
from src.domain.value_objects.tipo_valor import TipoValor
from src.domain.entities.existencias import (
    ArchivoExistenciasOrigen,
    RegistroDetalleExistencias,
)

logger = logging.getLogger(__name__)

@dataclass
class ExistenciasTxtReader:
    """
    Lector de archivos de existencias (planos origen).

    Cada archivo debe contener:
    - 1 registro tipo 01 (cabecera)
    - 1+ registros tipo 02 (detalle)
    """
    path_manager: ExistenciasPathManager

    @classmethod
    def from_settings(cls) -> "ExistenciasTxtReader":
        return cls(ExistenciasPathManager.from_settings())

    def listar_archivos_en_origen(self) -> List[Path]:
        """
        Lista todos los .txt en la carpeta de PLANOS (no incluye gestionados).
        """
        base = self.path_manager.origen_planos
        if not base.exists():
            logger.warning("Carpeta de origen no existe: %s", base)
            return []

        return sorted(p for p in base.iterdir() if p.is_file() and p.suffix.lower() == ".txt")

    def leer_archivo(self, path: Path) -> ArchivoExistenciasOrigen | None:
        """
        Lee un archivo de existencias y lo mapea a ArchivoExistenciasOrigen.
        Si el formato es inválido, devuelve None (y loggea el problema).
        """
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            logger.exception("Error leyendo archivo %s", path)
            return None

        if not lines:
            logger.warning("Archivo vacío: %s", path)
            return None

        header_line = None
        detail_lines: List[str] = []
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split(",")
            if not parts:
                continue
            tipo = parts[0].strip()
            if tipo == "01" and header_line is None:
                header_line = parts
            elif tipo == "02":
                detail_lines.append(ln)

        if header_line is None or not detail_lines:
            logger.warning("Archivo inválido: %s", path)
            return None

        try:
            _, cod_dane, ciudad, fecha_str, transport, nit, cliente, cod_divisa, divisa, cod_fondo, nombre_fondo = header_line
        except ValueError:
            logger.warning("Cabecera 01 con número de campos inválido en %s: %s", path, header_line)
            return None

        fecha_contable = FechaContable.from_ddmmyyyy(fecha_str.replace("/", ""))
        tipo_valor = TipoValor.from_abreviatura(divisa.strip())

        registros: List[RegistroDetalleExistencias] = []

        for ln in detail_lines:
            parts = [p.strip() for p in ln.split(",")]
            if len(parts) < 21:
                logger.warning("Registro 02 con número de campos inválido en %s: %s", path, ln)
                continue
            try:
                (
                    _,
                    cod_tipo_valor,
                    nombre_tipo_valor,
                    cod_calidad,
                    nombre_calidad,
                    *denom_y_cant,
                ) = parts
            except ValueError:
                logger.warning("Registro 02 con número de campos inválido en %s: %s", path, ln)
                continue

            denoms: List[tuple[int, int]] = []
            for i in range(0, min(len(denom_y_cant), 16), 2):
                try:
                    val = int(denom_y_cant[i]) if denom_y_cant[i] else 0
                except ValueError:
                    val = 0
                try:
                    cant = int(denom_y_cant[i + 1]) if denom_y_cant[i + 1] else 0
                except (ValueError, IndexError):
                    cant = 0
                if val == 0 and cant == 0:
                    continue
                denoms.append((val, cant))

            reg = RegistroDetalleExistencias(
                cod_tipo_valor=int(cod_tipo_valor),
                nombre_tipo_valor=nombre_tipo_valor,
                cod_calidad=int(cod_calidad),
                nombre_calidad=nombre_calidad,
                denominaciones=denoms,
            )
            registros.append(reg)

        if not registros:
            logger.warning("Archivo %s no tiene registros 02 válidos", path)
            return None

        return ArchivoExistenciasOrigen(
            fecha_contable=fecha_contable,
            tipo_valor=tipo_valor,
            codigo_dane_ciudad=cod_dane.strip(),
            nombre_ciudad=ciudad.strip(),
            transportadora=transport.strip(),
            nit_cliente=nit.strip(),
            nombre_cliente=cliente.strip(),
            codigo_divisa=int(cod_divisa),
            nombre_divisa=divisa.strip(),
            codigo_fondo=int(cod_fondo),
            nombre_fondo=nombre_fondo.strip(),
            registros=registros,
            source_path=path,
        )