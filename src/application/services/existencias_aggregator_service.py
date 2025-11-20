from __future__ import annotations
from typing import Iterable
from src.application.interfaces.i_existencias_aggregator import IExistenciasAggregator
from src.domain.entities.existencias import ArchivoExistenciasOrigen, PlanoExistenciasNacional

class ExistenciasAggregatorService(IExistenciasAggregator):
    """
    Solo concatena bloques (01 + sus 02) de todos los archivos
    que tengan misma fecha contable y mismo tipo de valor.
    """
    def build_nacional(self, archivos: Iterable[ArchivoExistenciasOrigen]) -> PlanoExistenciasNacional:
        archivos_list = list(archivos)
        if not archivos_list:
            raise ValueError("No se recibieron archivos para agregación.")

        fecha = archivos_list[0].fecha_contable
        tipo_valor = archivos_list[0].tipo_valor

        for a in archivos_list[1:]:
            if a.fecha_contable != fecha:
                raise ValueError(f"Archivo {a.nombre_archivo} tiene fecha distinta: {a.fecha_contable}")
            if a.tipo_valor != tipo_valor:
                raise ValueError(f"Archivo {a.nombre_archivo} tiene tipo valor distinto: {a.tipo_valor}")

        return PlanoExistenciasNacional(
            fecha_contable=fecha,
            tipo_valor=tipo_valor,
            bloques=archivos_list,
        )