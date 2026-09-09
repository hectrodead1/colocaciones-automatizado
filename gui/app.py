"""
Módulo principal de la interfaz gráfica del Automatizador de Colocaciones BHD-MUDE.

Contiene la ventana principal de la aplicación con todas las secciones:
encabezado, selección de archivo, botones de acción y área de estado.
"""

import os
import subprocess
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont
from pathlib import Path
from datetime import datetime

from config import obtener_carpeta_salida, guardar_carpeta_salida
from core.validator import ValidadorArchivo
from core.processor import Procesador
from core.processor_banreservas import ProcesadorBanreservas
from core.file_manager import GestorArchivos
from core.registry import RegistroMensual
from utils.logger import iniciar_log, log_info, log_error, finalizar_log

# Se removió la importación de PreviewDialog para usar el nativo del SO


class AplicacionPrincipal(tk.Toplevel):
    """
    Ventana principal del Automatizador de Colocaciones BHD-MUDE.
    """

    # --- Constantes de diseño ---
    ANCHO_VENTANA = 700
    ALTO_VENTANA = 690
    COLOR_ENCABEZADO = "#1a237e"
    COLOR_SUBTITULO = "#7986cb"
    COLOR_FONDO = "#f5f7fa"
    COLOR_BLANCO = "#ffffff"
    COLOR_TEXTO = "#263238"
    COLOR_TEXTO_GRIS = "#90a4ae"
    COLOR_BTN_PRINCIPAL = "#1565c0"
    COLOR_BTN_CARPETA = "#546e7a"
    COLOR_BTN_TEXTO = "#ffffff"
    COLOR_EXITO = "#2e7d32"
    COLOR_ERROR = "#c62828"
    COLOR_INFO = "#1565c0"
    COLOR_STATUS_BG = "#eceff1"

    def __init__(self, master=None, al_cerrar=None):
        """Inicializa la ventana principal y todos sus componentes."""
        super().__init__(master)
        self._al_cerrar = al_cerrar
        self.archivo_seleccionado: str | None = None
        # Cargar carpetas dinámicas de ambos bancos
        from config import obtener_carpetas_salida
        self.carpetas_salida = obtener_carpetas_salida()
        self.carpeta_salida = self.carpetas_salida["BHD"]

        self._configurar_ventana()
        self._crear_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)

    # ==================================================================
    # Configuración de la ventana
    # ==================================================================

    def _configurar_ventana(self):
        """Configura el título, tamaño, posición y restricciones de la ventana."""
        self.title("Automatizador de Colocaciones BHD - MUDE")
        self.configure(bg=self.COLOR_FONDO)
        self.resizable(False, False)

        # Centrar la ventana en la pantalla
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        x = (ancho_pantalla - self.ANCHO_VENTANA) // 2
        y = (alto_pantalla - self.ALTO_VENTANA) // 2
        self.geometry(f"{self.ANCHO_VENTANA}x{self.ALTO_VENTANA}+{x}+{y}")

        # Intentar establecer icono (no crítico si falla)
        try:
            self.iconbitmap(default="")
        except tk.TclError:
            pass

    # ==================================================================
    # Creación de widgets
    # ==================================================================

    def _crear_widgets(self):
        """Construye todas las secciones de la interfaz gráfica."""
        self._crear_encabezado()
        self._crear_seccion_banco()
        self._crear_seccion_archivo()
        self._crear_seccion_carpeta_salida()
        self._crear_seccion_botones()
        self._crear_seccion_estado()

    # ------------------------------------------------------------------
    # 1. Encabezado
    # ------------------------------------------------------------------

    def _crear_encabezado(self):
        """Crea la sección superior con el título y subtítulo de la aplicación."""
        frm_encabezado = tk.Frame(self, bg=self.COLOR_ENCABEZADO, height=90)
        frm_encabezado.pack(fill=tk.X)
        frm_encabezado.pack_propagate(False)

        fuente_titulo = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        fuente_subtitulo = tkfont.Font(family="Segoe UI", size=11)

        tk.Label(
            frm_encabezado,
            text="AUTOMATIZADOR DE COLOCACIONES",
            font=fuente_titulo,
            bg=self.COLOR_ENCABEZADO,
            fg=self.COLOR_BLANCO,
        ).pack(pady=(18, 0))

        tk.Label(
            frm_encabezado,
            text="BHD — MUDE",
            font=fuente_subtitulo,
            bg=self.COLOR_ENCABEZADO,
            fg=self.COLOR_SUBTITULO,
        ).pack()

    # ------------------------------------------------------------------
    # 1b. Selección de Banco
    # ------------------------------------------------------------------

    def _crear_seccion_banco(self):
        """Crea la sección de selección de banco al inicio."""
        frm_banco_wrapper = tk.Frame(self, bg=self.COLOR_FONDO)
        frm_banco_wrapper.pack(fill=tk.X, padx=25, pady=(15, 0))
        
        frm_interior = tk.Frame(
            frm_banco_wrapper,
            bg=self.COLOR_BLANCO,
            highlightbackground="#dce1e8",
            highlightthickness=1,
        )
        frm_interior.pack(fill=tk.X, ipady=8, ipadx=15)
        
        fuente_etiqueta = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        fuente_radio = tkfont.Font(family="Segoe UI", size=9)
        
        tk.Label(
            frm_interior,
            text="Seleccione el banco a procesar:",
            font=fuente_etiqueta,
            bg=self.COLOR_BLANCO,
            fg=self.COLOR_TEXTO,
            anchor="w",
        ).pack(fill=tk.X, padx=10, pady=(5, 2))
        
        self.banco_seleccionado = tk.StringVar(master=self, value="BHD")
        
        frm_radios = tk.Frame(frm_interior, bg=self.COLOR_BLANCO)
        frm_radios.pack(fill=tk.X, padx=10)
        
        rb_bhd = tk.Radiobutton(
            frm_radios,
            text="BHD",
            variable=self.banco_seleccionado,
            value="BHD",
            font=fuente_radio,
            bg=self.COLOR_BLANCO,
            fg=self.COLOR_TEXTO,
            activebackground=self.COLOR_BLANCO,
            command=self._al_cambiar_banco
        )
        rb_bhd.pack(side=tk.LEFT, padx=(0, 20))
        
        rb_reservas = tk.Radiobutton(
            frm_radios,
            text="BANRESERVAS",
            variable=self.banco_seleccionado,
            value="BANRESERVAS",
            font=fuente_radio,
            bg=self.COLOR_BLANCO,
            fg=self.COLOR_TEXTO,
            activebackground=self.COLOR_BLANCO,
            command=self._al_cambiar_banco
        )
        rb_reservas.pack(side=tk.LEFT)
        
    def _al_cambiar_banco(self):
        """Manejador del cambio de banco seleccionado."""
        banco = self.banco_seleccionado.get()
        self.carpeta_salida = self.carpetas_salida[banco]
        self.lbl_carpeta_salida.configure(text=str(self.carpeta_salida))
        self._agregar_estado(f"Banco seleccionado: {banco}. Carpeta de salida actual: {self.carpeta_salida}", "info")

    # ------------------------------------------------------------------
    # 2. Selección de archivo
    # ------------------------------------------------------------------

    def _crear_seccion_archivo(self):
        """Crea la sección de selección de archivo con etiqueta y botón."""
        frm_archivo = tk.Frame(self, bg=self.COLOR_BLANCO)
        frm_archivo.pack(fill=tk.X, padx=25, pady=(20, 0))

        # Borde redondeado simulado con highlight
        frm_interior = tk.Frame(
            frm_archivo,
            bg=self.COLOR_BLANCO,
            highlightbackground="#dce1e8",
            highlightthickness=1,
        )
        frm_interior.pack(fill=tk.X, ipady=12, ipadx=15)

        fuente_etiqueta = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        fuente_ruta = tkfont.Font(family="Segoe UI", size=9)

        tk.Label(
            frm_interior,
            text="Archivo seleccionado:",
            font=fuente_etiqueta,
            bg=self.COLOR_BLANCO,
            fg=self.COLOR_TEXTO,
            anchor="w",
        ).pack(fill=tk.X, padx=10, pady=(5, 0))

        # Etiqueta para mostrar la ruta del archivo (o texto predeterminado)
        self.lbl_ruta = tk.Label(
            frm_interior,
            text="Ningún archivo seleccionado",
            font=fuente_ruta,
            bg=self.COLOR_BLANCO,
            fg=self.COLOR_TEXTO_GRIS,
            anchor="w",
        )
        self.lbl_ruta.pack(fill=tk.X, padx=10, pady=(2, 5))

        # Botón para abrir el diálogo de selección de archivo
        fuente_btn = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        btn_seleccionar = tk.Button(
            frm_interior,
            text="  📂  Seleccionar Archivo  ",
            font=fuente_btn,
            bg=self.COLOR_BTN_PRINCIPAL,
            fg=self.COLOR_BTN_TEXTO,
            activebackground="#1976d2",
            activeforeground=self.COLOR_BTN_TEXTO,
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=6,
            command=self._seleccionar_archivo,
        )
        btn_seleccionar.pack(pady=(5, 5))

    # ------------------------------------------------------------------
    # 2b. Selección de carpeta de salida
    # ------------------------------------------------------------------

    def _crear_seccion_carpeta_salida(self):
        """Crea la sección para ver y modificar permanentemente la carpeta de salida."""
        frm_salida = tk.Frame(self, bg=self.COLOR_BLANCO)
        frm_salida.pack(fill=tk.X, padx=25, pady=(15, 0))

        frm_interior = tk.Frame(
            frm_salida,
            bg=self.COLOR_BLANCO,
            highlightbackground="#dce1e8",
            highlightthickness=1,
        )
        frm_interior.pack(fill=tk.X, ipady=10, ipadx=15)

        fuente_etiqueta = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        fuente_ruta = tkfont.Font(family="Segoe UI", size=9)

        tk.Label(
            frm_interior,
            text="Carpeta de salida donde se guardará el archivo generado:",
            font=fuente_etiqueta,
            bg=self.COLOR_BLANCO,
            fg=self.COLOR_TEXTO,
            anchor="w",
        ).pack(fill=tk.X, padx=10, pady=(5, 0))

        # Etiqueta para mostrar la carpeta de salida actual
        self.lbl_carpeta_salida = tk.Label(
            frm_interior,
            text=str(self.carpeta_salida),
            font=fuente_ruta,
            bg=self.COLOR_BLANCO,
            fg=self.COLOR_TEXTO,
            anchor="w",
            wraplength=620,
            justify=tk.LEFT
        )
        self.lbl_carpeta_salida.pack(fill=tk.X, padx=10, pady=(2, 5))

        # Botón para cambiar la carpeta
        fuente_btn = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        btn_cambiar = tk.Button(
            frm_interior,
            text="  ⚙️  Cambiar Carpeta de Salida Permanentemente  ",
            font=fuente_btn,
            bg=self.COLOR_BTN_CARPETA,
            fg=self.COLOR_BTN_TEXTO,
            activebackground="#607d8b",
            activeforeground=self.COLOR_BTN_TEXTO,
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._cambiar_carpeta_salida,
        )
        btn_cambiar.pack(pady=(5, 5))

    def _cambiar_carpeta_salida(self):
        """Abre el diálogo para seleccionar una nueva carpeta de salida de forma permanente."""
        nueva_ruta = filedialog.askdirectory(
            title="Seleccionar Carpeta de Salida",
            initialdir=str(self.carpeta_salida)
        )
        if nueva_ruta:
            p_ruta = Path(nueva_ruta)
            banco = self.banco_seleccionado.get()
            
            # Actualizar en memoria
            self.carpeta_salida = p_ruta
            self.carpetas_salida[banco] = p_ruta
            self.lbl_carpeta_salida.configure(text=str(p_ruta))
            
            # Guardar permanentemente en config.json
            from config import guardar_carpeta_salida_banco
            guardar_carpeta_salida_banco(banco, p_ruta)
            
            self._agregar_estado(f"Carpeta de salida para {banco} cambiada permanentemente a: {p_ruta}", "exito")
            messagebox.showinfo("Carpeta Guardada", f"La carpeta de salida para {banco} se ha cambiado permanentemente a:\n\n{p_ruta}")

    # ------------------------------------------------------------------
    # 3. Botones de acción
    # ------------------------------------------------------------------

    def _crear_seccion_botones(self):
        """Crea la sección de botones: Procesar y Abrir Carpeta de Salida."""
        frm_botones = tk.Frame(self, bg=self.COLOR_FONDO)
        frm_botones.pack(fill=tk.X, padx=25, pady=18)

        fuente_btn = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        # Botón Procesar (deshabilitado hasta seleccionar archivo)
        self.btn_procesar = tk.Button(
            frm_botones,
            text="  ⚙️  Procesar  ",
            font=fuente_btn,
            bg=self.COLOR_BTN_PRINCIPAL,
            fg=self.COLOR_BTN_TEXTO,
            activebackground="#1976d2",
            activeforeground=self.COLOR_BTN_TEXTO,
            disabledforeground="#b0bec5",
            relief=tk.FLAT,
            cursor="hand2",
            padx=25,
            pady=8,
            state=tk.DISABLED,
            command=self._procesar_archivo,
        )
        self.btn_procesar.pack(side=tk.LEFT, expand=True)

        # Botón Abrir Carpeta de Salida
        btn_carpeta = tk.Button(
            frm_botones,
            text="  📁  Abrir Carpeta de Salida  ",
            font=fuente_btn,
            bg=self.COLOR_BTN_CARPETA,
            fg=self.COLOR_BTN_TEXTO,
            activebackground="#607d8b",
            activeforeground=self.COLOR_BTN_TEXTO,
            relief=tk.FLAT,
            cursor="hand2",
            padx=25,
            pady=8,
            command=self._abrir_carpeta_salida,
        )
        btn_carpeta.pack(side=tk.RIGHT, expand=True)

    # ------------------------------------------------------------------
    # 4. Área de estado
    # ------------------------------------------------------------------

    def _crear_seccion_estado(self):
        """Crea el área de mensajes de estado (scrollable) en la parte inferior."""
        frm_estado = tk.Frame(self, bg=self.COLOR_FONDO)
        frm_estado.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))

        fuente_etiqueta = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        tk.Label(
            frm_estado,
            text="Estado:",
            font=fuente_etiqueta,
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        # Área de texto para los mensajes de estado
        frm_texto = tk.Frame(
            frm_estado,
            bg=self.COLOR_STATUS_BG,
            highlightbackground="#dce1e8",
            highlightthickness=1,
        )
        frm_texto.pack(fill=tk.BOTH, expand=True)

        fuente_estado = tkfont.Font(family="Consolas", size=9)

        self.txt_estado = tk.Text(
            frm_texto,
            font=fuente_estado,
            bg=self.COLOR_STATUS_BG,
            fg=self.COLOR_TEXTO,
            wrap=tk.WORD,
            relief=tk.FLAT,
            state=tk.DISABLED,
            padx=10,
            pady=8,
            height=8,
        )
        self.txt_estado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(
            frm_texto, orient=tk.VERTICAL, command=self.txt_estado.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_estado.configure(yscrollcommand=scrollbar.set)

        # Configurar etiquetas de color para los mensajes
        self.txt_estado.tag_configure("info", foreground=self.COLOR_INFO)
        self.txt_estado.tag_configure("exito", foreground=self.COLOR_EXITO)
        self.txt_estado.tag_configure("error", foreground=self.COLOR_ERROR)

        # Mensaje inicial
        self._agregar_estado(
            "Listo. Seleccione un archivo Excel (.xlsx) para comenzar.", "info"
        )

    # ==================================================================
    # Métodos de acción
    # ==================================================================

    def _seleccionar_archivo(self):
        """Abre el diálogo de selección de archivo y actualiza la interfaz."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de colocaciones",
            filetypes=[
                ("Archivos Excel", "*.xlsx"),
                ("Todos los archivos", "*.*"),
            ],
        )

        if ruta:
            self.archivo_seleccionado = ruta
            # Mostrar la ruta en la etiqueta (solo el nombre si es muy largo)
            nombre = Path(ruta).name
            self.lbl_ruta.configure(text=nombre, fg=self.COLOR_TEXTO)
            self.btn_procesar.configure(state=tk.NORMAL)
            self._agregar_estado(f"Archivo seleccionado: {nombre}", "info")

    def _procesar_archivo(self):
        """
        Ejecuta el flujo completo de procesamiento:
        validación → vista previa → procesamiento → guardado → registro.
        """
        if not self.archivo_seleccionado:
            return

        filepath = self.archivo_seleccionado

        # Deshabilitar el botón durante el procesamiento
        self.btn_procesar.configure(state=tk.DISABLED)
        self.update_idletasks()

        try:
            inicio = time.time()

            # ---- 1. Iniciar log y validar ----
            self._agregar_estado("Iniciando validación del archivo...", "info")
            self.update_idletasks()

            iniciar_log(filepath)
            banco = self.banco_seleccionado.get()
            validador = ValidadorArchivo()
            es_valido, mensaje, datos = validador.validar(filepath, banco)

            if not es_valido:
                log_error(mensaje)
                self._agregar_estado(f"❌ Error de validación: {mensaje}", "error")
                self.btn_procesar.configure(state=tk.NORMAL)
                return

            num_registros = datos.get("num_registros", 0)
            log_info(
                f"Archivo leído correctamente. {num_registros} préstamos encontrados."
            )
            self._agregar_estado(
                f"✔ Validación exitosa. {num_registros} préstamos encontrados.",
                "exito",
            )
            self.update_idletasks()

            # ---- 2. Mostrar diálogo de vista previa usando messagebox nativo ----
            num_duplicados = len(datos.get("duplicados", []))
            gestor_temp = GestorArchivos()
            banco = self.banco_seleccionado.get()
            
            if banco == "BHD":
                nombre_salida = gestor_temp.generar_ruta_salida(self.carpeta_salida).name
            else:
                nombre_salida = gestor_temp.generar_ruta_salida_txt(self.carpeta_salida).name
            
            resumen = (
                f"📋 VISTA PREVIA ({banco})\n\n"
                f"Archivo seleccionado:\n{Path(filepath).name}\n\n"
                f"Registros encontrados: {num_registros}\n"
                f"Préstamos duplicados: {num_duplicados}\n"
                f"Errores: 0\n\n"
                f"Archivo de salida:\n{nombre_salida}\n\n"
                f"¿Deseas procesar este archivo ahora?"
            )
            
            confirmado = messagebox.askokcancel("Vista Previa", resumen)

            if not confirmado:
                self._agregar_estado("Procesamiento cancelado por el usuario.", "info")
                self.btn_procesar.configure(state=tk.NORMAL)
                return

            # ---- 3. Procesar el archivo ----
            self._agregar_estado(f"Procesando archivo para {banco}...", "info")
            self.update_idletasks()

            gestor = GestorArchivos()
            
            if banco == "BHD":
                procesador = Procesador()
                workbook, lista_prestamos = procesador.procesar(filepath, datos)
                
                # ---- 4. Guardar el archivo de salida ----
                self._agregar_estado("Guardando archivo de salida (Excel)...", "info")
                self.update_idletasks()
                ruta_salida = gestor.generar_ruta_salida(self.carpeta_salida)
                gestor.guardar(workbook, ruta_salida)
            else:
                procesador_res = ProcesadorBanreservas()
                lineas_texto, lista_prestamos = procesador_res.procesar(filepath, datos)
                
                # ---- 4. Guardar el archivo de salida ----
                self._agregar_estado("Guardando archivo de salida (TXT)...", "info")
                self.update_idletasks()
                ruta_salida = gestor.generar_ruta_salida_txt(self.carpeta_salida)
                gestor.guardar_txt(lineas_texto, ruta_salida)

            # ---- 5. Registrar en el registro mensual ----
            registro = RegistroMensual()
            registro.registrar(lista_prestamos, ruta_salida.name)

            # ---- 6. Finalizar log ----
            tiempo = time.time() - inicio
            log_info(f"Archivo para {banco} generado correctamente.")
            finalizar_log(tiempo, ruta_salida.name)

            # ---- 7. Mostrar resultado exitoso ----
            self._agregar_estado(
                f"✅ ¡Proceso completado exitosamente para {banco}!", "exito"
            )
            self._agregar_estado(
                f"   Archivo generado: {ruta_salida.name}", "exito"
            )
            self._agregar_estado(
                f"   Tiempo total: {tiempo:.2f} segundos", "exito"
            )

            # Abrir el archivo generado automáticamente
            try:
                os.startfile(str(ruta_salida))
            except Exception as e:
                self._agregar_estado(f"⚠ No se pudo abrir automáticamente el archivo: {e}", "error")

            messagebox.showinfo(
                "Proceso Completado",
                f"El archivo para {banco} se generó correctamente y se abrirá a continuación:\n\n{ruta_salida.name}\n\n"
                f"Ubicación:\n{ruta_salida.parent}",
            )

        except Exception as e:
            # Capturar cualquier error inesperado
            error_msg = f"Error inesperado: {str(e)}"
            try:
                log_error(error_msg)
            except Exception:
                pass  # Si el logger también falla, no interrumpir
            self._agregar_estado(f"❌ {error_msg}", "error")
            messagebox.showerror(
                "Error",
                f"Ocurrió un error durante el procesamiento:\n\n{str(e)}",
            )

        finally:
            # Rehabilitar el botón al finalizar
            self.btn_procesar.configure(state=tk.NORMAL)

    def _abrir_carpeta_salida(self):
        """Abre la carpeta de salida en el Explorador de Windows."""
        carpeta = self.carpeta_salida
        if carpeta.exists():
            subprocess.Popen(["explorer", str(carpeta)])
            self._agregar_estado("Carpeta de salida abierta en el explorador.", "info")
        else:
            self._agregar_estado(
                f"⚠ La carpeta de salida no existe: {carpeta}", "error"
            )
            messagebox.showwarning(
                "Carpeta no encontrada",
                f"La carpeta de salida no existe:\n\n{carpeta}",
            )

    # ==================================================================
    # Utilidades internas
    # ==================================================================

    def _agregar_estado(self, mensaje: str, tipo: str = "info"):
        """
        Agrega un mensaje al área de estado con formato de color.

        Args:
            mensaje: Texto del mensaje a mostrar.
            tipo: Tipo de mensaje ('info', 'exito', 'error') para el color.
        """
        self.txt_estado.configure(state=tk.NORMAL)

        # Agregar timestamp al mensaje
        hora = datetime.now().strftime("%H:%M:%S")
        linea = f"[{hora}] {mensaje}\n"

        self.txt_estado.insert(tk.END, linea, tipo)
        self.txt_estado.see(tk.END)
        self.txt_estado.configure(state=tk.DISABLED)

    def _on_cerrar(self):
        self.destroy()
        if self._al_cerrar:
            self._al_cerrar()

