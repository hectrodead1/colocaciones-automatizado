"""
Ventana del módulo de Pagarés — Monitor de PDFs por sucursal.

Permite al usuario vigilar hasta DOS carpetas simultáneamente,
escribir/seleccionar las carpetas de red, iniciar y detener el monitoreo,
y ver en tiempo real los PDFs detectados.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont
from datetime import datetime
from core.monitor_pagares import MonitorPagares


class VentanaPagares(tk.Toplevel):
    """Ventana del módulo de monitoreo de pagarés."""

    ANCHO_VENTANA = 720
    ALTO_VENTANA = 620
    COLOR_ENCABEZADO = "#1b5e20"
    COLOR_SUBTITULO = "#81c784"
    COLOR_FONDO = "#f5f7fa"
    COLOR_BLANCO = "#ffffff"
    COLOR_TEXTO = "#263238"
    COLOR_TEXTO_GRIS = "#90a4ae"
    COLOR_BTN_INICIAR = "#2e7d32"
    COLOR_BTN_DETENER = "#c62828"
    COLOR_BTN_CARPETA = "#546e7a"
    COLOR_BTN_TEXTO = "#ffffff"
    COLOR_EXITO = "#2e7d32"
    COLOR_ERROR = "#c62828"
    COLOR_INFO = "#1565c0"
    COLOR_STATUS_BG = "#eceff1"

    def __init__(self, master, al_cerrar):
        super().__init__(master)
        self._al_cerrar = al_cerrar
        self._monitor_1 = None
        self._monitor_2 = None

        self._configurar_ventana()
        self._crear_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)

    # ==================================================================
    # Configuración
    # ==================================================================

    def _configurar_ventana(self):
        self.title("Monitor de Pagarés — MUDE")
        self.configure(bg=self.COLOR_FONDO)
        self.resizable(False, False)

        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        x = (ancho - self.ANCHO_VENTANA) // 2
        y = (alto - self.ALTO_VENTANA) // 2
        self.geometry(f"{self.ANCHO_VENTANA}x{self.ALTO_VENTANA}+{x}+{y}")

    # ==================================================================
    # Widgets
    # ==================================================================

    def _crear_widgets(self):
        self._crear_encabezado()
        self._crear_seccion_carpeta("Carpeta 1:", 1)
        self._crear_seccion_carpeta("Carpeta 2 (opcional):", 2)
        self._crear_seccion_botones()
        self._crear_seccion_estado()

    def _crear_encabezado(self):
        frm = tk.Frame(self, bg=self.COLOR_ENCABEZADO, height=80)
        frm.pack(fill=tk.X)
        frm.pack_propagate(False)

        fuente_titulo = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        fuente_sub = tkfont.Font(family="Segoe UI", size=10)

        tk.Label(frm, text="MONITOR DE PAGARÉS",
                 font=fuente_titulo, bg=self.COLOR_ENCABEZADO,
                 fg=self.COLOR_BLANCO).pack(pady=(16, 0))
        tk.Label(frm, text="Detectar PDFs nuevos y abrir para imprimir",
                 font=fuente_sub, bg=self.COLOR_ENCABEZADO,
                 fg=self.COLOR_SUBTITULO).pack()

    # ------------------------------------------------------------------
    # Sección carpeta (reutilizable para carpeta 1 y 2)
    # ------------------------------------------------------------------

    def _crear_seccion_carpeta(self, label_text: str, numero: int):
        frm_wrapper = tk.Frame(self, bg=self.COLOR_FONDO)
        frm_wrapper.pack(fill=tk.X, padx=25, pady=(12, 0))

        frm = tk.Frame(frm_wrapper, bg=self.COLOR_BLANCO,
                        highlightbackground="#dce1e8", highlightthickness=1)
        frm.pack(fill=tk.X, ipady=8, ipadx=15)

        fuente_etiqueta = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        fuente_ruta = tkfont.Font(family="Segoe UI", size=9)

        tk.Label(frm, text=label_text,
                 font=fuente_etiqueta, bg=self.COLOR_BLANCO,
                 fg=self.COLOR_TEXTO, anchor="w").pack(fill=tk.X, padx=10, pady=(5, 2))

        frm_entrada = tk.Frame(frm, bg=self.COLOR_BLANCO)
        frm_entrada.pack(fill=tk.X, padx=10, pady=(0, 5))

        entry = tk.Entry(frm_entrada, font=fuente_ruta, relief=tk.SOLID, borderwidth=1)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        fuente_btn_sm = tkfont.Font(family="Segoe UI", size=9)
        btn_explorar = tk.Button(
            frm_entrada, text=" 📂 Explorar ",
            font=fuente_btn_sm, bg=self.COLOR_BTN_CARPETA,
            fg=self.COLOR_BTN_TEXTO, relief=tk.FLAT, cursor="hand2",
            command=lambda e=entry: self._explorar_carpeta(e)
        )
        btn_explorar.pack(side=tk.RIGHT, padx=(8, 0))

        # Guardar referencia al entry
        if numero == 1:
            self.entry_carpeta_1 = entry
        else:
            self.entry_carpeta_2 = entry

    # ------------------------------------------------------------------
    # Botones iniciar / detener
    # ------------------------------------------------------------------

    def _crear_seccion_botones(self):
        frm = tk.Frame(self, bg=self.COLOR_FONDO)
        frm.pack(fill=tk.X, padx=25, pady=12)

        fuente_btn = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        self.btn_iniciar = tk.Button(
            frm, text="  ▶  Iniciar Monitoreo  ", font=fuente_btn,
            bg=self.COLOR_BTN_INICIAR, fg=self.COLOR_BTN_TEXTO,
            activebackground="#388e3c", relief=tk.FLAT, cursor="hand2",
            padx=20, pady=8, command=self._iniciar_monitoreo
        )
        self.btn_iniciar.pack(side=tk.LEFT, expand=True)

        self.btn_detener = tk.Button(
            frm, text="  ⏹  Detener Monitoreo  ", font=fuente_btn,
            bg=self.COLOR_BTN_DETENER, fg=self.COLOR_BTN_TEXTO,
            activebackground="#d32f2f", relief=tk.FLAT, cursor="hand2",
            padx=20, pady=8, state=tk.DISABLED,
            command=self._detener_monitoreo
        )
        self.btn_detener.pack(side=tk.RIGHT, expand=True)

    # ------------------------------------------------------------------
    # Área de estado
    # ------------------------------------------------------------------

    def _crear_seccion_estado(self):
        frm_estado = tk.Frame(self, bg=self.COLOR_FONDO)
        frm_estado.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))

        fuente_etiqueta = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        tk.Label(frm_estado, text="Estado:", font=fuente_etiqueta,
                 bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
                 anchor="w").pack(fill=tk.X, pady=(0, 4))

        frm_texto = tk.Frame(frm_estado, bg=self.COLOR_STATUS_BG,
                              highlightbackground="#dce1e8", highlightthickness=1)
        frm_texto.pack(fill=tk.BOTH, expand=True)

        fuente_estado = tkfont.Font(family="Consolas", size=9)
        self.txt_estado = tk.Text(
            frm_texto, font=fuente_estado, bg=self.COLOR_STATUS_BG,
            fg=self.COLOR_TEXTO, wrap=tk.WORD, relief=tk.FLAT,
            state=tk.DISABLED, padx=10, pady=8, height=10
        )
        self.txt_estado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frm_texto, orient=tk.VERTICAL,
                                   command=self.txt_estado.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_estado.configure(yscrollcommand=scrollbar.set)

        self.txt_estado.tag_configure("info", foreground=self.COLOR_INFO)
        self.txt_estado.tag_configure("exito", foreground=self.COLOR_EXITO)
        self.txt_estado.tag_configure("error", foreground=self.COLOR_ERROR)

        self._agregar_estado(
            "Escriba o seleccione las carpetas de pagarés y presione Iniciar Monitoreo.", "info"
        )

    # ==================================================================
    # Acciones
    # ==================================================================

    def _explorar_carpeta(self, entry_widget):
        ruta = filedialog.askdirectory(title="Seleccionar carpeta de pagarés")
        if ruta:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, ruta)

    def _iniciar_monitoreo(self):
        import os

        carpeta_1 = self.entry_carpeta_1.get().strip()
        carpeta_2 = self.entry_carpeta_2.get().strip()

        if not carpeta_1 and not carpeta_2:
            messagebox.showwarning("Carpetas vacías",
                                    "Debe escribir o seleccionar al menos una carpeta.")
            return

        # Validar carpeta 1
        if carpeta_1 and not os.path.isdir(carpeta_1):
            messagebox.showerror("Carpeta 1 no encontrada",
                                  f"La carpeta 1 no existe o no es accesible:\n\n{carpeta_1}")
            return

        # Validar carpeta 2 (solo si se escribió algo)
        if carpeta_2 and not os.path.isdir(carpeta_2):
            messagebox.showerror("Carpeta 2 no encontrada",
                                  f"La carpeta 2 no existe o no es accesible:\n\n{carpeta_2}")
            return

        # Iniciar monitor 1
        if carpeta_1:
            self._monitor_1 = MonitorPagares(carpeta_1, self._on_nuevo_pdf)
            self._monitor_1.iniciar()
            self._agregar_estado(f"🟢 Monitoreo activo — Carpeta 1: {carpeta_1}", "exito")

        # Iniciar monitor 2
        if carpeta_2:
            self._monitor_2 = MonitorPagares(carpeta_2, self._on_nuevo_pdf)
            self._monitor_2.iniciar()
            self._agregar_estado(f"🟢 Monitoreo activo — Carpeta 2: {carpeta_2}", "exito")

        self.btn_iniciar.configure(state=tk.DISABLED)
        self.btn_detener.configure(state=tk.NORMAL)
        self.entry_carpeta_1.configure(state=tk.DISABLED)
        self.entry_carpeta_2.configure(state=tk.DISABLED)

    def _detener_monitoreo(self):
        if self._monitor_1:
            self._monitor_1.detener()
            self._monitor_1 = None

        if self._monitor_2:
            self._monitor_2.detener()
            self._monitor_2 = None

        self.btn_iniciar.configure(state=tk.NORMAL)
        self.btn_detener.configure(state=tk.DISABLED)
        self.entry_carpeta_1.configure(state=tk.NORMAL)
        self.entry_carpeta_2.configure(state=tk.NORMAL)
        self._agregar_estado("🔴 Monitoreo detenido.", "error")

    def _on_nuevo_pdf(self, ruta_pdf):
        """Callback invocado desde el hilo de watchdog cuando aparece un PDF."""
        self.after(0, lambda: self._procesar_nuevo_pdf(ruta_pdf))

    def _procesar_nuevo_pdf(self, ruta_pdf):
        import os
        nombre = os.path.basename(ruta_pdf)
        carpeta = os.path.dirname(ruta_pdf)
        self._agregar_estado(f"📄 PDF detectado: {nombre}  (de: {os.path.basename(carpeta)})", "exito")

        respuesta = messagebox.askyesno(
            "Nuevo PDF detectado",
            f"¿Desea abrir para imprimir?\n\n{nombre}",
            parent=self
        )

        if respuesta:
            try:
                nombre_abierto = MonitorPagares.abrir_en_edge(ruta_pdf)
                self._agregar_estado(f"   ✅ Abierto en Edge: {nombre_abierto}", "exito")
            except Exception as e:
                self._agregar_estado(f"   ❌ Error al abrir: {e}", "error")
        else:
            self._agregar_estado(f"   ⏭ Omitido por el usuario.", "info")

    def _on_cerrar(self):
        if self._monitor_1 and self._monitor_1.activo:
            self._monitor_1.detener()
        if self._monitor_2 and self._monitor_2.activo:
            self._monitor_2.detener()
        self.destroy()
        self._al_cerrar()

    # ==================================================================
    # Utilidades
    # ==================================================================

    def _agregar_estado(self, mensaje: str, tipo: str = "info"):
        self.txt_estado.configure(state=tk.NORMAL)
        hora = datetime.now().strftime("%H:%M:%S")
        linea = f"[{hora}] {mensaje}\n"
        self.txt_estado.insert(tk.END, linea, tipo)
        self.txt_estado.see(tk.END)
        self.txt_estado.configure(state=tk.DISABLED)
