"""
Script para verificar que los extractores están registrados correctamente.
Ejecutar desde la carpeta del proyecto:
    python verificar_extractores.py
"""
import sys
import os

# Añadir carpeta del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from extractores import EXTRACTORES
    
    print("=" * 60)
    print("EXTRACTORES REGISTRADOS")
    print("=" * 60)
    
    # Mostrar todos los extractores registrados
    for nombre, extractor in sorted(EXTRACTORES.items()):
        print(f"  {nombre:<30} -> {extractor.__name__}")
    
    print(f"\nTotal: {len(EXTRACTORES)} extractores registrados")
    
    # Verificar los nuevos
    print("\n" + "=" * 60)
    print("VERIFICACION EXTRACTORES NUEVOS")
    print("=" * 60)
    
    nuevos = ['MOLLETES', 'MOLLETES ARTESANOS', 'ECOFICUS', 'LA BARRA DULCE', 'BARRA DULCE', 'SABORES DE PATERNA', 'SABORES PATERNA']
    
    for nombre in nuevos:
        if nombre in EXTRACTORES:
            print(f"  ✅ {nombre} -> {EXTRACTORES[nombre].__name__}")
        else:
            print(f"  ❌ {nombre} -> NO REGISTRADO")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
