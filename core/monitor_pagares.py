"""
Monitor de Pagarés — lógica de watchdog extraída y unificada.

Vigila una carpeta en red y notifica cuando aparece un PDF nuevo.
"""

import os
import shutil
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
TEMP_DIR = os.path.join(os.getenv("TEMP"), "pdf_monitor_mude")

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


class _PDFHandler(FileSystemEventHandler):
    """Detecta archivos PDF nuevos en la carpeta vigilada."""

    def __init__(self, callback_nuevo_pdf):
        super().__init__()
        self._callback = callback_nuevo_pdf

    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith(".pdf"):
            return
        self._callback(event.src_path)


class MonitorPagares:
    """
    Encapsula la lógica de monitoreo de una carpeta.

    Uso:
        monitor = MonitorPagares(carpeta, callback_nuevo_pdf)
        monitor.iniciar()
        ...
        monitor.detener()
    """

    def __init__(self, carpeta: str, callback_nuevo_pdf):
        """
        Args:
            carpeta: ruta absoluta de la carpeta a vigilar.
            callback_nuevo_pdf: función(ruta_pdf: str) que se invocará
                                cada vez que aparezca un PDF nuevo.
        """
        self._carpeta = carpeta
        self._callback = callback_nuevo_pdf
        self._observer = None

    @property
    def activo(self) -> bool:
        return self._observer is not None and self._observer.is_alive()

    def iniciar(self):
        """Inicia el monitoreo en un hilo de fondo."""
        if self.activo:
            return
        handler = _PDFHandler(self._callback)
        self._observer = Observer()
        self._observer.schedule(handler, self._carpeta, recursive=False)
        self._observer.daemon = True
        self._observer.start()

    def detener(self):
        """Detiene el monitoreo."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=3)
            self._observer = None

    @staticmethod
    def abrir_en_edge(ruta_pdf: str) -> str:
        """
        Copia el PDF a una carpeta temporal local y lo abre en Edge.
        Retorna el nombre del archivo.
        """
        nombre = os.path.basename(ruta_pdf)
        destino = os.path.join(TEMP_DIR, nombre)
        shutil.copy2(ruta_pdf, destino)
        subprocess.Popen([EDGE_PATH, destino], shell=True)
        return nombre
