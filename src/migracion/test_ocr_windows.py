#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de OCR en Windows.
Ejecutar: python test_ocr_windows.py <archivo.pdf>
"""

import sys
from pathlib import Path

def test_ocr(pdf_path):
    print("="*60)
    print("DIAGNÓSTICO OCR - Windows")
    print("="*60)
    
    # 1. Verificar archivo
    pdf = Path(pdf_path)
    if not pdf.exists():
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    print(f"✅ Archivo: {pdf.name}")
    
    # 2. Probar pytesseract
    print("\n--- Verificando pytesseract ---")
    try:
        import pytesseract
        print(f"✅ pytesseract importado")
        # Verificar Tesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        # Listar idiomas
        langs = pytesseract.get_languages()
        print(f"   Idiomas disponibles: {', '.join(langs)}")
        if 'spa' in langs:
            print("✅ Idioma español disponible")
        else:
            print("⚠️ Idioma español NO disponible - instalar: ")
            print("   Descargar spa.traineddata de:")
            print("   https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata")
            print("   y copiar a: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
    except Exception as e:
        print(f"❌ Error pytesseract: {e}")
        return
    
    # 3. Probar pdf2image
    print("\n--- Verificando pdf2image ---")
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image importado")
        # Intentar convertir
        images = convert_from_path(str(pdf), dpi=150, first_page=1, last_page=1)
        print(f"✅ PDF convertido a imagen: {images[0].size}")
    except Exception as e:
        print(f"❌ Error pdf2image: {e}")
        if "poppler" in str(e).lower() or "pdftoppm" in str(e).lower():
            print("\n⚠️ POPPLER NO INSTALADO")
            print("   Descargar de: https://github.com/oschwartz10612/poppler-windows/releases")
            print("   Extraer y añadir bin/ al PATH del sistema")
        return
    
    # 4. Probar pdfplumber (alternativa)
    print("\n--- Verificando pdfplumber ---")
    try:
        import pdfplumber
        print("✅ pdfplumber importado")
        with pdfplumber.open(str(pdf)) as p:
            page = p.pages[0]
            # Texto nativo
            texto = page.extract_text() or ""
            print(f"   Texto nativo: {len(texto)} chars")
            # Imagen
            img = page.to_image(resolution=300)
            print(f"✅ Imagen generada: {img.original.size}")
    except Exception as e:
        print(f"❌ Error pdfplumber: {e}")
    
    # 5. Probar OCR completo
    print("\n--- Probando OCR ---")
    try:
        from PIL import Image, ImageEnhance
        # Usar la imagen de pdfplumber
        with pdfplumber.open(str(pdf)) as p:
            img = p.pages[0].to_image(resolution=400)
            pil_img = img.original.convert('L')
            pil_img = ImageEnhance.Contrast(pil_img).enhance(2)
            
            # OCR
            try:
                texto = pytesseract.image_to_string(pil_img, lang='spa', config='--psm 6')
            except:
                texto = pytesseract.image_to_string(pil_img, lang='eng', config='--psm 6')
            
            print(f"✅ OCR completado: {len(texto)} caracteres")
            print("\nPrimeras 10 líneas del texto:")
            for i, linea in enumerate(texto.split('\n')[:10]):
                print(f"   {i+1}: {linea[:70]}")
    except Exception as e:
        print(f"❌ Error OCR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("FIN DIAGNÓSTICO")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_ocr_windows.py <archivo.pdf>")
        sys.exit(1)
    test_ocr(sys.argv[1])
