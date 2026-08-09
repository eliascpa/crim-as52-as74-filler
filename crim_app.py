# -*- coding: utf-8 -*-
"""
Generador Oficial de Formularios CRIM PR (AS-52 / AS-74).

Los datos del usuario (configuración, historial, casos y borrador automático)
se guardan fuera del repositorio, en la carpeta personal del sistema:
    ~/.crim_filler/
"""

import os
import re
import io
import sys
import copy
import json
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, date

import customtkinter as ctk
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import legal
from reportlab.pdfbase.pdfmetrics import stringWidth

APP_VERSION = "3.01"
MAX_DUENOS = 10
PAGINA_ALTO = 1008.0  # Legal 8.5" x 14" en puntos
FUENTE = "Helvetica"

# --- Rutas -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DIR = os.path.join(os.path.expanduser("~"), ".crim_filler")
CASOS_DIR = os.path.join(USER_DIR, "casos")
CONFIG_PATH = os.path.join(USER_DIR, "config.json")
RECIENTES_PATH = os.path.join(USER_DIR, "recientes.json")
HISTORIAL_PATH = os.path.join(USER_DIR, "historial.jsonl")
BORRADOR_PATH = os.path.join(USER_DIR, "borrador_auto.json")
COORD_PATH = os.path.join(BASE_DIR, "coordenadas.json")

PLANTILLA_AS52 = "SOLICITUD DE CAMBIO DE DUEÑO.pdf"
PLANTILLA_AS74 = "Modelo AS-74-base.pdf"

TAB_AS52 = "Formulario AS-52 (Cambio de Dueño)"
TAB_AS74 = "Formulario AS-74 (Comunidad / Herencia)"
TAB_HIST = "Historial de Casos"

CONFIG_DEFAULT = {
    "certificante_default": "",
    "carpeta_salida": "",          # vacío = carpeta del programa
    "autoguardado_min": 3,
    "max_recientes": 10,
    "apariencia": "System",
}

# --- Coordenadas de impresión ------------------------------------------------
# Formato de cada campo: [x, y, tamaño_fuente, ancho_máximo_opcional]
#   x, y  -> en puntos, medidos desde la esquina SUPERIOR izquierda de la hoja.
#   ancho -> si el texto lo excede, la fuente se reduce automáticamente y,
#            si aun así no cabe, se emite un aviso antes de generar el PDF.
# Para calibrar sin tocar el código: Herramientas > Exportar coordenadas.
COORDENADAS_DEFAULT = {
    "as52": {
        "catastro":              [109, 168, 10, 300],
        "localizacion":          [35, 226, 9, 520],
        # -- Negocio jurídico efectuado (2 filas x 4-5 opciones) --
        # X centrada en el recuadro: centro detectado - 1.45
        "marca_neg_compraventa": [24.1, 265.5, 8],
        "marca_neg_donacion":    [113.7, 265.5, 8],
        "marca_neg_particion":   [172.5, 265.5, 8],
        "marca_neg_liquidacion": [278.4, 265.5, 8],
        "marca_neg_permuta":     [24.1, 278.1, 8],
        "marca_neg_cesion":      [113.7, 278.1, 8],
        "marca_neg_segregacion": [172.5, 278.1, 8],
        "marca_neg_agrupacion":  [278.4, 278.1, 8],
        "marca_neg_otros":       [394.0, 278.1, 8],
        "neg_otros_texto":       [434.0, 278.1, 8.5, 70],
        "tomo":                  [203, 296, 10, 95],
        "folio":                 [310, 296, 10, 110],
        "finca":                 [430, 296, 10, 160],
        "registro":              [165, 314, 10, 145],
        "seccion":               [320, 314, 10, 240],
        "escritura":             [110, 331, 10, 250],
        "fecha_escritura":       [445, 331, 10, 150],
        "notario":               [148, 398, 10, 220],
        "tel_notario":           [380, 398, 10, 200],
        "importe":               [140, 349, 10, 200],
        "cabida":                [60, 376, 10, 80],
        "marca_mts":             [144.0, 373.5, 8],
        "marca_cds":             [209.5, 373.5, 8],
        # -- Tipo de solar --
        "marca_vacante":         [312.0, 351.5, 8],
        "marca_con_estructura":  [396.0, 351.5, 8],
        # -- Uso --
        "marca_comercial":       [312.0, 363.0, 8],
        "marca_residencial":     [396.0, 362.5, 8],
        # -- Material de la estructura --
        "marca_hormigon":        [312.0, 374.5, 8],
        "marca_mixto":           [396.0, 374.5, 8],
        "marca_madera":          [470.2, 374.5, 8],
        "transmitente_nombre":   [65, 435, 10, 340],
        "transmitente_ssn":      [415, 435, 10, 180],
        "adq1_nombre":           [72, 488, 10, 335],
        "adq1_ssn":              [415, 488, 10, 180],
        "adq1_dob":              [180, 508, 10, 165],
        "adq1_tel":              [355, 508, 10, 200],
        "adq1_email":            [110, 525, 10, 300],
        "adq1_porciento":        [425, 525, 10, 150],
        "adq1_dir":              [92, 542, 8.5, 480],
        "adq2_nombre":           [72, 583, 10, 335],
        "adq2_ssn":              [415, 583, 10, 180],
        "adq2_dob":              [180, 599, 10, 165],
        "adq2_tel":              [355, 599, 10, 200],
        "adq2_email":            [110, 615, 10, 300],
        "adq2_porciento":        [425, 615, 10, 150],
        "adq2_dir":              [92, 632, 8.5, 480],
        "res_ant_dir":           [275, 714, 8.5, 285],
        "res_ant_dueno":         [275, 732, 9, 285],
        "res_ant_ano":           [192, 750, 9, 25],
        "marca_vivia_si":        [224, 750, 8],
        "marca_vivia_no":        [262, 750, 8],
        "marca_poseia_si":       [370, 750, 8],
        "marca_poseia_no":       [404, 750, 8],
        "res_ant_renta":         [195, 771, 9, 220],
        "res_ant_desde":         [422, 771, 9, 75],
        "res_ant_hasta":         [505, 771, 9, 100],
    },
    "as74": {
        "marca_pro_indiviso":      [210.0, 94.2, 9],
        "marca_hereditaria":       [330.0, 94.2, 9],
        "hoja_num":                [95.0, 108.2, 9, 30],
        "hoja_total":              [135.0, 108.2, 9, 30],
        "catastro":                [148.0, 158.5, 8.5, 380],
        "localizacion":            [148.0, 186.0, 8.5, 380],
        "cert_nombre":             [80.0, 864.0, 9, 280],
        "cert_marca_pro_indiviso": [476.0, 864.0, 9],
        "cert_marca_hereditaria":  [396.0, 864.0, 9],
        "cert_fecha":              [392.0, 896.0, 9, 100],
        # Inicio vertical de cada bloque de dueño (10 espacios disponibles).
        "_slots_y": [213.2, 274.8, 337.8, 399.4, 462.4,
                     526.1, 589.8, 653.5, 717.2, 780.9],
        # Dentro de un bloque, "y" es un desplazamiento sobre el slot.
        "_dueno": {
            "nombre": [100.0, 8.8, 10, 220],
            "ssn":    [430.0, 8.8, 10, 160],
            "dob":    [182.0, 19.3, 10, 180],
            "tel":    [375.0, 19.3, 10, 200],
            "email":  [128.0, 29.8, 10, 290],
            "porc":   [432.0, 29.8, 10, 150],
            "dir":    [120.0, 40.3, 8.5, 460],
            "cat2":   [238.0, 50.1, 8.5, 340],
            "loc2":   [118.0, 59.2, 8.5, 460],
        },
    },
}

CAMPOS_AS74_DUENO = ["nombre", "ssn", "dob", "tel", "email", "porc", "dir", "cat2", "loc2"]

SIN_MARCAR = "Sin Marcar"

# Opciones de casillas del AS-52. La clave es lo que ve el usuario;
# el valor es el nombre de la coordenada en COORDENADAS_DEFAULT["as52"].
OPCIONES_SOLAR = {
    "Vacante": "marca_vacante",
    "Con Estructura": "marca_con_estructura",
}
OPCIONES_USO = {
    "Residencial": "marca_residencial",
    "Comercial": "marca_comercial",
}
OPCIONES_MATERIAL = {
    "Hormigón": "marca_hormigon",
    "Mixto": "marca_mixto",
    "Madera": "marca_madera",
}
OPCIONES_NEGOCIO = {
    "Compra Venta": "marca_neg_compraventa",
    "Donación": "marca_neg_donacion",
    "Partición Hereditaria": "marca_neg_particion",
    "Liquidación de Sociedad de Ganaciales": "marca_neg_liquidacion",
    "Permuta": "marca_neg_permuta",
    "Cesión": "marca_neg_cesion",
    "Segregación": "marca_neg_segregacion",
    "Agrupación": "marca_neg_agrupacion",
    "Otros": "marca_neg_otros",
}


# =============================================================================
#  Validación y normalización de datos
# =============================================================================
RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def normalizar_ssn(valor):
    """Devuelve (valor_normalizado, error). Acepta 9 dígitos con o sin guiones."""
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) != 9:
        return valor, f"debe tener 9 dígitos (tiene {len(digitos)})"
    return f"{digitos[:3]}-{digitos[3:5]}-{digitos[5:]}", None


def normalizar_fecha(valor):
    """Normaliza a dd/mm/aaaa y verifica que la fecha exista de verdad."""
    crudo = valor.strip()
    partes = [p for p in re.split(r"[/\-.\s]+", crudo) if p]
    if len(partes) == 1:
        solo_digitos = re.sub(r"\D", "", crudo)
        if len(solo_digitos) == 8:
            partes = [solo_digitos[:2], solo_digitos[2:4], solo_digitos[4:]]
    if len(partes) != 3 or not all(p.isdigit() for p in partes):
        return crudo, "no tiene formato dd/mm/aaaa"
    dd, mm, aa = partes
    if len(aa) == 2:
        aa = "20" + aa
    try:
        fecha = date(int(aa), int(mm), int(dd))
    except ValueError:
        return crudo, "no es una fecha real (¿día o mes inválido?)"
    return fecha.strftime("%d/%m/%Y"), None


def normalizar_telefono(valor):
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) == 11 and digitos[0] == "1":
        digitos = digitos[1:]
    if len(digitos) != 10:
        return valor, f"debe tener 10 dígitos (tiene {len(digitos)})"
    return f"({digitos[:3]}) {digitos[3:6]}-{digitos[6:]}", None


def normalizar_porciento(valor):
    limpio = valor.strip().replace("%", "").replace(",", ".")
    try:
        numero = float(limpio)
    except ValueError:
        return valor, "no es un número"
    if not 0 <= numero <= 100:
        return valor, "debe estar entre 0 y 100"
    return f"{numero:g}", None


def normalizar_email(valor):
    limpio = valor.strip()
    if not RE_EMAIL.match(limpio):
        return limpio, "no parece un correo válido"
    return limpio, None


def valor_porciento(texto):
    """Convierte un porciento a float; devuelve None si no es numérico."""
    try:
        return float(texto.strip().replace("%", "").replace(",", "."))
    except (ValueError, AttributeError):
        return None


# =============================================================================
#  Persistencia de configuración, recientes e historial
# =============================================================================
def asegurar_carpetas():
    os.makedirs(USER_DIR, exist_ok=True)
    os.makedirs(CASOS_DIR, exist_ok=True)


def leer_json(ruta, por_defecto):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return copy.deepcopy(por_defecto)


def escribir_json(ruta, datos):
    try:
        asegurar_carpetas()
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def cargar_config():
    config = copy.deepcopy(CONFIG_DEFAULT)
    config.update({k: v for k, v in leer_json(CONFIG_PATH, {}).items() if k in CONFIG_DEFAULT})
    return config


def cargar_coordenadas():
    """Coordenadas internas, sobrescritas por coordenadas.json si existe."""
    coords = copy.deepcopy(COORDENADAS_DEFAULT)
    if not os.path.exists(COORD_PATH):
        return coords, None
    try:
        with open(COORD_PATH, "r", encoding="utf-8") as f:
            usuario = json.load(f)
    except (OSError, ValueError) as e:
        return coords, f"No se pudo leer coordenadas.json: {e}"

    for formulario in ("as52", "as74"):
        bloque = usuario.get(formulario)
        if not isinstance(bloque, dict):
            continue
        for clave, valor in bloque.items():
            if clave == "_dueno" and isinstance(valor, dict):
                coords[formulario]["_dueno"].update(valor)
            else:
                coords[formulario][clave] = valor
    return coords, None


def registrar_historial(entrada):
    try:
        asegurar_carpetas()
        with open(HISTORIAL_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    except OSError:
        pass


def leer_historial(limite=300):
    if not os.path.exists(HISTORIAL_PATH):
        return []
    filas = []
    try:
        with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    filas.append(json.loads(linea))
                except ValueError:
                    continue
    except OSError:
        return []
    return list(reversed(filas))[:limite]


# =============================================================================
#  Dibujo sobre el PDF
# =============================================================================
def ajustar_fuente(texto, tamano, ancho_max, minimo=6.0):
    """Reduce la fuente hasta que el texto quepa. Devuelve (tamaño, desborda)."""
    if not ancho_max:
        return tamano, False
    actual = float(tamano)
    while actual > minimo and stringWidth(texto, FUENTE, actual) > ancho_max:
        actual -= 0.25
    return actual, stringWidth(texto, FUENTE, actual) > ancho_max


def dibujar(lienzo, spec, texto, avisos=None, etiqueta="", y_absoluta=None):
    """Escribe `texto` según `spec` = [x, y, tamaño, ancho_max?]."""
    if texto is None or str(texto).strip() == "":
        return
    texto = str(texto)
    x = spec[0]
    y = spec[1] if y_absoluta is None else y_absoluta
    tamano = spec[2] if len(spec) > 2 else 10
    ancho = spec[3] if len(spec) > 3 else 0

    tamano_final, desborda = ajustar_fuente(texto, tamano, ancho)
    if desborda and avisos is not None and etiqueta:
        avisos.append(f"• «{etiqueta}» es demasiado largo y podría salirse del recuadro.")
    lienzo.setFont(FUENTE, tamano_final)
    lienzo.drawString(x, PAGINA_ALTO - y, texto)


def componer_pdf(plantilla, salida, packet):
    """Superpone el overlay sobre la primera página de la plantilla."""
    with open(plantilla, "rb") as f:
        lector = PdfReader(f)
        escritor = PdfWriter()
        overlay = PdfReader(packet)

        primera = lector.pages[0]
        primera.merge_page(overlay.pages[0])
        escritor.add_page(primera)
        for i in range(1, len(lector.pages)):
            escritor.add_page(lector.pages[i])

        with open(salida, "wb") as destino:
            escritor.write(destino)


# =============================================================================
#  Aplicación
# =============================================================================
class CRIMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        asegurar_carpetas()
        self.config_app = cargar_config()
        self.coords, error_coords = cargar_coordenadas()
        self.recientes = leer_json(RECIENTES_PATH, [])
        if not isinstance(self.recientes, list):
            self.recientes = []

        ctk.set_appearance_mode(self.config_app.get("apariencia", "System"))

        self.title(f"Generador Oficial de Formularios CRIM PR — v{APP_VERSION}")
        self.geometry("1000x920")
        self.minsize(850, 700)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_menu()

        # --- Encabezado ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray85", "gray15"))
        self.header_frame.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            self.header_frame,
            text=f"📑 Llenado de Formularios Oficiales CRIM (v{APP_VERSION})",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            self.header_frame,
            text="Generador Notarial & Sucesiones — Modelo AS-74 Base Integrado",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray60",
        ).pack(side="left", padx=10, pady=15)

        # --- Pestañas ---
        self.tabview = ctk.CTkTabview(self, command=self._al_cambiar_pestana)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 0))

        self.tab_as52 = self.tabview.add(TAB_AS52)
        self.tab_as74 = self.tabview.add(TAB_AS74)
        self.tab_hist = self.tabview.add(TAB_HIST)

        self.setup_as52_tab()
        self.setup_as74_tab()
        self.setup_historial_tab()

        # --- Barra de estado ---
        self.status_var = tk.StringVar(value="Listo.")
        self.status_bar = ctk.CTkLabel(
            self, textvariable=self.status_var, anchor="w",
            font=ctk.CTkFont(size=11), text_color="gray60",
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=25, pady=(4, 8))

        self._enlazar_atajos()
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

        if error_coords:
            self.estado(error_coords)

        self._programar_autoguardado()
        self.after(300, self._quizas_restaurar_borrador)

    # -- utilidades de UI ----------------------------------------------------
    def estado(self, mensaje):
        marca = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"[{marca}] {mensaje}")

    def _enlazar_atajos(self):
        self.bind_all("<Control-n>", lambda e: self.nuevo_caso())
        self.bind_all("<Control-o>", lambda e: self.abrir_caso())
        self.bind_all("<Control-s>", lambda e: self.guardar_caso())
        self.bind_all("<Control-g>", lambda e: self.generar_pdf_activo())

    def _construir_menu(self):
        menubar = tk.Menu(self)

        m_archivo = tk.Menu(menubar, tearoff=0)
        m_archivo.add_command(label="Nuevo caso (limpiar pestaña)", accelerator="Ctrl+N",
                              command=self.nuevo_caso)
        m_archivo.add_command(label="Abrir caso...", accelerator="Ctrl+O", command=self.abrir_caso)
        m_archivo.add_command(label="Guardar caso...", accelerator="Ctrl+S", command=self.guardar_caso)
        self.menu_recientes = tk.Menu(m_archivo, tearoff=0)
        m_archivo.add_cascade(label="Casos recientes", menu=self.menu_recientes)
        m_archivo.add_separator()
        m_archivo.add_command(label="Generar PDF de la pestaña activa", accelerator="Ctrl+G",
                              command=self.generar_pdf_activo)
        m_archivo.add_separator()
        m_archivo.add_command(label="Salir", command=self._al_cerrar)
        menubar.add_cascade(label="Archivo", menu=m_archivo)

        m_herr = tk.Menu(menubar, tearoff=0)
        m_herr.add_command(label="Preferencias...", command=self.abrir_preferencias)
        m_herr.add_separator()
        m_herr.add_command(label="Abrir carpeta de salida", command=self.abrir_carpeta_salida)
        m_herr.add_command(label="Abrir carpeta de datos (historial)",
                           command=lambda: self.abrir_ruta(USER_DIR))
        m_herr.add_separator()
        m_herr.add_command(label="Exportar coordenadas para calibrar",
                           command=self.exportar_coordenadas)
        m_herr.add_command(label="Recargar coordenadas", command=self.recargar_coordenadas)
        menubar.add_cascade(label="Herramientas", menu=m_herr)

        m_ver = tk.Menu(menubar, tearoff=0)
        self.var_apariencia = tk.StringVar(value=self.config_app.get("apariencia", "System"))
        for etiqueta, modo in (("Según el sistema", "System"), ("Claro", "Light"), ("Oscuro", "Dark")):
            m_ver.add_radiobutton(label=etiqueta, value=modo, variable=self.var_apariencia,
                                  command=self._cambiar_apariencia)
        menubar.add_cascade(label="Ver", menu=m_ver)

        m_ayuda = tk.Menu(menubar, tearoff=0)
        m_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=m_ayuda)

        self.configure(menu=menubar)
        self._refrescar_menu_recientes()

    def _cambiar_apariencia(self):
        modo = self.var_apariencia.get()
        ctk.set_appearance_mode(modo)
        self.config_app["apariencia"] = modo
        escribir_json(CONFIG_PATH, self.config_app)

    def _al_cambiar_pestana(self):
        if self.tabview.get() == TAB_HIST:
            self.refrescar_historial()

    # =========================================================================
    #  Pestaña AS-52
    # =========================================================================
    def setup_as52_tab(self):
        tab = self.tab_as52
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(toolbar, text="📂 Abrir Caso AS-52 (JSON)", command=self.open_as52_json,
                      fg_color="#37474f", hover_color="#263238", width=170).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="💾 Guardar Caso AS-52 (JSON)", command=self.save_as52_json,
                      fg_color="#00695c", hover_color="#004d40", width=170).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="📄 Limpiar AS-52", command=self.clear_as52,
                      fg_color="gray50", hover_color="gray40", width=120).pack(side="right", padx=5)

        scroll = ctk.CTkScrollableFrame(tab)
        scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scroll.grid_columnconfigure((0, 1), weight=1)

        # --- 1. Propiedad ---
        ctk.CTkLabel(scroll, text="📍 1. Datos de la Propiedad Inmueble",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.as52_catastro = self.create_input(scroll, 1, 0, "Número de Catastro:")
        self.as52_localizacion = self.create_input(scroll, 1, 1, "Localización de la Propiedad:")
        self.as52_finca = self.create_input(scroll, 2, 0, "Finca N°:")
        self.as52_tomo = self.create_input(scroll, 2, 1, "Tomo:")
        self.as52_folio = self.create_input(scroll, 3, 0, "Folio:")
        self.as52_registro = self.create_input(scroll, 3, 1, "Registro de la Propiedad:")
        self.as52_seccion = self.create_input(scroll, 4, 0, "Sección de Registro:")
        self.as52_importe = self.create_input(scroll, 4, 1, "Importe de la Transacción ($):")

        cabida_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cabida_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(cabida_frame, text="Cabida:").pack(side="left", padx=(0, 5))
        self.as52_cabida_val = ctk.CTkEntry(cabida_frame, width=120)
        self.as52_cabida_val.pack(side="left", padx=5)
        self.as52_cabida_unit = ctk.CTkSegmentedButton(cabida_frame, values=["CDS", "MTS", SIN_MARCAR])
        self.as52_cabida_unit.set(SIN_MARCAR)
        self.as52_cabida_unit.pack(side="left", padx=10)

        tipo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_frame.grid(row=5, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(tipo_frame, text="Tipo de Uso:").pack(side="left", padx=(0, 5))
        self.as52_tipo_uso = ctk.CTkSegmentedButton(
            tipo_frame, values=list(OPCIONES_USO) + [SIN_MARCAR])
        self.as52_tipo_uso.set(SIN_MARCAR)
        self.as52_tipo_uso.pack(side="left", padx=5)

        # Tipo de solar y material de la estructura
        estructura = ctk.CTkFrame(scroll, fg_color="transparent")
        estructura.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(estructura, text="Tipo de Solar:").pack(side="left", padx=(0, 5))
        self.as52_tipo_solar = ctk.CTkSegmentedButton(
            estructura, values=list(OPCIONES_SOLAR) + [SIN_MARCAR])
        self.as52_tipo_solar.set(SIN_MARCAR)
        self.as52_tipo_solar.pack(side="left", padx=5)

        ctk.CTkLabel(estructura, text="Material de la Estructura:").pack(side="left", padx=(25, 5))
        self.as52_material = ctk.CTkSegmentedButton(
            estructura, values=list(OPCIONES_MATERIAL) + [SIN_MARCAR])
        self.as52_material.set(SIN_MARCAR)
        self.as52_material.pack(side="left", padx=5)

        # Negocio jurídico efectuado (9 opciones -> menú desplegable)
        negocio = ctk.CTkFrame(scroll, fg_color="transparent")
        negocio.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(negocio, text="Negocio Jurídico Efectuado:").pack(side="left", padx=(0, 5))
        self.as52_negocio = ctk.CTkOptionMenu(
            negocio, values=[SIN_MARCAR] + list(OPCIONES_NEGOCIO), width=250,
            command=self._al_cambiar_negocio)
        self.as52_negocio.set(SIN_MARCAR)
        self.as52_negocio.pack(side="left", padx=5)

        ctk.CTkLabel(negocio, text="Especifica (si es \"Otros\"):").pack(side="left", padx=(20, 5))
        self.as52_negocio_otros = ctk.CTkEntry(negocio, width=200, state="disabled")
        self.as52_negocio_otros.pack(side="left", padx=5)

        # --- 2. Escritura / Notario ---
        ctk.CTkLabel(scroll, text="📜 2. Datos de Escritura y Notario Otorgante",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=8, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))

        self.as52_escritura = self.create_input(scroll, 9, 0, "Número de Escritura:")
        self.as52_fecha_escritura = self.create_input(scroll, 9, 1, "Fecha de Transacción / Escritura (dd/mm/aaaa):")
        self.as52_notario = self.create_input(scroll, 10, 0, "Nombre del Notario Otorgante:")
        self.as52_tel_notario = self.create_input(scroll, 10, 1, "Teléfono del Notario:")

        # --- 3. Transmitente ---
        ctk.CTkLabel(scroll, text="👤 3. Datos del Transmitente (Dueño Anterior)",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=11, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))

        self.as52_trans_nombre = self.create_input(scroll, 12, 0, "Nombre Completo Transmitente:")
        self.as52_trans_ssn = self.create_input(scroll, 12, 1, "Seguro Social Transmitente:")

        # --- 4. Adquirente 1 ---
        ctk.CTkLabel(scroll, text="🔑 4. Adquirente 1 (Nuevo Dueño)",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=13, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))

        self.as52_adq1_nombre = self.create_input(scroll, 14, 0, "Nombre Completo:")
        self.as52_adq1_ssn = self.create_input(scroll, 14, 1, "Seguro Social:")
        self.as52_adq1_dob = self.create_input(scroll, 15, 0, "Fecha Nacimiento (dd/mm/aaaa):")
        self.as52_adq1_tel = self.create_input(scroll, 15, 1, "Teléfono:")
        self.as52_adq1_email = self.create_input(scroll, 16, 0, "Correo Electrónico:")
        self.as52_adq1_porc = self.create_input(scroll, 16, 1, "Porciento de Participación:")
        self.as52_adq1_dir = self.create_input(scroll, 17, 0, "Dirección Postal:", colspan=2)

        # --- 5. Adquirente 2 ---
        ctk.CTkLabel(scroll, text="🔑 5. Adquirente 2 (Opcional)",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=18, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))

        self.as52_adq2_nombre = self.create_input(scroll, 19, 0, "Nombre Completo:")
        self.as52_adq2_ssn = self.create_input(scroll, 19, 1, "Seguro Social:")
        self.as52_adq2_dob = self.create_input(scroll, 20, 0, "Fecha Nacimiento (dd/mm/aaaa):")
        self.as52_adq2_tel = self.create_input(scroll, 20, 1, "Teléfono:")
        self.as52_adq2_email = self.create_input(scroll, 21, 0, "Correo Electrónico:")
        self.as52_adq2_porc = self.create_input(scroll, 21, 1, "Porciento de Participación:")
        self.as52_adq2_dir = self.create_input(scroll, 22, 0, "Dirección Postal:", colspan=2)

        # --- 6. Residencia anterior ---
        ctk.CTkLabel(scroll, text="🏠 6. Datos de la Residencia Anterior del Adquirente",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=23, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))

        self.as52_res_ant_dir = self.create_input(scroll, 24, 0, "1. Localización de la residencia anterior:", colspan=2)
        self.as52_res_ant_dueno = self.create_input(scroll, 25, 0, "2. Nombre del dueño de la residencia anterior:", colspan=2)

        res3 = ctk.CTkFrame(scroll, fg_color="transparent")
        res3.grid(row=26, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(res3, text="3. Año 20__:").pack(side="left", padx=(0, 2))
        self.as52_res_ant_ano = ctk.CTkEntry(res3, width=45)
        self.as52_res_ant_ano.pack(side="left", padx=2)
        ctk.CTkLabel(res3, text="¿Vivía la propiedad?:").pack(side="left", padx=(15, 2))
        self.as52_res_ant_vivia = ctk.CTkSegmentedButton(res3, values=["Si", "No", "Sin Marcar"])
        self.as52_res_ant_vivia.set("Sin Marcar")
        self.as52_res_ant_vivia.pack(side="left", padx=5)
        ctk.CTkLabel(res3, text="¿La poseía?:").pack(side="left", padx=(15, 2))
        self.as52_res_ant_poseia = ctk.CTkSegmentedButton(res3, values=["Si", "No", SIN_MARCAR])
        self.as52_res_ant_poseia.set(SIN_MARCAR)
        self.as52_res_ant_poseia.pack(side="left", padx=5)

        self.as52_res_ant_renta = self.create_input(scroll, 27, 0, "4. Renta de la residencia anterior (si alguna):")

        ocup = ctk.CTkFrame(scroll, fg_color="transparent")
        ocup.grid(row=27, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(ocup, text="Ocupación desde:").pack(side="left", padx=(0, 2))
        self.as52_res_ant_desde = ctk.CTkEntry(ocup, width=95)
        self.as52_res_ant_desde.pack(side="left", padx=2)
        ctk.CTkLabel(ocup, text="Hasta:").pack(side="left", padx=(10, 2))
        self.as52_res_ant_hasta = ctk.CTkEntry(ocup, width=95)
        self.as52_res_ant_hasta.pack(side="left", padx=2)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text=f"🖨️ Generar y Abrir PDF AS-52 (v{APP_VERSION})",
                      font=ctk.CTkFont(size=15, weight="bold"), fg_color="#1b5e20",
                      hover_color="#2e7d32", height=45,
                      command=self.generate_as52_pdf).pack(fill="x")

    def _al_cambiar_negocio(self, valor):
        """Solo habilita el campo de texto cuando el negocio jurídico es "Otros"."""
        if valor == "Otros":
            self.as52_negocio_otros.configure(state="normal")
        else:
            self.as52_negocio_otros.configure(state="normal")
            self.as52_negocio_otros.delete(0, "end")
            self.as52_negocio_otros.configure(state="disabled")

    # =========================================================================
    #  Pestaña AS-74
    # =========================================================================
    def setup_as74_tab(self):
        tab = self.tab_as74
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(toolbar, text="📂 Abrir Caso AS-74 (JSON)", command=self.open_as74_json,
                      fg_color="#37474f", hover_color="#263238", width=170).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="💾 Guardar Caso AS-74 (JSON)", command=self.save_as74_json,
                      fg_color="#00695c", hover_color="#004d40", width=170).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="📄 Limpiar AS-74", command=self.clear_as74,
                      fg_color="gray50", hover_color="gray40", width=120).pack(side="right", padx=5)

        scroll = ctk.CTkScrollableFrame(tab)
        scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scroll.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(scroll, text="📋 1. Tipo de Comunidad y Datos de la Propiedad (Modelo AS-74 Base)",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        hoja = ctk.CTkFrame(scroll, fg_color="transparent")
        hoja.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(hoja, text="Hoja N°:").pack(side="left", padx=(0, 2))
        self.as74_hoja_num = ctk.CTkEntry(hoja, width=50)
        self.as74_hoja_num.insert(0, "1")
        self.as74_hoja_num.pack(side="left", padx=2)
        ctk.CTkLabel(hoja, text="de:").pack(side="left", padx=(5, 2))
        self.as74_hoja_total = ctk.CTkEntry(hoja, width=50)
        self.as74_hoja_total.insert(0, "1")
        self.as74_hoja_total.pack(side="left", padx=2)

        tipo_com = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_com.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(tipo_com, text="Tipo de Comunidad:").pack(side="left", padx=(0, 5))
        self.as74_tipo_comunidad = ctk.CTkSegmentedButton(tipo_com, values=["HEREDITARIA", "PRO-INDIVISO"])
        self.as74_tipo_comunidad.set("HEREDITARIA")
        self.as74_tipo_comunidad.pack(side="left", padx=5)

        self.as74_catastro = self.create_input(scroll, 2, 0, "Número de Catastro:")
        self.as74_localizacion = self.create_input(scroll, 2, 1, "Localización de la Propiedad:")

        # Encabezado de la sección de dueños, con controles para añadir/quitar
        sec_duenos = ctk.CTkFrame(scroll, fg_color="transparent")
        sec_duenos.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(15, 5))
        ctk.CTkLabel(sec_duenos, text="👥 2. Dueños / Comuneros",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        self.as74_contador_lbl = ctk.CTkLabel(sec_duenos, text="", text_color="gray60",
                                              font=ctk.CTkFont(size=11))
        self.as74_contador_lbl.pack(side="left", padx=10)
        ctk.CTkButton(sec_duenos, text="➖ Quitar último", width=120, height=26,
                      fg_color="gray50", hover_color="gray40",
                      command=self.quitar_dueno).pack(side="right", padx=4)
        ctk.CTkButton(sec_duenos, text="➕ Añadir dueño", width=130, height=26,
                      command=self.anadir_dueno).pack(side="right", padx=4)

        self.as74_owners_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.as74_owners_container.grid(row=4, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.as74_owners_container.grid_columnconfigure(0, weight=1)

        self.as74_owners = []
        for _ in range(3):
            self.anadir_dueno(silencioso=True)
        self._actualizar_contador_duenos()

        ctk.CTkLabel(scroll, text="✍️ 3. Certificación del Informante / Miembro",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 5))

        self.as74_cert_nombre = self.create_input(
            scroll, 6, 0, "Nombre del Miembro / Certificante:",
            self.config_app.get("certificante_default", ""))
        self.as74_cert_fecha = self.create_input(
            scroll, 6, 1, "Fecha de Certificación (dd/mm/aaaa):",
            date.today().strftime("%d/%m/%Y"))

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text=f"🖨️ Generar y Abrir PDF AS-74 (Modelo Base v{APP_VERSION})",
                      font=ctk.CTkFont(size=15, weight="bold"), fg_color="#0d47a1",
                      hover_color="#1565c0", height=45,
                      command=self.generate_as74_pdf).pack(fill="x")

    def anadir_dueno(self, silencioso=False):
        if len(self.as74_owners) >= MAX_DUENOS:
            if not silencioso:
                messagebox.showinfo("Límite alcanzado",
                                    f"El Modelo AS-74 base admite hasta {MAX_DUENOS} dueños por hoja.\n"
                                    "Para más comuneros, genera una segunda hoja (Hoja 2 de 2).")
            return

        indice = len(self.as74_owners) + 1
        marco = ctk.CTkFrame(self.as74_owners_container, border_width=1)
        marco.pack(fill="x", padx=5, pady=6)
        marco.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(marco, text=f"👤 Dueño {indice}", font=ctk.CTkFont(size=12, weight="bold")
                     ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 2))

        campos = {
            "nombre": self.create_input(marco, 1, 0, f"{indice}) Nombre Completo:"),
            "ssn":    self.create_input(marco, 1, 1, "Seguro Social:"),
            "dob":    self.create_input(marco, 2, 0, "Fecha Nacimiento (dd/mm/aaaa):"),
            "tel":    self.create_input(marco, 2, 1, "Teléfono:"),
            "email":  self.create_input(marco, 3, 0, "Correo Electrónico:"),
            "porc":   self.create_input(marco, 3, 1, "Porciento de Participación:"),
            "dir":    self.create_input(marco, 4, 0, "Dirección Postal:", colspan=2),
            "cat2":   self.create_input(marco, 5, 0, "Si tiene otra propiedad - (a) Catastro:"),
            "loc2":   self.create_input(marco, 5, 1, "(b) Localización:"),
        }
        campos["_marco"] = marco
        self.as74_owners.append(campos)

        if not silencioso:
            self._actualizar_contador_duenos()
            self.estado(f"Dueño {indice} añadido.")

    def quitar_dueno(self):
        if len(self.as74_owners) <= 1:
            messagebox.showinfo("Aviso", "Debe quedar al menos un bloque de dueño.")
            return
        bloque = self.as74_owners.pop()
        if bloque["nombre"].get().strip() and not messagebox.askyesno(
                "Confirmar", "Ese bloque tiene datos escritos. ¿Eliminarlo de todos modos?"):
            self.as74_owners.append(bloque)
            return
        bloque["_marco"].destroy()
        self._actualizar_contador_duenos()
        self.estado("Último bloque de dueño eliminado.")

    def _actualizar_contador_duenos(self):
        self.as74_contador_lbl.configure(text=f"({len(self.as74_owners)} de {MAX_DUENOS})")

    # =========================================================================
    #  Pestaña Historial
    # =========================================================================
    def setup_historial_tab(self):
        tab = self.tab_hist
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(toolbar,
                     text="Cada PDF generado queda registrado aquí junto a una copia de sus datos.",
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="🔄 Actualizar", width=110,
                      command=self.refrescar_historial).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="🗑️ Vaciar historial", width=140, fg_color="#b71c1c",
                      hover_color="#7f0000", command=self.vaciar_historial).pack(side="right", padx=5)

        self.hist_scroll = ctk.CTkScrollableFrame(tab)
        self.hist_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.hist_scroll.grid_columnconfigure(0, weight=1)

        self.refrescar_historial()

    def refrescar_historial(self):
        for hijo in self.hist_scroll.winfo_children():
            hijo.destroy()

        filas = leer_historial()
        if not filas:
            ctk.CTkLabel(self.hist_scroll,
                         text="Todavía no has generado ningún formulario.\n"
                              "Cuando generes un PDF, aparecerá aquí para reabrirlo o restaurarlo.",
                         text_color="gray60", justify="left"
                         ).pack(anchor="w", padx=15, pady=20)
            return

        for entrada in filas:
            self._fila_historial(entrada)

    def _fila_historial(self, entrada):
        marco = ctk.CTkFrame(self.hist_scroll, border_width=1)
        marco.pack(fill="x", padx=5, pady=4)

        izq = ctk.CTkFrame(marco, fg_color="transparent")
        izq.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        try:
            momento = datetime.fromisoformat(entrada.get("ts", "")).strftime("%d/%m/%Y %I:%M %p")
        except ValueError:
            momento = entrada.get("ts", "—")

        formulario = entrada.get("formulario", "?")
        color = "#2e7d32" if formulario == "AS-52" else "#1565c0"

        cabecera = ctk.CTkFrame(izq, fg_color="transparent")
        cabecera.pack(anchor="w", fill="x")
        ctk.CTkLabel(cabecera, text=f" {formulario} ", fg_color=color, corner_radius=4,
                     text_color="white", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        ctk.CTkLabel(cabecera, text=f"  Catastro {entrada.get('catastro', '—')}",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        ctk.CTkLabel(cabecera, text=f"   {momento}", text_color="gray60",
                     font=ctk.CTkFont(size=11)).pack(side="left")

        resumen = entrada.get("resumen", "")
        if resumen:
            ctk.CTkLabel(izq, text=resumen, text_color="gray60", font=ctk.CTkFont(size=11),
                         justify="left").pack(anchor="w", pady=(2, 0))

        der = ctk.CTkFrame(marco, fg_color="transparent")
        der.pack(side="right", padx=10, pady=8)

        pdf = entrada.get("pdf", "")
        existe_pdf = bool(pdf) and os.path.exists(pdf)
        ctk.CTkButton(der, text="📄 Abrir PDF" if existe_pdf else "📄 PDF no encontrado",
                      width=140, height=28,
                      state="normal" if existe_pdf else "disabled",
                      command=lambda p=pdf: self.abrir_ruta(p)).pack(side="left", padx=3)

        snapshot = entrada.get("snapshot", "")
        existe_snap = bool(snapshot) and os.path.exists(snapshot)
        ctk.CTkButton(der, text="↩️ Restaurar datos", width=150, height=28,
                      fg_color="#00695c", hover_color="#004d40",
                      state="normal" if existe_snap else "disabled",
                      command=lambda s=snapshot, f=formulario: self.restaurar_snapshot(s, f)
                      ).pack(side="left", padx=3)

    def restaurar_snapshot(self, ruta, formulario):
        if not messagebox.askyesno(
                "Restaurar caso",
                f"Se reemplazarán los datos actuales del formulario {formulario} "
                "con los de este caso guardado.\n\n¿Continuar?"):
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (OSError, ValueError) as e:
            messagebox.showerror("Error", f"No se pudo leer el caso guardado:\n{e}")
            return

        if formulario == "AS-52":
            self.load_as52_dict(datos)
            self.tabview.set(TAB_AS52)
        else:
            self.load_as74_dict(datos)
            self.tabview.set(TAB_AS74)
        self.estado(f"Caso {formulario} restaurado desde el historial.")

    def vaciar_historial(self):
        if not messagebox.askyesno(
                "Vaciar historial",
                "Se borrará la lista de casos generados.\n\n"
                "Los PDFs y las copias de datos NO se eliminan; solo desaparecen de esta lista.\n\n"
                "¿Continuar?"):
            return
        try:
            if os.path.exists(HISTORIAL_PATH):
                os.remove(HISTORIAL_PATH)
        except OSError as e:
            messagebox.showerror("Error", f"No se pudo borrar el historial:\n{e}")
            return
        self.refrescar_historial()
        self.estado("Historial vaciado.")

    # =========================================================================
    #  Entradas y limpieza
    # =========================================================================
    def create_input(self, parent, row, col, label_text, default_val="", colspan=1):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=11)).pack(anchor="w")
        entry = ctk.CTkEntry(frame)
        if default_val:
            entry.insert(0, default_val)
        entry.pack(fill="x")
        return entry

    def set_entry(self, entry, text):
        entry.delete(0, "end")
        entry.insert(0, text if text else "")

    def clear_as52(self):
        for entry in [self.as52_catastro, self.as52_localizacion, self.as52_finca, self.as52_tomo,
                      self.as52_folio, self.as52_registro, self.as52_seccion, self.as52_importe,
                      self.as52_cabida_val, self.as52_escritura, self.as52_fecha_escritura,
                      self.as52_notario, self.as52_tel_notario, self.as52_trans_nombre, self.as52_trans_ssn,
                      self.as52_adq1_nombre, self.as52_adq1_ssn, self.as52_adq1_dob, self.as52_adq1_tel,
                      self.as52_adq1_email, self.as52_adq1_porc, self.as52_adq1_dir,
                      self.as52_adq2_nombre, self.as52_adq2_ssn, self.as52_adq2_dob, self.as52_adq2_tel,
                      self.as52_adq2_email, self.as52_adq2_porc, self.as52_adq2_dir,
                      self.as52_res_ant_dir, self.as52_res_ant_dueno, self.as52_res_ant_ano,
                      self.as52_res_ant_renta, self.as52_res_ant_desde, self.as52_res_ant_hasta]:
            self.set_entry(entry, "")

        self.as52_cabida_unit.set(SIN_MARCAR)
        self.as52_tipo_uso.set(SIN_MARCAR)
        self.as52_tipo_solar.set(SIN_MARCAR)
        self.as52_material.set(SIN_MARCAR)
        self.as52_negocio.set(SIN_MARCAR)
        self._al_cambiar_negocio(SIN_MARCAR)
        self.as52_res_ant_vivia.set(SIN_MARCAR)
        self.as52_res_ant_poseia.set(SIN_MARCAR)
        self.estado("Formulario AS-52 limpiado.")

    def clear_as74(self):
        self.set_entry(self.as74_catastro, "")
        self.set_entry(self.as74_localizacion, "")
        self.set_entry(self.as74_hoja_num, "1")
        self.set_entry(self.as74_hoja_total, "1")
        self.as74_tipo_comunidad.set("HEREDITARIA")

        for bloque in self.as74_owners:
            for clave in CAMPOS_AS74_DUENO:
                self.set_entry(bloque[clave], "")

        self.set_entry(self.as74_cert_nombre, self.config_app.get("certificante_default", ""))
        self.set_entry(self.as74_cert_fecha, date.today().strftime("%d/%m/%Y"))
        self.estado("Formulario AS-74 limpiado.")

    # =========================================================================
    #  Serialización
    # =========================================================================
    def get_as52_dict(self):
        return {
            "catastro": self.as52_catastro.get().strip(),
            "localizacion": self.as52_localizacion.get().strip(),
            "tomo": self.as52_tomo.get().strip(),
            "folio": self.as52_folio.get().strip(),
            "finca": self.as52_finca.get().strip(),
            "registro": self.as52_registro.get().strip(),
            "seccion": self.as52_seccion.get().strip(),
            "importe": self.as52_importe.get().strip(),
            "cabida": self.as52_cabida_val.get().strip(),
            "cabida_unidad": self.as52_cabida_unit.get(),
            "tipo_propiedad": self.as52_tipo_uso.get(),
            "tipo_solar": self.as52_tipo_solar.get(),
            "material": self.as52_material.get(),
            "negocio_juridico": self.as52_negocio.get(),
            "negocio_otros": self.as52_negocio_otros.get().strip(),

            "escritura": self.as52_escritura.get().strip(),
            "fecha_escritura": self.as52_fecha_escritura.get().strip(),
            "notario": self.as52_notario.get().strip(),
            "tel_notario": self.as52_tel_notario.get().strip(),

            "transmitente_nombre": self.as52_trans_nombre.get().strip(),
            "transmitente_ssn": self.as52_trans_ssn.get().strip(),

            "adq1_nombre": self.as52_adq1_nombre.get().strip(),
            "adq1_ssn": self.as52_adq1_ssn.get().strip(),
            "adq1_dob": self.as52_adq1_dob.get().strip(),
            "adq1_tel": self.as52_adq1_tel.get().strip(),
            "adq1_email": self.as52_adq1_email.get().strip(),
            "adq1_porciento": self.as52_adq1_porc.get().strip(),
            "adq1_dir": self.as52_adq1_dir.get().strip(),

            "adq2_nombre": self.as52_adq2_nombre.get().strip(),
            "adq2_ssn": self.as52_adq2_ssn.get().strip(),
            "adq2_dob": self.as52_adq2_dob.get().strip(),
            "adq2_tel": self.as52_adq2_tel.get().strip(),
            "adq2_email": self.as52_adq2_email.get().strip(),
            "adq2_porciento": self.as52_adq2_porc.get().strip(),
            "adq2_dir": self.as52_adq2_dir.get().strip(),

            "res_ant_dir": self.as52_res_ant_dir.get().strip(),
            "res_ant_dueno": self.as52_res_ant_dueno.get().strip(),
            "res_ant_ano": self.as52_res_ant_ano.get().strip(),
            "res_ant_vivia": self.as52_res_ant_vivia.get(),
            "res_ant_poseia": self.as52_res_ant_poseia.get(),
            "res_ant_renta": self.as52_res_ant_renta.get().strip(),
            "res_ant_desde": self.as52_res_ant_desde.get().strip(),
            "res_ant_hasta": self.as52_res_ant_hasta.get().strip(),
        }

    def get_as74_dict(self):
        duenos = []
        for bloque in self.as74_owners:
            duenos.append({c: bloque[c].get().strip() for c in CAMPOS_AS74_DUENO})
        return {
            "hoja_num": self.as74_hoja_num.get().strip(),
            "hoja_total": self.as74_hoja_total.get().strip(),
            "tipo_comunidad": self.as74_tipo_comunidad.get(),
            "catastro": self.as74_catastro.get().strip(),
            "localizacion": self.as74_localizacion.get().strip(),
            "dueños": duenos,
            "cert_nombre": self.as74_cert_nombre.get().strip(),
            "cert_fecha": self.as74_cert_fecha.get().strip(),
        }

    def load_as52_dict(self, data):
        mapa = {
            self.as52_catastro: "catastro", self.as52_localizacion: "localizacion",
            self.as52_tomo: "tomo", self.as52_folio: "folio", self.as52_finca: "finca",
            self.as52_registro: "registro", self.as52_seccion: "seccion",
            self.as52_importe: "importe", self.as52_cabida_val: "cabida",
            self.as52_escritura: "escritura", self.as52_fecha_escritura: "fecha_escritura",
            self.as52_notario: "notario", self.as52_tel_notario: "tel_notario",
            self.as52_trans_nombre: "transmitente_nombre", self.as52_trans_ssn: "transmitente_ssn",
            self.as52_adq1_nombre: "adq1_nombre", self.as52_adq1_ssn: "adq1_ssn",
            self.as52_adq1_dob: "adq1_dob", self.as52_adq1_tel: "adq1_tel",
            self.as52_adq1_email: "adq1_email", self.as52_adq1_porc: "adq1_porciento",
            self.as52_adq1_dir: "adq1_dir",
            self.as52_adq2_nombre: "adq2_nombre", self.as52_adq2_ssn: "adq2_ssn",
            self.as52_adq2_dob: "adq2_dob", self.as52_adq2_tel: "adq2_tel",
            self.as52_adq2_email: "adq2_email", self.as52_adq2_porc: "adq2_porciento",
            self.as52_adq2_dir: "adq2_dir",
            self.as52_res_ant_dir: "res_ant_dir", self.as52_res_ant_dueno: "res_ant_dueno",
            self.as52_res_ant_ano: "res_ant_ano", self.as52_res_ant_renta: "res_ant_renta",
            self.as52_res_ant_desde: "res_ant_desde", self.as52_res_ant_hasta: "res_ant_hasta",
        }
        for entry, clave in mapa.items():
            self.set_entry(entry, data.get(clave, ""))

        def opcion(clave, validas):
            """Casos viejos (v2.x) no traen estas claves: quedan sin marcar."""
            valor = data.get(clave, SIN_MARCAR)
            return valor if valor in validas else SIN_MARCAR

        self.as52_cabida_unit.set(opcion("cabida_unidad", ("CDS", "MTS")))
        self.as52_tipo_uso.set(opcion("tipo_propiedad", OPCIONES_USO))
        self.as52_tipo_solar.set(opcion("tipo_solar", OPCIONES_SOLAR))
        self.as52_material.set(opcion("material", OPCIONES_MATERIAL))

        negocio = opcion("negocio_juridico", OPCIONES_NEGOCIO)
        self.as52_negocio.set(negocio)
        self._al_cambiar_negocio(negocio)
        if negocio == "Otros":
            self.set_entry(self.as52_negocio_otros, data.get("negocio_otros", ""))

        self.as52_res_ant_vivia.set(opcion("res_ant_vivia", ("Si", "No")))
        self.as52_res_ant_poseia.set(opcion("res_ant_poseia", ("Si", "No")))

    def load_as74_dict(self, data):
        self.set_entry(self.as74_hoja_num, data.get("hoja_num", "1"))
        self.set_entry(self.as74_hoja_total, data.get("hoja_total", "1"))
        self.as74_tipo_comunidad.set(data.get("tipo_comunidad", "HEREDITARIA"))
        self.set_entry(self.as74_catastro, data.get("catastro", ""))
        self.set_entry(self.as74_localizacion, data.get("localizacion", ""))

        duenos = data.get("dueños", data.get("duenos", []))
        # Crea los bloques que falten para no perder dueños del archivo.
        while len(self.as74_owners) < min(len(duenos), MAX_DUENOS):
            self.anadir_dueno(silencioso=True)
        self._actualizar_contador_duenos()

        for idx, bloque in enumerate(self.as74_owners):
            origen = duenos[idx] if idx < len(duenos) else {}
            for clave in CAMPOS_AS74_DUENO:
                self.set_entry(bloque[clave], origen.get(clave, ""))

        self.set_entry(self.as74_cert_nombre,
                       data.get("cert_nombre", self.config_app.get("certificante_default", "")))
        self.set_entry(self.as74_cert_fecha,
                       data.get("cert_fecha", date.today().strftime("%d/%m/%Y")))

    # =========================================================================
    #  Validación previa a generar
    # =========================================================================
    def _norm(self, entry, funcion, etiqueta, avisos):
        original = entry.get().strip()
        if not original:
            return
        nuevo, error = funcion(original)
        if error:
            avisos.append(f"• {etiqueta}: {error} → «{original}»")
        elif nuevo != original:
            self.set_entry(entry, nuevo)

    def validar_as52(self):
        avisos = []
        self._norm(self.as52_trans_ssn, normalizar_ssn, "Seguro Social del transmitente", avisos)
        self._norm(self.as52_adq1_ssn, normalizar_ssn, "Seguro Social del Adquirente 1", avisos)
        self._norm(self.as52_adq2_ssn, normalizar_ssn, "Seguro Social del Adquirente 2", avisos)

        self._norm(self.as52_fecha_escritura, normalizar_fecha, "Fecha de la escritura", avisos)
        self._norm(self.as52_adq1_dob, normalizar_fecha, "Fecha de nacimiento del Adquirente 1", avisos)
        self._norm(self.as52_adq2_dob, normalizar_fecha, "Fecha de nacimiento del Adquirente 2", avisos)

        self._norm(self.as52_tel_notario, normalizar_telefono, "Teléfono del notario", avisos)
        self._norm(self.as52_adq1_tel, normalizar_telefono, "Teléfono del Adquirente 1", avisos)
        self._norm(self.as52_adq2_tel, normalizar_telefono, "Teléfono del Adquirente 2", avisos)

        self._norm(self.as52_adq1_email, normalizar_email, "Correo del Adquirente 1", avisos)
        self._norm(self.as52_adq2_email, normalizar_email, "Correo del Adquirente 2", avisos)

        self._norm(self.as52_adq1_porc, normalizar_porciento, "Porciento del Adquirente 1", avisos)
        self._norm(self.as52_adq2_porc, normalizar_porciento, "Porciento del Adquirente 2", avisos)

        # Los porcientos deben sumar 100 cuando hay dos adquirentes.
        if self.as52_adq2_nombre.get().strip():
            p1 = valor_porciento(self.as52_adq1_porc.get())
            p2 = valor_porciento(self.as52_adq2_porc.get())
            if p1 is not None and p2 is not None and abs((p1 + p2) - 100) > 0.01:
                avisos.append(f"• Los porcientos de participación suman {p1 + p2:g}% en vez de 100%.")

        if not self.as52_adq1_nombre.get().strip():
            avisos.append("• No hay nombre del Adquirente 1.")

        # Coherencia de las casillas de cotejo
        solar = self.as52_tipo_solar.get()
        material = self.as52_material.get()

        if self.as52_negocio.get() == SIN_MARCAR:
            avisos.append("• No elegiste el Negocio Jurídico Efectuado; quedará sin marcar.")
        elif self.as52_negocio.get() == "Otros" and not self.as52_negocio_otros.get().strip():
            avisos.append("• Elegiste \"Otros\" como negocio jurídico pero no especificaste cuál.")

        if solar == SIN_MARCAR:
            avisos.append("• No elegiste Tipo de Solar (Vacante / Con Estructura).")
        if solar == "Vacante" and material != SIN_MARCAR:
            avisos.append(f"• El solar es Vacante pero marcaste material «{material}»; "
                          "un solar vacante no tiene estructura.")
        if solar == "Con Estructura" and material == SIN_MARCAR:
            avisos.append("• El solar es Con Estructura pero no elegiste el material "
                          "(Hormigón / Mixto / Madera).")
        if solar == "Vacante" and self.as52_tipo_uso.get() != SIN_MARCAR:
            avisos.append(f"• El solar es Vacante pero marcaste uso «{self.as52_tipo_uso.get()}».")

        return avisos

    def validar_as74(self):
        avisos = []
        self._norm(self.as74_cert_fecha, normalizar_fecha, "Fecha de certificación", avisos)

        suma = 0.0
        con_porciento = 0
        for idx, bloque in enumerate(self.as74_owners, start=1):
            if not bloque["nombre"].get().strip():
                continue
            self._norm(bloque["ssn"], normalizar_ssn, f"Seguro Social del Dueño {idx}", avisos)
            self._norm(bloque["dob"], normalizar_fecha, f"Fecha de nacimiento del Dueño {idx}", avisos)
            self._norm(bloque["tel"], normalizar_telefono, f"Teléfono del Dueño {idx}", avisos)
            self._norm(bloque["email"], normalizar_email, f"Correo del Dueño {idx}", avisos)
            self._norm(bloque["porc"], normalizar_porciento, f"Porciento del Dueño {idx}", avisos)

            porc = valor_porciento(bloque["porc"].get())
            if porc is not None:
                suma += porc
                con_porciento += 1

        if con_porciento > 1 and abs(suma - 100) > 0.01:
            avisos.append(f"• Los porcientos de los dueños suman {suma:g}% en vez de 100%.")

        if not any(b["nombre"].get().strip() for b in self.as74_owners):
            avisos.append("• No hay ningún dueño con nombre.")
        if not self.as74_cert_nombre.get().strip():
            avisos.append("• Falta el nombre del certificante.")
        return avisos

    def _confirmar_avisos(self, avisos, titulo):
        """Muestra los avisos y devuelve True si el usuario quiere continuar."""
        if not avisos:
            return True
        mostrados = avisos[:14]
        texto = "\n".join(mostrados)
        if len(avisos) > len(mostrados):
            texto += f"\n\n…y {len(avisos) - len(mostrados)} aviso(s) más."
        return messagebox.askyesno(
            titulo,
            "Se encontraron posibles problemas en los datos:\n\n"
            f"{texto}\n\n¿Deseas generar el PDF de todos modos?",
            icon="warning",
        )

    # =========================================================================
    #  Guardar / abrir casos
    # =========================================================================
    def _pestana_activa(self):
        actual = self.tabview.get()
        if actual == TAB_AS52:
            return "AS-52"
        if actual == TAB_AS74:
            return "AS-74"
        return None

    def nuevo_caso(self):
        formulario = self._pestana_activa()
        if formulario == "AS-52":
            self.clear_as52()
        elif formulario == "AS-74":
            self.clear_as74()
        else:
            messagebox.showinfo("Aviso", "Cambia a una pestaña de formulario para crear un caso nuevo.")

    def abrir_caso(self):
        formulario = self._pestana_activa()
        if formulario == "AS-52":
            self.open_as52_json()
        elif formulario == "AS-74":
            self.open_as74_json()
        else:
            messagebox.showinfo("Aviso", "Cambia a una pestaña de formulario para abrir un caso.")

    def guardar_caso(self):
        formulario = self._pestana_activa()
        if formulario == "AS-52":
            self.save_as52_json()
        elif formulario == "AS-74":
            self.save_as74_json()
        else:
            messagebox.showinfo("Aviso", "Cambia a una pestaña de formulario para guardar un caso.")

    def generar_pdf_activo(self):
        formulario = self._pestana_activa()
        if formulario == "AS-52":
            self.generate_as52_pdf()
        elif formulario == "AS-74":
            self.generate_as74_pdf()

    def _guardar_json(self, datos, prefijo):
        catastro = datos.get("catastro") or "Nuevo_Caso"
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los Archivos", "*.*")],
            initialfile=f"Caso_{prefijo}_{self._slug(catastro)}.json",
            title=f"Guardar Datos del Caso {prefijo} (JSON)",
        )
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except OSError as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
            return
        self.anadir_reciente(ruta)
        self.estado(f"Caso guardado en {ruta}")
        messagebox.showinfo("Guardado", f"Caso {prefijo} guardado exitosamente en:\n{ruta}")

    def _abrir_json(self, prefijo, cargador, ruta=None):
        if ruta is None:
            ruta = filedialog.askopenfilename(
                filetypes=[("Archivos JSON", "*.json"), ("Todos los Archivos", "*.*")],
                title=f"Abrir Caso {prefijo} Guardado (JSON)",
            )
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (OSError, ValueError) as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo JSON:\n{e}")
            return
        cargador(datos)
        self.anadir_reciente(ruta)
        self.estado(f"Caso cargado desde {ruta}")

    def save_as52_json(self):
        self._guardar_json(self.get_as52_dict(), "AS52")

    def open_as52_json(self, ruta=None):
        self._abrir_json("AS-52", self.load_as52_dict, ruta)

    def save_as74_json(self):
        self._guardar_json(self.get_as74_dict(), "AS74")

    def open_as74_json(self, ruta=None):
        self._abrir_json("AS-74", self.load_as74_dict, ruta)

    # -- recientes -----------------------------------------------------------
    def anadir_reciente(self, ruta):
        ruta = os.path.abspath(ruta)
        self.recientes = [r for r in self.recientes if r != ruta]
        self.recientes.insert(0, ruta)
        del self.recientes[self.config_app.get("max_recientes", 10):]
        escribir_json(RECIENTES_PATH, self.recientes)
        self._refrescar_menu_recientes()

    def _refrescar_menu_recientes(self):
        self.menu_recientes.delete(0, "end")
        vigentes = [r for r in self.recientes if os.path.exists(r)]
        if not vigentes:
            self.menu_recientes.add_command(label="(vacío)", state="disabled")
            return
        for ruta in vigentes:
            etiqueta = os.path.basename(ruta)
            self.menu_recientes.add_command(
                label=etiqueta, command=lambda r=ruta: self._abrir_reciente(r))
        self.menu_recientes.add_separator()
        self.menu_recientes.add_command(label="Vaciar lista", command=self._vaciar_recientes)

    def _abrir_reciente(self, ruta):
        """Detecta por el contenido si el archivo es AS-52 o AS-74."""
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (OSError, ValueError) as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
            return
        if "dueños" in datos or "duenos" in datos or "tipo_comunidad" in datos:
            self.load_as74_dict(datos)
            self.tabview.set(TAB_AS74)
        else:
            self.load_as52_dict(datos)
            self.tabview.set(TAB_AS52)
        self.anadir_reciente(ruta)
        self.estado(f"Caso cargado desde {ruta}")

    def _vaciar_recientes(self):
        self.recientes = []
        escribir_json(RECIENTES_PATH, self.recientes)
        self._refrescar_menu_recientes()

    # =========================================================================
    #  Generación de PDFs
    # =========================================================================
    @staticmethod
    def _slug(texto):
        return re.sub(r"[^A-Za-z0-9._-]+", "_", texto).strip("_")[:40] or "sin_catastro"

    def carpeta_salida(self):
        carpeta = self.config_app.get("carpeta_salida") or BASE_DIR
        try:
            os.makedirs(carpeta, exist_ok=True)
        except OSError:
            carpeta = BASE_DIR
        return carpeta

    def _resolver_salida(self, nombre):
        """Devuelve la ruta destino, avisando antes de sobrescribir."""
        ruta = os.path.join(self.carpeta_salida(), nombre)
        if not os.path.exists(ruta):
            return ruta
        if messagebox.askyesno(
                "El archivo ya existe",
                f"Ya existe este PDF:\n{ruta}\n\n"
                "• Sí = sobrescribirlo\n"
                "• No = guardar una versión nueva sin borrar la anterior",
                icon="warning"):
            return ruta
        base, ext = os.path.splitext(ruta)
        n = 2
        while os.path.exists(f"{base}_v{n}{ext}"):
            n += 1
        return f"{base}_v{n}{ext}"

    def _plantilla(self, nombre):
        ruta = os.path.join(BASE_DIR, nombre)
        if not os.path.exists(ruta):
            messagebox.showerror(
                "Falta la plantilla",
                f"No se encontró la plantilla oficial:\n{nombre}\n\n"
                f"Debe estar en la carpeta del programa:\n{BASE_DIR}")
            return None
        return ruta

    def _archivar_caso(self, formulario, catastro, datos, pdf, resumen):
        """Guarda una copia de los datos y registra el caso en el historial."""
        marca = datetime.now()
        snapshot = os.path.join(
            CASOS_DIR,
            f"{formulario}_{self._slug(catastro)}_{marca:%Y%m%d_%H%M%S}.json")
        escribir_json(snapshot, datos)
        registrar_historial({
            "ts": marca.isoformat(timespec="seconds"),
            "formulario": formulario,
            "catastro": catastro,
            "pdf": pdf,
            "snapshot": snapshot,
            "resumen": resumen,
        })

    # -- AS-52 ---------------------------------------------------------------
    def generate_as52_pdf(self):
        if not self.as52_catastro.get().strip():
            messagebox.showerror("Error", "Por favor ingresa al menos el Número de Catastro.")
            return

        avisos = self.validar_as52()
        if not self._confirmar_avisos(avisos, "Revisión del AS-52"):
            self.estado("Generación del AS-52 cancelada para corregir datos.")
            return

        plantilla = self._plantilla(PLANTILLA_AS52)
        if not plantilla:
            return

        datos = self.get_as52_dict()
        salida = self._resolver_salida(f"Solicitud_Cambio_dueno_{self._slug(datos['catastro'])}.pdf")

        try:
            avisos_dibujo = self.fill_as52_vector(plantilla, salida, datos)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el PDF:\n{e}")
            return

        self._archivar_caso("AS-52", datos["catastro"], datos, salida,
                            f"Adquirente: {datos.get('adq1_nombre') or '—'}")
        self.estado(f"PDF AS-52 generado: {salida}")

        extra = ""
        if avisos_dibujo:
            extra = "\n\nAvisos:\n" + "\n".join(avisos_dibujo[:8])
        messagebox.showinfo("¡Éxito!", f"PDF AS-52 generado correctamente:\n{salida}{extra}")
        self.abrir_ruta(salida)

    def fill_as52_vector(self, plantilla, salida, data):
        coords = self.coords["as52"]
        avisos = []
        packet = io.BytesIO()
        lienzo = canvas.Canvas(packet, pagesize=legal)

        def campo(clave, valor, etiqueta=""):
            dibujar(lienzo, coords[clave], valor, avisos, etiqueta or clave)

        def marca(clave):
            dibujar(lienzo, coords[clave], "X")

        def marca_opcion(valor, opciones):
            """Marca la casilla que corresponde a la opción elegida, si alguna."""
            clave = opciones.get(valor)
            if clave:
                marca(clave)

        campo("catastro", data.get("catastro"), "Número de catastro")
        campo("localizacion", data.get("localizacion"), "Localización de la propiedad")

        # Negocio jurídico efectuado (antes se marcaba siempre "Partición Hereditaria")
        marca_opcion(data.get("negocio_juridico"), OPCIONES_NEGOCIO)
        if data.get("negocio_juridico") == "Otros":
            campo("neg_otros_texto", data.get("negocio_otros"), "Especificación de \"Otros\"")

        campo("tomo", data.get("tomo"), "Tomo")
        campo("folio", data.get("folio"), "Folio")
        campo("finca", data.get("finca"), "Finca")
        campo("registro", data.get("registro"), "Registro de la propiedad")
        campo("seccion", data.get("seccion"), "Sección")

        campo("escritura", data.get("escritura"), "Número de escritura")
        campo("fecha_escritura", data.get("fecha_escritura"), "Fecha de escritura")
        campo("notario", data.get("notario"), "Nombre del notario")
        campo("tel_notario", data.get("tel_notario"), "Teléfono del notario")

        campo("importe", data.get("importe"), "Importe de la transacción")
        campo("cabida", data.get("cabida"), "Cabida")

        if data.get("cabida_unidad") == "MTS":
            marca("marca_mts")
        elif data.get("cabida_unidad") == "CDS":
            marca("marca_cds")

        # Antes "Con Estructura" y "Hormigón" se marcaban siempre, sin importar
        # la propiedad; ahora las tres filas dependen de lo que elija el usuario.
        marca_opcion(data.get("tipo_solar"), OPCIONES_SOLAR)
        marca_opcion(data.get("tipo_propiedad"), OPCIONES_USO)
        marca_opcion(data.get("material"), OPCIONES_MATERIAL)

        campo("transmitente_nombre", data.get("transmitente_nombre"), "Nombre del transmitente")
        campo("transmitente_ssn", data.get("transmitente_ssn"), "Seguro Social del transmitente")

        for n in (1, 2):
            if n == 2 and not data.get("adq2_nombre"):
                continue
            campo(f"adq{n}_nombre", data.get(f"adq{n}_nombre"), f"Nombre del Adquirente {n}")
            campo(f"adq{n}_ssn", data.get(f"adq{n}_ssn"), f"Seguro Social del Adquirente {n}")
            campo(f"adq{n}_dob", data.get(f"adq{n}_dob"), f"Fecha de nacimiento del Adquirente {n}")
            campo(f"adq{n}_tel", data.get(f"adq{n}_tel"), f"Teléfono del Adquirente {n}")
            campo(f"adq{n}_email", data.get(f"adq{n}_email"), f"Correo del Adquirente {n}")
            campo(f"adq{n}_porciento", data.get(f"adq{n}_porciento"), f"Porciento del Adquirente {n}")
            campo(f"adq{n}_dir", data.get(f"adq{n}_dir"), f"Dirección del Adquirente {n}")

        campo("res_ant_dir", data.get("res_ant_dir"), "Localización de la residencia anterior")
        campo("res_ant_dueno", data.get("res_ant_dueno"), "Dueño de la residencia anterior")
        campo("res_ant_ano", data.get("res_ant_ano"), "Año de la residencia anterior")

        if data.get("res_ant_vivia") == "Si":
            marca("marca_vivia_si")
        elif data.get("res_ant_vivia") == "No":
            marca("marca_vivia_no")

        if data.get("res_ant_poseia") == "Si":
            marca("marca_poseia_si")
        elif data.get("res_ant_poseia") == "No":
            marca("marca_poseia_no")

        campo("res_ant_renta", data.get("res_ant_renta"), "Renta de la residencia anterior")
        campo("res_ant_desde", data.get("res_ant_desde"), "Ocupación desde")
        campo("res_ant_hasta", data.get("res_ant_hasta"), "Ocupación hasta")

        lienzo.save()
        packet.seek(0)
        componer_pdf(plantilla, salida, packet)
        return avisos

    # -- AS-74 ---------------------------------------------------------------
    def generate_as74_pdf(self):
        if not self.as74_catastro.get().strip():
            messagebox.showerror("Error", "Por favor ingresa al menos el Número de Catastro.")
            return

        avisos = self.validar_as74()
        if not self._confirmar_avisos(avisos, "Revisión del AS-74"):
            self.estado("Generación del AS-74 cancelada para corregir datos.")
            return

        plantilla = self._plantilla(PLANTILLA_AS74)
        if not plantilla:
            return

        datos = self.get_as74_dict()
        salida = self._resolver_salida(
            f"Solicitud_Anexo_AS74_Duenos_Comunidad_{self._slug(datos['catastro'])}.pdf")

        try:
            avisos_dibujo = self.fill_as74_vector(plantilla, salida, datos)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el PDF AS-74:\n{e}")
            return

        con_nombre = [d for d in datos["dueños"] if d.get("nombre")]
        self._archivar_caso("AS-74", datos["catastro"], datos, salida,
                            f"{len(con_nombre)} dueño(s) — {datos.get('tipo_comunidad', '')}")
        self.estado(f"PDF AS-74 generado: {salida}")

        extra = ""
        if avisos_dibujo:
            extra = "\n\nAvisos:\n" + "\n".join(avisos_dibujo[:8])
        messagebox.showinfo("¡Éxito!",
                            f"Anexo AS-74 (v{APP_VERSION}) generado correctamente:\n{salida}{extra}")
        self.abrir_ruta(salida)

    def fill_as74_vector(self, plantilla, salida, data):
        coords = self.coords["as74"]
        avisos = []
        packet = io.BytesIO()
        lienzo = canvas.Canvas(packet, pagesize=legal)

        pro_indiviso = data.get("tipo_comunidad") == "PRO-INDIVISO"

        dibujar(lienzo, coords["marca_pro_indiviso" if pro_indiviso else "marca_hereditaria"], "X")
        dibujar(lienzo, coords["hoja_num"], data.get("hoja_num", "1"))
        dibujar(lienzo, coords["hoja_total"], data.get("hoja_total", "1"))
        dibujar(lienzo, coords["catastro"], data.get("catastro"), avisos, "Número de catastro")
        dibujar(lienzo, coords["localizacion"], data.get("localizacion"), avisos, "Localización")

        slots = coords["_slots_y"]
        campos_dueno = coords["_dueno"]
        omitidos = 0

        for idx, dueno in enumerate(data.get("dueños", [])):
            if not dueno.get("nombre"):
                continue
            if idx >= len(slots):
                omitidos += 1
                continue
            base_y = slots[idx]
            for clave, spec in campos_dueno.items():
                dibujar(lienzo, spec, dueno.get(clave), avisos,
                        f"{clave} del Dueño {idx + 1}", y_absoluta=base_y + spec[1])

        if omitidos:
            avisos.append(f"• {omitidos} dueño(s) no caben en esta hoja; usa una hoja adicional.")

        cert_nombre = data.get("cert_nombre") or self.config_app.get("certificante_default", "")
        dibujar(lienzo, coords["cert_nombre"], cert_nombre, avisos, "Nombre del certificante")
        dibujar(lienzo, coords["cert_marca_pro_indiviso" if pro_indiviso else "cert_marca_hereditaria"], "X")
        dibujar(lienzo, coords["cert_fecha"],
                data.get("cert_fecha") or date.today().strftime("%d/%m/%Y"))

        lienzo.save()
        packet.seek(0)
        componer_pdf(plantilla, salida, packet)
        return avisos

    # =========================================================================
    #  Autoguardado / borrador
    # =========================================================================
    def _programar_autoguardado(self):
        minutos = self.config_app.get("autoguardado_min", 3)
        try:
            minutos = max(1, int(minutos))
        except (TypeError, ValueError):
            minutos = 3
        self.after(minutos * 60_000, self._tic_autoguardado)

    def _tic_autoguardado(self):
        self.guardar_borrador()
        self._programar_autoguardado()

    def guardar_borrador(self):
        try:
            borrador = {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "as52": self.get_as52_dict(),
                "as74": self.get_as74_dict(),
            }
        except tk.TclError:
            return  # ventana en proceso de cierre
        if self._tiene_contenido(borrador):
            escribir_json(BORRADOR_PATH, borrador)

    @staticmethod
    def _tiene_contenido(borrador):
        # Campos que traen un valor por defecto y no cuentan como "datos escritos".
        IGNORADOS = {"cabida_unidad", "tipo_propiedad", "tipo_solar", "material",
                     "negocio_juridico", "res_ant_vivia", "res_ant_poseia",
                     "tipo_comunidad", "hoja_num", "hoja_total", "cert_fecha"}
        for clave in ("as52", "as74"):
            datos = borrador.get(clave, {})
            for campo, valor in datos.items():
                if campo in IGNORADOS or valor == SIN_MARCAR:
                    continue
                if campo == "dueños":
                    if any(d.get("nombre") for d in valor):
                        return True
                elif str(valor).strip():
                    return True
        return False

    def _quizas_restaurar_borrador(self):
        if not os.path.exists(BORRADOR_PATH):
            return
        borrador = leer_json(BORRADOR_PATH, {})
        if not self._tiene_contenido(borrador):
            return
        try:
            momento = datetime.fromisoformat(borrador.get("ts", "")).strftime("%d/%m/%Y a las %I:%M %p")
        except ValueError:
            momento = "una sesión anterior"

        if messagebox.askyesno(
                "Continuar donde quedaste",
                f"Hay un borrador automático guardado el {momento}.\n\n"
                "• Sí = restaurarlo en los formularios\n"
                "• No = descartarlo y empezar en blanco"):
            self.load_as52_dict(borrador.get("as52", {}))
            self.load_as74_dict(borrador.get("as74", {}))
            self.estado("Borrador automático restaurado.")
        else:
            try:
                os.remove(BORRADOR_PATH)
            except OSError:
                pass

    # =========================================================================
    #  Preferencias y utilidades
    # =========================================================================
    def abrir_preferencias(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Preferencias")
        ventana.geometry("620x330")
        ventana.transient(self)
        ventana.grab_set()

        contenedor = ctk.CTkFrame(ventana, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=20, pady=20)
        contenedor.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(contenedor, text="Certificante por defecto (AS-74):").grid(
            row=0, column=0, sticky="w", pady=8)
        e_cert = ctk.CTkEntry(contenedor)
        e_cert.insert(0, self.config_app.get("certificante_default", ""))
        e_cert.grid(row=0, column=1, columnspan=2, sticky="ew", padx=10, pady=8)

        ctk.CTkLabel(contenedor, text="Carpeta donde guardar los PDFs:").grid(
            row=1, column=0, sticky="w", pady=8)
        e_carpeta = ctk.CTkEntry(contenedor)
        e_carpeta.insert(0, self.config_app.get("carpeta_salida", ""))
        e_carpeta.grid(row=1, column=1, sticky="ew", padx=10, pady=8)

        def elegir_carpeta():
            elegida = filedialog.askdirectory(title="Selecciona la carpeta de salida", parent=ventana)
            if elegida:
                e_carpeta.delete(0, "end")
                e_carpeta.insert(0, elegida)

        ctk.CTkButton(contenedor, text="Examinar…", width=100, command=elegir_carpeta).grid(
            row=1, column=2, pady=8)

        ctk.CTkLabel(contenedor, text="(vacío = la carpeta del programa)",
                     text_color="gray60", font=ctk.CTkFont(size=11)).grid(
            row=2, column=1, sticky="w", padx=10)

        ctk.CTkLabel(contenedor, text="Autoguardado cada (minutos):").grid(
            row=3, column=0, sticky="w", pady=8)
        e_auto = ctk.CTkEntry(contenedor, width=80)
        e_auto.insert(0, str(self.config_app.get("autoguardado_min", 3)))
        e_auto.grid(row=3, column=1, sticky="w", padx=10, pady=8)

        ctk.CTkLabel(
            contenedor,
            text="⚠️ Los casos guardados contienen Seguros Sociales sin cifrar.\n"
                 "Guárdalos en una carpeta protegida y no los subas a repositorios públicos.",
            text_color="#e65100", font=ctk.CTkFont(size=11), justify="left",
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=(15, 5))

        def guardar():
            self.config_app["certificante_default"] = e_cert.get().strip()
            self.config_app["carpeta_salida"] = e_carpeta.get().strip()
            try:
                self.config_app["autoguardado_min"] = max(1, int(e_auto.get().strip()))
            except ValueError:
                self.config_app["autoguardado_min"] = 3
            escribir_json(CONFIG_PATH, self.config_app)
            self.estado("Preferencias guardadas.")
            ventana.destroy()

        botones = ctk.CTkFrame(contenedor, fg_color="transparent")
        botones.grid(row=5, column=0, columnspan=3, sticky="e", pady=(10, 0))
        ctk.CTkButton(botones, text="Cancelar", width=100, fg_color="gray50",
                      hover_color="gray40", command=ventana.destroy).pack(side="left", padx=5)
        ctk.CTkButton(botones, text="Guardar", width=100, command=guardar).pack(side="left", padx=5)

    def exportar_coordenadas(self):
        if os.path.exists(COORD_PATH) and not messagebox.askyesno(
                "Ya existe", f"Ya existe {os.path.basename(COORD_PATH)}.\n"
                             "¿Sobrescribirlo con los valores internos actuales?"):
            return
        contenido = copy.deepcopy(COORDENADAS_DEFAULT)
        contenido["_formato"] = (
            "Cada campo es [x, y, tamaño_fuente, ancho_máximo_opcional]. "
            "x/y en puntos desde la esquina superior izquierda de la hoja legal (612 x 1008). "
            "En as74._dueno, la 'y' es un desplazamiento sobre el slot correspondiente."
        )
        if escribir_json(COORD_PATH, contenido):
            messagebox.showinfo(
                "Coordenadas exportadas",
                f"Se creó:\n{COORD_PATH}\n\n"
                "Edita ese archivo para ajustar posiciones sin tocar el código, "
                "y luego usa Herramientas > Recargar coordenadas.")
            self.estado("coordenadas.json exportado.")
        else:
            messagebox.showerror("Error", "No se pudo escribir coordenadas.json")

    def recargar_coordenadas(self):
        self.coords, error = cargar_coordenadas()
        if error:
            messagebox.showerror("Error", error)
            return
        origen = "coordenadas.json" if os.path.exists(COORD_PATH) else "valores internos"
        self.estado(f"Coordenadas recargadas desde {origen}.")
        messagebox.showinfo("Coordenadas", f"Coordenadas recargadas desde {origen}.")

    def abrir_carpeta_salida(self):
        self.abrir_ruta(self.carpeta_salida())

    def abrir_ruta(self, ruta):
        if not ruta or not os.path.exists(ruta):
            messagebox.showwarning("No encontrado", f"No existe la ruta:\n{ruta}")
            return
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", ruta], check=False)
            elif sys.platform == "win32":
                os.startfile(ruta)  # noqa: S606
            else:
                subprocess.run(["xdg-open", ruta], check=False)
        except OSError as e:
            self.estado(f"No se pudo abrir automáticamente: {e}")

    def mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            f"Generador Oficial de Formularios CRIM PR\n"
            f"Versión {APP_VERSION}\n\n"
            f"Formularios: AS-52 (Cambio de Dueño) y AS-74 (Comunidad / Herencia).\n\n"
            f"Carpeta del programa:\n{BASE_DIR}\n\n"
            f"Datos del usuario (historial, casos, preferencias):\n{USER_DIR}")

    def _al_cerrar(self):
        self.guardar_borrador()
        escribir_json(CONFIG_PATH, self.config_app)
        self.destroy()


if __name__ == "__main__":
    ctk.set_default_color_theme("blue")
    app = CRIMApp()
    app.mainloop()
