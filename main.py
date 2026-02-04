#!/usr/bin/env python3
"""
================================================================================
PH-Bot (Client Bot) v4.0.0
================================================================================
Last Updated: 2026-02-04
Repository: github.com/anacuero-bit/PH-Bot

CHANGELOG:
----------
v4.0.0 (2026-02-04)
  - Complete redesign with Latino-friendly warm welcome
  - Country selection with flags FIRST (personalizes experience)
  - Progressive payment: €9.99 → €89.01 → €199 → €38.28
  - FAQ carousel before payment commitment
  - /reset command for testing (clears user data)
  - Conversation flows from 01-BOT-FLOWS.md
  - Brand voice from BRAND-VOICE-CONVERSATION-GUIDE.md

v3.0.0 (2026-02-03)
  - NLU for random messages
  - 50+ FAQ topics
  - Stripe payments
  - Antecedentes penales service

v2.0.0 (2026-02-02)
  - Button-based interface
  - Document scanning
  - Fixed TELEGRAM_BOT_TOKEN env var

v1.0.0 (2026-02-01)
  - Basic eligibility quiz
  - Simple document collection

ENVIRONMENT VARIABLES:
----------------------
- TELEGRAM_BOT_TOKEN (required)
- ADMIN_CHAT_IDS (comma-separated Telegram user IDs)
- STRIPE_SECRET_KEY (optional)
- SUPPORT_PHONE (optional, default: +34 600 000 000)
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

DEADLINE = datetime(2026, 6, 30, 23, 59, 59)
DB_PATH = "tuspapeles.db"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =============================================================================
# PRICING STRUCTURE (Progressive)
# =============================================================================

PRICING = {
    "reservation": 9.99,       # Initial commitment (unlock full access)
    "evaluation": 89.01,       # After docs uploaded (completes €99)
    "processing": 199.00,      # When docs verified
    "government": 38.28,       # Before submission
    "total": 336.28,
}

# =============================================================================
# CONVERSATION STATES
# =============================================================================

(
    STATE_START,
    STATE_COUNTRY,
    STATE_ELIGIBILITY_INTRO,
    STATE_ELIGIBILITY_DATE,
    STATE_ELIGIBILITY_TIME,
    STATE_ELIGIBILITY_RECORD,
    STATE_ELIGIBLE_RESULT,
    STATE_NOT_ELIGIBLE,
    STATE_SERVICE_EXPLAIN,
    STATE_FAQ_CAROUSEL,
    STATE_PAYMENT_INTRO,
    STATE_AWAITING_PAYMENT,
    STATE_COLLECT_NAME,
    STATE_COLLECT_PHONE,
    STATE_MAIN_MENU,
    STATE_DOCUMENTS,
    STATE_UPLOAD_DOC,
    STATE_FAQ,
    STATE_CONTACT,
) = range(19)

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
    "ma": {"name": "Marruecos", "flag": "🇲🇦", "greeting": "¡Hola!", "demonym": "marroquí"},
    "other": {"name": "Otro país", "flag": "🌍", "greeting": "¡Hola!", "demonym": ""},
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
        entry_date TEXT,
        has_antecedentes INTEGER DEFAULT 0,
        eligible INTEGER DEFAULT 0,
        reservation_paid INTEGER DEFAULT 0,
        evaluation_paid INTEGER DEFAULT 0,
        processing_paid INTEGER DEFAULT 0,
        state TEXT DEFAULT 'new',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        case_number TEXT UNIQUE,
        status TEXT DEFAULT 'pending',
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
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    user_id = c.lastrowid
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
    
    # Get user ID
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


def generate_case_number() -> str:
    """Generate unique case number."""
    import random
    return f"PH-2026-{random.randint(1000, 9999)}"


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


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build main menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Mis Documentos", callback_data="menu_docs")],
        [InlineKeyboardButton("📤 Subir Documento", callback_data="menu_upload")],
        [InlineKeyboardButton("💳 Estado de Pagos", callback_data="menu_payments")],
        [InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="menu_faq")],
        [InlineKeyboardButton("📞 Hablar con Alguien", callback_data="menu_contact")],
    ])


# =============================================================================
# MESSAGES (Latino-friendly, warm tone)
# =============================================================================

MSG_WELCOME = """
👋 *¡Hola!*

Antes de nada, déjame presentarme...

Soy el asistente de *tuspapeles2026*, un servicio creado por el despacho de abogados *Pombo & Horowitz* para ayudarte con la regularización extraordinaria.

Sé que probablemente estás un poco nervioso/a o desconfiado/a. Es normal. Hay mucha gente por ahí prometiendo cosas que no cumple.

Por eso quiero ser 100% transparente contigo desde el principio. 🤝

*¿De qué país eres?* 👇
"""

MSG_COUNTRY_SELECTED = """
{greeting} 🎉

¡Qué bueno tener a alguien de {country} por aquí!

Tenemos mucha experiencia con casos de {demonym}s, así que conocemos bien los documentos que vas a necesitar.

Ahora necesito hacerte *3 preguntas rápidas* para verificar si cumples los requisitos. Son solo 3, lo prometo.

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

🔒 Esta información es confidencial y nos ayuda a evaluar tu caso correctamente.
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
⏰ *Quedan {days} días* para preparar todo

¿Qué te gustaría hacer ahora?
"""

MSG_NOT_ELIGIBLE_DATE = """
Gracias por tu honestidad.

Lamentablemente, la regularización extraordinaria de 2026 requiere haber entrado a España *antes del 31 de diciembre de 2025*.

Pero no todo está perdido. Hay otras opciones:
• Arraigo social (después de 3 años)
• Arraigo laboral
• Arraigo familiar
• Otras situaciones especiales

¿Te gustaría que un abogado revise tu caso?
"""

MSG_SERVICE_EXPLAIN = """
📋 *¿Qué hacemos exactamente?*

1️⃣ *Verificamos si cumples los requisitos*
   (✅ Ya lo hicimos - ¡cumples!)

2️⃣ *Te guiamos documento por documento*
   Te decimos exactamente qué necesitas

3️⃣ *Revisamos todo legalmente*
   Un abogado real revisa tu caso

4️⃣ *Presentamos tu solicitud*
   Nos encargamos de todo el papeleo

5️⃣ *Te acompañamos hasta el final*
   Hasta que tengas tu tarjeta en la mano

━━━━━━━━━━━━━━━━━━━━

💰 *Costo total: €336.28*

Pero NO pagas todo ahora. Lo dividimos en etapas:

• €9.99 ahora (reserva tu plaza)
• €89.01 después (completa evaluación)  
• €199 cuando presentamos
• €38.28 tasa del gobierno

¿Tienes preguntas antes de continuar?
"""

MSG_FAQ_INTRO = """
❓ *Preguntas Frecuentes*

Selecciona lo que quieras saber:
"""

FAQ_ITEMS = {
    "docs": ("📄 ¿Qué documentos necesito?", """
📄 *Documentos Necesarios*

*Obligatorios:*
• Pasaporte vigente
• Antecedentes penales (apostillado)
• Empadronamiento o prueba de residencia
• Foto tipo carnet

*Pruebas de estancia (al menos 2):*
• Facturas de luz, agua, internet
• Contrato de alquiler
• Extractos bancarios
• Recibos de Western Union/Ria
• Tarjeta sanitaria

Te ayudamos a conseguir cada uno. 💪
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
    "family": ("👨‍👩‍👧 ¿Y mis hijos menores?", """
👨‍👩‍👧 *Regularización de Menores*

Tus hijos menores pueden regularizarse contigo en la misma solicitud.

*Mejor aún:* Reciben permiso de *5 AÑOS* (no solo 1 año como los adultos).

Documentos adicionales:
• Pasaporte del menor
• Acta de nacimiento (apostillada)
• Certificado de escolarización
"""),
    "antecedentes": ("📜 ¿Cómo consigo los antecedentes?", """
📜 *Certificado de Antecedentes*

Depende de tu país:

🇨🇴 *Colombia:* Online en policia.gov.co (gratis)
🇻🇪 *Venezuela:* Consulado en Madrid (cita previa)
🇵🇪 *Perú:* Online (requiere validar en consulado)
🇪🇨 *Ecuador:* Online en mdi.gob.ec

⚠️ *Importante:* Debe estar APOSTILLADO

Te ayudamos con el proceso completo.
"""),
    "price": ("💰 ¿Por qué esos precios?", """
💰 *Desglose de Precios*

*Nuestro servicio: €298*
• Evaluación completa de tu caso
• Guía paso a paso para documentos
• Revisión legal por abogado
• Presentación de solicitud
• Seguimiento hasta resolución

*Tasa del gobierno: €38.28*
(Obligatoria, la paga todo el mundo)

*Total: €336.28*

Comparado con un abogado tradicional (€500-800), te ahorras bastante. Y dividimos los pagos para que no sea de golpe.
"""),
    "trust": ("🤔 ¿Por qué confiar en ustedes?", """
🤔 *¿Por qué confiar en nosotros?*

*Pombo & Horowitz Abogados*
• Desde 1988 (más de 35 años)
• +12,000 casos de extranjería
• Colegiados ICAM nº 12345 y 12346
• Oficina física: C/ Serrano 45, Madrid

No somos un chiringuito de internet.

Puedes venir a la oficina, llamarnos, verificar nuestra colegiación...

Estamos aquí para ayudarte, de verdad. 🤝
"""),
}

MSG_PAYMENT_INTRO = """
💳 *Reserva tu Plaza*

Para empezar con tu caso, necesitamos una pequeña reserva de *€9.99*.

¿Por qué?
• Filtra a gente que no va en serio
• Nos permite dedicar tiempo a tu caso
• Se descuenta del total (no es extra)

━━━━━━━━━━━━━━━━━━━━

*Formas de pago:*

💳 *Bizum:* {phone}
🏦 *Transferencia:* ES12 1234 5678 9012 3456

Cuando hagas el pago, pulsa el botón de abajo.
"""

MSG_PAYMENT_RECEIVED = """
⏳ *¡Recibido!*

Hemos registrado tu notificación de pago.

Lo verificaremos en las próximas horas y te activaremos el acceso completo.

Te enviaré un mensaje aquí cuando esté confirmado. 

_Mientras tanto, puedes cerrar esta ventana._
"""

MSG_MAIN_MENU = """
👤 Hola, *{name}*

📋 Caso #{case_number}
📊 Estado: {status}

━━━━━━━━━━━━━━━━━━━━
Progreso: {progress_bar} {progress}%
━━━━━━━━━━━━━━━━━━━━

¿Qué necesitas?
"""


# =============================================================================
# HANDLERS
# =============================================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command."""
    user = get_or_create_user(
        update.effective_user.id,
        update.effective_user.first_name or "Usuario"
    )
    
    # Check if returning user with reservation paid
    if user.get("reservation_paid"):
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
    telegram_id = update.effective_user.id
    delete_user(telegram_id)
    
    await update.message.reply_text(
        "✅ *Tu cuenta ha sido reseteada.*\n\n"
        "Escribe /start para empezar de nuevo como usuario nuevo.",
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
        # Not eligible
        await query.edit_message_text(
            MSG_NOT_ELIGIBLE_DATE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Consultar con abogado", callback_data="contact_lawyer")],
                [InlineKeyboardButton("📚 Ver otras opciones", callback_data="other_options")],
                [InlineKeyboardButton("← Volver al inicio", callback_data="restart")],
            ])
        )
        return STATE_NOT_ELIGIBLE
    
    elif data == "date_unsure":
        # Help them figure it out
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
                [InlineKeyboardButton("🤷 No sé qué documentos tengo", callback_data="contact_help")],
            ])
        )
        return STATE_ELIGIBILITY_DATE
    
    # date_yes - Continue to Q2
    context.user_data["q1_passed"] = True
    
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
            "Entiendo. Necesitas acreditar *al menos 5 meses* de estancia continuada.\n\n"
            "Si llegaste en diciembre 2025, ya casi cumples. El plazo abre en abril.\n\n"
            "¿Quieres que te avisemos cuando cumplas los 5 meses?",
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
            "El plazo abre el *1 de abril de 2026*. Si para entonces ya llevas 5 meses, perfecto.\n\n"
            "Mientras tanto, te recomiendo ir preparando los documentos.\n\n"
            "¿Continuamos con la última pregunta?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Continuar", callback_data="time_yes")],
                [InlineKeyboardButton("← Volver al inicio", callback_data="restart")],
            ])
        )
        return STATE_ELIGIBILITY_TIME
    
    # time_yes - Continue to Q3
    context.user_data["q2_passed"] = True
    
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
        await query.edit_message_text(
            "Gracias por compartirlo. Sé que no es fácil hablar de esto.\n\n"
            "Tener antecedentes *NO significa automáticamente* que no puedas regularizarte. "
            "Depende del tipo y la gravedad.\n\n"
            "Para darte información precisa, un abogado debe revisar tu caso.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Sí, quiero una consulta", callback_data="contact_lawyer")],
                [InlineKeyboardButton("❓ ¿Qué antecedentes impiden regularizarse?", callback_data="faq_antecedentes_block")],
                [InlineKeyboardButton("← Necesito pensarlo", callback_data="restart")],
            ])
        )
        return STATE_NOT_ELIGIBLE
    
    elif data == "record_unsure":
        await query.edit_message_text(
            "Si no estás seguro/a, probablemente no tengas.\n\n"
            "Los antecedentes penales son condenas por delitos graves "
            "(robo, violencia, drogas, etc.).\n\n"
            "Multas de tráfico o faltas leves *NO cuentan*.\n\n"
            "¿Tienes alguna condena por delito?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ No, ninguna", callback_data="record_clean")],
                [InlineKeyboardButton("⚠️ Sí, tengo alguna", callback_data="record_yes")],
                [InlineKeyboardButton("📞 Prefiero consultar con abogado", callback_data="contact_lawyer")],
            ])
        )
        return STATE_ELIGIBILITY_RECORD
    
    # record_clean - ELIGIBLE!
    update_user(update.effective_user.id, eligible=1, has_antecedentes=0)
    
    days = days_remaining()
    progress_bar = "█" * 3 + "░" * 7
    
    await query.edit_message_text(
        MSG_ELIGIBLE.format(name=name, days=days),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Ver qué documentos necesito", callback_data="faq_docs")],
            [InlineKeyboardButton("💰 Ver precios del servicio", callback_data="explain_service")],
            [InlineKeyboardButton("✅ Quiero empezar mi caso", callback_data="start_case")],
            [InlineKeyboardButton("❓ Tengo más preguntas", callback_data="faq_menu")],
        ])
    )
    return STATE_ELIGIBLE_RESULT


async def handle_eligible_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle actions from eligible result screen."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "explain_service" or data == "start_case":
        await query.edit_message_text(
            MSG_SERVICE_EXPLAIN,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Tengo preguntas", callback_data="faq_menu")],
                [InlineKeyboardButton("✅ Entendido, quiero empezar", callback_data="show_payment")],
                [InlineKeyboardButton("← Volver", callback_data="back_eligible")],
            ])
        )
        return STATE_SERVICE_EXPLAIN
    
    elif data == "faq_menu":
        return await show_faq_menu(update, context)
    
    elif data.startswith("faq_"):
        return await show_faq_item(update, context, data.replace("faq_", ""))
    
    return STATE_ELIGIBLE_RESULT


async def show_faq_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show FAQ menu."""
    query = update.callback_query
    
    buttons = []
    for key, (title, _) in FAQ_ITEMS.items():
        buttons.append([InlineKeyboardButton(title, callback_data=f"faq_{key}")])
    buttons.append([InlineKeyboardButton("✅ Ya no tengo dudas", callback_data="show_payment")])
    buttons.append([InlineKeyboardButton("← Volver", callback_data="back_eligible")])
    
    await query.edit_message_text(
        MSG_FAQ_INTRO,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return STATE_FAQ_CAROUSEL


async def show_faq_item(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> int:
    """Show specific FAQ item."""
    query = update.callback_query
    
    if key in FAQ_ITEMS:
        title, content = FAQ_ITEMS[key]
        await query.edit_message_text(
            content,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Más preguntas", callback_data="faq_menu")],
                [InlineKeyboardButton("✅ Quiero empezar", callback_data="show_payment")],
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
        key = data.replace("faq_", "")
        return await show_faq_item(update, context, key)
    
    elif data == "show_payment":
        return await show_payment(update, context)
    
    elif data == "back_eligible":
        # Go back to eligible result
        user = get_user(update.effective_user.id)
        name = user.get("first_name", "")
        days = days_remaining()
        
        await query.edit_message_text(
            MSG_ELIGIBLE.format(name=name, days=days),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 Ver qué documentos necesito", callback_data="faq_docs")],
                [InlineKeyboardButton("💰 Ver precios del servicio", callback_data="explain_service")],
                [InlineKeyboardButton("✅ Quiero empezar mi caso", callback_data="start_case")],
                [InlineKeyboardButton("❓ Tengo más preguntas", callback_data="faq_menu")],
            ])
        )
        return STATE_ELIGIBLE_RESULT
    
    return STATE_FAQ_CAROUSEL


async def show_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show payment instructions."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        MSG_PAYMENT_INTRO.format(phone=SUPPORT_PHONE),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Ya pagué", callback_data="payment_done")],
            [InlineKeyboardButton("❓ Tengo dudas sobre el pago", callback_data="payment_help")],
            [InlineKeyboardButton("← Volver", callback_data="faq_menu")],
        ])
    )
    return STATE_AWAITING_PAYMENT


async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment confirmation."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "payment_done":
        # Mark as payment pending verification
        update_user(update.effective_user.id, state="payment_pending")
        
        # Notify admins
        for admin_id in ADMIN_IDS:
            try:
                user = get_user(update.effective_user.id)
                await context.bot.send_message(
                    admin_id,
                    f"🔔 *Nuevo pago pendiente*\n\n"
                    f"Usuario: {user.get('first_name', 'N/A')}\n"
                    f"País: {user.get('country_code', 'N/A')}\n"
                    f"Telegram ID: {update.effective_user.id}\n\n"
                    f"Verificar y aprobar con:\n"
                    f"`/approve {update.effective_user.id}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error notifying admin {admin_id}: {e}")
        
        await query.edit_message_text(
            MSG_PAYMENT_RECEIVED,
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    elif data == "payment_help":
        await query.edit_message_text(
            "💬 *¿Dudas sobre el pago?*\n\n"
            f"Escríbenos por WhatsApp: {SUPPORT_PHONE}\n\n"
            "Te ayudamos con cualquier problema.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver", callback_data="show_payment_back")],
            ])
        )
        return STATE_AWAITING_PAYMENT
    
    elif data == "show_payment_back":
        return await show_payment(update, context)
    
    return STATE_AWAITING_PAYMENT


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show main menu for registered users."""
    user = get_user(update.effective_user.id)
    name = user.get("full_name") or user.get("first_name", "Usuario")
    
    # Get or create case
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT case_number, status, progress FROM cases WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)", (update.effective_user.id,))
    case = c.fetchone()
    
    if not case:
        case_number = generate_case_number()
        c.execute("INSERT INTO cases (user_id, case_number) SELECT id, ? FROM users WHERE telegram_id = ?", (case_number, update.effective_user.id))
        conn.commit()
        case = (case_number, "Recopilando documentos", 10)
    
    conn.close()
    
    case_number, status, progress = case
    progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
    
    msg = MSG_MAIN_MENU.format(
        name=name,
        case_number=case_number,
        status=status,
        progress_bar=progress_bar,
        progress=progress
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_main_menu_keyboard()
        )
    
    return STATE_MAIN_MENU


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu buttons."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "menu_docs":
        await query.edit_message_text(
            "📄 *Estado de Documentos*\n\n"
            "⏳ *Pendientes:*\n"
            "├─ Pasaporte\n"
            "├─ Antecedentes penales\n"
            "├─ Empadronamiento\n"
            "└─ Foto carnet\n\n"
            "Sube un documento para empezar 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Subir documento", callback_data="menu_upload")],
                [InlineKeyboardButton("← Volver al menú", callback_data="back_main")],
            ])
        )
    
    elif data == "menu_upload":
        await query.edit_message_text(
            "📤 *Subir Documento*\n\n"
            "Envíame una foto clara del documento.\n\n"
            "Puedo recibir:\n"
            "• 🪪 Pasaporte\n"
            "• 📜 Antecedentes penales\n"
            "• 📍 Empadronamiento\n"
            "• 📷 Foto carnet\n"
            "• 📄 Otros documentos\n\n"
            "_Envía la foto ahora..._",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver al menú", callback_data="back_main")],
            ])
        )
        return STATE_UPLOAD_DOC
    
    elif data == "menu_payments":
        user = get_user(update.effective_user.id)
        await query.edit_message_text(
            "💳 *Estado de Pagos*\n\n"
            f"✅ Reserva: €9.99 {'✓' if user.get('reservation_paid') else '⏳'}\n"
            f"⏳ Evaluación: €89.01\n"
            f"⏳ Presentación: €199.00\n"
            f"⏳ Tasa gobierno: €38.28\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Total pagado: €{9.99 if user.get('reservation_paid') else 0:.2f}\n"
            f"Pendiente: €{336.28 - (9.99 if user.get('reservation_paid') else 0):.2f}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver al menú", callback_data="back_main")],
            ])
        )
    
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
    
    elif data == "back_main":
        return await show_main_menu(update, context)
    
    return STATE_MAIN_MENU


async def handle_document_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle document photo upload."""
    if update.message.photo:
        photo = update.message.photo[-1]  # Highest resolution
        file_id = photo.file_id
        
        # Save to database
        user = get_user(update.effective_user.id)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO documents (user_id, doc_type, file_id) SELECT id, 'pending_review', ? FROM users WHERE telegram_id = ?",
            (file_id, update.effective_user.id)
        )
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            "✅ *¡Documento recibido!*\n\n"
            "Lo revisaremos en las próximas 24-48 horas y te avisaremos.\n\n"
            "¿Quieres subir otro documento?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Subir otro", callback_data="menu_upload")],
                [InlineKeyboardButton("← Volver al menú", callback_data="back_main")],
            ])
        )
    else:
        await update.message.reply_text(
            "Por favor, envía una *foto* del documento.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    return STATE_MAIN_MENU


async def handle_general_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callbacks that can happen in multiple states."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "restart":
        # Restart from beginning
        await query.message.reply_text(
            MSG_WELCOME,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_country_keyboard()
        )
        return STATE_COUNTRY
    
    elif data == "contact_lawyer" or data == "contact_help":
        await query.edit_message_text(
            f"📞 *Contactar con un Abogado*\n\n"
            f"Llámanos o escríbenos:\n\n"
            f"💬 WhatsApp: {SUPPORT_PHONE}\n"
            f"📞 Teléfono: +34 91 555 0123\n\n"
            f"Un abogado revisará tu caso personalmente.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver al inicio", callback_data="restart")],
            ])
        )
        return STATE_CONTACT
    
    return ConversationHandler.END


# =============================================================================
# ADMIN COMMANDS
# =============================================================================

async def cmd_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Approve user payment."""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Uso: /approve <telegram_id>")
        return
    
    try:
        target_id = int(context.args[0])
        update_user(target_id, reservation_paid=1, state="active")
        
        # Notify user
        await context.bot.send_message(
            target_id,
            "✅ *¡Pago confirmado!*\n\n"
            "Ya tienes acceso completo a tu caso.\n\n"
            "Escribe /menu para continuar.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        await update.message.reply_text(f"✅ Usuario {target_id} aprobado.")
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
    
    c.execute("SELECT COUNT(*) FROM users WHERE reservation_paid = 1")
    paid = c.fetchone()[0]
    
    conn.close()
    
    await update.message.reply_text(
        f"📊 *Estadísticas*\n\n"
        f"👥 Total usuarios: {total}\n"
        f"✅ Elegibles: {eligible}\n"
        f"💳 Pagaron reserva: {paid}\n"
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
                CallbackQueryHandler(handle_eligibility_date, pattern="^date_"),
                CallbackQueryHandler(handle_general_callback),
            ],
            STATE_ELIGIBILITY_TIME: [
                CallbackQueryHandler(handle_eligibility_time, pattern="^time_"),
                CallbackQueryHandler(handle_general_callback),
            ],
            STATE_ELIGIBILITY_RECORD: [
                CallbackQueryHandler(handle_eligibility_record, pattern="^record_"),
                CallbackQueryHandler(handle_general_callback),
            ],
            STATE_ELIGIBLE_RESULT: [
                CallbackQueryHandler(handle_eligible_actions),
            ],
            STATE_NOT_ELIGIBLE: [
                CallbackQueryHandler(handle_general_callback),
            ],
            STATE_SERVICE_EXPLAIN: [
                CallbackQueryHandler(handle_faq),
            ],
            STATE_FAQ_CAROUSEL: [
                CallbackQueryHandler(handle_faq),
            ],
            STATE_AWAITING_PAYMENT: [
                CallbackQueryHandler(handle_payment),
            ],
            STATE_MAIN_MENU: [
                CallbackQueryHandler(handle_main_menu),
            ],
            STATE_UPLOAD_DOC: [
                MessageHandler(filters.PHOTO, handle_document_upload),
                CallbackQueryHandler(handle_main_menu),
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
    
    # Admin commands (outside conversation)
    application.add_handler(CommandHandler("reset", cmd_reset))
    application.add_handler(CommandHandler("approve", cmd_approve))
    application.add_handler(CommandHandler("stats", cmd_stats))
    
    logger.info("🚀 PH-Bot v4.0.0 starting...")
    logger.info(f"📅 Days until deadline: {days_remaining()}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
