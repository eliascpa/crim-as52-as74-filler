# 📑 CRIM AS-52 & AS-74 Form Filler (Revisión 2.0)

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgray)
![License](https://img.shields.io/badge/License-MIT-green)

Aplicación de escritorio desarrollada en Python con interfaz gráfica moderna (**CustomTkinter**) diseñada para automatizar el llenado y generación de precisión vectorial de los formularios oficiales del **Centro de Recaudación de Ingresos Municipales (CRIM)** de Puerto Rico.

---

## 🌟 Características Principales

* **Formulario AS-52 (Solicitud de Cambio de Dueño):** Llenado automatizado con superposición vectorial de precisión calibrada sobre la plantilla oficial tamaño Legal (`8.5" x 14"`). Incluye datos registrales, notaría, transmitente, adquirentes y residencia anterior.
* **Formulario AS-74 (Hoja de Información de Dueños en Comunidad):** Generación del anexo para listar la totalidad de comuneros o herederos en propiedades comunitarias o sucesiones.
* **Gestión de Casos en JSON:** Permite guardar y abrir expedientes completos de clientes en formato `.json` para reutilizarlos o editarlos en cualquier momento.
* **Apertura Automática de PDF:** Compila y abre el documento generado inmediatamente en el visor PDF predeterminado del sistema operativo.
* **Alineación Vectorial Milimétrica:** Calibración exacta de baselines y casillas de cotejo (`X`) para evitar la obstrucción de texto impreso.

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

## 📋 Estructura del Proyecto

* `crim_app.py` — Código fuente principal de la aplicación gráfica y motor vectorial de generación PDF.
* `SOLICITUD DE CAMBIO DE DUEÑO.pdf` — Plantilla base oficial en blanco del Formulario AS-52.
* `as74_blank.pdf` — Plantilla base oficial en blanco del Formulario AS-74.
* `Caso_*.json` — Expedientes de prueba guardados en formato JSON.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
