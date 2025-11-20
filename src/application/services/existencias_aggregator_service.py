from __future__ import annotations
from typing import Iterable, List, Dict, Tuple
from collections import defaultdict

from src.application.interfaces.i_existencias_aggregator import IExistenciasAggregator
from src.domain.entities.existencias import ArchivoExistenciasOrigen, PlanoExistenciasNacional


class ExistenciasAggregatorService(IExistenciasAggregator):
    """
    Servicio de agregación de existencias.

    - construir_planos_nacionales:
        Agrupa todos los archivos de origen por (fecha_contable, tipo_valor)
        usando llaves hashables (strings), y devuelve una lista de
        planos nacionales (uno por grupo).

    - build_nacional:
        Construye un plano nacional a partir de un grupo de archivos que
        comparten misma fecha_contable y mismo tipo_valor.
    """

    def construir_planos_nacionales(
        self,
        archivos: Iterable[ArchivoExistenciasOrigen],
    ) -> List[PlanoExistenciasNacional]:
        archivos_list = list(archivos)
        if not archivos_list:
            return []

        # Agrupamos por (fecha_key, tipo_key) usando strings para evitar problemas de hash
        grupos: Dict[Tuple[str, str], List[ArchivoExistenciasOrigen]] = defaultdict(list)

        for a in archivos_list:
            fecha = self._get_fecha(a)
            tipo_valor = self._get_tipo_valor(a)

            # Claves hashables (strings)
            fecha_key = self._get_fecha_key(fecha)
            tipo_key = self._get_tipo_valor_key(tipo_valor)

            key = (fecha_key, tipo_key)
            grupos[key].append(a)

        planos: List[PlanoExistenciasNacional] = []
        for _, grupo in grupos.items():
            plano = self.build_nacional(grupo)
            planos.append(plano)

        return planos

    def build_nacional(
        self,
        archivos: Iterable[ArchivoExistenciasOrigen],
    ) -> PlanoExistenciasNacional:
        archivos_list = list(archivos)
        if not archivos_list:
            raise ValueError("No se recibieron archivos para agregación.")

        # Tomamos fecha y tipo_valor del primer archivo del grupo
        fecha = self._get_fecha(archivos_list[0])
        tipo_valor = self._get_tipo_valor(archivos_list[0])

        # Validamos que todos los archivos del grupo sean consistentes
        for a in archivos_list[1:]:
            if self._get_fecha(a) != fecha:
                raise ValueError(
                    f"Archivo {a.nombre_archivo} tiene fecha distinta: "
                    f"{self._get_fecha(a)}"
                )
            if self._get_tipo_valor(a) != tipo_valor:
                raise ValueError(
                    f"Archivo {a.nombre_archivo} tiene tipo valor distinto: "
                    f"{self._get_tipo_valor(a)}"
                )

        # Aquí seguimos usando los objetos reales (FechaContable, TipoValor)
        return PlanoExistenciasNacional(
            fecha_contable=fecha,
            tipo_valor=tipo_valor,
            bloques=archivos_list,
        )

    # ---------- Helpers internos para derivar datos ----------

    def _get_fecha(self, archivo: ArchivoExistenciasOrigen):
        """
        Devuelve la fecha contable del archivo.
        Asumimos que está en archivo.header.fecha_certificado (tipo FechaContable).
        """
        return archivo.header.fecha_certificado

    def _get_tipo_valor(self, archivo: ArchivoExistenciasOrigen):
        """
        Devuelve el tipo de valor del archivo.
        Asumimos que todos los detalles comparten el mismo tipo_valor
        y lo tomamos del primer detalle.
        """
        if not archivo.detalles:
            return None
        return archivo.detalles[0].tipo_valor

    def _get_fecha_key(self, fecha_obj) -> str:
        """
        Convierte la fecha (FechaContable o date) a una clave hashable.
        Usamos str(fecha_obj) para agrupar.
        """
        return str(fecha_obj)

    def _get_tipo_valor_key(self, tipo_valor_obj) -> str:
        """
        Convierte el tipo de valor a una clave hashable.
        Usamos str(tipo_valor_obj) para agrupar.
        """
        return str(tipo_valor_obj)