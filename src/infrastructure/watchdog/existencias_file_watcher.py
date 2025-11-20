from __future__ import annotations
from pathlib import Path
import logging
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.infrastructure.file_system.existencias_path_manager import ExistenciasPathManager

logger = logging.getLogger(__name__)


class ExistenciasEventHandler(FileSystemEventHandler):
    """
    Handler de eventos del sistema de archivos para existencias.

    Llama a un callback(path: Path) cada vez que se crea un .txt
    en la carpeta de origen (PLANOS).
    """

    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def on_created(self, event):
        # Ignorar directorios
        if event.is_directory:
            return

        path = Path(event.src_path)
        # Solo nos interesan archivos .txt
        if path.suffix.lower() != ".txt":
            return

        logger.info("Nuevo archivo de existencias detectado: %s", path)
        try:
            self._callback(path)
        except Exception:
            logger.exception("Error ejecutando callback para archivo: %s", path)


class ExistenciasFileWatcher:
    """
    Encapsula el Observer de watchdog para monitorear la carpeta de PLANOS.

    - Observa la carpeta origen_planos
    - Llama al callback cuando se crea un archivo .txt
    """

    def __init__(self, path_manager: ExistenciasPathManager | None = None) -> None:
        self._paths = path_manager or ExistenciasPathManager.from_settings()
        self._observer: Observer | None = None

    def run_forever(self, callback) -> None:
        """
        Inicia el watcher y se queda en loop infinito hasta Ctrl+C.
        """
        carpeta = self._paths.origen_planos

        if not carpeta.exists():
            logger.warning("Carpeta de origen para watcher no existe: %s", carpeta)
            carpeta.mkdir(parents=True, exist_ok=True)

        event_handler = ExistenciasEventHandler(callback)

        observer = Observer()
        observer.schedule(event_handler, str(carpeta), recursive=False)
        observer.start()
        self._observer = observer

        logger.info("Watcher de existencias iniciado en: %s", carpeta)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Watcher detenido por KeyboardInterrupt")
        finally:
            observer.stop()
            observer.join()
            logger.info("Watcher de existencias finalizado")