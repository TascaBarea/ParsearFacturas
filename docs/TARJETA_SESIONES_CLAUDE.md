# 📋 TARJETA RÁPIDA - SESIONES CLAUDE

Imprimir y tener visible junto al ordenador.

---

## ▶️ AL INICIAR SESIÓN

```
□ 1. Abrir terminal en carpeta del proyecto
□ 2. Ejecutar: git pull
□ 3. Ir a Claude.ai
□ 4. Subir archivo: docs/ESTADO_PROYECTO.md
□ 5. Escribir: "Continúo proyecto facturas, contexto adjunto"
```

---

## ⏹️ AL FINALIZAR SESIÓN

```
□ 1. Pedir a Claude: "Actualiza ESTADO_PROYECTO.md"
□ 2. Descargar archivos generados
□ 3. Copiar archivos a carpeta del proyecto
□ 4. Ejecutar en terminal:
      git add .
      git commit -m "sesión FECHA: DESCRIPCIÓN"
      git push
□ 5. Verificar en GitHub que subió correctamente
```

---

## ❌ NUNCA HACER

- Crear archivos .bak, .bak2, .backup
- Saltarse el git pull al inicio
- Terminar sin hacer git push
- Modificar código sin documentar

---

## 📁 ARCHIVOS IMPORTANTES

| Qué | Dónde |
|-----|-------|
| Estado proyecto | `docs/ESTADO_PROYECTO.md` |
| Script migración | `src/migracion/migracion_historico.py` |
| Plantilla YAML | `patterns/_PLANTILLA.yml` |
| Diccionario | `DiccionarioProveedoresCategoria.xlsx` |

---

## 🆘 SI ALGO SALE MAL

```bash
# Ver estado de cambios
git status

# Deshacer cambios locales (¡CUIDADO!)
git checkout -- archivo.py

# Ver historial
git log --oneline -10
```

---

## 📞 CONTEXTO RÁPIDO PARA CLAUDE

Si no tienes ESTADO_PROYECTO.md, copia esto:

```
Proyecto: ParsearFacturas (GitHub privado TascaBarea)
Script actual: migracion_historico v3.4
Extractores: 16 proveedores
Pendiente: Migrar extractores a YAML
```
