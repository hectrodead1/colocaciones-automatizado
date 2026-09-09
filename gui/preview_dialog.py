"""
Diálogo de vista previa para confirmar el procesamiento del archivo.

Muestra un resumen con la información del archivo antes de ejecutar
el proceso de carga de colocaciones.
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
from pathlib import Path

from core.file_manager import GestorArchivos


class PreviewDialog(tk.Toplevel):
    """
    Diálogo modal que muestra una vista previa de los datos
    antes de procesar el archivo de colocaciones.
    """

    # --- Constantes de diseño ---
    ANCHO_VENTANA = 480
    ALTO_VENTANA = 400
    COLOR_FONDO = "#ffffff"
    COLOR_ENCABEZADO = "#1a237e"
    COLOR_TEXTO_ENCABEZADO = "#ffffff"
    COLOR_CARD = "#f5f7fa"
    COLOR_BORDE_CARD = "#dce1e8"
    COLOR_ETIQUETA = "#546e7a"
    COLOR_VALOR = "#1a237e"
    COLOR_BTN_PROCESAR = "#2e7d32"
    COLOR_BTN_CANCELAR = "#c62828"
    COLOR_BTN_TEXTO = "#ffffff"

    def __init__(self, parent, filepath: str, datos_validacion: dict):
        """
        Inicializa el diálogo de vista previa.

        Args:
            parent: Ventana padre (AplicacionPrincipal).
            filepath: Ruta completa del archivo de entrada.
            datos_validacion: Diccionario con los datos de la validación
                              (num_registros, duplicados, errores, etc.).
        """
        super().__init__(parent)
        self.confirmed = False
        self.filepath = filepath
        self.datos = datos_validacion

        # Generar nombre de archivo de salida para mostrarlo en la vista previa
        gestor = GestorArchivos()
        self.ruta_salida = gestor.generar_ruta_salida()

        self._configurar_ventana(parent)
        self._crear_widgets()

        # Hacer el diálogo modal y siempre arriba
        self.transient(parent)
        self.attributes('-topmost', True)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancelar)
        self.wait_window(self)

    # ------------------------------------------------------------------
    # Configuración de la ventana
    # ------------------------------------------------------------------

    def _configurar_ventana(self, parent):
        """Configura el tamaño, posición y propiedades de la ventana."""
        self.title("Vista Previa")
        self.configure(bg=self.COLOR_FONDO)
        self.resizable(False, False)

        # Centrar respecto a la ventana padre
        parent.update_idletasks()
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - self.ANCHO_VENTANA) // 2
        y = py + (ph - self.ALTO_VENTANA) // 2
        self.geometry(f"{self.ANCHO_VENTANA}x{self.ALTO_VENTANA}+{x}+{y}")

    # ------------------------------------------------------------------
    # Creación de widgets
    # ------------------------------------------------------------------

    def _crear_widgets(self):
        """Construye toda la interfaz del diálogo de vista previa."""
        self._crear_encabezado()
        self._crear_tarjeta_resumen()
        self._crear_botones()

    def _crear_encabezado(self):
        """Crea la sección del encabezado con el título."""
        frm_encabezado = tk.Frame(
            self, bg=self.COLOR_ENCABEZADO, height=55
        )
        frm_encabezado.pack(fill=tk.X)
        frm_encabezado.pack_propagate(False)

        fuente_titulo = tkfont.Font(family="Segoe UI", size=15, weight="bold")
        tk.Label(
            frm_encabezado,
            text="📋  VISTA PREVIA",
            font=fuente_titulo,
            bg=self.COLOR_ENCABEZADO,
            fg=self.COLOR_TEXTO_ENCABEZADO,
        ).pack(expand=True)

    def _crear_tarjeta_resumen(self):
        """Crea la tarjeta con el resumen de la información del archivo."""
        # Contenedor con margen
        frm_contenido = tk.Frame(self, bg=self.COLOR_FONDO)
        frm_contenido.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Tarjeta (card) con borde suave
        tarjeta = tk.Frame(
            frm_contenido,
            bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_BORDE_CARD,
            highlightthickness=1,
        )
        tarjeta.pack(fill=tk.BOTH, expand=True)

        # Contenido de la tarjeta con padding interno
        interior = tk.Frame(tarjeta, bg=self.COLOR_CARD)
        interior.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # --- Filas de información ---
        nombre_archivo = Path(self.filepath).name
        num_registros = self.datos.get("num_registros", 0)
        lista_duplicados = self.datos.get("duplicados", [])
        num_duplicados = len(lista_duplicados)
        errores = 0  # Si llegó hasta aquí, no hay errores fatales
        nombre_salida = self.ruta_salida.name

        filas = [
            ("Archivo seleccionado:", nombre_archivo),
            ("Registros encontrados:", str(num_registros)),
            ("Préstamos duplicados:", str(num_duplicados)),
            ("Errores:", str(errores)),
            ("Archivo de salida:", nombre_salida),
        ]

        fuente_etiqueta = tkfont.Font(family="Segoe UI", size=9)
        fuente_valor = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        for i, (etiqueta, valor) in enumerate(filas):
            frm_fila = tk.Frame(interior, bg=self.COLOR_CARD)
            frm_fila.pack(fill=tk.X, pady=(0 if i == 0 else 8, 0))

            tk.Label(
                frm_fila,
                text=etiqueta,
                font=fuente_etiqueta,
                bg=self.COLOR_CARD,
                fg=self.COLOR_ETIQUETA,
                anchor="w",
            ).pack(fill=tk.X)

            tk.Label(
                frm_fila,
                text=valor,
                font=fuente_valor,
                bg=self.COLOR_CARD,
                fg=self.COLOR_VALOR,
                anchor="w",
            ).pack(fill=tk.X)

    def _crear_botones(self):
        """Crea los botones de acción: Procesar y Cancelar."""
        frm_botones = tk.Frame(self, bg=self.COLOR_FONDO)
        frm_botones.pack(fill=tk.X, padx=30, pady=(0, 20))

        fuente_btn = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        # Botón Procesar
        btn_procesar = tk.Button(
            frm_botones,
            text="  ✅  Procesar  ",
            font=fuente_btn,
            bg=self.COLOR_BTN_PROCESAR,
            fg=self.COLOR_BTN_TEXTO,
            activebackground="#388e3c",
            activeforeground=self.COLOR_BTN_TEXTO,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._confirmar,
        )
        btn_procesar.pack(side=tk.LEFT, expand=True, padx=(0, 10))

        # Botón Cancelar
        btn_cancelar = tk.Button(
            frm_botones,
            text="  ❌  Cancelar  ",
            font=fuente_btn,
            bg=self.COLOR_BTN_CANCELAR,
            fg=self.COLOR_BTN_TEXTO,
            activebackground="#d32f2f",
            activeforeground=self.COLOR_BTN_TEXTO,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._cancelar,
        )
        btn_cancelar.pack(side=tk.RIGHT, expand=True, padx=(10, 0))

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _confirmar(self):
        """El usuario confirma el procesamiento."""
        self.confirmed = True
        self.destroy()

    def _cancelar(self):
        """El usuario cancela el procesamiento."""
        self.confirmed = False
        self.destroy()
