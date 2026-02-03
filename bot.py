#!/usr/bin/env python3
"""
tuspapeles2026 Enhanced Client Bot
==================================
Full-featured Telegram/WhatsApp bot with:
- Rich button interfaces
- Document scanning via photos
- Daily personalized messages
- Case status tracking
- Payment integration
- Searchable database
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from io import BytesIO

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InputMediaPhoto
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    JobQueue
)
from telegram.constants import ParseMode

# For OCR
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR not available. Install: pip install pytesseract pillow")

# For face comparison (optional)
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

# Database (using SQLite for simplicity, upgrade to PostgreSQL for production)
import sqlite3

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_CHAT_IDS = [int(x) for x in os.environ.get("ADMIN_CHAT_IDS", "").split(",") if x]

# Deadline
DEADLINE = datetime(2026, 6, 30, 23, 59, 59)

# Pricing
PRICING = {
    "evaluation": 99.00,
    "processing": 199.00,
    "government": 38.28,
    "total": 336.28
}

# Conversation states
(
    ONBOARDING_NAME,
    ONBOARDING_NATIONALITY,
    ONBOARDING_PHONE,
    ONBOARDING_ENTRY_DATE,
    ONBOARDING_SELFIE,
    ONBOARDING_PASSPORT,
    AWAITING_DOCUMENT,
    CONFIRMING_DOCUMENT,
) = range(8)

# =============================================================================
# DATABASE
# =============================================================================

def init_database():
    """Initialize SQLite database with all required tables."""
    conn = sqlite3.connect('tuspapeles.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            phone TEXT,
            first_name TEXT,
            last_name TEXT,
            nationality TEXT,
            passport_number TEXT,
            date_of_birth TEXT,
            entry_date TEXT,
            selfie_verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT,
            language TEXT DEFAULT 'es'
        )
    ''')
    
    # Cases table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE,
            user_id INTEGER REFERENCES users(id),
            status TEXT DEFAULT 'new',
            eligibility_score INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            submitted_at TEXT,
            resolved_at TEXT
        )
    ''')
    
    # Documents table
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER REFERENCES cases(id),
            user_id INTEGER REFERENCES users(id),
            document_type TEXT,
            file_id TEXT,
            extracted_data TEXT,
            status TEXT DEFAULT 'pending',
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            verified_at TEXT,
            notes TEXT
        )
    ''')
    
    # Payments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            case_id INTEGER REFERENCES cases(id),
            amount REAL,
            payment_type TEXT,
            status TEXT DEFAULT 'pending',
            transaction_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_at TEXT
        )
    ''')
    
    # Messages table (for analytics)
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            direction TEXT,
            content TEXT,
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

def get_db():
    """Get database connection."""
    return sqlite3.connect('tuspapeles.db')

# =============================================================================
# DOCUMENT TYPES & CLASSIFICATION
# =============================================================================

DOCUMENT_TYPES = {
    "passport": {
        "name": "Pasaporte",
        "icon": "🪪",
        "keywords": ["PASSPORT", "PASAPORTE", "REPÚBLICA", "REPUBLICA"],
        "required": True,
        "validity_months": None,  # Must be valid
        "needs_apostille": False
    },
    "empadronamiento": {
        "name": "Empadronamiento",
        "icon": "📍",
        "keywords": ["PADRÓN", "PADRON", "EMPADRONAMIENTO", "AYUNTAMIENTO", "CERTIFICADO DE INSCRIPCIÓN"],
        "required": True,
        "validity_months": 3,
        "needs_apostille": False
    },
    "antecedentes": {
        "name": "Antecedentes Penales",
        "icon": "📜",
        "keywords": ["ANTECEDENTES", "PENALES", "POLICÍA", "POLICIA", "CRIMINAL", "CONDUCTA"],
        "required": True,
        "validity_months": 3,
        "needs_apostille": True
    },
    "factura_luz": {
        "name": "Factura de Luz",
        "icon": "💡",
        "keywords": ["ENDESA", "IBERDROLA", "NATURGY", "FACTURA", "kWh", "ELECTRICIDAD"],
        "required": False,
        "validity_months": 6,
        "needs_apostille": False
    },
    "factura_agua": {
        "name": "Factura de Agua",
        "icon": "💧",
        "keywords": ["AGUA", "CANAL", "ABASTECIMIENTO", "M³"],
        "required": False,
        "validity_months": 6,
        "needs_apostille": False
    },
    "contrato_alquiler": {
        "name": "Contrato de Alquiler",
        "icon": "🏠",
        "keywords": ["ARRENDAMIENTO", "ALQUILER", "ARRENDADOR", "ARRENDATARIO", "INQUILINO"],
        "required": False,
        "validity_months": None,
        "needs_apostille": False
    },
    "extracto_bancario": {
        "name": "Extracto Bancario",
        "icon": "🏦",
        "keywords": ["EXTRACTO", "BANCO", "CUENTA", "MOVIMIENTOS", "SANTANDER", "BBVA", "CAIXABANK"],
        "required": False,
        "validity_months": 3,
        "needs_apostille": False
    },
    "tarjeta_sanitaria": {
        "name": "Tarjeta Sanitaria",
        "icon": "🏥",
        "keywords": ["TARJETA SANITARIA", "SALUD", "SIP", "CIP", "SEGURIDAD SOCIAL"],
        "required": False,
        "validity_months": None,
        "needs_apostille": False
    },
    "western_union": {
        "name": "Recibo Western Union/Ria",
        "icon": "💸",
        "keywords": ["WESTERN UNION", "RIA", "REMESA", "TRANSFERENCIA", "ENVÍO DE DINERO"],
        "required": False,
        "validity_months": 12,
        "needs_apostille": False
    },
    "partida_nacimiento": {
        "name": "Partida de Nacimiento",
        "icon": "👶",
        "keywords": ["NACIMIENTO", "PARTIDA", "ACTA", "BIRTH"],
        "required": False,  # Required for minors
        "validity_months": None,
        "needs_apostille": True
    },
    "foto_carnet": {
        "name": "Foto Carnet",
        "icon": "📷",
        "keywords": [],  # Detected by image analysis
        "required": True,
        "validity_months": None,
        "needs_apostille": False
    },
    "otro": {
        "name": "Otro Documento",
        "icon": "📄",
        "keywords": [],
        "required": False,
        "validity_months": None,
        "needs_apostille": False
    }
}

NATIONALITIES = {
    "CO": {"name": "Colombia", "flag": "🇨🇴"},
    "PE": {"name": "Perú", "flag": "🇵🇪"},
    "VE": {"name": "Venezuela", "flag": "🇻🇪"},
    "EC": {"name": "Ecuador", "flag": "🇪🇨"},
    "HN": {"name": "Honduras", "flag": "🇭🇳"},
    "BO": {"name": "Bolivia", "flag": "🇧🇴"},
    "AR": {"name": "Argentina", "flag": "🇦🇷"},
    "MX": {"name": "México", "flag": "🇲🇽"},
    "DO": {"name": "Rep. Dominicana", "flag": "🇩🇴"},
    "GT": {"name": "Guatemala", "flag": "🇬🇹"},
    "SV": {"name": "El Salvador", "flag": "🇸🇻"},
    "NI": {"name": "Nicaragua", "flag": "🇳🇮"},
    "PY": {"name": "Paraguay", "flag": "🇵🇾"},
    "CL": {"name": "Chile", "flag": "🇨🇱"},
    "BR": {"name": "Brasil", "flag": "🇧🇷"},
    "MA": {"name": "Marruecos", "flag": "🇲🇦"},
    "SN": {"name": "Senegal", "flag": "🇸🇳"},
    "PK": {"name": "Pakistán", "flag": "🇵🇰"},
    "CN": {"name": "China", "flag": "🇨🇳"},
    "XX": {"name": "Otro", "flag": "🌍"},
}

# =============================================================================
# KEYBOARD BUILDERS
# =============================================================================

def build_main_menu() -> InlineKeyboardMarkup:
    """Build the main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("📊 Mi Caso", callback_data="status")],
        [
            InlineKeyboardButton("📄 Subir Documento", callback_data="upload"),
            InlineKeyboardButton("📋 Mis Documentos", callback_data="documents")
        ],
        [
            InlineKeyboardButton("💳 Pagos", callback_data="payments"),
            InlineKeyboardButton("❓ Preguntas", callback_data="faq")
        ],
        [InlineKeyboardButton("📞 Hablar con Abogado", callback_data="human")],
        [InlineKeyboardButton("🔔 Notificaciones", callback_data="notifications")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_document_selection() -> InlineKeyboardMarkup:
    """Build document type selection keyboard."""
    keyboard = []
    for doc_type, config in DOCUMENT_TYPES.items():
        if doc_type != "otro":  # Add "otro" at the end
            keyboard.append([
                InlineKeyboardButton(
                    f"{config['icon']} {config['name']}", 
                    callback_data=f"doc_{doc_type}"
                )
            ])
    keyboard.append([InlineKeyboardButton("📄 Otro Documento", callback_data="doc_otro")])
    keyboard.append([InlineKeyboardButton("« Volver", callback_data="main")])
    return InlineKeyboardMarkup(keyboard)

def build_nationality_keyboard() -> InlineKeyboardMarkup:
    """Build nationality selection keyboard."""
    keyboard = []
    row = []
    for code, info in NATIONALITIES.items():
        row.append(InlineKeyboardButton(
            f"{info['flag']} {info['name'][:8]}", 
            callback_data=f"nat_{code}"
        ))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def build_yes_no_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Build a yes/no confirmation keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí", callback_data=f"{prefix}_yes"),
            InlineKeyboardButton("❌ No", callback_data=f"{prefix}_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_confirm_document_keyboard(doc_type: str) -> InlineKeyboardMarkup:
    """Build document confirmation keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí, guardar", callback_data=f"confirm_doc_{doc_type}"),
            InlineKeyboardButton("❌ Volver a tomar", callback_data="upload")
        ],
        [InlineKeyboardButton("🏠 Menú Principal", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_quick_actions_keyboard() -> InlineKeyboardMarkup:
    """Build quick actions after document upload."""
    keyboard = [
        [InlineKeyboardButton("📤 Subir Otro", callback_data="upload")],
        [InlineKeyboardButton("📊 Ver Progreso", callback_data="status")],
        [InlineKeyboardButton("🏠 Menú Principal", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_payment_keyboard() -> InlineKeyboardMarkup:
    """Build payment options keyboard."""
    keyboard = [
        [InlineKeyboardButton("💳 Pagar Evaluación (€99)", callback_data="pay_evaluation")],
        [InlineKeyboardButton("💳 Pagar Gestión (€199)", callback_data="pay_processing")],
        [InlineKeyboardButton("📋 Ver Historial", callback_data="payment_history")],
        [InlineKeyboardButton("« Volver", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_faq_keyboard() -> InlineKeyboardMarkup:
    """Build FAQ categories keyboard."""
    keyboard = [
        [InlineKeyboardButton("📝 Requisitos", callback_data="faq_requisitos")],
        [InlineKeyboardButton("📄 Documentos", callback_data="faq_documentos")],
        [InlineKeyboardButton("📜 Apostilla", callback_data="faq_apostilla")],
        [InlineKeyboardButton("💼 Trabajo", callback_data="faq_trabajo")],
        [InlineKeyboardButton("👨‍👩‍👧 Familia/Menores", callback_data="faq_familia")],
        [InlineKeyboardButton("⏰ Plazos", callback_data="faq_plazos")],
        [InlineKeyboardButton("« Volver", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# =============================================================================
# DOCUMENT PROCESSING
# =============================================================================

def classify_document(text: str) -> str:
    """Classify document type based on OCR text."""
    text_upper = text.upper()
    
    for doc_type, config in DOCUMENT_TYPES.items():
        if config["keywords"]:
            for keyword in config["keywords"]:
                if keyword in text_upper:
                    return doc_type
    
    return "otro"

async def process_document_image(photo_file, user_id: int) -> Dict:
    """Process uploaded document image with OCR."""
    result = {
        "success": False,
        "document_type": "otro",
        "extracted_text": "",
        "extracted_data": {},
        "confidence": 0
    }
    
    if not OCR_AVAILABLE:
        result["success"] = True
        result["message"] = "OCR no disponible, documento guardado sin procesar"
        return result
    
    try:
        # Download photo
        photo_bytes = await photo_file.download_as_bytearray()
        image = Image.open(BytesIO(photo_bytes))
        
        # Run OCR
        text = pytesseract.image_to_string(image, lang='spa+eng')
        result["extracted_text"] = text
        
        # Classify document
        doc_type = classify_document(text)
        result["document_type"] = doc_type
        result["success"] = True
        
        # Extract specific data based on document type
        if doc_type == "passport":
            result["extracted_data"] = extract_passport_data(text)
        elif doc_type == "empadronamiento":
            result["extracted_data"] = extract_empadronamiento_data(text)
        elif doc_type == "antecedentes":
            result["extracted_data"] = extract_antecedentes_data(text)
        
        result["confidence"] = 85 if doc_type != "otro" else 50
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        result["error"] = str(e)
    
    return result

def extract_passport_data(text: str) -> Dict:
    """Extract data from passport OCR text."""
    import re
    data = {}
    
    # Try to find passport number (alphanumeric, usually 8-9 chars)
    passport_match = re.search(r'\b[A-Z]{1,2}\d{6,8}\b', text)
    if passport_match:
        data["passport_number"] = passport_match.group()
    
    # Try to find dates (DD/MM/YYYY or DD-MM-YYYY)
    dates = re.findall(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
    if len(dates) >= 2:
        data["birth_date"] = dates[0]
        data["expiry_date"] = dates[-1]
    
    return data

def extract_empadronamiento_data(text: str) -> Dict:
    """Extract data from empadronamiento OCR text."""
    data = {}
    # Add specific extraction logic
    return data

def extract_antecedentes_data(text: str) -> Dict:
    """Extract data from criminal record OCR text."""
    data = {}
    text_upper = text.upper()
    
    # Check if it says "no records"
    if "NO CONSTA" in text_upper or "SIN ANTECEDENTES" in text_upper or "NEGATIVO" in text_upper:
        data["result"] = "clean"
    elif "CONSTA" in text_upper:
        data["result"] = "has_records"
    
    return data

# =============================================================================
# USER & CASE MANAGEMENT
# =============================================================================

def get_or_create_user(telegram_id: int) -> Dict:
    """Get user from database or create new one."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    
    if row:
        columns = [desc[0] for desc in c.description]
        user = dict(zip(columns, row))
    else:
        # Create new user
        c.execute(
            "INSERT INTO users (telegram_id) VALUES (?)",
            (telegram_id,)
        )
        conn.commit()
        user_id = c.lastrowid
        
        # Create case
        case_number = f"TP2026-{user_id:04d}"
        c.execute(
            "INSERT INTO cases (case_number, user_id) VALUES (?, ?)",
            (case_number, user_id)
        )
        conn.commit()
        
        user = {
            "id": user_id,
            "telegram_id": telegram_id,
            "case_number": case_number
        }
    
    conn.close()
    return user

def update_user(telegram_id: int, **kwargs) -> None:
    """Update user data."""
    conn = get_db()
    c = conn.cursor()
    
    # Build update query dynamically
    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [telegram_id]
    
    c.execute(f"UPDATE users SET {fields} WHERE telegram_id = ?", values)
    conn.commit()
    conn.close()

def get_user_case(telegram_id: int) -> Dict:
    """Get user's case with all documents."""
    conn = get_db()
    c = conn.cursor()
    
    # Get user
    c.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    user_row = c.fetchone()
    if not user_row:
        return None
    user_id = user_row[0]
    
    # Get case
    c.execute("SELECT * FROM cases WHERE user_id = ?", (user_id,))
    case_row = c.fetchone()
    if not case_row:
        return None
    
    columns = [desc[0] for desc in c.description]
    case = dict(zip(columns, case_row))
    
    # Get documents
    c.execute("SELECT * FROM documents WHERE case_id = ?", (case["id"],))
    doc_rows = c.fetchall()
    doc_columns = [desc[0] for desc in c.description]
    case["documents"] = [dict(zip(doc_columns, row)) for row in doc_rows]
    
    # Get payments
    c.execute("SELECT * FROM payments WHERE case_id = ?", (case["id"],))
    pay_rows = c.fetchall()
    pay_columns = [desc[0] for desc in c.description]
    case["payments"] = [dict(zip(pay_columns, row)) for row in pay_rows]
    
    conn.close()
    return case

def save_document(user_id: int, case_id: int, doc_type: str, file_id: str, extracted_data: Dict) -> int:
    """Save document to database."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute(
        """INSERT INTO documents (case_id, user_id, document_type, file_id, extracted_data)
           VALUES (?, ?, ?, ?, ?)""",
        (case_id, user_id, doc_type, file_id, json.dumps(extracted_data))
    )
    conn.commit()
    doc_id = c.lastrowid
    conn.close()
    
    return doc_id

def calculate_progress(case: Dict) -> Dict:
    """Calculate case progress percentage and stats."""
    # Required documents
    required = ["passport", "empadronamiento", "antecedentes", "foto_carnet"]
    optional = ["factura_luz", "factura_agua", "contrato_alquiler", "extracto_bancario"]
    
    uploaded_docs = {d["document_type"] for d in case.get("documents", [])}
    verified_docs = {d["document_type"] for d in case.get("documents", []) if d["status"] == "verified"}
    
    # Calculate progress
    required_uploaded = len(uploaded_docs.intersection(required))
    required_verified = len(verified_docs.intersection(required))
    optional_uploaded = len(uploaded_docs.intersection(optional))
    
    # Progress calculation (required docs are 70%, optional 30%)
    required_progress = (required_uploaded / len(required)) * 70
    optional_progress = min((optional_uploaded / 2), 1) * 30  # Max 2 optional for 30%
    
    total_progress = int(required_progress + optional_progress)
    
    # Determine status
    if case["status"] == "submitted":
        status_text = "📬 Solicitud Presentada"
    elif case["status"] == "admitted":
        status_text = "✅ Admitida a Trámite"
    elif case["status"] == "resolved_positive":
        status_text = "🎉 ¡Aprobada!"
    elif total_progress >= 70:
        status_text = "📋 Lista para Revisión"
    elif total_progress >= 40:
        status_text = "📄 Recopilando Documentos"
    else:
        status_text = "🚀 Comenzando"
    
    return {
        "progress": total_progress,
        "status_text": status_text,
        "required_uploaded": required_uploaded,
        "required_total": len(required),
        "required_verified": required_verified,
        "optional_uploaded": optional_uploaded,
        "uploaded_docs": list(uploaded_docs),
        "missing_required": list(set(required) - uploaded_docs),
        "days_until_deadline": (DEADLINE - datetime.now()).days
    }

# =============================================================================
# MESSAGE FORMATTERS
# =============================================================================

def format_status_message(user: Dict, case: Dict, progress: Dict) -> str:
    """Format case status message."""
    # Progress bar
    filled = int(progress["progress"] / 10)
    bar = "█" * filled + "░" * (10 - filled)
    
    message = f"""
📊 *Estado de tu Caso*
━━━━━━━━━━━━━━━━━━━━━

*Caso:* `{case['case_number']}`
*Estado:* {progress['status_text']}

*Progreso:* {progress['progress']}%
{bar}

*Documentos:*
✅ Subidos: {progress['required_uploaded']}/{progress['required_total']} obligatorios
📄 Verificados: {progress['required_verified']}/{progress['required_total']}
📎 Opcionales: {progress['optional_uploaded']}

"""
    
    # Missing documents
    if progress["missing_required"]:
        message += "*⚠️ Pendiente de subir:*\n"
        for doc_type in progress["missing_required"]:
            config = DOCUMENT_TYPES.get(doc_type, {})
            message += f"• {config.get('icon', '📄')} {config.get('name', doc_type)}\n"
    
    # Deadline
    message += f"\n⏰ *Faltan {progress['days_until_deadline']} días* para el cierre"
    
    return message

def format_documents_list(case: Dict) -> str:
    """Format list of uploaded documents."""
    if not case.get("documents"):
        return "📁 *Mis Documentos*\n\n_No has subido ningún documento todavía._"
    
    message = "📁 *Mis Documentos*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    status_icons = {
        "pending": "⏳",
        "verified": "✅",
        "rejected": "❌",
        "needs_apostille": "📜"
    }
    
    for doc in case["documents"]:
        config = DOCUMENT_TYPES.get(doc["document_type"], {})
        status_icon = status_icons.get(doc["status"], "⏳")
        
        message += f"{config.get('icon', '📄')} *{config.get('name', doc['document_type'])}*\n"
        message += f"   Estado: {status_icon} {doc['status']}\n"
        message += f"   Subido: {doc['uploaded_at'][:10]}\n\n"
    
    return message

def format_welcome_message(user: Dict) -> str:
    """Format welcome message for new users."""
    days = (DEADLINE - datetime.now()).days
    
    return f"""
¡Hola! 👋 Soy el asistente de *tuspapeles2026.es*

Te ayudaré a preparar tu solicitud de regularización extraordinaria.

📅 *Fechas clave:*
• Solicitudes: Abril - 30 Junio 2026
• ⏰ Faltan *{days} días* para el cierre

✅ *Requisitos:*
• Haber entrado a España antes del 31/12/2025
• Acreditar 5 meses de estancia
• Sin antecedentes penales

💰 *Precio transparente:*
• €99 Evaluación inicial
• €199 Gestión completa
• €38.28 Tasa gobierno
• *Total: €336.28*

¿Empezamos? 👇
"""

# =============================================================================
# FAQ RESPONSES
# =============================================================================

FAQ_RESPONSES = {
    "requisitos": """
📝 *Requisitos para la Regularización*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ *Fecha de entrada*
   Haber entrado a España antes del 31/12/2025

2️⃣ *Tiempo de estancia*
   Acreditar al menos 5 meses de permanencia

3️⃣ *Antecedentes penales*
   No tener antecedentes en España ni en tu país de origen

4️⃣ *NO necesitas:*
   ❌ Contrato de trabajo
   ❌ Oferta de empleo
   ❌ Padrón de 3 años

*¿Tienes más preguntas?*
""",
    
    "documentos": """
📄 *Documentos Necesarios*
━━━━━━━━━━━━━━━━━━━━━━━━

*Obligatorios:*
🪪 Pasaporte vigente
📍 Empadronamiento (o alternativa)
📜 Antecedentes penales con apostilla
📷 Foto tipo carnet

*Pruebas de estancia (mínimo 2):*
💡 Facturas de servicios (luz, agua)
🏠 Contrato de alquiler
🏦 Extractos bancarios
💸 Recibos de Western Union/Ria
🏥 Tarjeta sanitaria
📝 Cualquier documento a tu nombre

*¿No tienes empadronamiento?*
Puedes acreditarlo con combinación de otros documentos.
""",

    "apostilla": """
📜 *¿Qué es la Apostilla?*
━━━━━━━━━━━━━━━━━━━━━━━━

La apostilla certifica que un documento oficial de tu país es auténtico para usarse en España.

*¿Qué documentos necesitan apostilla?*
• Certificado de antecedentes penales
• Partida de nacimiento (para menores)
• Acta de matrimonio (si aplica)

*¿Cómo la consigo?*
Debes tramitarla en tu país de origen, en el Ministerio de Relaciones Exteriores o equivalente.

*Países del Convenio de La Haya:*
🇨🇴 Colombia, 🇵🇪 Perú, 🇪🇨 Ecuador, 🇻🇪 Venezuela, 🇭🇳 Honduras, etc.
→ Solo necesitan APOSTILLA

*Países sin convenio:*
🇲🇦 Marruecos, 🇸🇳 Senegal, etc.
→ Necesitan LEGALIZACIÓN consular
""",

    "trabajo": """
💼 *¿Puedo trabajar mientras tramitan?*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*¡SÍ!* 🎉

Desde que tu solicitud es *admitida a trámite* (máximo 15 días), obtienes autorización provisional para trabajar legalmente.

*Importante:*
• Puedes trabajar en cualquier sector
• En toda España
• Mientras esperan la resolución (hasta 3 meses)

*NO necesitas:*
❌ Contrato previo
❌ Oferta de empleo
❌ Permiso de trabajo separado
""",

    "familia": """
👨‍👩‍👧 *Regularización de Menores*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*¡Buenas noticias!*
Tus hijos menores pueden regularizarse contigo en la misma solicitud.

*Ventajas para menores:*
✅ Permiso de *5 años* (no solo 1 año)
✅ Trámite conjunto con los padres
✅ Mismo plazo de resolución

*Documentos adicionales:*
• Pasaporte del menor
• Partida de nacimiento apostillada
• Certificado de escolarización
• Libro de familia (si aplica)
""",

    "plazos": """
⏰ *Plazos Importantes*
━━━━━━━━━━━━━━━━━━━━━

*Presentación de solicitudes:*
📅 Desde: Abril 2026
📅 Hasta: *30 Junio 2026* (CIERRE)

*Una vez presentada:*
• Admisión a trámite: máx. 15 días
• Resolución final: máx. 3 meses

*Importante:*
⚠️ Después del 30/06/2026 NO se aceptan más solicitudes
⚠️ Esta es la 7ª regularización en España
⚠️ La anterior fue en 2005 (¡21 años!)

*No dejes pasar esta oportunidad.*
"""
}

# =============================================================================
# COMMAND HANDLERS
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command."""
    user = update.effective_user
    db_user = get_or_create_user(user.id)
    
    # Check if user is new (no first_name in DB)
    if not db_user.get("first_name"):
        # Start onboarding
        await update.message.reply_text(
            format_welcome_message(db_user),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 ¡Empezar!", callback_data="start_onboarding")],
                [InlineKeyboardButton("❓ Tengo preguntas", callback_data="faq")]
            ])
        )
    else:
        # Existing user - show main menu
        await update.message.reply_text(
            f"¡Hola de nuevo, {db_user['first_name']}! 👋\n\n¿En qué puedo ayudarte hoy?",
            reply_markup=build_main_menu()
        )
    
    return ConversationHandler.END

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show main menu."""
    await update.message.reply_text(
        "📱 *Menú Principal*\n\nElige una opción:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_main_menu()
    )

# =============================================================================
# CALLBACK HANDLERS
# =============================================================================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all callback queries."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = get_or_create_user(query.from_user.id)
    
    # Main menu
    if data == "main":
        await query.edit_message_text(
            "📱 *Menú Principal*\n\nElige una opción:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_main_menu()
        )
    
    # Status
    elif data == "status":
        case = get_user_case(query.from_user.id)
        if case:
            progress = calculate_progress(case)
            await query.edit_message_text(
                format_status_message(user, case, progress),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📄 Subir Documento", callback_data="upload")],
                    [InlineKeyboardButton("🏠 Menú Principal", callback_data="main")]
                ])
            )
        else:
            await query.edit_message_text(
                "No se encontró tu caso. Por favor, inicia con /start",
                reply_markup=build_main_menu()
            )
    
    # Upload document
    elif data == "upload":
        await query.edit_message_text(
            "📤 *Subir Documento*\n\n¿Qué tipo de documento vas a subir?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_document_selection()
        )
    
    # Document type selected
    elif data.startswith("doc_"):
        doc_type = data.replace("doc_", "")
        config = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["otro"])
        
        context.user_data["awaiting_document"] = doc_type
        
        message = f"""
{config['icon']} *{config['name']}*

📸 Por favor, toma una foto clara del documento.

*Consejos:*
• Buena iluminación
• Documento completo visible
• Sin reflejos ni sombras
• Texto legible

_Envía la foto ahora..._
"""
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("« Volver", callback_data="upload")]
            ])
        )
    
    # Documents list
    elif data == "documents":
        case = get_user_case(query.from_user.id)
        await query.edit_message_text(
            format_documents_list(case),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Subir Documento", callback_data="upload")],
                [InlineKeyboardButton("🏠 Menú Principal", callback_data="main")]
            ])
        )
    
    # Payments
    elif data == "payments":
        case = get_user_case(query.from_user.id)
        progress = calculate_progress(case) if case else {"progress": 0}
        
        message = f"""
💳 *Pagos y Facturación*
━━━━━━━━━━━━━━━━━━━━━

*Precio transparente:*
• Evaluación inicial: €99
• Gestión completa: €199
• Tasa del gobierno: €38.28
• *Total: €336.28*

*Tu caso:* Progreso {progress['progress']}%

*Métodos de pago:*
💳 Tarjeta de crédito/débito
📱 Bizum
🏦 Transferencia bancaria
"""
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_payment_keyboard()
        )
    
    # FAQ
    elif data == "faq":
        await query.edit_message_text(
            "❓ *Preguntas Frecuentes*\n\nElige un tema:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_faq_keyboard()
        )
    
    # FAQ topics
    elif data.startswith("faq_"):
        topic = data.replace("faq_", "")
        response = FAQ_RESPONSES.get(topic, "Información no disponible.")
        await query.edit_message_text(
            response,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("« Más preguntas", callback_data="faq")],
                [InlineKeyboardButton("🏠 Menú Principal", callback_data="main")]
            ])
        )
    
    # Human support
    elif data == "human":
        await query.edit_message_text(
            """
📞 *Contactar con un Abogado*
━━━━━━━━━━━━━━━━━━━━━━━━

Nuestro equipo está disponible para ayudarte.

*Opciones:*
📱 WhatsApp: +34 600 000 000
📧 Email: info@tuspapeles2026.es
📍 Oficina: Calle Serrano 45, Madrid

*Horario:*
Lunes a Viernes: 9:00 - 19:00
Sábados: 10:00 - 14:00

_Te responderemos lo antes posible._
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Menú Principal", callback_data="main")]
            ])
        )
    
    # Onboarding start
    elif data == "start_onboarding":
        await query.edit_message_text(
            "¡Genial! 🚀\n\n¿Cuál es tu nombre completo? (Como aparece en tu pasaporte)"
        )
        return ONBOARDING_NAME
    
    # Nationality selection
    elif data.startswith("nat_"):
        code = data.replace("nat_", "")
        nationality = NATIONALITIES.get(code, {})
        context.user_data["nationality"] = code
        
        await query.edit_message_text(
            f"Perfecto, {nationality['flag']} {nationality['name']}!\n\n¿Cuándo entraste a España aproximadamente?\n\n(Formato: DD/MM/AAAA)"
        )
        return ONBOARDING_ENTRY_DATE

# =============================================================================
# MESSAGE HANDLERS
# =============================================================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo uploads (document scanning)."""
    user = update.effective_user
    photo = update.message.photo[-1]  # Get highest resolution
    
    # Check if we're expecting a document
    expected_type = context.user_data.get("awaiting_document")
    
    await update.message.reply_text("🔍 Analizando documento...")
    
    # Download and process
    photo_file = await photo.get_file()
    result = await process_document_image(photo_file, user.id)
    
    # If we have an expected type, use it; otherwise use classified type
    doc_type = expected_type or result.get("document_type", "otro")
    config = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["otro"])
    
    # Store file_id for later saving
    context.user_data["pending_document"] = {
        "file_id": photo.file_id,
        "doc_type": doc_type,
        "extracted_data": result.get("extracted_data", {})
    }
    
    # Build response
    message = f"""
✅ *Documento detectado:* {config['icon']} {config['name']}
"""
    
    if result.get("extracted_data"):
        message += "\n*Datos extraídos:*\n"
        for key, value in result["extracted_data"].items():
            message += f"• {key}: {value}\n"
    
    message += "\n¿Los datos son correctos?"
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_confirm_document_keyboard(doc_type)
    )
    
    # Clear awaiting document
    context.user_data.pop("awaiting_document", None)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle text messages during onboarding."""
    text = update.message.text
    
    # Check conversation state
    # This is a simplified handler - in production, use ConversationHandler properly
    if context.user_data.get("awaiting") == "name":
        # Save name
        parts = text.strip().split()
        first_name = parts[0] if parts else text
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        update_user(update.effective_user.id, first_name=first_name, last_name=last_name)
        
        await update.message.reply_text(
            f"Encantado, {first_name}! 👋\n\n¿De qué país eres?",
            reply_markup=build_nationality_keyboard()
        )
        context.user_data["awaiting"] = None
        return ONBOARDING_NATIONALITY
    
    return ConversationHandler.END

# =============================================================================
# SCHEDULED JOBS (Daily Messages)
# =============================================================================

async def send_daily_updates(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send daily personalized updates to all active users."""
    conn = get_db()
    c = conn.cursor()
    
    # Get all users with Telegram IDs
    c.execute("""
        SELECT u.telegram_id, u.first_name, c.case_number, c.status
        FROM users u
        JOIN cases c ON u.id = c.user_id
        WHERE u.telegram_id IS NOT NULL
    """)
    
    users = c.fetchall()
    conn.close()
    
    days_left = (DEADLINE - datetime.now()).days
    
    for telegram_id, first_name, case_number, status in users:
        try:
            case = get_user_case(telegram_id)
            if not case:
                continue
            
            progress = calculate_progress(case)
            
            # Personalized message based on status
            if progress["progress"] < 30:
                message = f"""
☀️ Buenos días, {first_name}!

Tu caso *{case_number}* está al {progress['progress']}%.

📋 *Siguiente paso:* Sube tu {DOCUMENT_TYPES.get(progress['missing_required'][0] if progress['missing_required'] else 'passport', {}).get('name', 'documento')}

⏰ Faltan *{days_left} días* para el cierre.
"""
            elif progress["progress"] < 70:
                message = f"""
☀️ Buenos días, {first_name}!

¡Vas muy bien! 🎉 Tu progreso: {progress['progress']}%

📋 *Pendiente:* {len(progress['missing_required'])} documentos

💪 ¡Un poco más y estás listo!
"""
            else:
                message = f"""
☀️ Buenos días, {first_name}!

🏆 ¡Tu expediente está casi completo!

Progreso: {progress['progress']}%

Nuestro equipo está revisando tus documentos.
"""
            
            await context.bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=build_main_menu()
            )
            
        except Exception as e:
            logger.error(f"Error sending daily update to {telegram_id}: {e}")

# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """Start the bot."""
    # Initialize database
    init_database()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Schedule daily updates (8 AM)
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(
            send_daily_updates,
            time=datetime.strptime("08:00", "%H:%M").time(),
            name="daily_updates"
        )
    
    # Start polling
    logger.info("🚀 Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
