from __future__ import annotations
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional
import logging

from src.application.interfaces.i_existencias_parser import IExistenciasParser
from src.domain.entities.existencias import (
    ArchivoExistenciasOrigen,
    PlanoExistenciasHeader,
    PlanoExistenciasDetalle,
    DenominacionSaldo,
)
from src.domain.value_objects.tipo_valor import TipoValor
from src.domain.value_objects.fecha_contable import FechaContable
from src.domain.constants import TiposRegistro, LongitudesRegistro
from src.shared.text_utils import leer_archivo_con_encoding_auto
from src.infrastructure.file_system.existencias_txt_reader import ExistenciasTxtReader

logger = logging.getLogger(__name__)

class ExistenciasParserService(IExistenciasParser):
    """
    Servicio de aplicación que:
    - Localiza los TXT de origen de una fecha (vía reader)
    - Parsea cada TXT en ArchivoExistenciasOrigen
    """

    def __init__(self, reader: ExistenciasTxtReader) -> None:
        self._reader = reader

    def parse(self, path: Path) -> ArchivoExistenciasOrigen:
        lines = self._read_lines(path)
        if not lines:
            raise ValueError(f"Archivo vacio: {path}")

        header = self._parse_header(lines[0])
        detalles = [self._parse_detalle(ln) for ln in lines[1:]]

        if not detalles:
            raise ValueError(f"Archivo sin registros 02: {path}")

        return ArchivoExistenciasOrigen(
            nombre_archivo=path.name,
            header=header,
            detalles=detalles,
        )

    def _read_lines(self, path: Path) -> list[str]:
        """
        Lee las líneas del archivo detectando automáticamente el encoding.
        
        Soporta:
        - UTF-8
        - ANSI (Windows-1252)
        - Otros encodings detectados automáticamente
        """
        try:
            contenido = leer_archivo_con_encoding_auto(path)
            return contenido.splitlines()
        except Exception as e:
            logger.error(f"No se pudo leer el archivo {path}: {e}")
            raise

    def _parse_header(self, line: str) -> PlanoExistenciasHeader:
        parts = line.split(",")
        if len(parts) < LongitudesRegistro.MIN_CAMPOS_HEADER:
            raise ValueError(f"Registro 01 debe tener al menos {LongitudesRegistro.MIN_CAMPOS_HEADER} campos")

        tipo_registro = parts[0].strip()
        if tipo_registro != TiposRegistro.HEADER:
            raise ValueError(f"Esperaba tipo {TiposRegistro.HEADER}, recibió {tipo_registro}")

        codigo_dane_ciudad = parts[1].strip()
        nombre_ciudad = parts[2].strip()
        fecha_str = parts[3].strip()

        if "/" in fecha_str:
            fecha = FechaContable.from_ddmmyyyy(fecha_str)
        else:
            fecha = FechaContable.from_yymmdd(fecha_str)

        codigo_transportadora = parts[4].strip()
        nit_cliente = parts[5].strip()
        nombre_cliente = parts[6].strip()
        codigo_divisa = int(parts[7].strip()) if parts[7].strip() else 0
        nombre_divisa = parts[8].strip()
        codigo_fondo = int(parts[9].strip()) if parts[9].strip() else 0
        nombre_fondo = parts[10].strip()

        return PlanoExistenciasHeader(
            tipo_registro=tipo_registro,
            codigo_dane_ciudad=codigo_dane_ciudad,
            nombre_ciudad=nombre_ciudad,
            fecha_certificado=fecha,
            codigo_transportadora=codigo_transportadora,
            nit_cliente=nit_cliente,
            nombre_cliente=nombre_cliente,
            codigo_divisa=codigo_divisa,
            nombre_divisa=nombre_divisa,
            codigo_fondo=codigo_fondo,
            nombre_fondo=nombre_fondo,
        )

    def _parse_detalle(self, line: str) -> PlanoExistenciasDetalle:
        parts = line.split(",")
        if len(parts) < 21:
            raise ValueError(f"Registro 02 con longitud invalida ({len(parts)}): {line}")

        tipo_registro = parts[0].strip()
        if tipo_registro != "02":
            raise ValueError(f"Registro detalle no es 02: {line}")

        codigo_tipo_valor = int(parts[1].strip()) if parts[1].strip() else 0
        nombre_tipo_valor = parts[2].strip()
        codigo_calidad = int(parts[3].strip()) if parts[3].strip() else 0
        nombre_calidad = parts[4].strip()

        tipo_valor = TipoValor.from_codigo(codigo_tipo_valor)

        denoms: list[DenominacionSaldo] = []

        idx = 5
        while idx < len(parts):
            valor_str = parts[idx].strip() if idx < len(parts) else ""
            cant_str = parts[idx + 1].strip() if idx + 1 < len(parts) else ""

            if valor_str and cant_str:
                try:
                    valor = int(valor_str)
                except ValueError:
                    valor = 0

                try:
                    cantidad = int(cant_str)
                except ValueError:
                    cantidad = 0

                denoms.append(DenominacionSaldo(valor=valor, cantidad=cantidad))

            idx += 2

        return PlanoExistenciasDetalle(
            tipo_registro=tipo_registro,
            tipo_valor=tipo_valor,
            nombre_tipo_valor=nombre_tipo_valor,
            codigo_calidad=codigo_calidad,
            nombre_calidad=nombre_calidad,
            denominaciones=denoms,
        )

    def _extract_fecha_from_filename(self, nombre: str) -> Optional[date]:
        fecha_contable = FechaContable.from_filename(nombre)
        return fecha_contable.value if fecha_contable else None