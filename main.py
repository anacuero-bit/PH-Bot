"""
P&H Regularización - Telegram Bot
Bot de asistencia para el proceso de regularización extraordinaria 2026 en España

Este bot guía a usuarios a través del proceso de evaluación de elegibilidad,
recopilación de documentos y seguimiento de su caso.
"""

import os
import logging
from datetime import datetime, date
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Conversation states
class State(Enum):
    WELCOME = auto()
    ASK_ENTRY_DATE = auto()
    ASK_TIME_IN_SPAIN = auto()
    ASK_CRIMINAL_RECORD = auto()
    ASK_HAS_PADRON = auto()
    ASK_HAS_CHILDREN = auto()
    COLLECT_NAME = auto()
    COLLECT_NATIONALITY = auto()
    COLLECT_PHONE = auto()
    COLLECT_EMAIL = auto()
    SHOW_DOCUMENTS = auto()
    UPLOAD_DOCUMENTS = auto()
    CONFIRM_DATA = auto()
    PAYMENT = auto()
    HUMAN_HANDOFF = auto()
    FAQ = auto()

# User data structure
@dataclass
class UserCase:
    telegram_id: int
    started_at: datetime = field(default_factory=datetime.now)
    
    # Eligibility data
    entry_before_deadline: Optional[bool] = None
    months_in_spain: Optional[int] = None
    has_criminal_record: Optional[bool] = None
    has_padron: Optional[bool] = None
    has_minor_children: Optional[bool] = None
    
    # Personal data
    full_name: Optional[str] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Status
    is_eligible: Optional[bool] = None
    documents_uploaded: list = field(default_factory=list)
    payment_status: str = "pending"
    case_status: str = "intake"
    
    def to_dict(self):
        return {
            'telegram_id': self.telegram_id,
            'started_at': self.started_at.isoformat(),
            'entry_before_deadline': self.entry_before_deadline,
            'months_in_spain': self.months_in_spain,
            'has_criminal_record': self.has_criminal_record,
            'has_padron': self.has_padron,
            'has_minor_children': self.has_minor_children,
            'full_name': self.full_name,
            'nationality': self.nationality,
            'phone': self.phone,
            'email': self.email,
            'is_eligible': self.is_eligible,
            'documents_uploaded': self.documents_uploaded,
            'payment_status': self.payment_status,
            'case_status': self.case_status,
        }

# In-memory storage (replace with database in production)
user_cases: dict[int, UserCase] = {}

# =============================================================================
# MESSAGES IN SPANISH
# =============================================================================

MESSAGES = {
    'welcome': """
🇪🇸 *¡Bienvenido a P&H Regularización!*

Soy tu asistente para el proceso de *regularización extraordinaria 2026*. 

El gobierno español ha aprobado un Real Decreto que permite a extranjeros en situación irregular obtener:
✅ Permiso de residencia de 1 año
✅ Autorización de trabajo en toda España
✅ Posibilidad de regularizar a hijos menores

⏰ *Plazo límite:* 30 de junio de 2026

Voy a hacerte unas preguntas para evaluar si calificas. ¿Empezamos?
""",

    'ask_entry_date': """
📅 *Primera pregunta:*

¿Entraste a España *antes del 31 de diciembre de 2025*?

(No importa cómo entraste ni si tu visa expiró)
""",

    'ask_time_spain': """
🏠 *Segunda pregunta:*

¿Cuántos meses llevas viviendo en España de forma continua?

Escribe el número de meses (ejemplo: 6, 12, 24...)
""",

    'ask_criminal': """
⚖️ *Tercera pregunta:*

¿Tienes antecedentes penales en España o en tu país de origen?

(Sé honesto, esto es importante para tu caso)
""",

    'ask_padron': """
📋 *Sobre el empadronamiento:*

¿Estás empadronado/a en algún municipio de España (tienes padrón)?

El padrón es el documento más importante para demostrar tu estancia.
""",

    'ask_children': """
👨‍👩‍👧‍👦 *Última pregunta:*

¿Tienes hijos menores de edad que viven contigo en España?

(Ellos pueden regularizarse contigo y obtener un permiso de 5 años)
""",

    'eligible_yes': """
🎉 *¡Excelentes noticias!*

Según tus respuestas, *SÍ cumples los requisitos* para la regularización extraordinaria.

*Tu situación:*
• ✅ Entrada antes del 31/12/2025
• ✅ Más de 5 meses en España
• ✅ Sin antecedentes penales
{children_text}

*Siguiente paso:* Vamos a recopilar tus datos y preparar tu expediente.

¿Quieres continuar?
""",

    'eligible_no_entry': """
❌ *Lo sentimos*

Para acceder a este proceso extraordinario, debes haber entrado a España *antes del 31 de diciembre de 2025*.

Si entraste después de esa fecha, hay otras opciones como el arraigo social o laboral, pero requieren más tiempo.

¿Quieres que un abogado revise tu caso?
""",

    'eligible_no_time': """
⚠️ *Atención*

Necesitas demostrar *al menos 5 meses* de estancia en España.

Sin embargo, si entraste antes del 31/12/2025, aún puedes esperar a cumplir los 5 meses antes del cierre del plazo (30 de junio de 2026).

*Consejo:* Empieza a reunir documentos que prueben tu estancia (tickets, recibos, etc.)

¿Quieres que te avisemos cuando cumplas el tiempo?
""",

    'eligible_no_criminal': """
❌ *Lo sentimos*

Las personas con antecedentes penales *no pueden acceder* a este proceso extraordinario de regularización.

Sin embargo, dependiendo del tipo de antecedente y si ya ha pasado tiempo, podría haber opciones.

¿Quieres hablar con un abogado para revisar tu situación específica?
""",

    'collect_name': """
📝 *Datos personales*

Por favor, escribe tu *nombre completo* tal como aparece en tu pasaporte.

(Nombre y apellidos)
""",

    'collect_nationality': """
🌍 *Nacionalidad*

¿Cuál es tu país de origen / nacionalidad?
""",

    'collect_phone': """
📱 *Teléfono de contacto*

Escribe tu número de teléfono en España (con prefijo +34).

Ejemplo: +34 612 345 678
""",

    'collect_email': """
📧 *Correo electrónico*

Escribe tu email para recibir actualizaciones de tu caso.
""",

    'documents_needed': """
📄 *Documentos necesarios*

Para tu expediente, necesitaremos:

*Obligatorios:*
1️⃣ Pasaporte (todas las páginas con sellos)
2️⃣ Certificado de empadronamiento histórico
3️⃣ Certificado de antecedentes penales de tu país
4️⃣ Certificado de antecedentes penales de España

*Para demostrar estancia (al menos 3):*
• Contrato de alquiler
• Recibos de envíos de dinero
• Facturas a tu nombre
• Tickets de transporte
• Historial médico
• Cualquier documento con fecha

{children_docs}

¿Tienes dudas sobre algún documento?
""",

    'children_docs': """
*Para tus hijos menores:*
• Pasaporte del menor
• Partida de nacimiento
• Certificado de empadronamiento del menor
""",

    'confirm_data': """
✅ *Confirma tus datos*

*Nombre:* {name}
*Nacionalidad:* {nationality}
*Teléfono:* {phone}
*Email:* {email}
*Hijos menores:* {children}

¿Los datos son correctos?
""",

    'payment_intro': """
💳 *Reserva tu plaza*

Para asegurar tu lugar y el precio de lanzamiento, realiza el pago inicial de *€99*.

Este pago incluye:
• Evaluación completa de tu caso
• Lista personalizada de documentos
• Acceso prioritario a nuestro equipo

*Métodos de pago:*
""",

    'payment_received': """
✅ *¡Pago recibido!*

Tu reserva está confirmada. Un asesor de P&H Abogados se pondrá en contacto contigo en las próximas 24-48 horas.

*Tu número de caso:* #{case_id}

Mientras tanto, puedes empezar a reunir los documentos que te indicamos.

¿Tienes alguna pregunta?
""",

    'human_handoff': """
👨‍💼 *Conectando con un asesor*

Un miembro de nuestro equipo legal revisará tu caso y te contactará pronto.

*Horario de atención:*
Lunes a Viernes: 9:00 - 19:00
Sábados: 10:00 - 14:00

También puedes escribirnos a:
📧 info@ph-regularizacion.es
📞 +34 XXX XXX XXX
""",

    'faq_menu': """
❓ *Preguntas Frecuentes*

Selecciona un tema:
""",

    'faq_documents': """
📄 *¿Qué documentos necesito?*

*Para demostrar tu estancia puedes usar:*
• Certificado de empadronamiento (padrón)
• Contrato de alquiler
• Recibos de envíos de dinero (Western Union, etc.)
• Tickets de transporte
• Facturas de servicios (luz, agua, internet)
• Historial médico o citas
• Contratos de trabajo (aunque fueran irregulares)
• Cualquier documento oficial con fecha

*Importante:* No necesitas TODOS. Con 3-4 documentos que cubran el período de 5 meses suele ser suficiente.
""",

    'faq_expulsion': """
⚠️ *¿Puedo aplicar con orden de expulsión?*

*¡Sí!* Esta es una de las grandes ventajas del proceso extraordinario.

Si tienes un procedimiento de retorno o una orden de expulsión por razones *administrativas* (no penales), al presentar tu solicitud de regularización, ese procedimiento queda *suspendido automáticamente*.

Esto NO aplica si la expulsión es por motivos penales.
""",

    'faq_timeline': """
⏱️ *¿Cuánto tiempo tarda?*

• *15 días* - Verificación inicial (ya puedes trabajar legalmente)
• *3 meses* - Resolución final y tarjeta física

*Plazo para solicitar:* Hasta el 30 de junio de 2026
*Aplicaciones abren:* Abril 2026
""",

    'faq_children': """
👶 *¿Mis hijos pueden regularizarse?*

*Sí.* Los hijos menores de edad que residen contigo en España pueden regularizarse de forma simultánea.

*Ventaja adicional:* Ellos obtienen un permiso de *5 años*, mucho más favorable que el permiso estándar de 1 año.

Necesitarás: pasaporte del menor, partida de nacimiento, y empadronamiento.
""",

    'faq_work': """
💼 *¿Puedo trabajar durante el proceso?*

*Sí.* Una vez que tu solicitud pasa la verificación inicial (15 días después de presentar), puedes trabajar legalmente.

El permiso te autoriza a trabajar:
• En cualquier sector
• En cualquier parte de España
• Sin restricciones geográficas ni sectoriales
""",

    'error': """
❌ Lo siento, ha ocurrido un error. Por favor, intenta de nuevo o escribe /start para comenzar.
""",

    'help': """
ℹ️ *Comandos disponibles*

/start - Comenzar evaluación
/estado - Ver estado de tu caso  
/documentos - Lista de documentos
/faq - Preguntas frecuentes
/contacto - Hablar con un asesor
/ayuda - Ver este mensaje
"""
}

# =============================================================================
# KEYBOARD BUILDERS
# =============================================================================

def yes_no_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Sí", callback_data="yes"),
            InlineKeyboardButton("❌ No", callback_data="no"),
        ]
    ])

def continue_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Continuar", callback_data="continue")],
        [InlineKeyboardButton("❓ Tengo dudas", callback_data="faq")],
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Correcto", callback_data="confirm"),
            InlineKeyboardButton("✏️ Corregir", callback_data="edit"),
        ]
    ])

def faq_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Documentos necesarios", callback_data="faq_documents")],
        [InlineKeyboardButton("⚠️ Orden de expulsión", callback_data="faq_expulsion")],
        [InlineKeyboardButton("⏱️ Tiempos del proceso", callback_data="faq_timeline")],
        [InlineKeyboardButton("👶 Regularizar hijos", callback_data="faq_children")],
        [InlineKeyboardButton("💼 Trabajar durante proceso", callback_data="faq_work")],
        [InlineKeyboardButton("◀️ Volver", callback_data="back")],
    ])

def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pagar con tarjeta", callback_data="pay_card")],
        [InlineKeyboardButton("🏦 Transferencia bancaria", callback_data="pay_transfer")],
        [InlineKeyboardButton("❓ Tengo dudas", callback_data="human")],
    ])

def contact_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💼 Hablar con asesor", callback_data="human")],
        [InlineKeyboardButton("◀️ Volver al inicio", callback_data="restart")],
    ])

# =============================================================================
# HANDLERS
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask about entry date."""
    user_id = update.effective_user.id
    
    # Create or reset user case
    user_cases[user_id] = UserCase(telegram_id=user_id)
    
    await update.message.reply_text(
        MESSAGES['welcome'],
        parse_mode='Markdown',
        reply_markup=continue_keyboard()
    )
    
    return State.WELCOME.value

async def welcome_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle welcome screen callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "continue":
        await query.edit_message_text(
            MESSAGES['ask_entry_date'],
            parse_mode='Markdown',
            reply_markup=yes_no_keyboard()
        )
        return State.ASK_ENTRY_DATE.value
    elif query.data == "faq":
        await query.edit_message_text(
            MESSAGES['faq_menu'],
            parse_mode='Markdown',
            reply_markup=faq_keyboard()
        )
        return State.FAQ.value

async def entry_date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle entry date response."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    if query.data == "yes":
        user_case.entry_before_deadline = True
        await query.edit_message_text(
            MESSAGES['ask_time_spain'],
            parse_mode='Markdown'
        )
        return State.ASK_TIME_IN_SPAIN.value
    else:
        user_case.entry_before_deadline = False
        user_case.is_eligible = False
        await query.edit_message_text(
            MESSAGES['eligible_no_entry'],
            parse_mode='Markdown',
            reply_markup=contact_keyboard()
        )
        return State.HUMAN_HANDOFF.value

async def time_in_spain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle time in Spain response."""
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    try:
        months = int(update.message.text.strip())
        user_case.months_in_spain = months
        
        if months < 5:
            user_case.is_eligible = False
            await update.message.reply_text(
                MESSAGES['eligible_no_time'],
                parse_mode='Markdown',
                reply_markup=contact_keyboard()
            )
            return State.HUMAN_HANDOFF.value
        else:
            await update.message.reply_text(
                MESSAGES['ask_criminal'],
                parse_mode='Markdown',
                reply_markup=yes_no_keyboard()
            )
            return State.ASK_CRIMINAL_RECORD.value
    except ValueError:
        await update.message.reply_text(
            "Por favor, escribe solo el número de meses. Ejemplo: 6"
        )
        return State.ASK_TIME_IN_SPAIN.value

async def criminal_record_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle criminal record response."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    if query.data == "yes":
        user_case.has_criminal_record = True
        user_case.is_eligible = False
        await query.edit_message_text(
            MESSAGES['eligible_no_criminal'],
            parse_mode='Markdown',
            reply_markup=contact_keyboard()
        )
        return State.HUMAN_HANDOFF.value
    else:
        user_case.has_criminal_record = False
        await query.edit_message_text(
            MESSAGES['ask_padron'],
            parse_mode='Markdown',
            reply_markup=yes_no_keyboard()
        )
        return State.ASK_HAS_PADRON.value

async def padron_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle padron response."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    user_case.has_padron = (query.data == "yes")
    
    await query.edit_message_text(
        MESSAGES['ask_children'],
        parse_mode='Markdown',
        reply_markup=yes_no_keyboard()
    )
    return State.ASK_HAS_CHILDREN.value

async def children_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle children response and show eligibility result."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    user_case.has_minor_children = (query.data == "yes")
    
    # User is eligible if we got here
    user_case.is_eligible = True
    
    children_text = "• ✅ Con hijos menores (permiso de 5 años para ellos)" if user_case.has_minor_children else ""
    
    message = MESSAGES['eligible_yes'].format(children_text=children_text)
    
    await query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=continue_keyboard()
    )
    return State.COLLECT_NAME.value

async def start_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start collecting personal data."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "continue":
        await query.edit_message_text(
            MESSAGES['collect_name'],
            parse_mode='Markdown'
        )
        return State.COLLECT_NAME.value
    elif query.data == "faq":
        await query.edit_message_text(
            MESSAGES['faq_menu'],
            parse_mode='Markdown',
            reply_markup=faq_keyboard()
        )
        return State.FAQ.value

async def collect_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's name."""
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    user_case.full_name = update.message.text.strip()
    
    await update.message.reply_text(
        MESSAGES['collect_nationality'],
        parse_mode='Markdown'
    )
    return State.COLLECT_NATIONALITY.value

async def collect_nationality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's nationality."""
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    user_case.nationality = update.message.text.strip()
    
    await update.message.reply_text(
        MESSAGES['collect_phone'],
        parse_mode='Markdown'
    )
    return State.COLLECT_PHONE.value

async def collect_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's phone."""
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    user_case.phone = update.message.text.strip()
    
    await update.message.reply_text(
        MESSAGES['collect_email'],
        parse_mode='Markdown'
    )
    return State.COLLECT_EMAIL.value

async def collect_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's email and show confirmation."""
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    user_case.email = update.message.text.strip()
    
    children_text = "Sí" if user_case.has_minor_children else "No"
    
    message = MESSAGES['confirm_data'].format(
        name=user_case.full_name,
        nationality=user_case.nationality,
        phone=user_case.phone,
        email=user_case.email,
        children=children_text
    )
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=confirm_keyboard()
    )
    return State.CONFIRM_DATA.value

async def confirm_data_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle data confirmation."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    if query.data == "confirm":
        # Show documents needed
        children_docs = MESSAGES['children_docs'] if user_case.has_minor_children else ""
        message = MESSAGES['documents_needed'].format(children_docs=children_docs)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Continuar al pago", callback_data="to_payment")],
                [InlineKeyboardButton("❓ Dudas sobre documentos", callback_data="faq_documents")],
            ])
        )
        return State.SHOW_DOCUMENTS.value
    else:
        # Restart data collection
        await query.edit_message_text(
            MESSAGES['collect_name'],
            parse_mode='Markdown'
        )
        return State.COLLECT_NAME.value

async def documents_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle documents screen callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "to_payment":
        await query.edit_message_text(
            MESSAGES['payment_intro'],
            parse_mode='Markdown',
            reply_markup=payment_keyboard()
        )
        return State.PAYMENT.value
    elif query.data == "faq_documents":
        await query.edit_message_text(
            MESSAGES['faq_documents'],
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Volver", callback_data="back_to_docs")],
            ])
        )
        return State.SHOW_DOCUMENTS.value

async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle payment callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    if query.data == "pay_card":
        # In production, integrate with Stripe/payment provider
        # For now, simulate payment
        case_id = f"PH{user_id}2026"
        user_case.payment_status = "paid"
        user_case.case_status = "active"
        
        await query.edit_message_text(
            MESSAGES['payment_received'].format(case_id=case_id),
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 Ver documentos", callback_data="show_docs")],
                [InlineKeyboardButton("❓ Preguntas", callback_data="faq")],
            ])
        )
        
        # Log new case (in production, save to database and notify team)
        logger.info(f"New case created: {user_case.to_dict()}")
        
        return ConversationHandler.END
    
    elif query.data == "pay_transfer":
        await query.edit_message_text(
            """🏦 *Transferencia bancaria*

Realiza una transferencia de €99 a:

*Banco:* [Nombre del banco]
*IBAN:* ES00 0000 0000 0000 0000 0000
*Beneficiario:* Pombo & Horowitz Abogados
*Concepto:* REG2026-{telegram_id}

Una vez realizada, envíanos el comprobante y activaremos tu caso en 24h.
""".format(telegram_id=user_id),
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📎 Enviar comprobante", callback_data="upload_receipt")],
                [InlineKeyboardButton("◀️ Volver", callback_data="back_to_payment")],
            ])
        )
        return State.PAYMENT.value
    
    elif query.data == "human":
        await query.edit_message_text(
            MESSAGES['human_handoff'],
            parse_mode='Markdown'
        )
        return ConversationHandler.END

async def faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle FAQ callbacks."""
    query = update.callback_query
    await query.answer()
    
    faq_responses = {
        "faq_documents": MESSAGES['faq_documents'],
        "faq_expulsion": MESSAGES['faq_expulsion'],
        "faq_timeline": MESSAGES['faq_timeline'],
        "faq_children": MESSAGES['faq_children'],
        "faq_work": MESSAGES['faq_work'],
    }
    
    if query.data in faq_responses:
        await query.edit_message_text(
            faq_responses[query.data],
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Más preguntas", callback_data="faq_menu")],
                [InlineKeyboardButton("▶️ Continuar", callback_data="continue")],
            ])
        )
    elif query.data == "faq_menu":
        await query.edit_message_text(
            MESSAGES['faq_menu'],
            parse_mode='Markdown',
            reply_markup=faq_keyboard()
        )
    elif query.data == "back":
        await query.edit_message_text(
            MESSAGES['welcome'],
            parse_mode='Markdown',
            reply_markup=continue_keyboard()
        )
        return State.WELCOME.value
    
    return State.FAQ.value

async def human_handoff_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle human handoff callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "human":
        await query.edit_message_text(
            MESSAGES['human_handoff'],
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    elif query.data == "restart":
        await query.edit_message_text(
            MESSAGES['welcome'],
            parse_mode='Markdown',
            reply_markup=continue_keyboard()
        )
        return State.WELCOME.value

# Command handlers
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    await update.message.reply_text(
        MESSAGES['help'],
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show case status."""
    user_id = update.effective_user.id
    user_case = user_cases.get(user_id)
    
    if user_case and user_case.case_status == "active":
        await update.message.reply_text(
            f"""📋 *Estado de tu caso*

*Número:* #PH{user_id}2026
*Estado:* En proceso
*Pago:* ✅ Recibido

*Próximos pasos:*
1. Un asesor te contactará en 24-48h
2. Revisaremos tu documentación
3. Prepararemos tu expediente

¿Tienes alguna pregunta?
""",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "No tienes un caso activo. Escribe /start para comenzar tu evaluación."
        )

async def documents_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show documents needed."""
    await update.message.reply_text(
        MESSAGES['faq_documents'],
        parse_mode='Markdown'
    )

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show contact info."""
    await update.message.reply_text(
        MESSAGES['human_handoff'],
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "Proceso cancelado. Escribe /start cuando quieras comenzar de nuevo.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            State.WELCOME.value: [
                CallbackQueryHandler(welcome_callback)
            ],
            State.ASK_ENTRY_DATE.value: [
                CallbackQueryHandler(entry_date_callback)
            ],
            State.ASK_TIME_IN_SPAIN.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, time_in_spain)
            ],
            State.ASK_CRIMINAL_RECORD.value: [
                CallbackQueryHandler(criminal_record_callback)
            ],
            State.ASK_HAS_PADRON.value: [
                CallbackQueryHandler(padron_callback)
            ],
            State.ASK_HAS_CHILDREN.value: [
                CallbackQueryHandler(children_callback)
            ],
            State.COLLECT_NAME.value: [
                CallbackQueryHandler(start_data_collection),
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)
            ],
            State.COLLECT_NATIONALITY.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_nationality)
            ],
            State.COLLECT_PHONE.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone)
            ],
            State.COLLECT_EMAIL.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_email)
            ],
            State.CONFIRM_DATA.value: [
                CallbackQueryHandler(confirm_data_callback)
            ],
            State.SHOW_DOCUMENTS.value: [
                CallbackQueryHandler(documents_callback)
            ],
            State.PAYMENT.value: [
                CallbackQueryHandler(payment_callback)
            ],
            State.HUMAN_HANDOFF.value: [
                CallbackQueryHandler(human_handoff_callback)
            ],
            State.FAQ.value: [
                CallbackQueryHandler(faq_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("estado", status_command))
    application.add_handler(CommandHandler("documentos", documents_command))
    application.add_handler(CommandHandler("contacto", contact_command))
    
    # Run the bot
    print("🤖 P&H Regularización Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
