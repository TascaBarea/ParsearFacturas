# 🚀 LÉEME PRIMERO - ParsearFacturas

> **Este documento es tu punto de entrada.** Léelo antes de cada sesión.

---

## 📍 ESTADO ACTUAL

| Dato | Valor |
|------|-------|
| **Versión** | v3.50 |
| **Fecha** | 13/12/2025 |
| **Script** | `src/migracion/migracion_historico_2025_v3_50.py` |
| **Facturas OK** | 188/252 (74.6%) |
| **Pendiente** | 13 CUADRE_PENDIENTE, 24 PDF_SIN_TEXTO |

---

## ▶️ AL EMPEZAR SESIÓN CON CLAUDE

```
1. Abre Claude.ai
2. Sube este archivo: docs/LEEME_PRIMERO.md
3. Escribe: "Continúo proyecto ParsearFacturas"
4. Si necesitas contexto específico, sube también:
   - docs/ESTADO_ACTUAL.md (detalles técnicos)
   - El script v3.XX que estés usando
```

---

## ⏹️ AL TERMINAR SESIÓN

```
1. Pide a Claude: "Actualiza ESTADO_ACTUAL.md con los cambios de hoy"
2. Descarga los archivos nuevos (script, docs)
3. Copia a tu carpeta del proyecto
4. En terminal:
   git add .
   git commit -m "sesión YYYY-MM-DD: descripción breve"
   git push
```

---

## 🖥️ COMANDO PARA EJECUTAR

```bash
python "C:\...\src\migracion\migracion_historico_2025_v3_50.py" -i "RUTA_FACTURAS" -d "RUTA_DICCIONARIO.xlsx"
```

**Ejemplo completo:**
```bash
python "C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\src\migracion\migracion_historico_2025_v3_50.py" -i "C:\Users\jaime\Dropbox\File inviati\TASCA BAREA S.L.L\CONTABILIDAD\FACTURAS 2025\FACTURAS RECIBIDAS\1 TRI 2025" -d "C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\DiccionarioProveedoresCategoria.xlsx"
```

---

## 📁 ARCHIVOS IMPORTANTES

| Qué | Dónde |
|-----|-------|
| Script principal | `src/migracion/migracion_historico_2025_v3_50.py` |
| Estado del proyecto | `docs/ESTADO_ACTUAL.md` |
| Lista de proveedores | `docs/PROVEEDORES.md` |
| Diccionario categorías | `DiccionarioProveedoresCategoria.xlsx` |
| Maestro proveedores | `MAESTRO_PROVEEDORES.xlsx` |

---

## ❌ NO HACER

- ❌ Crear archivos `.bak`, `.bak2`, `.backup`
- ❌ Modificar versiones antiguas (v3.41, v3.42...)
- ❌ Terminar sesión sin hacer git commit + push
- ❌ Trabajar sin saber qué versión es la actual

---

## 🆘 SI ALGO FALLA

1. **El script no encuentra el archivo:**
   - Verifica las rutas entre comillas
   - Usa rutas absolutas completas

2. **Error de Python:**
   - Copia el error completo
   - Pégalo a Claude

3. **No sé qué versión usar:**
   - La versión actual está arriba de este documento
   - Siempre usa la más alta (v3.50 > v3.49 > v3.48...)

---

*Última actualización: 13/12/2025*
