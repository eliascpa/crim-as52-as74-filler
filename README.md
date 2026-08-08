# 📑 CRIM AS-52 & AS-74 Form Filler (v2.04)

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgray)
![License](https://img.shields.io/badge/License-MIT-green)

Aplicación de escritorio desarrollada en Python con interfaz gráfica moderna (**CustomTkinter**) diseñada para automatizar el llenado y generación de precisión vectorial de los formularios oficiales del **Centro de Recaudación de Ingresos Municipales (CRIM)** de Puerto Rico.

---

## 🌟 Características Principales

* **Formulario AS-52 (Solicitud de Cambio de Dueño):** Llenado automatizado con superposición vectorial de precisión calibrada sobre la plantilla oficial tamaño Legal (`8.5" x 14"`). Incluye datos registrales, notaría, transmitente, adquirentes y residencia anterior.
* **Formulario AS-74 (Hoja de Información de Dueños en Comunidad - Modelo Base):** Generación del anexo oficial (`Modelo AS-74-base.pdf`) para listar la totalidad de comuneros o herederos en propiedades comunitarias o sucesiones.
* **Gestión de Casos en JSON:** Permite guardar y abrir expedientes completos de clientes en formato `.json` tanto para el Formulario AS-52 como para el Anexo AS-74.
* **Apertura Automática de PDF:** Compila y abre el documento generado inmediatamente en el visor PDF predeterminado del sistema operativo.
* **Alineación Vectorial Milimétrica:** Calibración exacta de baselines, campos de texto y casillas de cotejo (`X`) para evitar la obstrucción de texto impreso.

---

## 🛠️ Requisitos e Instalación

### Requisitos previos:
* Python 3.9 o superior.

### Librerías requeridas:
Instala las dependencias necesarias ejecutando en tu terminal:

```bash
pip install customtkinter PyPDF2 reportlab
```

---

## 🚀 Uso de la Aplicación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/eliascpa/crim-as52-as74-filler.git
   cd crim-as52-as74-filler
   ```

2. Ejecuta la aplicación:
   ```bash
   python3 crim_app.py
   ```

---

## 📋 Historial de Actualizaciones (Changelog)

### **v2.04 (Versión Actual)**
* ✍️ **Tipografía Unificada:** Se cambió la fuente de la certificación del AS-74 a `Helvetica` para mantener uniformidad con todo el documento.
* 🎯 **Alineación de Casilla Hereditaria:** Se corrigió la posición horizontal de la `X` de comunidad hereditaria a `X = 396.0` para que caiga exactamente dentro del espacio correspondiente.
* 📏 **Fecha de Certificación sobre la Línea:** Se ajustó la coordenada vertical de la fecha a `Y = 896.0` para que se pose limpiamente encima de la línea oficial.

### **v2.03**
* ➡️ **Seguro Social en AS-74:** Se desplazó la posición inicial del texto del Seguro Social a `X = 430.0` para evitar que se encimara sobre la etiqueta *"Número de Seguro Social:"*.

### **v2.02**
* 📄 **Integración de `Modelo AS-74-base.pdf`:** Sustitución de la plantilla genérica por el documento oficial base del CRIM.
* 👥 **Soporte Multi-Dueño:** Incorporación de campos completos para listar múltiples dueños/comuneros (entradas 1 a 10) y tipo de comunidad (*Hereditaria* vs *Pro-Indiviso*).
* 💾 **Persistencia JSON AS-74:** Botones independientes para guardar y abrir expedientes AS-74 en formato JSON.

### **v2.01**
* 🔢 **Sistema de Versiones Semánticas:** Integración de la versión visible en el título de la ventana y el encabezado de la aplicación.

### **v2.00**
* 📜 **Campos Notariales y Residencia Anterior:** Adición de número de escritura, fecha, notario otorgante, teléfono y sección completa de la residencia anterior del adquirente.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
