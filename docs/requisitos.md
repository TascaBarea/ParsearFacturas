# Requisitos de instalación

Este documento explica cómo preparar el entorno de trabajo para el proyecto **ParsearFacturas**.

## 1. Requisitos previos
- **Python 3.11+** (recomendado 3.11 o superior).
- **pip** (gestor de paquetes de Python).
- Opcional: **virtualenv** o **venv** para aislar dependencias.

## 2. Instalar dependencias
En la raíz del proyecto encontrarás el archivo estándar `requirements.txt`.

Ejecuta:
```bash
pip install -r requirements.txt
```

Esto instalará las librerías necesarias, entre ellas:
- `pypdf` → lectura de PDFs.
- `pandas`, `openpyxl` → manipulación y exportación de datos.
- `rapidfuzz` → coincidencia tolerante de categorías.
- `loguru` → logging.
- `pytesseract`, `pillow` → OCR opcional si se necesitara.

## 3. Entorno virtual (recomendado)
Para no mezclar dependencias con otros proyectos:
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## 4. Verificar instalación
Ejecuta:
```bash
python -m src.facturas.cli --help
```

Deberías ver las opciones de la CLI (`--lines`, `--tsv`, `--total`, etc.).

## 5. Notas adicionales
- En Windows, asegúrate de instalar también [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) si deseas usar OCR avanzado.
- En caso de problemas con `openpyxl`, actualiza a la última versión:
```bash
pip install --upgrade openpyxl
```

## 6. Guía rápida Windows
1. Verifica que tienes Python instalado:
   ```powershell
   py --version
   ```
   Si no aparece, descarga [Python 3.11+ para Windows](https://www.python.org/downloads/windows/).

2. Crea el entorno virtual:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

3. Instala dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

4. Prueba la CLI:
   ```powershell
   py -m src.facturas.cli --help
   ```

5. Si usas OCR: instala [Tesseract OCR para Windows](https://github.com/UB-Mannheim/tesseract/wiki).
   Luego añade la ruta de instalación (ejemplo: `C:\Program Files\Tesseract-OCR`) a la variable de entorno `PATH`.

---

Este documento complementa a `requirements.txt` y se debe mantener sincronizado con él cuando se añadan o eliminen dependencias.

