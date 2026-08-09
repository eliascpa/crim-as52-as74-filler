# 🗒️ Bitácora de Trabajo

Registro de los cambios trabajados en el proyecto, en orden cronológico.
El detalle "de cara al usuario" vive en el changelog del [README](README.md);
aquí queda el **por qué** de cada decisión y lo que quedó pendiente.

---

## 📅 8 de agosto de 2026 — de v2.04 a v3.01

Punto de partida: commit `0ce2a31` (v2.04). Todo lo de abajo está **sin commit**
al momento de escribir esta bitácora.

### 1. Revisión de dependencias

**Pregunta:** ¿qué falta instalar en esta PC para correr el programa?

**Hallazgo:** nada. Todo estaba ya instalado:

| Dependencia | Versión en la PC |
|---|---|
| Python | 3.11.9 |
| customtkinter | 6.0.0 |
| PyPDF2 | 3.0.1 |
| reportlab | 5.0.0 |
| tkinter, pillow, darkdetect, packaging | presentes |

**Nota:** en Windows el comando es `python crim_app.py`, no `python3` como decía
el README (eso aplica a macOS/Linux). Ya está corregido.

---

### 2. v3.00 — Historial, validación y mantenimiento

Salió de una revisión crítica del código. Se agrupa en cuatro bloques.

#### Bugs corregidos

| Bug | Riesgo | Arreglo |
|---|---|---|
| `PdfReader(open(...))` sin cerrar | Fuga de manejadores de archivo | Se usa `with open(...)` en `componer_pdf()` |
| Plantillas buscadas en el directorio *actual* | El programa fallaba si se corría desde otra carpeta | Se resuelven contra `BASE_DIR` (carpeta del script) |
| Nombre `"Lcdo. Elías Fernández"` fijo en el código | Dato personal en el fuente; inservible para otro usuario | Pasó a preferencia configurable |
| Faltaba `requirements.txt` | Instalación dependía de recordar el `pip install` | Añadido |
| `.gitignore` no exceptuaba `Modelo AS-74-base.pdf` | La plantilla oficial se hubiera podido perder | Excepción añadida |

#### Historial y recuperación

Era la petición central: *poder ver qué se generó y poder restaurarlo.*

- Tercera pestaña **Historial de Casos**.
- **Cada** generación de PDF guarda automáticamente una copia completa de los
  datos en `~/.crim_filler/casos/`, aunque nunca se haya oprimido "Guardar".
  Esto es lo que hace posible restaurar sin depender de la disciplina del usuario.
- Por fila: **Abrir PDF** y **↩️ Restaurar datos**.
- Autoguardado periódico + diálogo *"¿Continuar donde quedaste?"* al reabrir.

> Este mecanismo ya se ganó el sueldo: durante las pruebas de la v3.01 hubo que
> reiniciar la app y el borrador recuperó datos que se habían escrito en la
> ventana anterior (catastro 380-00-000-00-10, Ponce). Sin él se habrían perdido.

#### Validación de datos

Normalización automática, con avisos que **no bloquean** la generación:

- SSN → `599112233` se convierte en `599-11-2233`
- Fechas → `3/7/1975` se convierte en `03/07/1975`; se rechaza `31/02/2026`
- Teléfonos → `7875551234` se convierte en `(787) 555-1234`
- Correos y porcientos; se avisa si los porcientos no suman 100 %

**Decisión:** avisar sin bloquear. El usuario a veces necesita generar un
formulario incompleto a propósito; el programa no debe impedirlo, solo advertir.

#### Interfaz

- Barra de menú: Archivo (con **casos recientes**), Herramientas, Ver, Ayuda.
- Atajos `Ctrl+N` / `Ctrl+O` / `Ctrl+S` / `Ctrl+G`.
- Barra de estado con la última acción.
- **AS-74: dueños dinámicos.** El código ya soportaba 10 comuneros pero la
  interfaz solo mostraba 3. Se añadieron botones ➕ / ➖ hasta el límite real.
- Protección contra sobrescritura de PDFs (opción de guardar `_v2`, `_v3`…).
- Ajuste automático de fuente cuando un texto no cabe en su recuadro.
- **Coordenadas externalizables** a `coordenadas.json` para recalibrar sin
  tocar el código si el CRIM cambia la plantilla.

---

### 3. v3.01 — Casillas de cotejo del AS-52

**Problema reportado:** el formulario no daba opciones para marcar vacante,
comercial, hormigón, con estructura, residencial o madera.

**Lo que se encontró al investigar** — el problema era mayor. Tres casillas
estaban **fijas en el código** y se estampaban siempre:

```python
marca("marca_particion")        # ← siempre, en TODOS los AS-52
marca("marca_con_estructura")   # ← siempre
marca("marca_hormigon")         # ← siempre
```

Y otras cinco casillas de la plantilla oficial **ni siquiera existían** en el
programa: `Vacante`, `Mixto`, `Madera`, y las 8 alternativas de negocio jurídico.

| Fila del formulario | Antes | Ahora |
|---|---|---|
| Tipo de Solar | `Con Estructura` siempre; `Vacante` no existía | Vacante / Con Estructura / Sin Marcar |
| Uso | Funcionaba | Residencial / Comercial / **Sin Marcar** |
| Material | `Hormigón` siempre; **`Mixto` y `Madera` no existían** | Hormigón / Mixto / Madera / Sin Marcar |
| Negocio Jurídico | `Partición Hereditaria` siempre; **las otras 8 no existían** | Desplegable con las 9 + texto para "Otros" |

> ⚠️ **La más seria era la del negocio jurídico:** cada AS-52 generado con
> v2.x/v3.00 salía caracterizado como *partición hereditaria*, fuera compra
> venta, donación o permuta. Vale la pena revisar los formularios ya radicados.

Ahora **todo arranca en "Sin Marcar"**: el programa no marca nada por su cuenta.

#### Cómo se obtuvieron las coordenadas

No se estimaron a ojo:

1. Se extrajo el texto de la plantilla con sus posiciones para ubicar las filas.
2. Se renderizó el PDF a imagen y se **detectaron automáticamente los 18
   recuadros** de cotejo, obteniendo el centro exacto de cada uno.
3. Al comparar con la calibración aprobada en v2.04 se dedujo que la convención
   existente era exactamente **`centro − 1.45`**. Se aplicó esa misma regla a
   las casillas nuevas, para que todo el formulario quede uniforme.
4. Se generó un PDF de prueba con **las 18 casillas marcadas a la vez** y se
   revisó visualmente.

Ese paso 4 detectó un error: `Compra Venta` y `Permuta` estaban 2.7 pt corridas
y la `X` se salía del recuadro. Corregido de `26.5` a `24.1`.

#### Avisos de coherencia añadidos

- Solar vacante pero con material o uso marcado
- Solar con estructura pero sin material
- "Otros" elegido sin especificar cuál

---

## ✅ Pruebas

79 pruebas automatizadas, todas pasando. Los scripts viven en el scratchpad de
la sesión (no en el repo). Cubren:

- Validadores y normalización de datos
- Autoajuste de fuente
- Generación real de ambos PDFs, verificando que el texto cae sobre la plantilla
- Anti-sobrescritura (`_v2`)
- Historial, snapshots y restauración
- Dueños dinámicos del AS-74 (1 a 10)
- **Que se marque exactamente lo elegido**, incluyendo que un formulario vacío
  no marque *ninguna* casilla
- Compatibilidad con casos guardados en v2.x
- Ida y vuelta guardar → cargar

---

## 📌 Pendientes y decisiones abiertas

| Tema | Estado |
|---|---|
| **Commit** | Nada se ha commiteado. `.gitignore`, `README.md`, `crim_app.py` modificados; `requirements.txt` y este archivo son nuevos. |
| **Casos v2.x** | Al abrirlos, las casillas nuevas quedan *Sin Marcar* — el programa no adivina lo que antes se estampaba solo. Hay que volver a elegirlas al reimprimir. |
| **Formularios ya radicados** | Revisar cuáles salieron con `Partición Hereditaria`, `Con Estructura` y `Hormigón` incorrectos. |
| **Cifrado de casos** | Los `.json` guardan Seguros Sociales **en texto plano**. Hay aviso en Preferencias y README, pero el cifrado real está pendiente. |
| **Carpeta `PDFgear/`** | Apareció sin rastrear en el repo. No es parte de este trabajo; decidir si se ignora o se borra. |
| **Ventanas de Foxit** | Las pruebas abrieron ~15 visores de PDF (7:35 PM del 8/8/2026). Los scripts ya están corregidos para no abrirlos, pero esas ventanas quedaron abiertas. |

---

## 📂 Dónde queda cada cosa

| Qué | Dónde |
|---|---|
| PDFs generados | Carpeta del programa, o la configurada en Herramientas › Preferencias |
| Historial | `~/.crim_filler/historial.jsonl` |
| Copia de cada caso generado | `~/.crim_filler/casos/` |
| Borrador automático | `~/.crim_filler/borrador_auto.json` |
| Preferencias y recientes | `~/.crim_filler/config.json`, `recientes.json` |
| Calibración local (opcional) | `coordenadas.json` en la carpeta del programa (ignorado por git) |
