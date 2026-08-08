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

class CRIMApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Generador Oficial de Formularios CRIM PR — Revisión 2.0")
        self.geometry("980x900")
        self.minsize(850, 700)
        
        # Grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray85", "gray15"))
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="📑 Llenado de Formularios Oficiales CRIM (Revisión 2.0)", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Generador Notarial & Sucesiones — Vector Overlay Calibrado", 
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
            text="📂 Abrir Caso (JSON)", 
            command=self.open_as52_json,
            fg_color="#37474f",
            hover_color="#263238",
            width=160
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="💾 Guardar Datos (JSON)", 
            command=self.save_as52_json,
            fg_color="#00695c",
            hover_color="#004d40",
            width=160
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="📄 Nuevo / Limpiar", 
            command=self.clear_as52, 
            fg_color="gray50", 
            hover_color="gray40", 
            width=130
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
        
        # --- Section 2: Datos del Acto / Notario (NUEVO REVISIÓN 2.0) ---
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
        
        # --- Section 6: Residencia Anterior (NUEVO REVISIÓN 2.0) ---
        sec6 = ctk.CTkLabel(scroll, text="🏠 6. Datos de la Residencia Anterior del Adquirente", font=ctk.CTkFont(size=14, weight="bold"))
        sec6.grid(row=21, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.as52_res_ant_dir = self.create_input(scroll, 22, 0, "1. Localización de la residencia anterior:", colspan=2)
        self.as52_res_ant_dueno = self.create_input(scroll, 23, 0, "2. Nombre del dueño de la residencia anterior:", colspan=2)
        
        # Line 3: Vivía / Poseía
        res3_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        res3_frame.grid(row=24, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(res3_frame, text="3. Año 20__:").pack(side="left", padx=(0, 2))
        self.as52_res_ant_ano = ctk.CTkEntry(res3_frame, placeholder_text="26", width=45)
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
        self.as52_res_ant_desde = ctk.CTkEntry(ocup_frame, placeholder_text="01/2020", width=95)
        self.as52_res_ant_desde.pack(side="left", padx=2)
        
        ctk.CTkLabel(ocup_frame, text="Hasta:").pack(side="left", padx=(10, 2))
        self.as52_res_ant_hasta = ctk.CTkEntry(ocup_frame, placeholder_text="08/2026", width=95)
        self.as52_res_ant_hasta.pack(side="left", padx=2)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        self.btn_gen_as52 = ctk.CTkButton(
            btn_frame, 
            text="🖨️ Generar y Abrir PDF AS-52 (Revisión 2.0)", 
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
        
        info = ctk.CTkLabel(tab, text="📄 Este formulario genera el Anexo AS-74 para listar la totalidad de los comuneros/herederos.", font=ctk.CTkFont(size=12, slant="italic"))
        info.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        scroll = ctk.CTkScrollableFrame(tab)
        scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scroll.grid_columnconfigure((0, 1), weight=1)
        
        self.as74_catastro = self.create_input(scroll, 0, 0, "Número de Catastro:")
        self.as74_localizacion = self.create_input(scroll, 0, 1, "Localización de la Propiedad:")
        
        self.as74_certificante = self.create_input(scroll, 1, 0, "Representante Legal / Certificante:", "Lcdo. Elías Fernández (abogado sucesion)", colspan=2)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        self.btn_gen_as74 = ctk.CTkButton(
            btn_frame, 
            text="🖨️ Generar y Abrir PDF AS-74", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#0d47a1", 
            hover_color="#1565c0",
            height=45,
            command=self.generate_as74_pdf
        )
        self.btn_gen_as74.pack(fill="x")

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

    def save_as52_json(self):
        data = self.get_as52_dict()
        catastro = data.get("catastro") or "Nuevo_Caso"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los Archivos", "*.*")],
            initialfile=f"Caso_{catastro}.json",
            title="Guardar Datos del Caso (JSON)"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Guardado", f"Datos del caso guardados exitosamente en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def open_as52_json(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json"), ("Todos los Archivos", "*.*")],
            title="Abrir Caso Guardado (JSON)"
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.load_as52_dict(data)
                messagebox.showinfo("Cargado", f"Caso cargado exitosamente desde:\n{filepath}")
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
            messagebox.showinfo("¡Éxito!", f"PDF AS-52 (Revisión 2.0) generado correctamente:\n{output_pdf}")
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
        
        # 3. Datos de Escritura y Notario (REVISIÓN 2.0)
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
            
        # 8. Datos Residencia Anterior del Adquirente (NUEVO REVISIÓN 2.0)
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
        catastro = self.as74_catastro.get().strip()
        if not catastro:
            messagebox.showerror("Error", "Por favor ingresa el Número de Catastro.")
            return
            
        output_pdf = f"Solicitud_Anexo_AS74_Duenos_Comunidad_{catastro}.pdf"
        template_pdf = "as74_blank.pdf"
        
        if not os.path.exists(template_pdf):
            messagebox.showerror("Error", f"No se encontró la plantilla {template_pdf}.")
            return
            
        try:
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=legal)
            
            def draw(x, y, text, font_size=10, font_name="Helvetica"):
                if text:
                    c.setFont(font_name, font_size)
                    c.drawString(x, 1008 - y, str(text))
                    
            draw(335.0, 95.0, "X")
            draw(148.0, 158.5, catastro, font_size=8.5)
            draw(148.0, 186.0, self.as74_localizacion.get().strip(), font_size=8.5)
            
            # Adquirente 1
            draw(115.0, 222.0, "Juan del Pueblo")
            draw(405.0, 222.0, "000-00-0000")
            draw(210.0, 233.0, "01/01/1980")
            draw(345.0, 233.0, "787-555-0000")
            draw(135.0, 242.0, "ejemplo@email.com")
            draw(465.0, 242.0, "33.33%")
            draw(135.0, 252.1, "PO BOX 0000, San Juan, PR 00901", font_size=8.5)
            
            # Adquirente 2
            draw(115.0, 284.0, "Maria del Pueblo")
            draw(405.0, 284.0, "000-00-0000")
            draw(210.0, 295.0, "01/01/1982")
            draw(345.0, 295.0, "787-555-0000")
            draw(135.0, 304.0, "ejemplo2@email.com")
            draw(465.0, 304.0, "33.33%")
            draw(135.0, 313.6, "PO BOX 0000, San Juan, PR 00901", font_size=8.5)
            
            # Adquirente 3
            draw(115.0, 347.0, "Carlos del Pueblo")
            draw(405.0, 347.0, "000-00-0000")
            draw(210.0, 358.0, "01/01/1985")
            draw(135.0, 365.0, "ejemplo3@email.com")
            draw(465.0, 365.0, "33.33%")
            draw(135.0, 375.2, "PO BOX 0000, San Juan, PR 00901", font_size=8.5)
            
            # Certificación
            cert = self.as74_certificante.get().strip() or "Lcdo. Juan del Pueblo (Representante Legal)"
            draw(80.0, 864.0, cert, font_size=9, font_name="Courier")
            draw(400.0, 864.0, "X")
            draw(450.0, 915.0, "01/01/2026")
            
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

            messagebox.showinfo("¡Éxito!", f"Anexo AS-74 generado correctamente:\n{output_pdf}")
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
