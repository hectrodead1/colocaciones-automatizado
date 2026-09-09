"""
Menú Principal — Ventana de selección de módulo.

Punto de entrada visual de la aplicación unificada MUDE.
Permite elegir entre Colocaciones y Pagarés.
"""

import tkinter as tk
from tkinter import font as tkfont


class MenuPrincipal(tk.Tk):
    """Ventana principal con los dos módulos disponibles."""

    ANCHO_VENTANA = 480
    ALTO_VENTANA = 380
    COLOR_FONDO = "#1a237e"
    COLOR_BLANCO = "#ffffff"
    COLOR_TEXTO_GRIS = "#b0bec5"
    COLOR_BTN_COLOCACIONES = "#1565c0"
    COLOR_BTN_PAGARES = "#2e7d32"
    COLOR_BTN_TEXTO = "#ffffff"

    def __init__(self):
        super().__init__()
        self._ventana_hija = None
        self._configurar_ventana()
        self._crear_widgets()

    def _configurar_ventana(self):
        self.title("Automatizador MUDE")
        self.configure(bg=self.COLOR_FONDO)
        self.resizable(False, False)

        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        x = (ancho - self.ANCHO_VENTANA) // 2
        y = (alto - self.ALTO_VENTANA) // 2
        self.geometry(f"{self.ANCHO_VENTANA}x{self.ALTO_VENTANA}+{x}+{y}")

    def _crear_widgets(self):
        # --- Título ---
        fuente_titulo = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        fuente_sub = tkfont.Font(family="Segoe UI", size=11)
        fuente_instruccion = tkfont.Font(family="Segoe UI", size=10)
        fuente_btn = tkfont.Font(family="Segoe UI", size=12, weight="bold")

        tk.Label(self, text="AUTOMATIZADOR MUDE",
                 font=fuente_titulo, bg=self.COLOR_FONDO,
                 fg=self.COLOR_BLANCO).pack(pady=(40, 4))

        tk.Label(self, text="Herramientas de automatización",
                 font=fuente_sub, bg=self.COLOR_FONDO,
                 fg=self.COLOR_TEXTO_GRIS).pack()

        tk.Label(self, text="Seleccione el módulo a utilizar:",
                 font=fuente_instruccion, bg=self.COLOR_FONDO,
                 fg=self.COLOR_BLANCO).pack(pady=(30, 15))

        # --- Botón Colocaciones ---
        btn_colocaciones = tk.Button(
            self, text="  📊  Carga de Colocaciones  ",
            font=fuente_btn,
            bg=self.COLOR_BTN_COLOCACIONES,
            fg=self.COLOR_BTN_TEXTO,
            activebackground="#1976d2",
            activeforeground=self.COLOR_BTN_TEXTO,
            relief=tk.FLAT, cursor="hand2",
            padx=30, pady=12,
            command=self._abrir_colocaciones
        )
        btn_colocaciones.pack(pady=(0, 12))

        # --- Botón Pagarés ---
        btn_pagares = tk.Button(
            self, text="  📄  Monitor de Pagarés  ",
            font=fuente_btn,
            bg=self.COLOR_BTN_PAGARES,
            fg=self.COLOR_BTN_TEXTO,
            activebackground="#388e3c",
            activeforeground=self.COLOR_BTN_TEXTO,
            relief=tk.FLAT, cursor="hand2",
            padx=30, pady=12,
            command=self._abrir_pagares
        )
        btn_pagares.pack()

    # ==================================================================
    # Navegación
    # ==================================================================

    def _abrir_colocaciones(self):
        """Oculta el menú y abre la ventana de colocaciones."""
        self.withdraw()
        from gui.app import AplicacionPrincipal
        self._ventana_hija = AplicacionPrincipal(self, al_cerrar=self._volver_desde_colocaciones)

    def _volver_desde_colocaciones(self):
        """Cierra colocaciones y vuelve al menú."""
        self._ventana_hija = None
        self.deiconify()

    def _abrir_pagares(self):
        """Oculta el menú y abre la ventana de pagarés."""
        self.withdraw()
        from gui.pagares import VentanaPagares
        self._ventana_hija = VentanaPagares(self, al_cerrar=self._volver_desde_pagares)

    def _volver_desde_pagares(self):
        """Cierra pagarés y vuelve al menú."""
        self._ventana_hija = None
        self.deiconify()
