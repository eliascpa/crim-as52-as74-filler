# 📑 CRIM AS-52 & AS-74 Form Filler (v3.01)

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgray)
![License](https://img.shields.io/badge/License-MIT-green)

Aplicación de escritorio desarrollada en Python con interfaz gráfica moderna (**CustomTkinter**) diseñada para automatizar el llenado y generación de precisión vectorial de los formularios oficiales del **Centro de Recaudación de Ingresos Municipales (CRIM)** de Puerto Rico.

---

## 🌟 Características Principales

* **Formulario AS-52 (Solicitud de Cambio de Dueño):** Llenado automatizado con superposición vectorial de precisión calibrada sobre la plantilla oficial tamaño Legal (`8.5" x 14"`). Incluye datos registrales, notaría, transmitente, adquirentes y residencia anterior.
* **Formulario AS-74 (Hoja de Información de Dueños en Comunidad):** Generación del anexo oficial (`Modelo AS-74-base.pdf`) para listar la totalidad de comuneros o herederos, con bloques de dueño que se añaden y quitan dinámicamente (hasta 10 por hoja).
* **Historial de Casos:** Cada PDF generado queda registrado con fecha, catastro y una copia completa de sus datos, para reabrir el PDF o **restaurar el caso en el formulario** con un clic.
* **Validación de Datos:** Antes de generar, la app normaliza y verifica seguros sociales, fechas, teléfonos, correos y porcientos de participación (incluyendo que sumen 100 %), y avisa de cualquier problema sin bloquear.
* **Ajuste Automático de Texto:** Si un nombre o dirección no cabe en su recuadro, la fuente se reduce automáticamente; si aun así se desborda, se emite un aviso.
* **Protección contra Sobrescritura:** Si ya existe un PDF con el mismo nombre, la app pregunta antes de reemplazarlo y puede guardar una versión nueva (`_v2`, `_v3`…).
* **Autoguardado y Recuperación:** Un borrador se guarda periódicamente; al reabrir la app puedes continuar donde quedaste.
* **Coordenadas Calibrables sin Código:** Las posiciones de impresión se pueden exportar a `coordenadas.json` y ajustar a mano si el CRIM modifica la plantilla.
* **Gestión de Casos en JSON:** Guarda y abre expedientes completos, con menú de **casos recientes**.

---

## 🛠️ Requisitos e Instalación

### Requisitos previos:
* Python 3.9 o superior (incluye `tkinter` en Windows y macOS; en Linux: `sudo apt install python3-tk`).

### Librerías requeridas:

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install customtkinter PyPDF2 reportlab
```

---

## 🚀 Uso de la Aplicación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/eliascpa/crim-as52-as74-filler.git
   ```

2. Ejecuta la aplicación desde la carpeta del proyecto:
   ```bash
   python crim_app.py
   ```
   *(En macOS y Linux usa `python3 crim_app.py`.)*

### Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+N` | Nuevo caso (limpia la pestaña activa) |
| `Ctrl+O` | Abrir caso guardado |
| `Ctrl+S` | Guardar caso |
| `Ctrl+G` | Generar el PDF de la pestaña activa |

---

## 📂 Dónde se guardan las cosas

| Qué | Dónde |
|-----|-------|
| PDFs generados | Carpeta del programa, o la que elijas en *Herramientas > Preferencias* |
| Historial de casos | `~/.crim_filler/historial.jsonl` |
| Copias de cada caso generado | `~/.crim_filler/casos/` |
| Borrador automático | `~/.crim_filler/borrador_auto.json` |
| Preferencias y recientes | `~/.crim_filler/config.json`, `recientes.json` |

> ⚠️ **Aviso de privacidad:** los archivos de casos contienen números de Seguro Social **sin cifrar**. Guárdalos en una carpeta protegida y nunca los subas a un repositorio público. El `.gitignore` ya excluye `*.json` y `*.pdf` por esta razón.

---

## 🎯 Calibrar las posiciones de impresión

Si el CRIM actualiza la plantilla y el texto se descuadra, **no hace falta editar el código**:

1. *Herramientas > Exportar coordenadas para calibrar* → crea `coordenadas.json`.
2. Edita los valores. Cada campo es `[x, y, tamaño_fuente, ancho_máximo]`, medidos en puntos desde la esquina **superior izquierda** de la hoja legal (612 × 1008 pt).
3. *Herramientas > Recargar coordenadas* y vuelve a generar.

---

## 📋 Historial de Actualizaciones (Changelog)

### **v3.01 (Versión Actual)**
* ☑️ **Casillas de cotejo del AS-52 ahora las elige el usuario.** Hasta la v3.00 el programa estampaba siempre `Con Estructura`, `Hormigón` y `Partición Hereditaria`, sin importar la propiedad ni el negocio. Ahora hay controles para las cuatro filas:
  * **Tipo de Solar:** Vacante / Con Estructura
  * **Tipo de Uso:** Residencial / Comercial
  * **Material de la Estructura:** Hormigón / **Mixto** / **Madera** *(las dos últimas no existían en el programa)*
  * **Negocio Jurídico Efectuado:** Compra Venta, Donación, Partición Hereditaria, Liquidación de Sociedad de Ganaciales, Permuta, Cesión, Segregación, Agrupación y **Otros** (con campo de texto) *(sólo existía Partición Hereditaria)*
* 🚫 **Todas las casillas admiten "Sin Marcar"** y ese es el valor inicial: el programa ya no marca nada por su cuenta.
* 🎯 **Coordenadas verificadas contra la plantilla oficial.** Las 18 casillas se detectaron automáticamente sobre el PDF del CRIM y las `X` se centraron con la misma convención de la calibración anterior.
* ⚠️ **Avisos de coherencia:** solar vacante con material o uso marcado, solar con estructura sin material, y "Otros" sin especificar.
* ↩️ **Casos v2.x siguen abriendo:** conservan uso y cabida; las casillas nuevas quedan *Sin Marcar* (el programa no adivina lo que antes se estampaba solo).

### **v3.00**
* 📜 **Historial de Casos:** Nueva pestaña que registra cada PDF generado con su fecha, catastro y una copia de los datos, permitiendo reabrir el PDF o restaurar el caso completo en el formulario.
* ✅ **Validación y Normalización:** Seguros sociales, fechas, teléfonos, correos y porcientos se corrigen de formato automáticamente y se avisa de errores (fechas inexistentes, SSN incompletos, porcientos que no suman 100 %).
* 📐 **Ajuste Automático de Texto:** La fuente se reduce cuando un valor no cabe en su recuadro, con aviso si aun así se desborda.
* 🛡️ **Protección contra Sobrescritura:** Se pregunta antes de reemplazar un PDF existente, con opción de guardar una versión nueva.
* 💾 **Autoguardado y Recuperación:** Borrador periódico y opción de "continuar donde quedaste" al reabrir la app.
* 🎛️ **Barra de Menú Completa:** Archivo (con casos recientes), Herramientas (preferencias, calibración de coordenadas), Ver (tema claro/oscuro) y Ayuda, más atajos de teclado.
* 👥 **Dueños Dinámicos en AS-74:** Botones para añadir y quitar bloques de comuneros hasta los 10 que admite la hoja oficial (antes solo se mostraban 3).
* 📐 **Coordenadas Externalizables:** Las posiciones de impresión se pueden exportar a `coordenadas.json` y ajustar sin tocar el código.
* ⚙️ **Preferencias:** Certificante por defecto, carpeta de salida e intervalo de autoguardado configurables (se eliminó el nombre que estaba fijo en el código).
* 🐛 **Correcciones:** Se cerraron los manejadores de archivo de las plantillas PDF, las plantillas y salidas ahora se resuelven desde la carpeta del programa (antes fallaba si se ejecutaba desde otro directorio), y se añadió `requirements.txt`.

### **v2.04**
* ✍️ **Tipografía Unificada:** Se cambió la fuente de la certificación del AS-74 a `Helvetica` para mantener uniformidad con todo el documento.
* 🎯 **Alineación de Casilla Hereditaria:** Se corrigió la posición horizontal de la `X` de comunidad hereditaria a `X = 396.0`.
* 📏 **Fecha de Certificación sobre la Línea:** Se ajustó la coordenada vertical de la fecha a `Y = 896.0`.

### **v2.03**
* ➡️ **Seguro Social en AS-74:** Se desplazó la posición inicial del texto del Seguro Social a `X = 430.0` para evitar que se encimara sobre la etiqueta *"Número de Seguro Social:"*.

### **v2.02**
* 📄 **Integración de `Modelo AS-74-base.pdf`:** Sustitución de la plantilla genérica por el documento oficial base del CRIM.
* 👥 **Soporte Multi-Dueño:** Incorporación de campos para múltiples dueños/comuneros y tipo de comunidad (*Hereditaria* vs *Pro-Indiviso*).
* 💾 **Persistencia JSON AS-74:** Botones independientes para guardar y abrir expedientes AS-74.

### **v2.01**
* 🔢 **Sistema de Versiones Semánticas:** Integración de la versión visible en el título de la ventana y el encabezado.

### **v2.00**
* 📜 **Campos Notariales y Residencia Anterior:** Adición de número de escritura, fecha, notario otorgante, teléfono y sección completa de la residencia anterior del adquirente.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
