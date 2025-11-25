from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from datetime import date
from typing import Optional
import logging
import shutil

from src.application.interfaces.i_existencias_parser import IExistenciasParser
from src.application.interfaces.i_existencias_aggregator import IExistenciasAggregator
from src.application.interfaces.i_existencias_output import IExistenciasOutput
from src.domain.value_objects.fecha_contable import FechaContable
from src.infrastructure.file_system.existencias_txt_reader import ExistenciasTxtReader
from src.infrastructure.file_system.existencias_path_manager import ExistenciasPathManager

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
    Orquestador del flujo completo de procesamiento de existencias.
    
    Responsabilidades:
    1. Obtener paths de archivos de una fecha
    2. Parsear cada archivo (delegando al parser)
    3. Agrupar por tipo_valor (delegando al aggregator)
    4. Generar archivos nacionales (delegando al output)
    5. Mover archivos procesados a gestionados
    6. Mover archivos con errores a carpeta ERRORES
    """
    def __init__(
        self,
        parser: IExistenciasParser,
        aggregator: IExistenciasAggregator,
        output: IExistenciasOutput,
        reader: ExistenciasTxtReader,
        path_manager: ExistenciasPathManager,
    ) -> None:
        self._parser = parser
        self._aggregator = aggregator
        self._output = output
        self._reader = reader
        self._paths = path_manager

    def procesar_dia(self, opts: ExistenciasOrchestratorOptions | None = None) -> None:
        """
        Procesa todos los archivos de existencias para la fecha indicada.
        Si no se indica fecha, usa hoy.
        """
        if opts is None:
            opts = ExistenciasOrchestratorOptions()
        
        fecha = opts.fecha_contable or date.today()
        logger.info(f"Procesando existencias para la fecha: {fecha}")

        paths = self._obtener_paths_del_dia(fecha)
        if not paths:
            logger.warning(f"No se encontraron archivos para la fecha: {fecha}")
            return

        logger.info(f"Se encontraron {len(paths)} archivos para la fecha: {fecha}")

        archivos_origen = []
        archivos_con_error = []

        for path in paths:
            try:
                archivo = self._parser.parse(path)
                archivos_origen.append(archivo)
                logger.info(f"Archivo procesado: {path.name}")
            except Exception as e:
                logger.error(f"Error al procesar archivo: {path.name}: {e}")
                archivos_con_error.append((path, e))

        if not archivos_origen:
            logger.error(f"Ningun archivo pudo ser procesado para la fecha: {fecha}")
            for path, error in archivos_con_error:
                self._mover_a_errores(path, error)
            return
        
        logger.info(f"Agrupando {len(archivos_origen)} archivos por tipo_valor")
        planos_nacionales = self._aggregator.construir_planos_nacionales(archivos_origen)

        if not planos_nacionales:
            logger.warning(f"No se encontraron planos nacionales para la fecha: {fecha}")
            return

        logger.info(f"Se generaron {len(planos_nacionales)} planos nacionales")

        for plano in planos_nacionales:
            try:
                ruta = self._output.write_nacional(plano)
                logger.info(
                    f"Archivo nacional generado: {ruta.name}"
                    f"(tipo: {plano.tipo_valor.abreviatura})"
                    )
            except Exception as e:
                logger.error(f"Error generando nacional: {e}")
            
        for path in paths:
            if path not in [p for p, _ in archivos_con_error]:
                self._mover_a_gestionados(path)

        for path, error in archivos_con_error:
            self._mover_a_errores(path, error)

        logger.info(f"Proceso completado para la fecha: {fecha}")

    # ========== MÉTODOS PRIVADOS ==========
    def _obtener_paths_del_dia(self, fecha: date) -> list[Path]:
        """
        Obtiene los paths de todos los archivos de una fecha específica.
        
        Esta lógica antes estaba en ExistenciasParserService.obtener_archivos_del_dia()
        pero ahora la movemos aquí porque es responsabilidad del orchestrator
        coordinar CUÁLES archivos procesar.
        
        Args:
            fecha: Fecha contable a filtrar
            
        Returns:
            Lista de paths de archivos que coinciden con la fecha
        """
        todos_los_paths = self._reader.listar_archivos_en_origen()

        paths_del_dia = []
        for path in todos_los_paths:
            fecha_archivo = self._extraer_fecha_de_nombre(path.name)

            if fecha_archivo and fecha_archivo == fecha:
                paths_del_dia.append(path)
        
        return paths_del_dia
    
    def _extraer_fecha_de_nombre(self, nombre_archivo: str) -> date | None:
        """
        Extrae la fecha contable desde el nombre del archivo.
        
        Ejemplo: VYBUCTG2511210601EU.TXT
                        ^^^^^^
                      yymmdd en posiciones 7-12
        """
        fecha_contable = FechaContable.from_filename(nombre_archivo)
        return fecha_contable.value if fecha_contable else None

    def _mover_a_gestionados(self, path: Path) -> None:
        """
        Mueve un archivo procesado correctamente a la carpeta GESTIONADOS.
        
        Args:
            path: Ruta del archivo a mover
            
        Raises:
            Exception: Si no se puede mover el archivo (loguea el error)
        """
        try:
            destino_dir = self._paths.origen_gestionados
            destino_dir.mkdir(exist_ok=True)
            destino = destino_dir / path.name

            if destino.exists():
                logger.warning(f"Archivo ya existe en gestionados, sobreescribiendo: {destino.name}")
                destino.unlink()

            shutil.move(str(path), str(destino))
            logger.info(f"Archivo movido a gestionados: {destino.name}")
        except Exception as e:
            logger.error(f"Error moviendo archivo a gestionados: {path.name}: {e}")

    def _mover_a_errores(self, path: Path, error: Exception) -> None:
        """
        Mueve un archivo con errores a la carpeta ERRORES.
        
        Crea un archivo .log con el detalle del error para debugging.
        
        Args:
            path: Ruta del archivo con error
            error: Excepción capturada durante el procesamiento
            
        Raises:
            Exception: Si no se puede mover el archivo (loguea el error)
        """
        try:
            destino_dir = self._paths.origen_planos / "ERRORES"
            destino_dir.mkdir(exist_ok=True)
            destino = destino_dir / path.name

            if destino.exists():
                logger.warning(f"Archivo ya existe en errores, sobreescribiendo: {destino.name}")
                destino.unlink()

            shutil.move(str(path), str(destino))

            log_file = destino_dir / f"{path.stem}_error.log"
            with log_file.open("w", encoding="utf-8") as f:
                f.write(f"Archivo: {path.name}\n")
                f.write(f"Fecha procesamiento: {date.today()}\n")
                f.write(f"Error: {type(error).__name__}\n")
                f.write(f"Detalle: {str(error)}\n")

            logger.info(f"Archivo movido a errores: {destino.name}")
        except Exception as e:
            logger.error(f"Error moviendo archivo a errores: {path.name}: {e}")