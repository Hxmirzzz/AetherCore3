from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from src.domain.value_objects.tipo_valor import TipoValor
from src.domain.value_objects.fecha_contable import FechaContable


@dataclass
class PlanoExistenciasHeader:
    tipo_registro: str          # "01"
    codigo_dane_ciudad: str
    nombre_ciudad: str
    fecha_certificado: FechaContable
    codigo_transportadora: str  # VAT, VGL, BRK...
    nit_cliente: str
    nombre_cliente: str
    codigo_divisa: int          # ej. 24
    nombre_divisa: str          # "EURO"
    codigo_fondo: int           # 1 oficina, 9 ATM...
    nombre_fondo: str


@dataclass
class DenominacionSaldo:
    valor: int
    cantidad: int


@dataclass
class PlanoExistenciasDetalle:
    tipo_registro: str              # "02"
    tipo_valor: TipoValor           # VO 1->CU, 24->EU...
    nombre_tipo_valor: str          # "Euro"
    codigo_calidad: int             # 2, 23, ...
    nombre_calidad: str             # "Buen Estado", "Deteriorado"
    denominaciones: list[DenominacionSaldo]


@dataclass
class ArchivoExistenciasOrigen:
    nombre_archivo: str
    header: PlanoExistenciasHeader
    detalles: list[PlanoExistenciasDetalle]

    @property
    def fecha_certificado(self) -> FechaContable:
        return self.header.fecha_certificado

    @property
    def tipo_valor(self) -> TipoValor:
        """
        Retorna el tipo de valor del archivo.
        VALIDA que todos los detalles tengan el mismo tipo.
        """
        if not self.detalles:
            return TipoValor.from_codigo(self.header.codigo_divisa)

        tipos = {d.tipo_valor for d in self.detalles}
        
        if len(tipos) > 1:
            raise ValueError(
                f"Archivo {self.nombre_archivo} tiene múltiples tipos de valor: {tipos}"
            )
        
        return self.detalles[0].tipo_valor


@dataclass
class PlanoExistenciasNacional:
    """
    Representa el archivo nacional final de una divisa en una fecha:
    combina varios `ArchivoExistenciasOrigen` (BOG, CTG, etc.).
    """
    fecha_contable: FechaContable
    tipo_valor: TipoValor
    bloques: list[ArchivoExistenciasOrigen] = field(default_factory=list)

    def to_lines(self) -> list[str]:
        """
        Devuelve las líneas TXT listas para escribir en el archivo nacional.
        Respeta la estructura 01 + N * (01 + 02...) concatenados.
        """
        lines: list[str] = []

        for archivo in self.bloques:
            h = archivo.header

            # Línea 01
            line_01 = ",".join([
                "01",
                h.codigo_dane_ciudad,
                h.nombre_ciudad,
                h.fecha_certificado.to_ddmmyyyy(),  # dd/mm/aaaa
                h.codigo_transportadora,
                h.nit_cliente,
                h.nombre_cliente,
                str(h.codigo_divisa),
                h.nombre_divisa,
                str(h.codigo_fondo),
                h.nombre_fondo,
            ])
            lines.append(line_01)

            # Líneas 02
            for d in archivo.detalles:
                denoms = d.denominaciones
                max_slots = 8  # 8 denominaciones como máximo

                if len(denoms) < max_slots:
                    denoms = denoms + [DenominacionSaldo(0, 0)] * (max_slots - len(denoms))

                campos: list[str] = [
                    "02",
                    str(d.tipo_valor.codigo),        # código numérico 1, 24, etc.
                    d.nombre_tipo_valor,
                    str(d.codigo_calidad),
                    d.nombre_calidad,
                ]

                # 8 pares valor/cantidad → 16 campos
                for ds in denoms[:max_slots]:
                    campos.append(str(ds.valor) or "")
                    campos.append(str(ds.cantidad) or "")

                line_02 = ",".join(campos)
                lines.append(line_02)

        return lines