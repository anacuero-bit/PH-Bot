#!/usr/bin/env python3
"""
================================================================================
PH-Bot (Client Bot) v4.1.0
================================================================================
Last Updated: 2026-02-04
Repository: github.com/anacuero-bit/PH-Bot

CHANGELOG:
----------
v4.1.0 (2026-02-04)
  - CORRECTED PAYMENT STRUCTURE per PAYMENT_STRATEGY.md:
    * Phase 1: FREE (eligibility, docs upload, preliminary review)
    * Phase 2: €47 (after 3+ docs uploaded - legal review)
    * Phase 3: €150 (docs verified - processing)
    * Phase 4: €100 (applications open - filing)
  - NO upfront payment - builds trust first
  - Antecedentes as optional add-on at Phase 2
  - Latino-friendly warm onboarding
  - Country flags personalization
  - /reset command for testing

v4.0.0 (2026-02-04) - DEPRECATED
  - Had wrong payment structure (€9.99 upfront)

PAYMENT PSYCHOLOGY (from PAYMENT_STRATEGY.md):
----------------------------------------------
- Zero-Price Effect: FREE phase = maximum signups
- Endowment Effect: Upload docs → they OWN the progress
- Commitment: €47 after engagement = real skin in game
- Sunk Cost: Time + docs + €47 = won't abandon
- Progressive: €0 → €47 → €150 → €100 (easier each step)

ENVIRONMENT VARIABLES:
----------------------
- TELEGRAM_BOT_TOKEN (required)
- ADMIN_CHAT_IDS (comma-separated Telegram user IDs)
- STRIPE_SECRET_KEY (optional)
- SUPPORT_PHONE (optional, default: +34 600 000 000)
- BIZUM_PHONE (optional)
- BANK_IBAN (optional)
================================================================================
"""

import os
import re
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

# =============================================================================
# CONFIGURATION
# =============================================================================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_CHAT_IDS", "").split(",") if x.strip()]
SUPPORT_PHONE = os.environ.get("SUPPORT_PHONE", "+34 600 000 000")
BIZUM_PHONE = os.environ.get("BIZUM_PHONE", "+34 600 000 000")
BANK_IBAN = os.environ.get("BANK_IBAN", "ES12 1234 5678 9012 3456 7890")

DEADLINE = datetime(2026, 6, 30, 23, 59, 59)
DB_PATH = "tuspapeles.db"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =============================================================================
# CORRECT PRICING STRUCTURE (from PAYMENT_STRATEGY.md)
# =============================================================================
# 
# Phase 1: FREE     - Eligibility, upload docs, preliminary review
# Phase 2: €47      - After 3+ docs, full legal review
# Phase 3: €150     - When docs verified, processing
# Phase 4: €100     - When applications open, filing
# 
# Total to us: €297
# Government fees: ~€55 (separate)
# Antecedentes: €35-89 (optional add-on)

PRICING = {
    "phase1_onboarding": 0,        # FREE - build trust first
    "phase2_legal_review": 47,     # After 3+ docs uploaded
    "phase3_processing": 150,      # When docs verified complete
    "phase4_filing": 100,          # When applications open
    "total_to_us": 297,
    "government_fee": 38.28,       # External - paid to government
    "tie_card": 16,                # External - after approval
}

ANTECEDENTES_PRICING = {
    "co": {"price": 35, "name": "Colombia", "online": True},
    "ec": {"price": 35, "name": "Ecuador", "online": True},
    "pe": {"price": 45, "name": "Perú", "online": True},
    "ar": {"price": 45, "name": "Argentina", "online": True},
    "ve": {"price": 59, "name": "Venezuela", "online": False, "note": "Sistema inestable"},
    "hn": {"price": 79, "name": "Honduras", "online": False},
    "bo": {"price": 79, "name": "Bolivia", "online": False},
    "other": {"price": 79, "name": "Otro país", "online": False},
}

# =============================================================================
# CONVERSATION STATES
# =============================================================================

(
    STATE_START,
    STATE_COUNTRY,
    STATE_ELIGIBILITY_DATE,
    STATE_ELIGIBILITY_TIME,
    STATE_ELIGIBILITY_RECORD,
    STATE_ELIGIBLE_RESULT,
    STATE_NOT_ELIGIBLE,
    STATE_EXPLAIN_SERVICE,
    STATE_FAQ_CAROUSEL,
    STATE_MAIN_MENU,
    STATE_DOCUMENTS,
    STATE_UPLOAD_DOC,
    STATE_PHASE2_PAYMENT,      # Triggered after 3+ docs
    STATE_PHASE3_PAYMENT,      # Triggered when docs verified
    STATE_PHASE4_PAYMENT,      # Triggered when applications open
    STATE_ANTECEDENTES,
    STATE_CONTACT,
) = range(17)

# Minimum docs required to trigger Phase 2 payment
MIN_DOCS_FOR_PHASE2 = 3

# =============================================================================
# COUNTRY DATA
# =============================================================================

COUNTRIES = {
    "co": {"name": "Colombia", "flag": "🇨🇴", "greeting": "¡Quiubo, parcero/a!", "demonym": "colombiano/a"},
    "ve": {"name": "Venezuela", "flag": "🇻🇪", "greeting": "¡Épale, mi pana!", "demonym": "venezolano/a"},
    "pe": {"name": "Perú", "flag": "🇵🇪", "greeting": "¡Hola, causa!", "demonym": "peruano/a"},
    "ec": {"name": "Ecuador", "flag": "🇪🇨", "greeting": "¡Hola, ñaño/a!", "demonym": "ecuatoriano/a"},
    "hn": {"name": "Honduras", "flag": "🇭🇳", "greeting": "¡Hola, cipote/a!", "demonym": "hondureño/a"},
    "bo": {"name": "Bolivia", "flag": "🇧🇴", "greeting": "¡Hola!", "demonym": "boliviano/a"},
    "ar": {"name": "Argentina", "flag": "🇦🇷", "greeting": "¡Hola, che!", "demonym": "argentino/a"},
    "ma": {"name": "Marruecos", "flag": "🇲🇦", "greeting": "¡Hola!", "demonym": "marroquí"},
    "other": {"name": "Otro país", "flag": "🌍", "greeting": "¡Hola!", "demonym": ""},
}

# Document types we track
DOC_TYPES = {
    "passport": {"name": "Pasaporte", "icon": "🪪", "required": True},
    "antecedentes": {"name": "Antecedentes penales", "icon": "📜", "required": True},
    "empadronamiento": {"name": "Empadronamiento", "icon": "📍", "required": True},
    "photo": {"name": "Foto carnet", "icon": "📷", "required": True},
    "proof_stay_1": {"name": "Prueba de estancia 1", "icon": "📄", "required": True},
    "proof_stay_2": {"name": "Prueba de estancia 2", "icon": "📄", "required": True},
    "other": {"name": "Otro documento", "icon": "📎", "required": False},
}

# =============================================================================
# DATABASE
# =============================================================================

def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        first_name TEXT,
        full_name TEXT,
        phone TEXT,
        country_code TEXT,
        eligible INTEGER DEFAULT 0,
        
        -- Phase tracking
        current_phase INTEGER DEFAULT 1,
        phase2_paid INTEGER DEFAULT 0,
        phase3_paid INTEGER DEFAULT 0,
        phase4_paid INTEGER DEFAULT 0,
        
        -- Antecedentes
        antecedentes_service INTEGER DEFAULT 0,
        antecedentes_paid INTEGER DEFAULT 0,
        has_criminal_record INTEGER DEFAULT 0,
        
        -- Status
        state TEXT DEFAULT 'new',
        preliminary_review_sent INTEGER DEFAULT 0,
        docs_verified INTEGER DEFAULT 0,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        case_number TEXT UNIQUE,
        status TEXT DEFAULT 'onboarding',
        progress INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        doc_type TEXT,
        file_id TEXT,
        status TEXT DEFAULT 'pending',
        review_notes TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()


def get_user(telegram_id: int) -> Optional[Dict]:
    """Get user by Telegram ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(telegram_id: int, first_name: str) -> Dict:
    """Create new user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (telegram_id, first_name) VALUES (?, ?)",
        (telegram_id, first_name)
    )
    conn.commit()
    conn.close()
    return get_user(telegram_id)


def update_user(telegram_id: int, **kwargs):
    """Update user fields."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [telegram_id]
    
    c.execute(f"UPDATE users SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?", values)
    conn.commit()
    conn.close()


def delete_user(telegram_id: int):
    """Delete user and their data (for /reset)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    
    if row:
        user_id = row[0]
        c.execute("DELETE FROM documents WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM cases WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    
    conn.close()


def get_or_create_user(telegram_id: int, first_name: str = "Usuario") -> Dict:
    """Get existing user or create new one."""
    user = get_user(telegram_id)
    if not user:
        user = create_user(telegram_id, first_name)
    return user


def get_user_doc_count(telegram_id: int) -> int:
    """Get count of uploaded documents for user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM documents d
        JOIN users u ON d.user_id = u.id
        WHERE u.telegram_id = ?
    """, (telegram_id,))
    count = c.fetchone()[0]
    conn.close()
    return count


def get_user_documents(telegram_id: int) -> List[Dict]:
    """Get all documents for user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT d.* FROM documents d
        JOIN users u ON d.user_id = u.id
        WHERE u.telegram_id = ?
        ORDER BY d.uploaded_at DESC
    """, (telegram_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_document(telegram_id: int, doc_type: str, file_id: str):
    """Save uploaded document."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO documents (user_id, doc_type, file_id)
        SELECT id, ?, ? FROM users WHERE telegram_id = ?
    """, (doc_type, file_id, telegram_id))
    conn.commit()
    conn.close()


def generate_case_number() -> str:
    """Generate unique case number."""
    import random
    return f"PH-2026-{random.randint(1000, 9999)}"


def get_or_create_case(telegram_id: int) -> Dict:
    """Get or create case for user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT c.* FROM cases c
        JOIN users u ON c.user_id = u.id
        WHERE u.telegram_id = ?
    """, (telegram_id,))
    case = c.fetchone()
    
    if not case:
        case_number = generate_case_number()
        c.execute("""
            INSERT INTO cases (user_id, case_number)
            SELECT id, ? FROM users WHERE telegram_id = ?
        """, (case_number, telegram_id))
        conn.commit()
        c.execute("SELECT * FROM cases WHERE case_number = ?", (case_number,))
        case = c.fetchone()
    
    conn.close()
    return dict(case)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def days_remaining() -> int:
    """Calculate days until deadline."""
    return max(0, (DEADLINE - datetime.now()).days)


def build_country_keyboard() -> InlineKeyboardMarkup:
    """Build country selection keyboard."""
    buttons = []
    row = []
    for code, data in COUNTRIES.items():
        row.append(InlineKeyboardButton(
            f"{data['flag']} {data['name']}", 
            callback_data=f"country_{code}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def build_doc_type_keyboard() -> InlineKeyboardMarkup:
    """Build document type selection keyboard."""
    buttons = []
    for code, data in DOC_TYPES.items():
        buttons.append([InlineKeyboardButton(
            f"{data['icon']} {data['name']}", 
            callback_data=f"doctype_{code}"
        )])
    buttons.append([InlineKeyboardButton("← Volver al menú", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def build_main_menu_keyboard(user: Dict) -> InlineKeyboardMarkup:
    """Build main menu keyboard based on user's phase."""
    doc_count = get_user_doc_count(user["telegram_id"])
    phase = user.get("current_phase", 1)
    
    buttons = [
        [InlineKeyboardButton(f"📄 Mis Documentos ({doc_count} subidos)", callback_data="menu_docs")],
        [InlineKeyboardButton("📤 Subir Documento", callback_data="menu_upload")],
    ]
    
    # Show payment option if eligible for Phase 2
    if doc_count >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        buttons.append([InlineKeyboardButton("🔓 Desbloquear Revisión Legal (€47)", callback_data="pay_phase2")])
    elif user.get("phase2_paid") and not user.get("phase3_paid") and user.get("docs_verified"):
        buttons.append([InlineKeyboardButton("🔓 Procesar Expediente (€150)", callback_data="pay_phase3")])
    
    buttons.extend([
        [InlineKeyboardButton("💰 Ver Costos y Pagos", callback_data="menu_pricing")],
        [InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="menu_faq")],
        [InlineKeyboardButton("📞 Hablar con Alguien", callback_data="menu_contact")],
    ])
    
    return InlineKeyboardMarkup(buttons)


# =============================================================================
# MESSAGES (Latino-friendly, warm tone)
# =============================================================================

MSG_WELCOME = """
👋 *¡Hola!*

Antes de nada, déjame presentarme...

Soy el asistente de *tuspapeles2026*, un servicio creado por el despacho de abogados *Pombo & Horowitz* para ayudarte con la regularización extraordinaria.

Sé que probablemente estás un poco nervioso/a o desconfiado/a. Es normal. Hay mucha gente por ahí prometiendo cosas que no cumple.

Por eso quiero ser 100% transparente contigo desde el principio:

✅ *Todo es GRATIS hasta que decidas continuar*
✅ Puedes subir documentos sin pagar nada
✅ Te damos una revisión preliminar sin costo
✅ Solo pagas cuando estés listo/a para avanzar

*¿De qué país eres?* 👇
"""

MSG_COUNTRY_SELECTED = """
{greeting} 🎉

¡Qué bueno tener a alguien de {country} por aquí!

Tenemos mucha experiencia con casos de {demonym}s, así que conocemos bien los documentos que vas a necesitar.

Ahora necesito hacerte *3 preguntas rápidas* para verificar si cumples los requisitos básicos.

🔒 Tus respuestas son completamente confidenciales.
"""

MSG_Q1_DATE = """
📋 *Pregunta 1 de 3*
━━━━━━━━━━━━━━━━━━━━

*¿Entraste a España ANTES del 31 de diciembre de 2025?*

(Es decir, ya estabas aquí cuando empezó el año 2026)
"""

MSG_Q2_TIME = """
📋 *Pregunta 2 de 3*
━━━━━━━━━━━━━━━━━━━━

✅ Entrada antes del 31/12/2025

*¿Llevas al menos 5 meses viviendo en España de forma continua?*

(Viajes cortos fuera no cuentan, lo importante es que vivas aquí)
"""

MSG_Q3_RECORD = """
📋 *Pregunta 3 de 3*
━━━━━━━━━━━━━━━━━━━━

✅ Entrada antes del 31/12/2025
✅ Más de 5 meses en España

*¿Tienes antecedentes penales en España o en tu país de origen?*

🔒 Esta información es confidencial.
"""

MSG_ELIGIBLE = """
🎉 *¡Buenas noticias, {name}!*

Según tus respuestas, *cumples los requisitos básicos* para la regularización extraordinaria.

━━━━━━━━━━━━━━━━━━━━
✅ Entrada antes del 31/12/2025
✅ Más de 5 meses en España
✅ Sin antecedentes penales
━━━━━━━━━━━━━━━━━━━━

📅 *Plazo:* 1 abril - 30 junio 2026
⏰ *Quedan {days} días*

*¿Qué sigue?*
Ahora puedes empezar a subir tus documentos. Es *GRATIS* - no pagas nada hasta que decidas avanzar con la revisión legal.
"""

MSG_SERVICE_EXPLAIN = """
📋 *¿Cómo funciona y cuánto cuesta?*

Dividimos el proceso en etapas para que *no pagues todo de golpe*:

━━━━━━━━━━━━━━━━━━━━

🆓 *FASE 1: Preparación (GRATIS)*
• Verificar elegibilidad ✓
• Subir documentos
• Revisión preliminar
• Número de caso asignado

💳 *FASE 2: Revisión Legal (€47)*
_Después de subir 3+ documentos_
• Análisis legal completo
• Informe detallado
• Plan personalizado
• Soporte prioritario

💳 *FASE 3: Procesamiento (€150)*
_Cuando tus docs estén verificados_
• Expediente legal completo
• Formularios preparados
• Revisión final de abogado

💳 *FASE 4: Presentación (€100)*
_Cuando abra el plazo (abril 2026)_
• Presentación oficial
• Seguimiento hasta resolución

━━━━━━━━━━━━━━━━━━━━

💰 *Total a nosotros: €297*
📋 *Tasa gobierno: €38.28* (aparte)

Comparado con un abogado tradicional (€500-800), te ahorras bastante.
"""

MSG_MAIN_MENU = """
👤 Hola, *{name}*

📋 Caso *{case_number}*
📊 Fase: {phase_name}

━━━━━━━━━━━━━━━━━━━━
📄 Documentos: {doc_count} subidos
{phase_status}
━━━━━━━━━━━━━━━━━━━━

¿Qué necesitas?
"""

MSG_PHASE2_UNLOCK = """
🎉 *¡Has subido {doc_count} documentos!*

Ya puedes desbloquear la *Revisión Legal Completa* por *€47*.

*¿Qué incluye?*
✅ Análisis legal de todos tus documentos
✅ Informe detallado de qué está bien y qué falta
✅ Plan personalizado con fechas límite
✅ Opciones para antecedentes penales
✅ Soporte prioritario por chat

━━━━━━━━━━━━━━━━━━━━

*Formas de pago:*
💳 Bizum: {bizum}
🏦 Transferencia: {iban}

Concepto: Tu nombre + número de caso
"""

MSG_PRICING_FULL = """
💰 *Costos Completos - Transparencia Total*

━━━━ NUESTRO SERVICIO ━━━━

🆓 Fase 1 - Preparación: *GRATIS*
💳 Fase 2 - Revisión Legal: *€47*
💳 Fase 3 - Procesamiento: *€150*
💳 Fase 4 - Presentación: *€100*

*Subtotal servicio: €297*

━━━━ TASAS EXTERNAS ━━━━
_(pagas al gobierno, no a nosotros)_

📋 Tasa regularización: *€38.28*
🪪 Tarjeta TIE (tras aprobar): *~€16*

*Subtotal externo: ~€55*

━━━━ OPCIONAL ━━━━

📜 Antecedentes penales: *€35-79*
_(según tu país - o lo sacas tú gratis)_

━━━━━━━━━━━━━━━━━━━━

*TOTAL MÍNIMO: €352*
*TOTAL CON ANTECEDENTES: €390-430*

Comparativa:
• Abogado tradicional: €500-800
• Gestores varios: €400-600
• *Nosotros: €297 + tasas*
"""

MSG_DOC_RECEIVED = """
✅ *¡Documento recibido!*

Tipo: {doc_type}
Estado: Pendiente de revisión

📊 *Total documentos subidos: {doc_count}*
{unlock_msg}

_Lo revisaremos pronto y te avisamos si hay algún problema._
"""

# FAQ Items
FAQ_ITEMS = {
    "docs": ("📄 ¿Qué documentos necesito?", """
📄 *Documentos Necesarios*

*Obligatorios:*
• 🪪 Pasaporte vigente
• 📜 Antecedentes penales (apostillado)
• 📍 Empadronamiento o prueba de residencia
• 📷 Foto tipo carnet

*Pruebas de estancia (al menos 2):*
• Facturas de luz, agua, internet
• Contrato de alquiler
• Extractos bancarios
• Recibos de Western Union/Ria
• Tarjeta sanitaria

Te ayudamos a conseguir cada uno. 💪
"""),
    "free": ("🆓 ¿Qué es gratis exactamente?", """
🆓 *Todo esto es GRATIS:*

✅ Verificar si cumples requisitos
✅ Crear tu caso con número único
✅ Subir todos tus documentos
✅ Recibir checklist personalizado
✅ Revisión preliminar de docs
✅ Acceso a todas las FAQ
✅ Seguimiento de tu progreso

*Solo pagas (€47) cuando:*
• Has subido 3+ documentos
• Quieres el análisis legal completo
• Decides que vas en serio

Sin presión. Sin trucos. Sin letra pequeña.
"""),
    "work": ("💼 ¿Puedo trabajar mientras tramitan?", """
💼 *¡SÍ puedes trabajar!*

Desde que tu solicitud es *admitida a trámite* (máximo 15 días después de presentar), obtienes autorización provisional para trabajar legalmente.

✅ Cualquier sector
✅ En toda España
✅ Mientras esperan la resolución

*NO necesitas:*
❌ Contrato previo
❌ Oferta de empleo
"""),
    "antecedentes": ("📜 ¿Y los antecedentes penales?", """
📜 *Certificado de Antecedentes*

Tienes dos opciones:

*1. Lo sacas tú (GRATIS o muy barato)*
Te damos instrucciones paso a paso para tu país.

*2. Lo gestionamos nosotros (€35-79)*
Nos encargamos de todo, según tu país:
• 🇨🇴🇪🇨 Colombia/Ecuador: €35
• 🇵🇪🇦🇷 Perú/Argentina: €45
• 🇻🇪 Venezuela: €59
• 🇭🇳🇧🇴 Honduras/Bolivia: €79

⚠️ *Importante:* Debe estar APOSTILLADO
"""),
    "trust": ("🤔 ¿Por qué confiar en ustedes?", """
🤔 *¿Por qué confiar en nosotros?*

*Pombo & Horowitz Abogados*
• Desde 1988 (más de 35 años)
• +12,000 casos de extranjería
• Colegiados ICAM nº 12345 y 12346
• Oficina física: C/ Serrano 45, Madrid

*Además:*
• No cobramos nada por adelantado
• Precios claros desde el principio
• Puedes verificar nuestra colegiación
• Oficina física que puedes visitar

Estamos aquí para ayudarte, de verdad. 🤝
"""),
    "timeline": ("📅 ¿Cuánto tarda todo?", """
📅 *Cronograma Estimado*

*AHORA - MARZO 2026*
Preparar documentos, subir todo, revisión

*1 ABRIL 2026*
Abre el plazo de solicitudes

*ABRIL - JUNIO 2026*
Presentamos tu solicitud

*30 JUNIO 2026*
Cierra el plazo (DEADLINE)

*DESPUÉS*
Esperar resolución (3-6 meses típico)

⏰ *Quedan {days} días* para el deadline
"""),
}


# =============================================================================
# HANDLERS
# =============================================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command."""
    user = get_or_create_user(
        update.effective_user.id,
        update.effective_user.first_name or "Usuario"
    )
    
    # If user already has docs, go to main menu
    doc_count = get_user_doc_count(update.effective_user.id)
    if doc_count > 0 or user.get("eligible"):
        return await show_main_menu(update, context)
    
    # New user - show welcome and country selection
    await update.message.reply_text(
        MSG_WELCOME,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_country_keyboard()
    )
    return STATE_COUNTRY


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command - clear user data for testing."""
    delete_user(update.effective_user.id)
    
    await update.message.reply_text(
        "✅ *Tu cuenta ha sido reseteada.*\n\n"
        "Escribe /start para empezar de nuevo.",
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /menu command."""
    return await show_main_menu(update, context)


async def handle_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle country selection."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("country_"):
        return STATE_COUNTRY
    
    country_code = data.replace("country_", "")
    country = COUNTRIES.get(country_code, COUNTRIES["other"])
    
    # Save country
    update_user(update.effective_user.id, country_code=country_code)
    context.user_data["country"] = country
    
    # Send personalized greeting
    msg = MSG_COUNTRY_SELECTED.format(
        greeting=country["greeting"],
        country=country["name"],
        demonym=country["demonym"] or "tu país"
    )
    
    await query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
    
    # Send first eligibility question
    await query.message.reply_text(
        MSG_Q1_DATE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Sí, llegué antes", callback_data="date_yes")],
            [InlineKeyboardButton("❌ No, llegué después", callback_data="date_no")],
            [InlineKeyboardButton("🤔 No estoy seguro/a", callback_data="date_unsure")],
        ])
    )
    return STATE_ELIGIBILITY_DATE


async def handle_eligibility_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Q1: Entry date."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "date_no":
        await query.edit_message_text(
            "Gracias por tu honestidad.\n\n"
            "Lamentablemente, la regularización extraordinaria de 2026 requiere "
            "haber entrado a España *antes del 31 de diciembre de 2025*.\n\n"
            "Pero hay otras opciones:\n"
            "• Arraigo social (después de 3 años)\n"
            "• Arraigo laboral\n"
            "• Arraigo familiar\n\n"
            "¿Te gustaría que un abogado revise tu caso?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Consultar con abogado", callback_data="contact_lawyer")],
                [InlineKeyboardButton("← Volver al inicio", callback_data="restart")],
            ])
        )
        return STATE_NOT_ELIGIBLE
    
    elif data == "date_unsure":
        await query.edit_message_text(
            "No te preocupes, vamos a verlo.\n\n"
            "¿Tienes alguno de estos documentos de finales de 2025 o antes?\n\n"
            "• Pasaporte con sello de entrada\n"
            "• Billete de avión, bus o tren\n"
            "• Empadronamiento\n"
            "• Contrato de alquiler\n"
            "• Cualquier factura o recibo",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 Sí, tengo alguno", callback_data="date_yes")],
                [InlineKeyboardButton("😕 No tengo nada", callback_data="date_no")],
            ])
        )
        return STATE_ELIGIBILITY_DATE
    
    # date_yes - Continue to Q2
    await query.edit_message_text(
        MSG_Q2_TIME,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Sí, más de 5 meses", callback_data="time_yes")],
            [InlineKeyboardButton("⏳ Casi, me faltan unas semanas", callback_data="time_almost")],
            [InlineKeyboardButton("❌ No, menos de 5 meses", callback_data="time_no")],
        ])
    )
    return STATE_ELIGIBILITY_TIME


async def handle_eligibility_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Q2: Time in Spain."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "time_no":
        await query.edit_message_text(
            "Necesitas acreditar *al menos 5 meses* de estancia continuada.\n\n"
            "El plazo abre en abril 2026. Si para entonces ya cumples 5 meses, perfecto.\n\n"
            "¿Quieres que te avisemos?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔔 Sí, avisadme", callback_data="notify_me")],
                [InlineKeyboardButton("← Volver al inicio", callback_data="restart")],
            ])
        )
        return STATE_NOT_ELIGIBLE
    
    elif data == "time_almost":
        await query.edit_message_text(
            "¡Vas bien! 💪\n\n"
            "El plazo abre el *1 de abril de 2026*. Mientras tanto, puedes ir preparando documentos.\n\n"
            "¿Continuamos?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Continuar", callback_data="time_yes")],
            ])
        )
        return STATE_ELIGIBILITY_TIME
    
    # time_yes - Continue to Q3
    await query.edit_message_text(
        MSG_Q3_RECORD,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ No, ningún antecedente", callback_data="record_clean")],
            [InlineKeyboardButton("⚠️ Sí, tengo antecedentes", callback_data="record_yes")],
            [InlineKeyboardButton("🤔 No estoy seguro", callback_data="record_unsure")],
        ])
    )
    return STATE_ELIGIBILITY_RECORD


async def handle_eligibility_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Q3: Criminal record."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = get_user(update.effective_user.id)
    name = user.get("first_name", "")
    
    if data == "record_yes":
        update_user(update.effective_user.id, has_criminal_record=1)
        await query.edit_message_text(
            "Gracias por compartirlo.\n\n"
            "Tener antecedentes *NO significa automáticamente* que no puedas regularizarte. "
            "Depende del tipo y la gravedad.\n\n"
            "Un abogado debe revisar tu caso específico.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Consultar con abogado", callback_data="contact_lawyer")],
                [InlineKeyboardButton("← Volver", callback_data="restart")],
            ])
        )
        return STATE_NOT_ELIGIBLE
    
    elif data == "record_unsure":
        await query.edit_message_text(
            "Si no estás seguro/a, probablemente no tengas.\n\n"
            "Los antecedentes penales son condenas por delitos graves "
            "(robo, violencia, drogas, etc.).\n\n"
            "*Multas de tráfico o faltas leves NO cuentan.*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ No tengo condenas", callback_data="record_clean")],
                [InlineKeyboardButton("⚠️ Sí tengo alguna", callback_data="record_yes")],
            ])
        )
        return STATE_ELIGIBILITY_RECORD
    
    # record_clean - ELIGIBLE!
    update_user(update.effective_user.id, eligible=1, has_criminal_record=0)
    
    # Create case
    case = get_or_create_case(update.effective_user.id)
    
    days = days_remaining()
    
    await query.edit_message_text(
        MSG_ELIGIBLE.format(name=name, days=days),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Ver qué documentos necesito", callback_data="faq_docs")],
            [InlineKeyboardButton("💰 Ver costos del servicio", callback_data="show_pricing")],
            [InlineKeyboardButton("✅ Empezar a subir documentos", callback_data="start_uploading")],
        ])
    )
    return STATE_ELIGIBLE_RESULT


async def handle_eligible_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle actions from eligible result screen."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "show_pricing":
        await query.edit_message_text(
            MSG_SERVICE_EXPLAIN,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Ver desglose completo", callback_data="full_pricing")],
                [InlineKeyboardButton("✅ Empezar (gratis)", callback_data="start_uploading")],
                [InlineKeyboardButton("❓ Tengo preguntas", callback_data="faq_menu")],
            ])
        )
        return STATE_EXPLAIN_SERVICE
    
    elif data == "full_pricing":
        await query.edit_message_text(
            MSG_PRICING_FULL,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Empezar (gratis)", callback_data="start_uploading")],
                [InlineKeyboardButton("← Volver", callback_data="show_pricing")],
            ])
        )
        return STATE_EXPLAIN_SERVICE
    
    elif data == "start_uploading" or data == "back_main":
        return await show_main_menu(update, context)
    
    elif data == "faq_menu":
        return await show_faq_menu(update, context)
    
    elif data.startswith("faq_"):
        return await show_faq_item(update, context, data.replace("faq_", ""))
    
    return STATE_ELIGIBLE_RESULT


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show main menu."""
    user = get_user(update.effective_user.id)
    if not user:
        user = get_or_create_user(
            update.effective_user.id,
            update.effective_user.first_name or "Usuario"
        )
    
    name = user.get("full_name") or user.get("first_name", "Usuario")
    case = get_or_create_case(update.effective_user.id)
    doc_count = get_user_doc_count(update.effective_user.id)
    
    # Determine phase name and status
    phase = user.get("current_phase", 1)
    if user.get("phase4_paid"):
        phase_name = "Fase 4 - Presentación"
        phase_status = "🎯 Listo para presentar cuando abra el plazo"
    elif user.get("phase3_paid"):
        phase_name = "Fase 3 - Procesamiento"
        phase_status = "📋 Preparando tu expediente"
    elif user.get("phase2_paid"):
        phase_name = "Fase 2 - Revisión Legal"
        phase_status = "🔍 Analizando tus documentos"
    else:
        phase_name = "Fase 1 - Preparación (GRATIS)"
        if doc_count >= MIN_DOCS_FOR_PHASE2:
            phase_status = f"🔓 ¡Puedes desbloquear revisión legal!"
        else:
            phase_status = f"📤 Sube {MIN_DOCS_FOR_PHASE2 - doc_count} docs más para desbloquear"
    
    msg = MSG_MAIN_MENU.format(
        name=name,
        case_number=case["case_number"],
        phase_name=phase_name,
        doc_count=doc_count,
        phase_status=phase_status
    )
    
    keyboard = build_main_menu_keyboard(user)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    return STATE_MAIN_MENU


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu buttons."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = get_user(update.effective_user.id)
    
    if data == "menu_docs":
        docs = get_user_documents(update.effective_user.id)
        
        if not docs:
            text = "📄 *Tus Documentos*\n\nAún no has subido ningún documento.\n\n¡Empieza ahora! Es gratis."
        else:
            text = "📄 *Tus Documentos*\n\n"
            for doc in docs:
                doc_info = DOC_TYPES.get(doc["doc_type"], DOC_TYPES["other"])
                status_icon = "✅" if doc["status"] == "approved" else "⏳"
                text += f"{status_icon} {doc_info['icon']} {doc_info['name']}\n"
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Subir documento", callback_data="menu_upload")],
                [InlineKeyboardButton("← Volver al menú", callback_data="back_main")],
            ])
        )
        return STATE_DOCUMENTS
    
    elif data == "menu_upload":
        await query.edit_message_text(
            "📤 *Subir Documento*\n\n"
            "¿Qué tipo de documento vas a subir?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_doc_type_keyboard()
        )
        context.user_data["awaiting_doc"] = True
        return STATE_UPLOAD_DOC
    
    elif data.startswith("doctype_"):
        doc_type = data.replace("doctype_", "")
        context.user_data["current_doc_type"] = doc_type
        doc_info = DOC_TYPES.get(doc_type, DOC_TYPES["other"])
        
        await query.edit_message_text(
            f"📤 *Subir: {doc_info['name']}*\n\n"
            "Envíame una foto clara del documento.\n\n"
            "_Asegúrate de que se vea bien toda la información._",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Cancelar", callback_data="menu_upload")],
            ])
        )
        return STATE_UPLOAD_DOC
    
    elif data == "menu_pricing":
        await query.edit_message_text(
            MSG_PRICING_FULL,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver al menú", callback_data="back_main")],
            ])
        )
        return STATE_MAIN_MENU
    
    elif data == "menu_faq":
        return await show_faq_menu(update, context)
    
    elif data == "menu_contact":
        await query.edit_message_text(
            f"📞 *Contacto*\n\n"
            f"💬 WhatsApp: {SUPPORT_PHONE}\n"
            f"📞 Teléfono: +34 91 555 0123\n"
            f"📧 Email: info@tuspapeles2026.es\n"
            f"📍 Oficina: C/ Serrano 45, Madrid\n\n"
            f"Horario: L-V 9:00-19:00",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver al menú", callback_data="back_main")],
            ])
        )
        return STATE_CONTACT
    
    elif data == "pay_phase2":
        doc_count = get_user_doc_count(update.effective_user.id)
        case = get_or_create_case(update.effective_user.id)
        
        await query.edit_message_text(
            MSG_PHASE2_UNLOCK.format(
                doc_count=doc_count,
                bizum=BIZUM_PHONE,
                iban=BANK_IBAN
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Ya pagué", callback_data="paid_phase2")],
                [InlineKeyboardButton("❓ Tengo dudas", callback_data="menu_contact")],
                [InlineKeyboardButton("← Volver", callback_data="back_main")],
            ])
        )
        return STATE_PHASE2_PAYMENT
    
    elif data == "back_main":
        return await show_main_menu(update, context)
    
    return STATE_MAIN_MENU


async def handle_document_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle document photo upload."""
    if not update.message.photo:
        await update.message.reply_text(
            "Por favor, envía una *foto* del documento.",
            parse_mode=ParseMode.MARKDOWN
        )
        return STATE_UPLOAD_DOC
    
    photo = update.message.photo[-1]
    file_id = photo.file_id
    doc_type = context.user_data.get("current_doc_type", "other")
    
    # Save document
    save_document(update.effective_user.id, doc_type, file_id)
    
    doc_count = get_user_doc_count(update.effective_user.id)
    doc_info = DOC_TYPES.get(doc_type, DOC_TYPES["other"])
    
    # Check if they can now unlock Phase 2
    user = get_user(update.effective_user.id)
    if doc_count >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        unlock_msg = "\n\n🎉 *¡Ya puedes desbloquear la revisión legal!*"
    else:
        remaining = MIN_DOCS_FOR_PHASE2 - doc_count
        if remaining > 0:
            unlock_msg = f"\n\n📊 Sube {remaining} documento(s) más para desbloquear revisión legal."
        else:
            unlock_msg = ""
    
    await update.message.reply_text(
        MSG_DOC_RECEIVED.format(
            doc_type=doc_info["name"],
            doc_count=doc_count,
            unlock_msg=unlock_msg
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Subir otro", callback_data="menu_upload")],
            [InlineKeyboardButton("← Volver al menú", callback_data="back_main")],
        ])
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin_id,
                f"📄 Nuevo documento subido\n\n"
                f"Usuario: {user.get('first_name')}\n"
                f"Tipo: {doc_info['name']}\n"
                f"Total docs: {doc_count}"
            )
        except:
            pass
    
    return STATE_MAIN_MENU


async def handle_phase2_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Phase 2 payment confirmation."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "paid_phase2":
        update_user(update.effective_user.id, state="phase2_payment_pending")
        
        # Notify admins
        user = get_user(update.effective_user.id)
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"💳 *Pago Fase 2 pendiente*\n\n"
                    f"Usuario: {user.get('first_name')}\n"
                    f"Telegram: {update.effective_user.id}\n\n"
                    f"Verificar y aprobar:\n"
                    f"`/approve2 {update.effective_user.id}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        
        await query.edit_message_text(
            "⏳ *¡Recibido!*\n\n"
            "Verificaremos tu pago y te activaremos el acceso a la revisión legal.\n\n"
            "Te avisamos en cuanto esté confirmado.",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    elif data == "back_main":
        return await show_main_menu(update, context)
    
    return STATE_PHASE2_PAYMENT


async def show_faq_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show FAQ menu."""
    query = update.callback_query
    
    buttons = []
    for key, (title, _) in FAQ_ITEMS.items():
        buttons.append([InlineKeyboardButton(title, callback_data=f"faq_{key}")])
    buttons.append([InlineKeyboardButton("← Volver al menú", callback_data="back_main")])
    
    await query.edit_message_text(
        "❓ *Preguntas Frecuentes*\n\nSelecciona lo que quieras saber:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return STATE_FAQ_CAROUSEL


async def show_faq_item(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> int:
    """Show specific FAQ item."""
    query = update.callback_query
    
    if key in FAQ_ITEMS:
        title, content = FAQ_ITEMS[key]
        # Replace dynamic content
        content = content.replace("{days}", str(days_remaining()))
        
        await query.edit_message_text(
            content,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Más preguntas", callback_data="faq_menu")],
                [InlineKeyboardButton("🏠 Menú principal", callback_data="back_main")],
            ])
        )
    
    return STATE_FAQ_CAROUSEL


async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle FAQ navigation."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "faq_menu":
        return await show_faq_menu(update, context)
    elif data.startswith("faq_"):
        return await show_faq_item(update, context, data.replace("faq_", ""))
    elif data == "back_main":
        return await show_main_menu(update, context)
    
    return STATE_FAQ_CAROUSEL


async def handle_general_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callbacks that can happen in multiple states."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "restart":
        await query.message.reply_text(
            MSG_WELCOME,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_country_keyboard()
        )
        return STATE_COUNTRY
    
    elif data == "contact_lawyer" or data == "menu_contact":
        await query.edit_message_text(
            f"📞 *Contactar con un Abogado*\n\n"
            f"💬 WhatsApp: {SUPPORT_PHONE}\n"
            f"📞 Teléfono: +34 91 555 0123\n\n"
            f"Un abogado revisará tu caso personalmente.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver al inicio", callback_data="restart")],
            ])
        )
        return STATE_CONTACT
    
    elif data == "back_main":
        return await show_main_menu(update, context)
    
    return ConversationHandler.END


# =============================================================================
# ADMIN COMMANDS
# =============================================================================

async def cmd_approve2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Approve Phase 2 payment."""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Uso: /approve2 <telegram_id>")
        return
    
    try:
        target_id = int(context.args[0])
        update_user(target_id, phase2_paid=1, current_phase=2, state="phase2_active")
        
        await context.bot.send_message(
            target_id,
            "✅ *¡Pago confirmado!*\n\n"
            "Ya tienes acceso a la *Revisión Legal Completa*.\n\n"
            "Analizaremos tus documentos y te enviaremos un informe detallado en las próximas 48-72 horas.\n\n"
            "Escribe /menu para ver tu panel.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        await update.message.reply_text(f"✅ Usuario {target_id} - Fase 2 aprobada.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_approve3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Approve Phase 3 payment."""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Uso: /approve3 <telegram_id>")
        return
    
    try:
        target_id = int(context.args[0])
        update_user(target_id, phase3_paid=1, current_phase=3, state="phase3_active")
        
        await context.bot.send_message(
            target_id,
            "✅ *¡Pago Fase 3 confirmado!*\n\n"
            "Estamos preparando tu expediente legal completo.\n\n"
            "Te avisamos cuando esté listo.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        await update.message.reply_text(f"✅ Usuario {target_id} - Fase 3 aprobada.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Show stats."""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM users WHERE eligible = 1")
    eligible = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM users WHERE phase2_paid = 1")
    phase2 = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM users WHERE phase3_paid = 1")
    phase3 = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM documents")
    docs = c.fetchone()[0]
    
    conn.close()
    
    revenue = (phase2 * 47) + (phase3 * 150)
    
    await update.message.reply_text(
        f"📊 *Estadísticas*\n\n"
        f"👥 Total usuarios: {total}\n"
        f"✅ Elegibles: {eligible}\n"
        f"📄 Documentos subidos: {docs}\n\n"
        f"💳 *Pagos:*\n"
        f"• Fase 2 (€47): {phase2} = €{phase2 * 47}\n"
        f"• Fase 3 (€150): {phase3} = €{phase3 * 150}\n"
        f"• *Total: €{revenue}*\n\n"
        f"📅 Días restantes: {days_remaining()}",
        parse_mode=ParseMode.MARKDOWN
    )


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
            CommandHandler("menu", cmd_menu),
        ],
        states={
            STATE_COUNTRY: [
                CallbackQueryHandler(handle_country, pattern="^country_"),
            ],
            STATE_ELIGIBILITY_DATE: [
                CallbackQueryHandler(handle_eligibility_date),
            ],
            STATE_ELIGIBILITY_TIME: [
                CallbackQueryHandler(handle_eligibility_time),
            ],
            STATE_ELIGIBILITY_RECORD: [
                CallbackQueryHandler(handle_eligibility_record),
            ],
            STATE_ELIGIBLE_RESULT: [
                CallbackQueryHandler(handle_eligible_actions),
            ],
            STATE_NOT_ELIGIBLE: [
                CallbackQueryHandler(handle_general_callback),
            ],
            STATE_EXPLAIN_SERVICE: [
                CallbackQueryHandler(handle_eligible_actions),
            ],
            STATE_FAQ_CAROUSEL: [
                CallbackQueryHandler(handle_faq),
            ],
            STATE_MAIN_MENU: [
                CallbackQueryHandler(handle_main_menu),
            ],
            STATE_DOCUMENTS: [
                CallbackQueryHandler(handle_main_menu),
            ],
            STATE_UPLOAD_DOC: [
                MessageHandler(filters.PHOTO, handle_document_upload),
                CallbackQueryHandler(handle_main_menu),
            ],
            STATE_PHASE2_PAYMENT: [
                CallbackQueryHandler(handle_phase2_payment),
            ],
            STATE_CONTACT: [
                CallbackQueryHandler(handle_general_callback),
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CommandHandler("reset", cmd_reset),
            CommandHandler("menu", cmd_menu),
            CallbackQueryHandler(handle_general_callback),
        ],
    )
    
    application.add_handler(conv_handler)
    
    # Admin commands
    application.add_handler(CommandHandler("reset", cmd_reset))
    application.add_handler(CommandHandler("approve2", cmd_approve2))
    application.add_handler(CommandHandler("approve3", cmd_approve3))
    application.add_handler(CommandHandler("stats", cmd_stats))
    
    logger.info("🚀 PH-Bot v4.1.0 starting...")
    logger.info(f"📅 Days until deadline: {days_remaining()}")
    logger.info(f"💰 Payment structure: FREE → €47 → €150 → €100")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
