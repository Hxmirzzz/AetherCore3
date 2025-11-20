from __future__ import annotations
from cgitb import handler
from pathlib import Path
import time
import logging
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.infrastructure.file_system.existencias_path_manager import ExistenciasPathManager

logger = logging.getLogger(__name__)


class _ExistenciasEventHandler(FileSystemEventHandler):
    """
    Handler para eventos del filesystem en la carpeta de PLANOS.
    Cuando llega un nuevo .txt, invoca un callback.
    """
    def __init__(self, on_new_file: Callable[[Path], None]) -> None:
        super().__init__()
        self._on_new_file = on_new_file

    def on_created(self, event):
        if event.is_directory:
            return
        p = Path(event.src_path)
        if p.suffix.lower() == ".txt":
            logger.info("Nuevo archivo: %s", p)
            self._on_new_file(p)

class ExistenciasFileWatcher:
    """
    Envoltorio alrededor de watchdog para monitorear la carpeta de PLANOS.
    """
    def __init__(self, path_manager: ExistenciasPathManager | None = None):
        self._paths = path_manager or ExistenciasPathManager.from_settings()
        self._observer = Observer | None = None


    def start(self, on_new_file: Callable[[Path], None]) -> None:
        """
        Inicia el watcher en la carpeta de PLANOS.

        on_new_file: callback que recibe la ruta del archivo nuevo.
        """
        carpeta = self._paths.origen_planos
        if not carpeta.exists():
            logger.warning("Carpeta de origen no existe, creando: %s", carpeta)
            carpeta.mkdir(parents=True, exist_ok=True)

        handler = _ExistenciasEventHandler(on_new_file)
        observer = Observer()
        observer.schedule(handler, str(carpeta), recursive=False)
        observer.start()
        self._observer = observer
        logger.info("FileWatcher de existencias iniciado en %s", carpeta)

    def stop(self) -> None:
        if self._observer is None:
            self._observer.stop()
            self._observer.join()
            logger.info("FileWatcher de existencias detenido")
            self._observer = None

    def run_forever(self, on_new_file: Callable[[Path], None]) -> None:
        """
        Loop bloqueante típico para modo servicio:
        watcher.run_forever(lambda p: ...).
        """
        self.start(on_new_file)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()