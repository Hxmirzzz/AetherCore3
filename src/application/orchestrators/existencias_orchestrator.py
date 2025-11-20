from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional
import logging

from src.application.interfaces.i_existencias_parser import IExistenciasParser
from src.application.interfaces.i_existencias_aggregator import IExistenciasAggregator
from src.application.interfaces.i_existencias_output import IExistenciasOutput

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExistenciasOrchestratorOptions:
    """
    Opciones de alto nivel para el procesamiento.
    Se puede extender luego con flags tipo:
    - strict_mode
    - solo_divisa
    - etc.
    """
    fecha_contable: Optional[date] = None

class ExistenciasProcessingOrchestrator:
    """
    Caso de uso de alto nivel:
    - Leer todos los TXT de existencias del día
    - Agrupar por tipo de valor
    - Generar los TXT nacionales en la carpeta de salida
    """

    def __init__(
        self,
        parser: IExistenciasParser,
        aggregator: IExistenciasAggregator,
        output: IExistenciasOutput,
    ) -> None:
        self._parser = parser
        self._aggregator = aggregator
        self._output = output

    def procesar_dia(self, opts: ExistenciasOrchestratorOptions | None = None) -> None:
        """
        Procesa todos los archivos de existencias para la fecha indicada.
        Si no se indica fecha, usa hoy.
        """
        if opts is None:
            opts = ExistenciasOrchestratorOptions()

        fecha = opts.fecha_contable or date.today()
        logger.info(f"Procesando existencias para la fecha: {fecha}")

        archivos_origen = self._parser.obtener_archivos_del_dia(fecha)
        if not archivos_origen:
            logger.warning(f"No se encontraron archivos para la fecha: {fecha}")
            return
        
        planos_nacionales = self._aggregator.construir_planos_nacionales(archivos_origen)
        if not planos_nacionales:
            logger.warning(f"No se encontraron planos nacionales para la fecha: {fecha}")
            return
        
        logger.info("Se generaron %d planos nacionales", len(planos_nacionales))
        self._output.generar_txt_nacionales(planos_nacionales, fecha)