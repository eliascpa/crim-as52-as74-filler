import os
import sys
import io
import json
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import legal

# Set appearance theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

APP_VERSION = "2.03"

class CRIMApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(f"Generador Oficial de Formularios CRIM PR — v{APP_VERSION}")
        self.geometry("1000x920")
        self.minsize(850, 700)
        
        # Grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray85", "gray15"))
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=f"📑 Llenado de Formularios Oficiales CRIM (v{APP_VERSION})", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Generador Notarial & Sucesiones — Modelo AS-74 Base Integrado", 
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray60"
        )
        self.subtitle_label.pack(side="left", padx=10, pady=15)
        
        # Main Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.tab_as52 = self.tabview.add("Formulario AS-52 (Cambio de Dueño)")
        self.tab_as74 = self.tabview.add("Formulario AS-74 (Comunidad / Herencia)")
        
        self.setup_as52_tab()
        self.setup_as74_tab()
        
    def setup_as52_tab(self):
        tab = self.tab_as52
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Action Toolbar (Open, Save, New)
        toolbar_frame = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="📂 Abrir Caso AS-52 (JSON)", 
            command=self.open_as52_json,
            fg_color="#37474f",
            hover_color="#263238",
            width=170
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="💾 Guardar Caso AS-52 (JSON)", 
            command=self.save_as52_json,
            fg_color="#00695c",
            hover_color="#004d40",
            width=170
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="📄 Limpiar AS-52", 
            command=self.clear_as52, 
            fg_color="gray50", 
            hover_color="gray40", 
            width=120
        ).pack(side="right", padx=5)
        
        # Scrollable form container
        scroll = ctk.CTkScrollableFrame(tab)
        scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scroll.grid_columnconfigure((0, 1), weight=1)
        
        # --- Section 1: Property Data ---
        sec1 = ctk.CTkLabel(scroll, text="📍 1. Datos de la Propiedad Inmueble", font=ctk.CTkFont(size=14, weight="bold"))
        sec1.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        self.as52_catastro = self.create_input(scroll, 1, 0, "Número de Catastro:")
        self.as52_localizacion = self.create_input(scroll, 1, 1, "Localización de la Propiedad:")
        
        self.as52_finca = self.create_input(scroll, 2, 0, "Finca N°:")
        self.as52_tomo = self.create_input(scroll, 2, 1, "Tomo:")
        
        self.as52_folio = self.create_input(scroll, 3, 0, "Folio:")
        self.as52_registro = self.create_input(scroll, 3, 1, "Registro de la Propiedad:")
        
        self.as52_seccion = self.create_input(scroll, 4, 0, "Sección de Registro:")
        self.as52_importe = self.create_input(scroll, 4, 1, "Importe de la Transacción ($):")
        
        # Cabida & Unidad
        cabida_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cabida_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(cabida_frame, text="Cabida:").pack(side="left", padx=(0, 5))
        self.as52_cabida_val = ctk.CTkEntry(cabida_frame, placeholder_text="", width=120)
        self.as52_cabida_val.pack(side="left", padx=5)
        
        self.as52_cabida_unit = ctk.CTkSegmentedButton(cabida_frame, values=["CDS", "MTS", "Sin Marcar"])
        self.as52_cabida_unit.set("Sin Marcar")
        self.as52_cabida_unit.pack(side="left", padx=10)
        
        # Tipo Uso
        tipo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_frame.grid(row=5, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(tipo_frame, text="Tipo de Uso:").pack(side="left", padx=(0, 5))
        self.as52_tipo_uso = ctk.CTkSegmentedButton(tipo_frame, values=["Residencial", "Comercial"])
        self.as52_tipo_uso.set("Residencial")
        self.as52_tipo_uso.pack(side="left", padx=5)
        
        # --- Section 2: Datos del Acto / Notario ---
        sec2 = ctk.CTkLabel(scroll, text="📜 2. Datos de Escritura y Notario Otorgante", font=ctk.CTkFont(size=14, weight="bold"))
        sec2.grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.as52_escritura = self.create_input(scroll, 7, 0, "Número de Escritura:")
        self.as52_fecha_escritura = self.create_input(scroll, 7, 1, "Fecha de Transacción / Escritura (dd/mm/aaaa):")
        
        self.as52_notario = self.create_input(scroll, 8, 0, "Nombre del Notario Otorgante:")
        self.as52_tel_notario = self.create_input(scroll, 8, 1, "Teléfono del Notario:")
        
        # --- Section 3: Transmitente ---
        sec3 = ctk.CTkLabel(scroll, text="👤 3. Datos del Transmitente (Dueño Anterior)", font=ctk.CTkFont(size=14, weight="bold"))
        sec3.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.as52_trans_nombre = self.create_input(scroll, 10, 0, "Nombre Completo Transmitente:")
        self.as52_trans_ssn = self.create_input(scroll, 10, 1, "Seguro Social Transmitente:")
        
        # --- Section 4: Adquirente 1 ---
        sec4 = ctk.CTkLabel(scroll, text="🔑 4. Adquirente 1 (Nuevo Dueño)", font=ctk.CTkFont(size=14, weight="bold"))
        sec4.grid(row=11, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.as52_adq1_nombre = self.create_input(scroll, 12, 0, "Nombre Completo:")
        self.as52_adq1_ssn = self.create_input(scroll, 12, 1, "Seguro Social:")
        
        self.as52_adq1_dob = self.create_input(scroll, 13, 0, "Fecha Nacimiento (dd/mm/aaaa):")
        self.as52_adq1_tel = self.create_input(scroll, 13, 1, "Teléfono:")
        
        self.as52_adq1_email = self.create_input(scroll, 14, 0, "Correo Electrónico:")
        self.as52_adq1_porc = self.create_input(scroll, 14, 1, "Porciento de Participación:")
        
        self.as52_adq1_dir = self.create_input(scroll, 15, 0, "Dirección Postal:", colspan=2)
        
        # --- Section 5: Adquirente 2 ---
        sec5 = ctk.CTkLabel(scroll, text="🔑 5. Adquirente 2 (Opcional)", font=ctk.CTkFont(size=14, weight="bold"))
        sec5.grid(row=16, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.as52_adq2_nombre = self.create_input(scroll, 17, 0, "Nombre Completo:")
        self.as52_adq2_ssn = self.create_input(scroll, 17, 1, "Seguro Social:")
        
        self.as52_adq2_dob = self.create_input(scroll, 18, 0, "Fecha Nacimiento (dd/mm/aaaa):")
        self.as52_adq2_tel = self.create_input(scroll, 18, 1, "Teléfono:")
        
        self.as52_adq2_email = self.create_input(scroll, 19, 0, "Correo Electrónico:")
        self.as52_adq2_porc = self.create_input(scroll, 19, 1, "Porciento de Participación:")
        
        self.as52_adq2_dir = self.create_input(scroll, 20, 0, "Dirección Postal:", colspan=2)
        
        # --- Section 6: Residencia Anterior ---
        sec6 = ctk.CTkLabel(scroll, text="🏠 6. Datos de la Residencia Anterior del Adquirente", font=ctk.CTkFont(size=14, weight="bold"))
        sec6.grid(row=21, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.as52_res_ant_dir = self.create_input(scroll, 22, 0, "1. Localización de la residencia anterior:", colspan=2)
        self.as52_res_ant_dueno = self.create_input(scroll, 23, 0, "2. Nombre del dueño de la residencia anterior:", colspan=2)
        
        # Line 3: Vivía / Poseía
        res3_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        res3_frame.grid(row=24, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(res3_frame, text="3. Año 20__:").pack(side="left", padx=(0, 2))
        self.as52_res_ant_ano = ctk.CTkEntry(res3_frame, placeholder_text="", width=45)
        self.as52_res_ant_ano.pack(side="left", padx=2)
        
        ctk.CTkLabel(res3_frame, text="¿Vivía la propiedad?:").pack(side="left", padx=(15, 2))
        self.as52_res_ant_vivia = ctk.CTkSegmentedButton(res3_frame, values=["Si", "No", "Sin Marcar"])
        self.as52_res_ant_vivia.set("Sin Marcar")
        self.as52_res_ant_vivia.pack(side="left", padx=5)
        
        ctk.CTkLabel(res3_frame, text="¿La poseía?:").pack(side="left", padx=(15, 2))
        self.as52_res_ant_poseia = ctk.CTkSegmentedButton(res3_frame, values=["Si", "No", "Sin Marcar"])
        self.as52_res_ant_poseia.set("Sin Marcar")
        self.as52_res_ant_poseia.pack(side="left", padx=5)
        
        # Line 4: Renta / Ocupacion
        self.as52_res_ant_renta = self.create_input(scroll, 25, 0, "4. Renta de la residencia anterior (si alguna):")
        
        ocup_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        ocup_frame.grid(row=25, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(ocup_frame, text="Ocupación desde:").pack(side="left", padx=(0, 2))
        self.as52_res_ant_desde = ctk.CTkEntry(ocup_frame, placeholder_text="", width=95)
        self.as52_res_ant_desde.pack(side="left", padx=2)
        
        ctk.CTkLabel(ocup_frame, text="Hasta:").pack(side="left", padx=(10, 2))
        self.as52_res_ant_hasta = ctk.CTkEntry(ocup_frame, placeholder_text="", width=95)
        self.as52_res_ant_hasta.pack(side="left", padx=2)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        self.btn_gen_as52 = ctk.CTkButton(
            btn_frame, 
            text=f"🖨️ Generar y Abrir PDF AS-52 (v{APP_VERSION})", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#1b5e20", 
            hover_color="#2e7d32",
            height=45,
            command=self.generate_as52_pdf
        )
        self.btn_gen_as52.pack(fill="x")
        
    def setup_as74_tab(self):
        tab = self.tab_as74
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Action Toolbar (Open, Save, New)
        toolbar_frame = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="📂 Abrir Caso AS-74 (JSON)", 
            command=self.open_as74_json,
            fg_color="#37474f",
            hover_color="#263238",
            width=170
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="💾 Guardar Caso AS-74 (JSON)", 
            command=self.save_as74_json,
            fg_color="#00695c",
            hover_color="#004d40",
            width=170
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="📄 Limpiar AS-74", 
            command=self.clear_as74, 
            fg_color="gray50", 
            hover_color="gray40", 
            width=120
        ).pack(side="right", padx=5)
        
        # Scrollable form container
        scroll = ctk.CTkScrollableFrame(tab)
        scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scroll.grid_columnconfigure((0, 1), weight=1)
        
        # Section 1: Header AS-74
        sec1 = ctk.CTkLabel(scroll, text="📋 1. Tipo de Comunidad y Datos de la Propiedad (Modelo AS-74 Base)", font=ctk.CTkFont(size=14, weight="bold"))
        sec1.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        hoja_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        hoja_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(hoja_frame, text="Hoja N°:").pack(side="left", padx=(0, 2))
        self.as74_hoja_num = ctk.CTkEntry(hoja_frame, placeholder_text="1", width=50)
        self.as74_hoja_num.insert(0, "1")
        self.as74_hoja_num.pack(side="left", padx=2)
        
        ctk.CTkLabel(hoja_frame, text="de:").pack(side="left", padx=(5, 2))
        self.as74_hoja_total = ctk.CTkEntry(hoja_frame, placeholder_text="1", width=50)
        self.as74_hoja_total.insert(0, "1")
        self.as74_hoja_total.pack(side="left", padx=2)
        
        tipo_com_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_com_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(tipo_com_frame, text="Tipo de Comunidad:").pack(side="left", padx=(0, 5))
        self.as74_tipo_comunidad = ctk.CTkSegmentedButton(tipo_com_frame, values=["HEREDITARIA", "PRO-INDIVISO"])
        self.as74_tipo_comunidad.set("HEREDITARIA")
        self.as74_tipo_comunidad.pack(side="left", padx=5)
        
        self.as74_catastro = self.create_input(scroll, 2, 0, "Número de Catastro:")
        self.as74_localizacion = self.create_input(scroll, 2, 1, "Localización de la Propiedad:")
        
        # Section 2: List of 3 Main Owners (Expandable to 10)
        sec2 = ctk.CTkLabel(scroll, text="👥 2. Dueños / Comuneros (Hasta 10 Entradas)", font=ctk.CTkFont(size=14, weight="bold"))
        sec2.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.as74_owners = []
        for i in range(1, 4): # Dueños 1, 2, 3 creados por defecto en la UI
            self.create_owner_block(scroll, row_start=4 + (i-1)*7, index=i)
            
        # Section 3: Certificación
        sec3 = ctk.CTkLabel(scroll, text="✍️ 3. Certificación del Informante / Miembro", font=ctk.CTkFont(size=14, weight="bold"))
        sec3.grid(row=25, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 5))
        
        self.as74_cert_nombre = self.create_input(scroll, 26, 0, "Nombre del Miembro / Certificante:", "Lcdo. Elías Fernández (abogado sucesion)")
        self.as74_cert_fecha = self.create_input(scroll, 26, 1, "Fecha de Certificación (dd/mm/aaaa):", "08/08/2026")
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        self.btn_gen_as74 = ctk.CTkButton(
            btn_frame, 
            text=f"🖨️ Generar y Abrir PDF AS-74 (Modelo Base v{APP_VERSION})", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#0d47a1", 
            hover_color="#1565c0",
            height=45,
            command=self.generate_as74_pdf
        )
        self.btn_gen_as74.pack(fill="x")

    def create_owner_block(self, parent, row_start, index):
        lbl = ctk.CTkLabel(parent, text=f"👤 Dueño {index}", font=ctk.CTkFont(size=12, weight="bold"))
        lbl.grid(row=row_start, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 2))
        
        nombre = self.create_input(parent, row_start+1, 0, f"{index}) Nombre Completo:")
        ssn = self.create_input(parent, row_start+1, 1, "Seguro Social:")
        
        dob = self.create_input(parent, row_start+2, 0, "Fecha Nacimiento (dd/mm/aaaa):")
        tel = self.create_input(parent, row_start+2, 1, "Teléfono:")
        
        email = self.create_input(parent, row_start+3, 0, "Correo Electrónico:")
        porc = self.create_input(parent, row_start+3, 1, "Porciento de Participación:")
        
        dir_post = self.create_input(parent, row_start+4, 0, "Dirección Postal:", colspan=2)
        
        cat2 = self.create_input(parent, row_start+5, 0, "Si tiene otra propiedad - (a) Catastro:")
        loc2 = self.create_input(parent, row_start+5, 1, "(b) Localización:")
        
        self.as74_owners.append({
            "nombre": nombre, "ssn": ssn, "dob": dob, "tel": tel,
            "email": email, "porc": porc, "dir": dir_post,
            "cat2": cat2, "loc2": loc2
        })

    def create_input(self, parent, row, col, label_text, default_val="", colspan=1):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=10, pady=5)
        
        lbl = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=11))
        lbl.pack(anchor="w")
        
        entry = ctk.CTkEntry(frame, placeholder_text="")
        if default_val:
            entry.insert(0, default_val)
        entry.pack(fill="x")
        return entry

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
            
        self.as52_cabida_unit.set("Sin Marcar")
        self.as52_tipo_uso.set("Residencial")
        self.as52_res_ant_vivia.set("Sin Marcar")
        self.as52_res_ant_poseia.set("Sin Marcar")

    def clear_as74(self):
        self.set_entry(self.as74_catastro, "")
        self.set_entry(self.as74_localizacion, "")
        self.set_entry(self.as74_hoja_num, "1")
        self.set_entry(self.as74_hoja_total, "1")
        self.as74_tipo_comunidad.set("HEREDITARIA")
        
        for o in self.as74_owners:
            for k in ["nombre", "ssn", "dob", "tel", "email", "porc", "dir", "cat2", "loc2"]:
                self.set_entry(o[k], "")
                
        self.set_entry(self.as74_cert_nombre, "")
        self.set_entry(self.as74_cert_fecha, "")

    def set_entry(self, entry, text):
        entry.delete(0, "end")
        entry.insert(0, text if text else "")

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
            "res_ant_hasta": self.as52_res_ant_hasta.get().strip()
        }

    def get_as74_dict(self):
        owners_data = []
        for o in self.as74_owners:
            owners_data.append({
                "nombre": o["nombre"].get().strip(),
                "ssn": o["ssn"].get().strip(),
                "dob": o["dob"].get().strip(),
                "tel": o["tel"].get().strip(),
                "email": o["email"].get().strip(),
                "porc": o["porc"].get().strip(),
                "dir": o["dir"].get().strip(),
                "cat2": o["cat2"].get().strip(),
                "loc2": o["loc2"].get().strip()
            })
        return {
            "hoja_num": self.as74_hoja_num.get().strip(),
            "hoja_total": self.as74_hoja_total.get().strip(),
            "tipo_comunidad": self.as74_tipo_comunidad.get(),
            "catastro": self.as74_catastro.get().strip(),
            "localizacion": self.as74_localizacion.get().strip(),
            "dueños": owners_data,
            "cert_nombre": self.as74_cert_nombre.get().strip(),
            "cert_fecha": self.as74_cert_fecha.get().strip()
        }

    def load_as52_dict(self, data):
        self.set_entry(self.as52_catastro, data.get("catastro", ""))
        self.set_entry(self.as52_localizacion, data.get("localizacion", ""))
        self.set_entry(self.as52_tomo, data.get("tomo", ""))
        self.set_entry(self.as52_folio, data.get("folio", ""))
        self.set_entry(self.as52_finca, data.get("finca", ""))
        self.set_entry(self.as52_registro, data.get("registro", ""))
        self.set_entry(self.as52_seccion, data.get("seccion", ""))
        self.set_entry(self.as52_importe, data.get("importe", ""))
        self.set_entry(self.as52_cabida_val, data.get("cabida", ""))
        self.as52_cabida_unit.set(data.get("cabida_unidad", "Sin Marcar"))
        self.as52_tipo_uso.set(data.get("tipo_propiedad", "Residencial"))
        
        self.set_entry(self.as52_escritura, data.get("escritura", ""))
        self.set_entry(self.as52_fecha_escritura, data.get("fecha_escritura", ""))
        self.set_entry(self.as52_notario, data.get("notario", ""))
        self.set_entry(self.as52_tel_notario, data.get("tel_notario", ""))
        
        self.set_entry(self.as52_trans_nombre, data.get("transmitente_nombre", ""))
        self.set_entry(self.as52_trans_ssn, data.get("transmitente_ssn", ""))
        
        self.set_entry(self.as52_adq1_nombre, data.get("adq1_nombre", ""))
        self.set_entry(self.as52_adq1_ssn, data.get("adq1_ssn", ""))
        self.set_entry(self.as52_adq1_dob, data.get("adq1_dob", ""))
        self.set_entry(self.as52_adq1_tel, data.get("adq1_tel", ""))
        self.set_entry(self.as52_adq1_email, data.get("adq1_email", ""))
        self.set_entry(self.as52_adq1_porc, data.get("adq1_porciento", ""))
        self.set_entry(self.as52_adq1_dir, data.get("adq1_dir", ""))
        
        self.set_entry(self.as52_adq2_nombre, data.get("adq2_nombre", ""))
        self.set_entry(self.as52_adq2_ssn, data.get("adq2_ssn", ""))
        self.set_entry(self.as52_adq2_dob, data.get("adq2_dob", ""))
        self.set_entry(self.as52_adq2_tel, data.get("adq2_tel", ""))
        self.set_entry(self.as52_adq2_email, data.get("adq2_email", ""))
        self.set_entry(self.as52_adq2_porc, data.get("adq2_porciento", ""))
        self.set_entry(self.as52_adq2_dir, data.get("adq2_dir", ""))
        
        self.set_entry(self.as52_res_ant_dir, data.get("res_ant_dir", ""))
        self.set_entry(self.as52_res_ant_dueno, data.get("res_ant_dueno", ""))
        self.set_entry(self.as52_res_ant_ano, data.get("res_ant_ano", ""))
        self.as52_res_ant_vivia.set(data.get("res_ant_vivia", "Sin Marcar"))
        self.as52_res_ant_poseia.set(data.get("res_ant_poseia", "Sin Marcar"))
        self.set_entry(self.as52_res_ant_renta, data.get("res_ant_renta", ""))
        self.set_entry(self.as52_res_ant_desde, data.get("res_ant_desde", ""))
        self.set_entry(self.as52_res_ant_hasta, data.get("res_ant_hasta", ""))

    def load_as74_dict(self, data):
        self.set_entry(self.as74_hoja_num, data.get("hoja_num", "1"))
        self.set_entry(self.as74_hoja_total, data.get("hoja_total", "1"))
        self.as74_tipo_comunidad.set(data.get("tipo_comunidad", "HEREDITARIA"))
        self.set_entry(self.as74_catastro, data.get("catastro", ""))
        self.set_entry(self.as74_localizacion, data.get("localizacion", ""))
        
        dueños = data.get("dueños", [])
        for idx, o in enumerate(self.as74_owners):
            if idx < len(dueños):
                d = dueños[idx]
                self.set_entry(o["nombre"], d.get("nombre", ""))
                self.set_entry(o["ssn"], d.get("ssn", ""))
                self.set_entry(o["dob"], d.get("dob", ""))
                self.set_entry(o["tel"], d.get("tel", ""))
                self.set_entry(o["email"], d.get("email", ""))
                self.set_entry(o["porc"], d.get("porc", ""))
                self.set_entry(o["dir"], d.get("dir", ""))
                self.set_entry(o["cat2"], d.get("cat2", ""))
                self.set_entry(o["loc2"], d.get("loc2", ""))
            else:
                for k in ["nombre", "ssn", "dob", "tel", "email", "porc", "dir", "cat2", "loc2"]:
                    self.set_entry(o[k], "")
                    
        self.set_entry(self.as74_cert_nombre, data.get("cert_nombre", ""))
        self.set_entry(self.as74_cert_fecha, data.get("cert_fecha", ""))

    def save_as52_json(self):
        data = self.get_as52_dict()
        catastro = data.get("catastro") or "Nuevo_Caso"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los Archivos", "*.*")],
            initialfile=f"Caso_AS52_{catastro}.json",
            title="Guardar Datos del Caso AS-52 (JSON)"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Guardado", f"Caso AS-52 guardado exitosamente en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def open_as52_json(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json"), ("Todos los Archivos", "*.*")],
            title="Abrir Caso AS-52 Guardado (JSON)"
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.load_as52_dict(data)
                messagebox.showinfo("Cargado", f"Caso AS-52 cargado exitosamente desde:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo JSON:\n{str(e)}")

    def save_as74_json(self):
        data = self.get_as74_dict()
        catastro = data.get("catastro") or "Nuevo_Caso"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los Archivos", "*.*")],
            initialfile=f"Caso_AS74_{catastro}.json",
            title="Guardar Datos del Caso AS-74 (JSON)"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Guardado", f"Caso AS-74 guardado exitosamente en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def open_as74_json(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json"), ("Todos los Archivos", "*.*")],
            title="Abrir Caso AS-74 Guardado (JSON)"
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.load_as74_dict(data)
                messagebox.showinfo("Cargado", f"Caso AS-74 cargado exitosamente desde:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo JSON:\n{str(e)}")

    def generate_as52_pdf(self):
        data = self.get_as52_dict()
        catastro = data.get("catastro")
        if not catastro:
            messagebox.showerror("Error", "Por favor ingresa al menos el Número de Catastro.")
            return
            
        template_pdf = "SOLICITUD DE CAMBIO DE DUEÑO.pdf"
        if not os.path.exists(template_pdf):
            messagebox.showerror("Error", f"No se encontró la plantilla {template_pdf} en la carpeta actual.")
            return
            
        output_pdf = f"Solicitud_Cambio_dueno_{catastro}.pdf"
        
        try:
            self.fill_as52_vector(template_pdf, output_pdf, data)
            messagebox.showinfo("¡Éxito!", f"PDF AS-52 generado correctamente:\n{output_pdf}")
            self.open_pdf(output_pdf)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el PDF:\n{str(e)}")

    def fill_as52_vector(self, input_pdf, output_pdf, data):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=legal)
        
        def draw(x, y, text, font_size=10):
            if text:
                c.setFont("Helvetica", font_size)
                c.drawString(x, 1008 - y, str(text))
                
        # 1. Catastro & Localización
        draw(109, 168, data.get("catastro", ""))
        draw(35, 226, data.get("localizacion", ""), font_size=9)
        draw(172.5, 265.5, "X", font_size=8) # Partición Hereditaria
        
        # 2. Datos Registrales
        draw(203, 296, data.get("tomo", ""))
        draw(310, 296, data.get("folio", ""))
        draw(430, 296, data.get("finca", ""))
        draw(165, 314, data.get("registro", ""))
        draw(320, 314, data.get("seccion", ""))
        
        # 3. Datos de Escritura y Notario
        draw(110, 331, data.get("escritura", ""))
        draw(445, 331, data.get("fecha_escritura", ""))
        draw(148, 398, data.get("notario", ""))
        draw(380, 398, data.get("tel_notario", ""))
        
        # 4. Importe & Cabida
        draw(140, 349, data.get("importe", ""))
        draw(60, 376, data.get("cabida", ""))
        
        if data.get("cabida_unidad") == "MTS":
            draw(144.0, 373.5, "X", font_size=8)
        elif data.get("cabida_unidad") == "CDS":
            draw(209.5, 373.5, "X", font_size=8)
            
        draw(396.0, 351.5, "X", font_size=8) # Con Estructura
        draw(312.0, 374.5, "X", font_size=8) # Hormigón
        
        if data.get("tipo_propiedad") == "Comercial":
            draw(312.0, 363.0, "X", font_size=8)
        elif data.get("tipo_propiedad") == "Residencial":
            draw(396.0, 362.5, "X", font_size=8)
            
        # 5. Transmitente
        draw(65, 435, data.get("transmitente_nombre", ""))
        draw(415, 435, data.get("transmitente_ssn", ""))
        
        # 6. Adquirente 1
        draw(72, 488, data.get("adq1_nombre", ""))
        draw(415, 488, data.get("adq1_ssn", ""))
        draw(180, 508, data.get("adq1_dob", ""))
        draw(355, 508, data.get("adq1_tel", ""))
        draw(110, 525, data.get("adq1_email", ""))
        draw(425, 525, data.get("adq1_porciento", ""))
        draw(92, 542, data.get("adq1_dir", ""), font_size=8.5)
        
        # 7. Adquirente 2
        if data.get("adq2_nombre"):
            draw(72, 583, data.get("adq2_nombre", ""))
            draw(415, 583, data.get("adq2_ssn", ""))
            draw(180, 599, data.get("adq2_dob", ""))
            draw(355, 599, data.get("adq2_tel", ""))
            draw(110, 615, data.get("adq2_email", ""))
            draw(425, 615, data.get("adq2_porciento", ""))
            draw(92, 632, data.get("adq2_dir", ""), font_size=8.5)
            
        # 8. Datos Residencia Anterior del Adquirente
        draw(275, 714, data.get("res_ant_dir", ""), font_size=8.5)
        draw(275, 732, data.get("res_ant_dueno", ""), font_size=9)
        draw(192, 750, data.get("res_ant_ano", ""), font_size=9)
        
        if data.get("res_ant_vivia") == "Si":
            draw(224, 750, "X", font_size=8)
        elif data.get("res_ant_vivia") == "No":
            draw(262, 750, "X", font_size=8)
            
        if data.get("res_ant_poseia") == "Si":
            draw(370, 750, "X", font_size=8)
        elif data.get("res_ant_poseia") == "No":
            draw(404, 750, "X", font_size=8)
            
        draw(195, 771, data.get("res_ant_renta", ""), font_size=9)
        draw(422, 771, data.get("res_ant_desde", ""), font_size=9)
        draw(505, 771, data.get("res_ant_hasta", ""), font_size=9)
            
        c.save()
        packet.seek(0)
        
        existing_pdf = PdfReader(open(input_pdf, "rb"))
        output = PdfWriter()
        
        overlay_pdf = PdfReader(packet)
        page = existing_pdf.pages[0]
        page.merge_page(overlay_pdf.pages[0])
        output.add_page(page)
        
        for i in range(1, len(existing_pdf.pages)):
            output.add_page(existing_pdf.pages[i])
            
        with open(output_pdf, "wb") as outputStream:
            output.write(outputStream)

    def generate_as74_pdf(self):
        data = self.get_as74_dict()
        catastro = data.get("catastro")
        if not catastro:
            messagebox.showerror("Error", "Por favor ingresa al menos el Número de Catastro.")
            return
            
        output_pdf = f"Solicitud_Anexo_AS74_Duenos_Comunidad_{catastro}.pdf"
        template_pdf = "Modelo AS-74-base.pdf"
        
        if not os.path.exists(template_pdf):
            messagebox.showerror("Error", f"No se encontró la plantilla base oficial {template_pdf} en la carpeta actual.")
            return
            
        try:
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=legal)
            
            def draw(x, y, text, font_size=10, font_name="Helvetica"):
                if text:
                    c.setFont(font_name, font_size)
                    c.drawString(x, 1008 - y, str(text))
                    
            # 1. Header AS-74
            if data.get("tipo_comunidad") == "PRO-INDIVISO":
                draw(210.0, 94.2, "X", font_size=9)
            else: # HEREDITARIA
                draw(330.0, 94.2, "X", font_size=9)
                
            draw(95.0, 108.2, data.get("hoja_num", "1"), font_size=9)
            draw(135.0, 108.2, data.get("hoja_total", "1"), font_size=9)
            
            # 2. Datos de la Propiedad
            draw(148.0, 158.5, catastro, font_size=8.5)
            draw(148.0, 186.0, data.get("localizacion", ""), font_size=8.5)
            
            # 3. Iteración de Dueños / Comuneros (Slot Y offsets: 213.2, 274.8, 337.8, 399.4, 462.4, 526.1...)
            slot_y_starts = [213.2, 274.8, 337.8, 399.4, 462.4, 526.1, 589.8, 653.5, 717.2, 780.9]
            
            for idx, o in enumerate(data.get("dueños", [])):
                if idx >= len(slot_y_starts):
                    break
                    
                if not o.get("nombre"):
                    continue
                    
                y0 = slot_y_starts[idx]
                
                # Line 1: Nombre & SSN (SSN movido a X=430.0 para no obstruir el texto "Número de Seguro Social:")
                draw(100.0, y0 + 8.8, o.get("nombre", ""))
                draw(430.0, y0 + 8.8, o.get("ssn", ""))
                
                # Line 2: DOB & Tel
                draw(182.0, y0 + 19.3, o.get("dob", ""))
                draw(375.0, y0 + 19.3, o.get("tel", ""))
                
                # Line 3: Email & %
                draw(128.0, y0 + 29.8, o.get("email", ""))
                draw(432.0, y0 + 29.8, o.get("porc", ""))
                
                # Line 4: Dirección Postal
                draw(120.0, y0 + 40.3, o.get("dir", ""), font_size=8.5)
                
                # Line 5 & 6: Otra Propiedad (Catastro / Localización)
                draw(238.0, y0 + 50.1, o.get("cat2", ""), font_size=8.5)
                draw(118.0, y0 + 59.2, o.get("loc2", ""), font_size=8.5)
            
            # 4. Certificación Final
            cert_nombre = data.get("cert_nombre") or "Lcdo. Elías Fernández (abogado sucesion)"
            draw(85.0, 864.0, cert_nombre, font_size=9, font_name="Courier")
            
            if data.get("tipo_comunidad") == "PRO-INDIVISO":
                draw(425.0, 864.0, "X", font_size=9)
            else:
                draw(335.0, 864.0, "X", font_size=9)
                
            draw(450.0, 915.0, data.get("cert_fecha", "08/08/2026"), font_size=9)
            
            c.save()
            packet.seek(0)
            
            existing_pdf = PdfReader(open(template_pdf, "rb"))
            output = PdfWriter()
            
            overlay_pdf = PdfReader(packet)
            page = existing_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            output.add_page(page)
            
            for i in range(1, len(existing_pdf.pages)):
                output.add_page(existing_pdf.pages[i])
                
            with open(output_pdf, "wb") as outputStream:
                output.write(outputStream)

            messagebox.showinfo("¡Éxito!", f"Anexo AS-74 (v{APP_VERSION}) generado correctamente:\n{output_pdf}")
            self.open_pdf(output_pdf)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el PDF AS-74:\n{str(e)}")

    def open_pdf(self, filepath):
        try:
            if sys.platform == "darwin": # macOS
                subprocess.run(["open", filepath])
            elif sys.platform == "win32": # Windows
                os.startfile(filepath)
            else: # Linux
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            print("No se pudo abrir automáticamente:", e)

if __name__ == "__main__":
    app = CRIMApp()
    app.mainloop()
