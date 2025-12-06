#!/usr/bin/env python3
"""
EXTRACTOR DE FACTURAS GMAIL
===========================
Proyecto ParsearFacturas - Fase 1
Versión: 1.0 (Prueba de conexión)

Este script:
1. Conecta con Gmail usando OAuth2
2. Lista los emails no leídos de la carpeta FACTURAS
3. Muestra información de cada email y sus adjuntos

Uso:
    python gmail_extractor.py

Primera ejecución:
    - Se abrirá el navegador para autorizar
    - Inicia sesión con quesoambrosio@gmail.com
    - Acepta los permisos
    - El token se guardará para futuras ejecuciones
"""

import os
import base64
import pickle
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

# Colores para la consola
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
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

def authenticate():
    """Autenticación OAuth2 con Gmail"""
    creds = None
    
    # Cargar token existente
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, autenticar
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
        
        # Guardar token para futuras ejecuciones
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
    query = f'is:unread'
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
                # Recursivo para partes anidadas
                attachments.extend(find_attachments(part))
        return attachments
    
    details['attachments'] = find_attachments(msg['payload'])
    
    return details

def is_invoice_attachment(filename):
    """Determinar si un adjunto parece ser una factura"""
    filename_lower = filename.lower()
    
    # Palabras que indican factura
    invoice_keywords = ['factura', 'fra', 'invoice', 'fatura', 'proforma']
    
    # Palabras que indican NO es factura
    exclude_keywords = ['transfer', 'justificante', 'comprobante', 'albaran', 
                       'albarán', 'presupuesto', 'quote', 'logo', 'firma']
    
    # Extensiones válidas
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    
    # Verificar extensión
    has_valid_ext = any(filename_lower.endswith(ext) for ext in valid_extensions)
    
    # Verificar si es factura
    is_invoice = any(kw in filename_lower for kw in invoice_keywords)
    is_excluded = any(kw in filename_lower for kw in exclude_keywords)
    
    # PDF sin keywords de exclusión se considera posible factura
    if filename_lower.endswith('.pdf') and not is_excluded:
        return True
    
    return has_valid_ext and is_invoice and not is_excluded

def main():
    print_header("EXTRACTOR DE FACTURAS GMAIL")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"Carpeta objetivo: {LABEL_FACTURAS}")
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
            print(f"  - {label['name']}")
        return
    
    print_success(f"Etiqueta encontrada (ID: {label_id})")
    
    # Obtener emails no leídos
    print("\n3. Buscando emails no leídos...")
    emails = get_unread_emails(service, label_id)
    
    if not emails:
        print_warning("No hay emails no leídos en FACTURAS")
        return
    
    print_success(f"Encontrados {len(emails)} emails no leídos")
    
    # Mostrar detalles de cada email
    print_header("EMAILS ENCONTRADOS")
    
    total_attachments = 0
    invoice_attachments = 0
    
    for i, email in enumerate(emails, 1):
        details = get_email_details(service, email['id'])
        
        print(f"{Color.BOLD}Email {i}/{len(emails)}{Color.END}")
        print(f"  De: {details['from'][:50]}...")
        print(f"  Asunto: {details['subject'][:50]}...")
        print(f"  Fecha: {details['date']}")
        
        if details['attachments']:
            print(f"  Adjuntos ({len(details['attachments'])}):")
            for att in details['attachments']:
                is_invoice = is_invoice_attachment(att['filename'])
                size_kb = att['size'] / 1024
                icon = "📄" if is_invoice else "📎"
                status = f"{Color.GREEN}[FACTURA]{Color.END}" if is_invoice else f"{Color.YELLOW}[OTRO]{Color.END}"
                print(f"    {icon} {att['filename']} ({size_kb:.1f} KB) {status}")
                total_attachments += 1
                if is_invoice:
                    invoice_attachments += 1
        else:
            print(f"  {Color.YELLOW}Sin adjuntos{Color.END}")
        
        print()
    
    # Resumen
    print_header("RESUMEN")
    print(f"  Emails procesados: {len(emails)}")
    print(f"  Total adjuntos: {total_attachments}")
    print(f"  Posibles facturas: {invoice_attachments}")
    print()
    print_success("Prueba de conexión completada")
    print()
    print("Próximo paso: Ejecutar con --download para descargar las facturas")

if __name__ == '__main__':
    main()
