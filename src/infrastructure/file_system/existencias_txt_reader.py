from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List
import logging

from src.domain.constants import NomenclaturaArchivo as NA
from src.infrastructure.file_system.existencias_path_manager import ExistenciasPathManager
from src.domain.value_objects.fecha_contable import FechaContable
from src.domain.value_objects.tipo_valor import TipoValor
from src.domain.entities.existencias import (
    PlanoExistenciasHeader,
    PlanoExistenciasDetalle,
    ArchivoExistenciasOrigen,
    DenominacionSaldo,
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

    # --------------------------------------------------------------------- #
    # LISTAR ARCHIVOS
    # --------------------------------------------------------------------- #
    def listar_archivos_en_origen(self) -> List[Path]:
        """
        Lista todos los .txt en la carpeta de PLANOS (no incluye 'gestionados').
        """
        base = self.path_manager.origen_planos
        if not base.exists():
            logger.warning("Carpeta de origen no existe: %s", base)
            return []

        return sorted(
            p for p in base.iterdir()
            if p.is_file() and p.suffix.lower() == NA.EXTENSION.lower()
        )

    # --------------------------------------------------------------------- #
    # LEER UN ARCHIVO
    # --------------------------------------------------------------------- #
    def leer_archivo(self, path: Path) -> ArchivoExistenciasOrigen | None:
        """
        Lee un archivo de existencias y lo mapea a ArchivoExistenciasOrigen.
        Si el formato es inválido, devuelve None (y loguea el problema).
        """
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            logger.exception("Error leyendo archivo %s", path)
            return None

        if not lines:
            logger.warning("Archivo vacío: %s", path)
            return None

        header_parts: list[str] | None = None
        detail_lines: List[str] = []

        # Separar 01 y 02
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split(",")
            if not parts:
                continue

            tipo = parts[0].strip()
            if tipo == "01" and header_parts is None:
                header_parts = [p.strip() for p in parts]
            elif tipo == "02":
                detail_lines.append(ln)

        if header_parts is None or not detail_lines:
            logger.warning(
                "Archivo inválido (falta 01 o no hay 02) en %s", path
            )
            return None

        # -------------------- CABECERA 01 -> PlanoExistenciasHeader -------- #
        try:
            (
                _,
                cod_dane,
                ciudad,
                fecha_str,
                transport,
                nit,
                cliente,
                cod_divisa,
                divisa,
                cod_fondo,
                nombre_fondo,
            ) = header_parts
        except ValueError:
            logger.warning(
                "Cabecera 01 con número de campos inválido en %s: %s",
                path,
                header_parts,
            )
            return None

        # fecha_str viene como '17/10/2025'
        # Ajusta aquí según cómo implemente FechaContable.from_ddmmyyyy:
        # si espera '17102025', usa fecha_str.replace("/", "")
        fecha_cert = FechaContable.from_ddmmyyyy(fecha_str)

        header = PlanoExistenciasHeader(
            tipo_registro="01",
            codigo_dane_ciudad=cod_dane.strip(),
            nombre_ciudad=ciudad.strip(),
            fecha_certificado=fecha_cert,
            codigo_transportadora=transport.strip(),
            nit_cliente=nit.strip(),
            nombre_cliente=cliente.strip(),
            codigo_divisa=int(cod_divisa),
            nombre_divisa=divisa.strip(),
            codigo_fondo=int(cod_fondo),
            nombre_fondo=nombre_fondo.strip(),
        )

        # -------------------- DETALLES 02 -> List[PlanoExistenciasDetalle] -- #
        detalles: List[PlanoExistenciasDetalle] = []

        for ln in detail_lines:
            parts = [p.strip() for p in ln.split(",")]
            if len(parts) < 21:  # 1..21 campos mínimo
                logger.warning(
                    "Registro 02 con número de campos inválido en %s: %s",
                    path,
                    ln,
                )
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
                logger.warning(
                    "Registro 02 con número de campos inválido en %s: %s",
                    path,
                    ln,
                )
                continue

            # TipoValor desde el código
            try:
                tipo_valor = TipoValor.from_codigo(int(cod_tipo_valor))
            except Exception:
                logger.exception(
                    "Error convirtiendo código de tipo valor '%s' en %s",
                    cod_tipo_valor,
                    path,
                )
                continue

            # Denominaciones (hasta 8 pares valor/cantidad)
            denominaciones: List[DenominacionSaldo] = []
            for i in range(0, min(len(denom_y_cant), 16), 2):
                valor_str = denom_y_cant[i] if i < len(denom_y_cant) else ""
                cant_str = denom_y_cant[i + 1] if i + 1 < len(denom_y_cant) else ""

                try:
                    valor = int(valor_str) if valor_str else 0
                except ValueError:
                    valor = 0
                try:
                    cantidad = int(cant_str) if cant_str else 0
                except ValueError:
                    cantidad = 0

                if valor == 0 and cantidad == 0:
                    continue

                denominaciones.append(
                    DenominacionSaldo(valor=valor, cantidad=cantidad)
                )

            detalle = PlanoExistenciasDetalle(
                tipo_registro="02",
                tipo_valor=tipo_valor,
                nombre_tipo_valor=nombre_tipo_valor.strip(),
                codigo_calidad=int(cod_calidad),
                nombre_calidad=nombre_calidad.strip(),
                denominaciones=denominaciones,
            )
            detalles.append(detalle)

        if not detalles:
            logger.warning(
                "Archivo %s no tiene registros 02 válidos", path
            )
            return None

        # -------------------- Construir ArchivoExistenciasOrigen ------------ #
        archivo = ArchivoExistenciasOrigen(
            nombre_archivo=path.name,
            header=header,
            detalles=detalles,
        )
        return archivo