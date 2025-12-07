# Extractor de Facturas Gmail

## Instalación

1. **Instalar Python 3.8+** (si no lo tienes)
   - Descargar de: https://www.python.org/downloads/

2. **Descargar esta carpeta** a tu ordenador

3. **Abrir terminal/CMD** en la carpeta del proyecto

4. **Instalar dependencias:**
   ```
   pip install -r requirements.txt
   ```

## Primera ejecución

1. **Ejecutar el script:**
   ```
   python gmail_extractor.py
   ```

2. **Se abrirá el navegador** - Inicia sesión con `quesoambrosio@gmail.com`

3. **Acepta los permisos** cuando te lo pida

4. **El script mostrará** los emails de la carpeta FACTURAS

## Archivos

- `credentials.json` - Credenciales OAuth (NO COMPARTIR)
- `token.pickle` - Token de acceso (se genera automáticamente)
- `gmail_extractor.py` - Script principal
- `requirements.txt` - Dependencias Python

## Seguridad

⚠️ **IMPORTANTE:** No compartas `credentials.json` ni `token.pickle` con nadie.
Contienen acceso a tu cuenta de Gmail.

## Soporte

Si hay errores, guarda el mensaje y consúltame.
