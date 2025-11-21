from __future__ import annotations
import argparse
from datetime import date, datetime
from pathlib import Path
import logging

from src.application.orchestrators.existencias_orchestrator import (
    ExistenciasProcessingOrchestrator,
    ExistenciasOrchestratorOptions,
)
from src.application.services.existencias_parser_service import ExistenciasParserService
from src.application.services.existencias_aggregator_service import ExistenciasAggregatorService
from src.application.services.existencias_output_service import ExistenciasOutputService
from src.infrastructure.file_system.existencias_txt_reader import ExistenciasTxtReader
from src.infrastructure.file_system.existencias_txt_writer import ExistenciasTxtWriter
from src.infrastructure.file_system.existencias_path_manager import ExistenciasPathManager
from src.infrastructure.watchdog.existencias_file_watcher import ExistenciasFileWatcher

logger = logging.getLogger(__name__)

# ---------- Helpers ----------

def _parse_fecha_arg(fecha_str: str | None) -> date | None:
    """
    Acepta:
      - '251120' -> ddmmyy
      - '2025-11-25' -> yyyy-mm-dd
    Si es None, usamos hoy.
    """
    if not fecha_str:
        return None

    fecha_str = fecha_str.strip()
    if len(fecha_str) == 6:
        # ddmmyy
        return datetime.strptime(fecha_str, "%y%m%d").date()
    elif len(fecha_str) == 10 and "-" in fecha_str:
        # yyyy-mm-dd
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()

    raise ValueError(f"Formato de fecha no soportado: {fecha_str}")


def _extract_fecha_from_filename(nombre: str) -> Optional[date]:
    fecha_contable = FechaContable.from_filename(nombre)
    return fecha_contable.value if fecha_contable else None

def build_orchestrator() -> ExistenciasProcessingOrchestrator:
    """
    Arma el grafo mínimo de dependencias para el caso de uso.
    Ajusta las firmas si tus servicios/constructores cambian.
    """
    paths = ExistenciasPathManager.from_settings()

    # Infraestructura
    reader = ExistenciasTxtReader(paths)
    writer = ExistenciasTxtWriter(paths)

    # Aplicación
    parser = ExistenciasParserService(reader)
    aggregator = ExistenciasAggregatorService()
    output = ExistenciasOutputService(writer)

    return ExistenciasProcessingOrchestrator(
        parser=parser,
        aggregator=aggregator,
        output=output,
        reader=reader,
        path_manager=paths,
    )

# ---------- Modo watcher ----------
def run_watcher(orchestrator: ExistenciasProcessingOrchestrator) -> None:
    watcher = ExistenciasFileWatcher()

    def on_new_existencias_file(path: Path):
        logger.info("Nuevo archivo de existencias: %s", path)
        
        fecha = _extract_fecha_from_filename(path.name)
        if fecha is None:
            fecha = date.today()
        
        opst = ExistenciasOrchestratorOptions(fecha_contable=fecha)
        orchestrator.procesar_dia(opst)

    watcher.run_forever(on_new_existencias_file)

# ---------- main CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Procesador de existencias (origen -> nacional)")
    parser.add_argument("--watch", action="store_true", help="Modo watcher (24/7)")
    parser.add_argument("--fecha", type=str, help="Fecha contable (ddmmyy o yyyy-mm-dd)")
    # FUTURO: parser.add_argument("--all", action="store_true", help="Procesar todas las fechas disponibles.")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    orch = build_orchestrator()

    if args.watch:
        run_watcher(orch)
    else:
        fecha = _parse_fecha_arg(args.fecha) if args.fecha else date.today()
        opst = ExistenciasOrchestratorOptions(fecha_contable=fecha)
        orch.procesar_dia(opst)

if __name__ == "__main__":
    main()
