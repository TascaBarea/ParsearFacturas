#!/usr/bin/env python3
"""
EXTRACTOR DE FACTURAS GMAIL
===========================
Proyecto ParsearFacturas - Fase 1
Versión: 2.3 (Filtrado inteligente de JPGs)

Cambios v2.3:
- Si email tiene PDF, ignora TODOS los JPG/PNG (son logos/firmas)
- Filtro por tamaño: <30KB = logo/icono
- Más patrones de exclusión: gnavision, tmp, aniversario, etc.

Uso:
    python gmail_extractor.py              # Solo listar emails
    python gmail_extractor.py --download   # Descargar PDFs
    python gmail_extractor.py --dry-run    # Simular sin marcar leídos

Primera ejecución:
    - Se abrirá el navegador para autorizar
    - Inicia sesión con la cuenta de Gmail
    - Acepta los permisos
    - El token se guardará para futuras ejecuciones
"""

import os
import sys
import base64
import pickle
import argparse
import json
from pathlib import Path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configuración
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
LABEL_FACTURAS = 'FACTURAS'
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
DOWNLOAD_DIR = 'downloads'
LOG_DIR = 'logs'

# Colores para la consola
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{text:^60}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}\n")

def print_success(text):
    print(f"{Color.GREEN}✓ {text}{Color.END}")

def print_warning(text):
    print(f"{Color.YELLOW}⚠ {text}{Color.END}")

def print_error(text):
    print(f"{Color.RED}✗ {text}{Color.END}")

def print_info(text):
    print(f"{Color.CYAN}ℹ {text}{Color.END}")

def authenticate():
    """Autenticación OAuth2 con Gmail"""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Renovando token...")
            creds.refresh(Request())
        else:
            print("Iniciando autenticación OAuth2...")
            print("Se abrirá el navegador para autorizar la aplicación.")
            print()
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print_success("Token guardado para futuras ejecuciones")
    
    return creds

def get_label_id(service, label_name):
    """Obtener el ID de una etiqueta por su nombre"""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    for label in labels:
        if label['name'].upper() == label_name.upper():
            return label['id']
    return None

def get_unread_emails(service, label_id):
    """Obtener emails no leídos de una etiqueta"""
    query = 'is:unread'
    results = service.users().messages().list(
        userId='me',
        labelIds=[label_id],
        q=query
    ).execute()
    
    return results.get('messages', [])

def get_email_details(service, msg_id):
    """Obtener detalles de un email"""
    msg = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()
    
    headers = msg['payload']['headers']
    
    details = {
        'id': msg_id,
        'subject': '',
        'from': '',
        'date': '',
        'attachments': []
    }
    
    for header in headers:
        name = header['name'].lower()
        if name == 'subject':
            details['subject'] = header['value']
        elif name == 'from':
            details['from'] = header['value']
        elif name == 'date':
            details['date'] = header['value']
    
    # Buscar adjuntos
    def find_attachments(payload):
        attachments = []
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    attachments.append({
                        'filename': part['filename'],
                        'mimeType': part['mimeType'],
                        'size': part['body'].get('size', 0),
                        'attachmentId': part['body'].get('attachmentId')
                    })
                attachments.extend(find_attachments(part))
        return attachments
    
    details['attachments'] = find_attachments(msg['payload'])
    
    return details

def is_invoice_attachment(filename, email_subject='', email_has_pdf=False, file_size=0):
    """
    Determinar si un adjunto parece ser una factura.
    
    Reglas:
    - PDF sin keywords de exclusión → SÍ es factura
    - JPG/PNG: SOLO si el email NO tiene PDF adjunto Y pasa filtros de tamaño
    - Imágenes pequeñas (<30KB) o con nombres de decoración → NO
    
    Args:
        filename: Nombre del archivo adjunto
        email_subject: Asunto del email
        email_has_pdf: True si el email ya contiene un PDF adjunto
        file_size: Tamaño del archivo en bytes
    """
    filename_lower = filename.lower()
    subject_lower = email_subject.lower()
    
    # Palabras que indican factura
    invoice_keywords = ['factura', 'fra', 'invoice', 'fatura', 'proforma']
    
    # Palabras que indican NO es factura
    exclude_keywords = ['transfer', 'justificante', 'comprobante', 'albaran', 
                       'albarán', 'presupuesto', 'quote', 'logo', 'firma',
                       'delivery', 'recibo', 'certificado', 'titularidad',
                       'banner', 'header', 'footer', 'pie']
    
    # Patrones de nombre que indican logo/firma/decoración
    decoration_patterns = ['logo', 'firma', 'signature', 'image00', 'outlook', 
                          'icon', 'avatar', 'banner', 'cid:', 'inline',
                          'gnavision', 'footer', 'header', 'fondo', 'aniversario',
                          'tmp', 'temp']
    
    # Extensiones
    pdf_extensions = ['.pdf']
    image_extensions = ['.jpg', '.jpeg', '.png']
    
    is_pdf = any(filename_lower.endswith(ext) for ext in pdf_extensions)
    is_image = any(filename_lower.endswith(ext) for ext in image_extensions)
    is_excluded = any(kw in filename_lower for kw in exclude_keywords)
    is_decoration = any(pat in filename_lower for pat in decoration_patterns)
    
    # PDF sin keywords de exclusión → SÍ es factura
    if is_pdf and not is_excluded:
        return True
    
    # REGLA CLAVE: Si el email ya tiene PDF, ignorar TODOS los JPG/PNG
    # (serán logos, firmas, banners decorativos)
    if is_image and email_has_pdf:
        return False
    
    # Imagen sin PDF en el email: evaluar si puede ser factura escaneada
    if is_image and not is_excluded and not is_decoration:
        # Filtro por tamaño: muy pequeño = logo/icono
        size_kb = file_size / 1024 if file_size else 0
        if size_kb < 30:  # Menos de 30KB probablemente es logo
            return False
        
        # Si el asunto menciona factura, más probable que sea válida
        subject_has_invoice = any(kw in subject_lower for kw in invoice_keywords)
        if subject_has_invoice:
            return True
        
        # Sin PDF y tamaño razonable: aceptar con precaución
        # (mejor descargar de más que perder una factura)
        if size_kb > 100:  # >100KB probablemente es documento escaneado
            return True
    
    return False


def email_has_pdf_attachment(attachments):
    """Comprobar si la lista de adjuntos contiene al menos un PDF"""
    for att in attachments:
        if att.get('filename', '').lower().endswith('.pdf'):
            return True
    return False

def sanitize_filename(filename):
    """Limpiar nombre de archivo para Windows"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def download_attachment(service, msg_id, attachment_id, filename, download_dir):
    """Descargar un adjunto"""
    try:
        attachment = service.users().messages().attachments().get(
            userId='me',
            messageId=msg_id,
            id=attachment_id
        ).execute()
        
        file_data = base64.urlsafe_b64decode(attachment['data'])
        
        # Crear directorio si no existe
        os.makedirs(download_dir, exist_ok=True)
        
        # Sanear nombre de archivo
        safe_filename = sanitize_filename(filename)
        filepath = os.path.join(download_dir, safe_filename)
        
        # Si ya existe, añadir número
        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}{ext}"
            counter += 1
        
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        return filepath
    except Exception as e:
        print_error(f"Error descargando {filename}: {e}")
        return None

def mark_as_read(service, msg_id):
    """Marcar email como leído"""
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return True
    except Exception as e:
        print_error(f"Error marcando como leído: {e}")
        return False

def save_execution_log(log_data, log_dir):
    """Guardar log de ejecución en JSON"""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    log_file = os.path.join(log_dir, f'ejecucion_{timestamp}.json')
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    return log_file

def main():
    # Parsear argumentos
    parser = argparse.ArgumentParser(description='Extractor de facturas de Gmail')
    parser.add_argument('--download', action='store_true', help='Descargar PDFs de facturas')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin marcar como leídos')
    parser.add_argument('--limit', type=int, default=None, help='Limitar número de emails a procesar')
    args = parser.parse_args()
    
    print_header("EXTRACTOR DE FACTURAS GMAIL")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"Carpeta objetivo: {LABEL_FACTURAS}")
    print(f"Modo: {'DESCARGA' if args.download else 'SOLO LISTAR'}")
    if args.dry_run:
        print_warning("MODO DRY-RUN: No se marcarán emails como leídos")
    print()
    
    # Autenticar
    print("1. Autenticando con Gmail...")
    try:
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)
        print_success("Conectado a Gmail")
    except Exception as e:
        print_error(f"Error de autenticación: {e}")
        return
    
    # Obtener ID de etiqueta FACTURAS
    print("\n2. Buscando carpeta FACTURAS...")
    label_id = get_label_id(service, LABEL_FACTURAS)
    
    if not label_id:
        print_error(f"No se encontró la etiqueta '{LABEL_FACTURAS}'")
        print("Etiquetas disponibles:")
        results = service.users().labels().list(userId='me').execute()
        for label in results.get('labels', []):
            if not label['name'].startswith('CATEGORY_'):
                print(f"  - {label['name']}")
        return
    
    print_success(f"Etiqueta encontrada (ID: {label_id})")
    
    # Obtener emails no leídos
    print("\n3. Buscando emails no leídos...")
    emails = get_unread_emails(service, label_id)
    
    if not emails:
        print_warning("No hay emails no leídos en FACTURAS")
        return
    
    # Aplicar límite si existe
    if args.limit:
        emails = emails[:args.limit]
        print_info(f"Limitado a {args.limit} emails")
    
    print_success(f"Encontrados {len(emails)} emails no leídos")
    
    # Preparar log de ejecución
    execution_log = {
        'id_ejecucion': datetime.now().strftime('%Y-%m-%d_%H%M'),
        'modo': 'descarga' if args.download else 'listar',
        'dry_run': args.dry_run,
        'emails_procesados': [],
        'resumen': {
            'emails_total': len(emails),
            'facturas_ok': 0,
            'facturas_error': 0,
            'archivos_descargados': []
        },
        'alertas': []
    }
    
    # Crear carpeta de descarga con fecha
    if args.download:
        download_subdir = os.path.join(DOWNLOAD_DIR, datetime.now().strftime('%Y-%m-%d'))
        os.makedirs(download_subdir, exist_ok=True)
        print_info(f"Carpeta de descarga: {download_subdir}")
    
    # Procesar cada email
    print_header("PROCESANDO EMAILS")
    
    for i, email in enumerate(emails, 1):
        details = get_email_details(service, email['id'])
        
        email_log = {
            'gmail_id': email['id'],
            'remitente': details['from'],
            'asunto': details['subject'],
            'fecha': details['date'],
            'adjuntos': []
        }
        
        print(f"\n{Color.BOLD}Email {i}/{len(emails)}{Color.END}")
        print(f"  De: {details['from'][:60]}...")
        print(f"  Asunto: {details['subject'][:60]}...")
        
        # Comprobar si el email tiene PDF (para filtrar JPGs decorativos)
        has_pdf = email_has_pdf_attachment(details['attachments'])
        if has_pdf and any(att['filename'].lower().endswith(('.jpg', '.jpeg', '.png')) for att in details['attachments']):
            print_info("  Email con PDF → ignorando imágenes adjuntas (logos/firmas)")
        
        facturas_descargadas = 0
        
        for att in details['attachments']:
            is_invoice = is_invoice_attachment(
                att['filename'], 
                details['subject'],
                email_has_pdf=has_pdf,
                file_size=att.get('size', 0)
            )
            
            adjunto_log = {
                'nombre_original': att['filename'],
                'es_factura': is_invoice,
                'descargado': False,
                'ruta_local': None
            }
            
            if is_invoice:
                icon = "📄"
                status = f"{Color.GREEN}[FACTURA]{Color.END}"
                
                if args.download and att.get('attachmentId'):
                    filepath = download_attachment(
                        service, 
                        email['id'], 
                        att['attachmentId'], 
                        att['filename'],
                        download_subdir
                    )
                    if filepath:
                        adjunto_log['descargado'] = True
                        adjunto_log['ruta_local'] = filepath
                        execution_log['resumen']['archivos_descargados'].append(filepath)
                        execution_log['resumen']['facturas_ok'] += 1
                        facturas_descargadas += 1
                        status += f" {Color.GREEN}✓ Descargado{Color.END}"
                    else:
                        execution_log['resumen']['facturas_error'] += 1
                        status += f" {Color.RED}✗ Error{Color.END}"
            else:
                icon = "📎"
                status = f"{Color.YELLOW}[OTRO]{Color.END}"
            
            size_kb = att['size'] / 1024
            print(f"    {icon} {att['filename'][:50]} ({size_kb:.1f} KB) {status}")
            
            email_log['adjuntos'].append(adjunto_log)
        
        # Marcar como leído si se descargó al menos una factura
        if args.download and facturas_descargadas > 0 and not args.dry_run:
            if mark_as_read(service, email['id']):
                print_success("  Email marcado como leído")
                email_log['marcado_leido'] = True
            else:
                email_log['marcado_leido'] = False
                execution_log['alertas'].append(f"No se pudo marcar como leído: {email['id']}")
        
        execution_log['emails_procesados'].append(email_log)
    
    # Guardar log
    log_file = save_execution_log(execution_log, LOG_DIR)
    
    # Resumen
    print_header("RESUMEN")
    print(f"  Emails procesados: {len(emails)}")
    if args.download:
        print(f"  Facturas descargadas: {execution_log['resumen']['facturas_ok']}")
        print(f"  Errores: {execution_log['resumen']['facturas_error']}")
        print(f"  Carpeta: {download_subdir}")
    print(f"  Log guardado: {log_file}")
    
    if execution_log['alertas']:
        print_warning(f"\nAlertas ({len(execution_log['alertas'])}):")
        for alerta in execution_log['alertas']:
            print(f"  - {alerta}")
    
    print()
    print_success("Proceso completado")
    
    if not args.download:
        print()
        print_info("Próximo paso: Ejecutar con --download para descargar las facturas")
        print(f"  python gmail_extractor.py --download")

if __name__ == '__main__':
    main()
