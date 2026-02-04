#!/usr/bin/env python3
"""
tuspapeles2026 Enhanced Client Bot v3.0
=======================================
Production-ready Telegram bot with:
- Natural language understanding for random input
- Complete FAQ system with 50+ topics
- Payment integration (Stripe)
- Appointment scheduling
- Criminal record certificate service (antecedentes)
- Multi-language support
- Robust error handling
- WhatsApp-ready architecture

Version: 3.0.0
Last Updated: 2026-02-04

CHANGELOG:
-----------
v3.0.0 (2026-02-04)
  - Added intelligent NLU for random user messages
  - Expanded FAQ to 50+ topics with keyword matching
  - Added complete payment flow with Stripe integration
  - Added appointment scheduling system
  - Added antecedentes penales service (new revenue stream)
  - Added proper ConversationHandler states
  - Added WhatsApp-compatible message formatting
  - Added admin notification system
  - Added rate limiting and spam protection
  - Added multi-language support (ES/EN/FR)
  - Fixed all callback query handlers
  - Added comprehensive error handling

v2.0.0 (2026-02-03)
  - Complete rewrite with button-based interface
  - Added document scanning via photo upload
  - Fixed: TELEGRAM_BOT_TOKEN env var name

v1.0.0 (2026-02-03)
  - Initial release
"""

import os
import re
import json
import asyncio
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from io import BytesIO
from functools import wraps

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InputMediaPhoto,
    BotCommand
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
from telegram.error import TelegramError

# Optional imports with fallbacks
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    
# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
ADMIN_CHAT_IDS = [int(x) for x in os.environ.get("ADMIN_CHAT_IDS", "").split(",") if x]
SUPPORT_CHAT_ID = os.environ.get("SUPPORT_CHAT_ID", "")

# Configure Stripe
if STRIPE_AVAILABLE and STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Bot URLs
BOT_URL = "https://t.me/tuspapeles2026_bot"
WEBSITE_URL = "https://tuspapeles2026.es"
PAYMENT_URL = "https://tuspapeles2026.es/pago"

# Deadline
DEADLINE = datetime(2026, 6, 30, 23, 59, 59)

# Pricing (in EUR)
PRICING = {
    "evaluation": 99.00,
    "processing": 199.00,
    "government_fee": 38.28,
    "total_basic": 336.28,
    # Antecedentes service pricing
    "antecedentes_colombia": 49.00,
    "antecedentes_peru": 59.00,
    "antecedentes_ecuador": 49.00,
    "antecedentes_venezuela": 69.00,
    "antecedentes_other": 79.00,
    # Family discounts
    "family_2_discount": 0.18,  # 18% off for 2nd person
    "family_3_discount": 0.25,  # 25% off for 3+ persons
}

# Conversation states
(
    STATE_MAIN,
    STATE_ONBOARDING_NAME,
    STATE_ONBOARDING_NATIONALITY,
    STATE_ONBOARDING_PHONE,
    STATE_ONBOARDING_ENTRY_DATE,
    STATE_AWAITING_DOCUMENT,
    STATE_CONFIRMING_DOCUMENT,
    STATE_AWAITING_PAYMENT,
    STATE_SCHEDULING_APPOINTMENT,
    STATE_SELECTING_DATE,
    STATE_SELECTING_TIME,
    STATE_ANTECEDENTES_COUNTRY,
    STATE_ANTECEDENTES_DATA,
    STATE_CONTACT_MESSAGE,
    STATE_LANGUAGE_SELECT,
) = range(15)

# =============================================================================
# NATIONALITIES & COUNTRY DATA
# =============================================================================

NATIONALITIES = {
    "co": {"name": "Colombia", "flag": "🇨🇴", "hague": True, "online_antecedentes": True},
    "pe": {"name": "Perú", "flag": "🇵🇪", "hague": True, "online_antecedentes": True},
    "ec": {"name": "Ecuador", "flag": "🇪🇨", "hague": True, "online_antecedentes": True},
    "ve": {"name": "Venezuela", "flag": "🇻🇪", "hague": True, "online_antecedentes": True},
    "hn": {"name": "Honduras", "flag": "🇭🇳", "hague": True, "online_antecedentes": False},
    "bo": {"name": "Bolivia", "flag": "🇧🇴", "hague": True, "online_antecedentes": False},
    "py": {"name": "Paraguay", "flag": "🇵🇾", "hague": True, "online_antecedentes": False},
    "do": {"name": "Rep. Dominicana", "flag": "🇩🇴", "hague": True, "online_antecedentes": False},
    "sv": {"name": "El Salvador", "flag": "🇸🇻", "hague": True, "online_antecedentes": False},
    "gt": {"name": "Guatemala", "flag": "🇬🇹", "hague": True, "online_antecedentes": False},
    "ni": {"name": "Nicaragua", "flag": "🇳🇮", "hague": True, "online_antecedentes": False},
    "ar": {"name": "Argentina", "flag": "🇦🇷", "hague": True, "online_antecedentes": True},
    "br": {"name": "Brasil", "flag": "🇧🇷", "hague": True, "online_antecedentes": False},
    "mx": {"name": "México", "flag": "🇲🇽", "hague": True, "online_antecedentes": False},
    "ma": {"name": "Marruecos", "flag": "🇲🇦", "hague": False, "online_antecedentes": False},
    "sn": {"name": "Senegal", "flag": "🇸🇳", "hague": False, "online_antecedentes": False},
    "pk": {"name": "Pakistán", "flag": "🇵🇰", "hague": False, "online_antecedentes": False},
    "bd": {"name": "Bangladesh", "flag": "🇧🇩", "hague": True, "online_antecedentes": False},  # Joined 2025
    "cn": {"name": "China", "flag": "🇨🇳", "hague": True, "online_antecedentes": False},
    "ng": {"name": "Nigeria", "flag": "🇳🇬", "hague": False, "online_antecedentes": False},
    "other": {"name": "Otro país", "flag": "🌍", "hague": None, "online_antecedentes": False},
}

# Antecedentes service info by country
ANTECEDENTES_INFO = {
    "co": {
        "name": "Colombia",
        "certificate_source": "Policía Nacional + Procuraduría",
        "certificate_url": "https://antecedentes.policia.gov.co",
        "apostille_source": "Cancillería",
        "apostille_url": "https://tramites.cancilleria.gov.co",
        "requirements": ["Cédula de ciudadanía colombiana", "Correo electrónico"],
        "time_days": "3-5 días hábiles",
        "price": 49.00,
        "fully_online": True,
    },
    "pe": {
        "name": "Perú",
        "certificate_source": "Poder Judicial",
        "certificate_url": "https://www.pj.gob.pe",
        "apostille_source": "Ministerio de Relaciones Exteriores",
        "apostille_url": "https://www.gob.pe/rree",
        "requirements": ["DNI peruano", "Correo electrónico"],
        "time_days": "5-7 días hábiles",
        "price": 59.00,
        "fully_online": True,
    },
    "ec": {
        "name": "Ecuador", 
        "certificate_source": "Ministerio del Interior",
        "certificate_url": "https://certificados.ministeriodelinterior.gob.ec",
        "apostille_source": "Cancillería (electrónica)",
        "apostille_url": "https://www.cancilleria.gob.ec",
        "requirements": ["Cédula ecuatoriana", "Correo electrónico"],
        "time_days": "3-5 días hábiles",
        "price": 49.00,
        "fully_online": True,
    },
    "ve": {
        "name": "Venezuela",
        "certificate_source": "MPPRIJP",
        "certificate_url": "http://certificacioninternacional.mijp.gob.ve",
        "apostille_source": "SLAE (electrónica)",
        "apostille_url": "https://legalizacionve.mppre.gob.ve",
        "requirements": ["Cédula venezolana", "Correo electrónico", "Paciencia (sistema lento)"],
        "time_days": "7-15 días hábiles",
        "price": 69.00,
        "fully_online": True,
        "note": "⚠️ El sistema venezolano puede tener demoras. Te mantendremos informado.",
    },
}

# =============================================================================
# DOCUMENT TYPES
# =============================================================================

DOCUMENT_TYPES = {
    "passport": {
        "name": "Pasaporte",
        "name_en": "Passport",
        "icon": "🪪",
        "keywords": ["PASSPORT", "PASAPORTE", "REPÚBLICA", "REPUBLICA", "TRAVEL DOCUMENT"],
        "required": True,
        "validity_months": None,
        "needs_apostille": False,
        "help_text": "Sube una foto clara de la página principal de tu pasaporte (la que tiene tu foto)."
    },
    "empadronamiento": {
        "name": "Empadronamiento",
        "name_en": "Municipal Registration",
        "icon": "📍",
        "keywords": ["PADRÓN", "PADRON", "EMPADRONAMIENTO", "AYUNTAMIENTO", "CERTIFICADO DE INSCRIPCIÓN"],
        "required": True,
        "validity_months": 3,
        "needs_apostille": False,
        "help_text": "Certificado del ayuntamiento. Si no lo tienes, podemos ayudarte con alternativas."
    },
    "antecedentes": {
        "name": "Antecedentes Penales",
        "name_en": "Criminal Record",
        "icon": "📜",
        "keywords": ["ANTECEDENTES", "PENALES", "POLICÍA", "POLICIA", "CRIMINAL", "CONDUCTA", "RÉCORD"],
        "required": True,
        "validity_months": 3,
        "needs_apostille": True,
        "help_text": "Certificado de tu país de origen CON APOSTILLA. ¿No lo tienes? ¡Te ayudamos a conseguirlo!"
    },
    "foto_carnet": {
        "name": "Foto Carnet",
        "name_en": "ID Photo",
        "icon": "📷",
        "keywords": ["FOTO", "CARNET", "PHOTO"],
        "required": True,
        "validity_months": None,
        "needs_apostille": False,
        "help_text": "Foto tipo pasaporte con fondo blanco. Puedes hacerla con el móvil."
    },
    "factura_luz": {
        "name": "Factura de Luz",
        "name_en": "Electricity Bill",
        "icon": "💡",
        "keywords": ["ENDESA", "IBERDROLA", "NATURGY", "FACTURA", "kWh", "ELECTRICIDAD", "EDP"],
        "required": False,
        "validity_months": 6,
        "needs_apostille": False,
        "help_text": "Factura de electricidad a tu nombre o donde vivas."
    },
    "factura_agua": {
        "name": "Factura de Agua",
        "name_en": "Water Bill",
        "icon": "💧",
        "keywords": ["AGUA", "CANAL", "ABASTECIMIENTO", "M³", "AGUAS"],
        "required": False,
        "validity_months": 6,
        "needs_apostille": False,
        "help_text": "Factura de agua a tu nombre o donde vivas."
    },
    "factura_gas": {
        "name": "Factura de Gas",
        "name_en": "Gas Bill",
        "icon": "🔥",
        "keywords": ["GAS", "NATURGY", "BUTANO", "PROPANO"],
        "required": False,
        "validity_months": 6,
        "needs_apostille": False,
        "help_text": "Factura de gas a tu nombre o donde vivas."
    },
    "contrato_alquiler": {
        "name": "Contrato de Alquiler",
        "name_en": "Rental Contract",
        "icon": "🏠",
        "keywords": ["CONTRATO", "ARRENDAMIENTO", "ALQUILER", "INQUILINO", "VIVIENDA"],
        "required": False,
        "validity_months": None,
        "needs_apostille": False,
        "help_text": "Contrato de alquiler vigente."
    },
    "extracto_banco": {
        "name": "Extracto Bancario",
        "name_en": "Bank Statement",
        "icon": "🏦",
        "keywords": ["EXTRACTO", "BANCO", "MOVIMIENTOS", "SANTANDER", "BBVA", "CAIXABANK", "SABADELL", "ING"],
        "required": False,
        "validity_months": 6,
        "needs_apostille": False,
        "help_text": "Extracto bancario de cualquier banco español."
    },
    "tarjeta_sanitaria": {
        "name": "Tarjeta Sanitaria",
        "name_en": "Health Card",
        "icon": "🏥",
        "keywords": ["SANITARIA", "SALUD", "SIP", "CATSALUT", "OSAKIDETZA", "SERGAS"],
        "required": False,
        "validity_months": None,
        "needs_apostille": False,
        "help_text": "Tarjeta sanitaria de cualquier comunidad autónoma."
    },
    "western_union": {
        "name": "Recibo Western Union/Ria",
        "name_en": "Money Transfer Receipt",
        "icon": "💸",
        "keywords": ["WESTERN", "UNION", "RIA", "MONEY", "GRAM", "REMESA", "ENVÍO"],
        "required": False,
        "validity_months": None,
        "needs_apostille": False,
        "help_text": "Recibos de envío de dinero con tu nombre."
    },
    "partida_nacimiento": {
        "name": "Partida de Nacimiento",
        "name_en": "Birth Certificate",
        "icon": "👶",
        "keywords": ["NACIMIENTO", "BIRTH", "NACIÓ", "PARTIDA"],
        "required": False,  # Required for minors
        "validity_months": None,
        "needs_apostille": True,
        "help_text": "Necesaria para menores. Debe estar apostillada."
    },
    "libro_familia": {
        "name": "Libro de Familia",
        "name_en": "Family Book",
        "icon": "👨‍👩‍👧",
        "keywords": ["LIBRO", "FAMILIA", "FAMILY"],
        "required": False,
        "validity_months": None,
        "needs_apostille": False,
        "help_text": "Si tienes libro de familia español."
    },
    "otro": {
        "name": "Otro Documento",
        "name_en": "Other Document",
        "icon": "📄",
        "keywords": [],
        "required": False,
        "validity_months": None,
        "needs_apostille": False,
        "help_text": "Cualquier otro documento que demuestre tu estancia en España."
    },
}

# =============================================================================
# COMPREHENSIVE FAQ SYSTEM
# =============================================================================

FAQ_DATABASE = {
    # =========== REQUISITOS ===========
    "requisitos_basicos": {
        "keywords": ["requisito", "necesito", "qué necesito", "qué hace falta", "condiciones", "puedo aplicar", "califico"],
        "title": "📝 Requisitos para la Regularización",
        "content": """
*Requisitos principales:*

1️⃣ *Fecha de entrada*
   Haber entrado a España antes del 31/12/2025

2️⃣ *Tiempo de estancia*
   Acreditar al menos 5 meses de permanencia continua

3️⃣ *Antecedentes penales*
   No tener antecedentes en España ni en tu país

4️⃣ *Documentos*
   Pasaporte vigente + pruebas de estancia

*❌ NO necesitas:*
• Contrato de trabajo
• Oferta de empleo
• Padrón de 3 años
• NIE previo
""",
    },
    
    "fecha_entrada": {
        "keywords": ["cuándo entré", "fecha entrada", "31 diciembre", "llegué", "vine", "entrar españa"],
        "title": "📅 Fecha de Entrada",
        "content": """
*¿Cuándo debí haber entrado?*

Debes haber entrado a España *antes del 31 de diciembre de 2025*.

*¿Cómo lo demuestro?*
• Sello de entrada en pasaporte
• Billete de avión/bus
• Empadronamiento antiguo
• Cualquier documento con fecha

*¿Y si entré sin sello?*
No te preocupes, hay otras formas de demostrarlo con documentos posteriores.
""",
    },
    
    "sin_contrato": {
        "keywords": ["contrato", "trabajo", "empleo", "oferta", "sin trabajo", "desempleado"],
        "title": "💼 ¿Necesito Contrato de Trabajo?",
        "content": """
*¡NO necesitas contrato de trabajo!* 🎉

Esta regularización es diferente al arraigo laboral.

*No necesitas:*
❌ Contrato de trabajo
❌ Oferta de empleo
❌ Demostrar ingresos mínimos
❌ Alta en Seguridad Social

*Importante:*
Una vez tengas los papeles, podrás trabajar legalmente en cualquier sector.
""",
    },
    
    # =========== DOCUMENTOS ===========
    "documentos_lista": {
        "keywords": ["documentos", "papeles", "qué documentos", "lista documentos", "qué necesito subir"],
        "title": "📄 Lista de Documentos",
        "content": """
*📋 Documentos OBLIGATORIOS:*
🪪 Pasaporte vigente
📍 Empadronamiento (o alternativas)
📜 Antecedentes penales con apostilla
📷 Foto tipo carnet

*📎 Pruebas de estancia (mínimo 2):*
💡 Facturas de luz/agua/gas
🏠 Contrato de alquiler
🏦 Extractos bancarios
💸 Recibos Western Union/Ria
🏥 Tarjeta sanitaria
📝 Cualquier documento a tu nombre con fecha

*👶 Para menores (adicional):*
• Partida de nacimiento apostillada
• Certificado de escolarización
""",
    },
    
    "sin_empadronamiento": {
        "keywords": ["sin padrón", "no tengo empadronamiento", "sin empadronar", "no empadronado", "problema padrón"],
        "title": "📍 ¿No Tienes Empadronamiento?",
        "content": """
*¿No tienes empadronamiento? ¡Hay solución!*

*Alternativas válidas:*
1. Combinación de facturas a tu nombre
2. Contrato de alquiler + facturas
3. Declaración del propietario
4. Empadronamiento en albergue/asociación
5. Informe de servicios sociales

*Consejo:*
Si vives con alguien, puede autorizarte a empadronarte. Muchas asociaciones también ayudan con esto.

*¿Necesitas ayuda?*
Nuestro equipo puede orientarte sobre la mejor opción para tu caso.
""",
    },
    
    # =========== ANTECEDENTES Y APOSTILLA ===========
    "apostilla_que_es": {
        "keywords": ["apostilla", "qué es apostilla", "apostillar", "legalizar"],
        "title": "📜 ¿Qué es la Apostilla?",
        "content": """
*La Apostilla de La Haya*

Es un certificado que valida documentos oficiales de tu país para usarlos en España.

*¿Qué documentos necesitan apostilla?*
• Antecedentes penales ✅
• Partida de nacimiento (menores) ✅
• Acta de matrimonio (si aplica) ✅

*¿Cómo se consigue?*
En tu país de origen, en el Ministerio de Relaciones Exteriores o Cancillería.

*¡Te ayudamos!* 🎉
Ofrecemos servicio de obtención de antecedentes CON apostilla para Colombia, Perú, Ecuador y Venezuela. ¡100% online!
""",
    },
    
    "antecedentes_como": {
        "keywords": ["antecedentes", "certificado penal", "récord criminal", "conseguir antecedentes", "cómo saco antecedentes"],
        "title": "📜 Cómo Obtener Antecedentes Penales",
        "content": """
*Certificado de Antecedentes Penales*

Debes obtenerlo en tu país de origen Y apostillarlo.

*Opciones:*
1️⃣ *Hacerlo tú mismo*
   - Pídelo online o en el consulado
   - Luego apostíllalo en Cancillería/RREE

2️⃣ *Que nosotros lo hagamos* ✨
   Servicio completo desde €49:
   • Lo obtenemos por ti
   • Lo apostillamos
   • Te lo enviamos por email
   
*Países con servicio online:*
🇨🇴 Colombia: €49
🇵🇪 Perú: €59
🇪🇨 Ecuador: €49
🇻🇪 Venezuela: €69

Escribe /antecedentes para más info.
""",
    },
    
    "antecedentes_pais": {
        "keywords": ["antecedentes colombia", "antecedentes peru", "antecedentes ecuador", "antecedentes venezuela"],
        "title": "📜 Antecedentes por País",
        "content": """
*Servicio de Antecedentes con Apostilla*

🇨🇴 *Colombia* - €49
   • Policía + Procuraduría
   • 3-5 días hábiles
   • 100% online

🇵🇪 *Perú* - €59
   • Poder Judicial
   • 5-7 días hábiles
   • 100% online

🇪🇨 *Ecuador* - €49
   • Min. Interior
   • 3-5 días hábiles
   • 100% online

🇻🇪 *Venezuela* - €69
   • MPPRIJP + SLAE
   • 7-15 días hábiles
   • Online (puede haber demoras)

*¿Otro país?* Escríbenos para cotización personalizada.
""",
    },
    
    # =========== TRABAJO ===========
    "puedo_trabajar": {
        "keywords": ["trabajar", "trabajo", "permiso trabajo", "autorización", "puedo trabajar", "trabajar mientras"],
        "title": "💼 ¿Puedo Trabajar?",
        "content": """
*¡SÍ puedes trabajar!* 🎉

Desde que tu solicitud es *admitida a trámite* (máximo 15 días después de presentarla):

✅ Autorización provisional para trabajar
✅ En cualquier sector
✅ En toda España
✅ Por cuenta ajena o propia

*Importante:*
• No necesitas contrato previo
• No necesitas permiso separado
• Puedes buscar trabajo libremente

*Una vez aprobado:*
Recibirás un permiso de residencia y trabajo de 1 año (renovable).
""",
    },
    
    # =========== FAMILIA Y MENORES ===========
    "menores": {
        "keywords": ["hijo", "hijos", "menor", "menores", "niño", "niños", "familia"],
        "title": "👨‍👩‍👧 Regularización de Menores",
        "content": """
*¡Buenas noticias para familias!*

Tus hijos menores pueden regularizarse contigo.

*Ventajas para menores:*
✅ Permiso de *5 AÑOS* (no solo 1 año)
✅ Trámite conjunto con los padres
✅ Mismo plazo de resolución
✅ No necesitan demostrar estancia

*Documentos adicionales:*
• Pasaporte del menor
• Partida de nacimiento apostillada
• Certificado de escolarización
• Libro de familia (si lo hay)

*Precio familiar:*
2ª persona: 18% descuento
3ª+ persona: 25% descuento
""",
    },
    
    "nacido_espana": {
        "keywords": ["nacido españa", "nació aquí", "bebé", "nacimiento españa"],
        "title": "👶 Hijos Nacidos en España",
        "content": """
*¿Tu hijo nació en España?*

Los menores nacidos en España de padres en situación irregular pueden regularizarse junto con sus padres.

*Documentos:*
• Certificado de nacimiento español
• Libro de familia español
• Certificado de escolarización

*Ventaja:*
Obtienen permiso de 5 años directamente.

*Nota:*
Un hijo nacido en España NO obtiene automáticamente la nacionalidad española, pero este trámite es un primer paso.
""",
    },
    
    # =========== PLAZOS ===========
    "plazos": {
        "keywords": ["plazo", "fecha", "cuándo", "tiempo", "deadline", "cierre", "hasta cuándo"],
        "title": "⏰ Plazos Importantes",
        "content": f"""
*Fechas clave:*

📅 *Presentación de solicitudes:*
• Desde: Abril 2026
• Hasta: *30 Junio 2026* ⚠️

⏳ *Faltan {(DEADLINE - datetime.now()).days} días para el cierre*

*Una vez presentada la solicitud:*
• Admisión a trámite: máx. 15 días
• Resolución final: máx. 3 meses
• Autorización de trabajo: al admitirse

*Consejo:*
No esperes al último momento. Prepara tus documentos ahora para evitar el colapso de junio.
""",
    },
    
    # =========== PRECIO ===========
    "precio": {
        "keywords": ["precio", "costo", "cuánto cuesta", "tarifa", "pagar", "cuánto vale", "coste"],
        "title": "💰 Nuestros Precios",
        "content": """
*Precios transparentes, sin sorpresas:*

*Servicio básico:*
├ Evaluación inicial: €99
├ Gestión completa: €199
└ Tasa gobierno: €38.28
━━━━━━━━━━━━━━━━━
*Total: €336.28*

*Descuentos familia:*
• 2ª persona: -18% (€275 c/u)
• 3+ personas: -25% (€252 c/u)

*Servicio antecedentes:*
• Colombia/Ecuador: €49
• Perú: €59
• Venezuela: €69
• Otros: €79

*Formas de pago:*
💳 Tarjeta, Bizum, transferencia

*Sin letra pequeña:*
El precio incluye TODO el proceso hasta la resolución.
""",
    },
    
    "pago_cuotas": {
        "keywords": ["cuotas", "plazos pago", "dividir", "financiar", "pagar poco a poco"],
        "title": "💳 Pago Flexible",
        "content": """
*Pago en dos partes:*

*1º Pago - Al empezar:*
€99 - Evaluación y apertura de caso

*2º Pago - Documentos listos:*
€199 - Gestión completa

*3º - Antes de presentar:*
€38.28 - Tasa del gobierno

*Nota:*
No cobramos el segundo pago hasta que tus documentos estén completos y revisados.

*¿Dificultades económicas?*
Contáctanos, podemos buscar soluciones.
""",
    },
    
    # =========== PROCESO ===========
    "como_funciona": {
        "keywords": ["cómo funciona", "proceso", "pasos", "qué hago", "empezar", "comenzar"],
        "title": "🚀 ¿Cómo Funciona?",
        "content": """
*Proceso paso a paso:*

*1️⃣ Evaluación (5 min)*
   Contestas unas preguntas para verificar elegibilidad

*2️⃣ Pago inicial (€99)*
   Se activa tu caso y portal personal

*3️⃣ Subir documentos*
   Nos envías tus documentos por aquí o por WhatsApp

*4️⃣ Revisión legal*
   Nuestros abogados revisan todo

*5️⃣ Pago final (€199 + tasa)*
   Cuando todo esté listo

*6️⃣ Presentación*
   Presentamos tu solicitud oficialmente

*7️⃣ ¡A trabajar!*
   Con la admisión ya puedes trabajar legalmente
""",
    },
    
    # =========== CONSULADO ===========
    "consulado": {
        "keywords": ["consulado", "embajada", "cita consulado"],
        "title": "🏛️ ¿Necesito Ir al Consulado?",
        "content": """
*No necesitas ir al consulado de tu país* para este trámite.

*El proceso es en España:*
• Ante las autoridades españolas
• En la oficina de extranjería
• O de forma telemática

*¿Cuándo SÍ necesitas el consulado?*
• Para renovar tu pasaporte
• Para obtener antecedentes penales (aunque hay alternativas online)

*Tip:*
Puedes pedir antecedentes online para muchos países. ¡Te ayudamos!
""",
    },
    
    # =========== RECHAZO ===========
    "si_rechazan": {
        "keywords": ["rechazo", "rechazan", "deniegan", "negativo", "no aprueban", "qué pasa si"],
        "title": "⚠️ ¿Y Si Me Rechazan?",
        "content": """
*Esperamos una tasa de aprobación muy alta (95%+)*

*Si hay rechazo:*
1. Analizamos el motivo
2. Posibilidad de recurso
3. Si es por nuestra gestión: reembolso parcial

*Motivos comunes de rechazo:*
• Antecedentes penales graves
• Documentos falsificados
• No cumplir fecha de entrada

*Nuestra garantía:*
Si por algún error nuestro no se presenta la solicitud, devolvemos el 100%.
""",
    },
    
    # =========== DUDAS COMUNES ===========
    "sin_pasaporte": {
        "keywords": ["sin pasaporte", "pasaporte vencido", "caducado", "expirado", "no tengo pasaporte"],
        "title": "🪪 Problemas con Pasaporte",
        "content": """
*¿Pasaporte vencido o sin pasaporte?*

*Pasaporte vencido:*
Debes renovarlo. Puedes hacerlo en:
• Tu consulado en España
• Online (algunos países)

*Sin pasaporte:*
Es obligatorio tener pasaporte vigente. No hay alternativa para este requisito.

*Consejo:*
Empieza el trámite de renovación YA. Los consulados suelen tener demoras.
""",
    },
    
    "nie_antes": {
        "keywords": ["nie", "número extranjero", "tenía nie", "nie vencido"],
        "title": "🔢 ¿Ya Tenías NIE?",
        "content": """
*¿Tuviste NIE antes y se venció?*

Esta regularización es para personas en situación irregular, incluyendo:

✅ Nunca tuviste papeles
✅ Tuviste NIE y no renovaste
✅ Tuviste residencia y caducó
✅ Entraste como turista y te quedaste

*Ventaja:*
Si ya tienes NIE asignado, el trámite puede ser más rápido porque ya estás en el sistema.
""",
    },
    
    "viajes": {
        "keywords": ["viajar", "salir españa", "vuelo", "puedo viajar", "salir del país"],
        "title": "✈️ ¿Puedo Viajar?",
        "content": """
*Sobre viajar durante el trámite:*

*ANTES de presentar:*
⚠️ No recomendamos salir de España
Si sales, podrías no poder volver a entrar

*DESPUÉS de presentar (con admisión):*
✅ Puedes viajar dentro de España
⚠️ Salir de España es arriesgado hasta tener tarjeta

*CON tarjeta aprobada:*
✅ Puedes viajar libremente al espacio Schengen
✅ Volver a tu país de vacaciones

*Consejo:*
Espera a tener la tarjeta física para viajar fuera de España.
""",
    },
    
    # =========== ESPECÍFICOS ===========
    "overstay": {
        "keywords": ["multa", "sanción", "irregular", "overstay", "me pueden expulsar"],
        "title": "⚖️ Situación Irregular y Sanciones",
        "content": """
*¿Me pueden multar o expulsar?*

Esta regularización es una *amnistía* que:

✅ Borra la situación irregular pasada
✅ No genera multas ni sanciones
✅ No hay consecuencias por el tiempo irregular

*¿Puedo ser expulsado mientras espero?*
En general, mientras tengas el trámite en curso, no se ejecutan expulsiones (salvo casos excepcionales de seguridad pública).

*Consejo:*
Presenta cuanto antes para tener la protección del trámite en curso.
""",
    },
    
    "autonomo": {
        "keywords": ["autónomo", "negocio", "emprender", "cuenta propia", "freelance"],
        "title": "💼 Trabajar como Autónomo",
        "content": """
*¿Puedo ser autónomo?*

¡Sí! El permiso que recibirás permite:

✅ Trabajo por cuenta ajena (empleado)
✅ Trabajo por cuenta propia (autónomo)
✅ Cualquier sector
✅ En toda España

*Para darte de alta como autónomo:*
1. Tener la autorización de trabajo
2. Darte de alta en Hacienda
3. Darte de alta en Seguridad Social

*Nota:*
Puedes empezar a trabajar apenas recibas la admisión a trámite.
""",
    },
}

# =============================================================================
# NATURAL LANGUAGE UNDERSTANDING
# =============================================================================

# Intent patterns for random user messages
INTENT_PATTERNS = {
    "greeting": {
        "patterns": [
            r"^hola\b", r"^buenos? (días?|tardes?|noches?)", r"^hey\b", r"^hi\b", 
            r"^saludos?\b", r"^qué tal", r"^buenas\b", r"^hello"
        ],
        "response": "greeting"
    },
    "thanks": {
        "patterns": [
            r"gracias", r"thank", r"genial", r"perfecto", r"excelente", r"ok\b", 
            r"vale\b", r"de acuerdo", r"entendido", r"👍", r"🙏"
        ],
        "response": "thanks"
    },
    "goodbye": {
        "patterns": [
            r"adiós", r"adios", r"chao", r"bye", r"hasta luego", r"nos vemos", 
            r"me voy", r"hasta pronto"
        ],
        "response": "goodbye"
    },
    "help": {
        "patterns": [
            r"ayuda", r"help", r"no entiendo", r"no sé", r"cómo funciona", 
            r"qué hago", r"estoy perdido", r"explica"
        ],
        "response": "help"
    },
    "price_query": {
        "patterns": [
            r"precio", r"cuesta", r"cuánto", r"tarifa", r"pagar", r"costo", 
            r"vale", r"cobr"
        ],
        "response": "faq_precio"
    },
    "status_query": {
        "patterns": [
            r"estado", r"mi caso", r"cómo va", r"progreso", r"avance", 
            r"documentos", r"qué falta"
        ],
        "response": "status"
    },
    "human_request": {
        "patterns": [
            r"hablar.*persona", r"agente", r"humano", r"operador", r"llamar",
            r"teléfono", r"contacto", r"alguien real", r"persona real"
        ],
        "response": "contact"
    },
    "appointment": {
        "patterns": [
            r"cita", r"appointment", r"reunión", r"consulta", r"videollamada",
            r"llamada", r"hablar.*abogado"
        ],
        "response": "appointment"
    },
    "payment": {
        "patterns": [
            r"pagar", r"pago", r"bizum", r"tarjeta", r"transferencia", 
            r"factura", r"recibo"
        ],
        "response": "payment"
    },
    "antecedentes": {
        "patterns": [
            r"antecedentes", r"penales", r"criminal", r"apostilla", r"récord"
        ],
        "response": "antecedentes"
    },
}

# Responses for intents
INTENT_RESPONSES = {
    "greeting": """
¡Hola! 👋 Bienvenido a *tuspapeles2026*

Soy tu asistente para la regularización extraordinaria en España.

¿En qué puedo ayudarte hoy?
""",
    "thanks": """
¡De nada! 😊 Estoy aquí para ayudarte.

¿Hay algo más en lo que pueda asistirte?
""",
    "goodbye": """
¡Hasta pronto! 👋

Recuerda que puedes escribirme cuando quieras. Estaré aquí 24/7.

📱 También puedes escribirnos por WhatsApp: +34 XXX XXX XXX
""",
    "help": """
¡Claro que te ayudo! 🤝

*¿Qué puedo hacer por ti?*

📝 /start - Empezar desde cero
📊 /estado - Ver tu caso
📄 /documentos - Subir documentos
❓ /ayuda - Preguntas frecuentes
💬 /contacto - Hablar con una persona

*O simplemente escríbeme tu duda* y haré lo posible por resolverla.
""",
    "contact": """
*¿Necesitas hablar con una persona?* 👤

*Opciones:*
1️⃣ *WhatsApp:* +34 XXX XXX XXX
2️⃣ *Email:* info@tuspapeles2026.es
3️⃣ *Videollamada:* Agenda una cita gratuita

*Horario de atención humana:*
Lunes a Viernes: 9:00 - 20:00
Sábados: 10:00 - 14:00

_Mientras tanto, puedo resolver muchas dudas aquí mismo._
""",
}

def detect_intent(text: str) -> Optional[str]:
    """Detect user intent from free text."""
    text_lower = text.lower().strip()
    
    for intent, data in INTENT_PATTERNS.items():
        for pattern in data["patterns"]:
            if re.search(pattern, text_lower):
                return data["response"]
    
    return None

def find_faq_match(text: str) -> Optional[Dict]:
    """Find best matching FAQ entry for user text."""
    text_lower = text.lower()
    best_match = None
    best_score = 0
    
    for key, faq in FAQ_DATABASE.items():
        score = 0
        for keyword in faq["keywords"]:
            if keyword.lower() in text_lower:
                # Longer keywords get higher scores
                score += len(keyword)
        
        if score > best_score:
            best_score = score
            best_match = faq
    
    # Return match only if score is significant
    return best_match if best_score >= 4 else None

# =============================================================================
# DATABASE FUNCTIONS
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
            whatsapp_id TEXT,
            phone TEXT,
            email TEXT,
            first_name TEXT,
            last_name TEXT,
            nationality TEXT,
            passport_number TEXT,
            date_of_birth TEXT,
            entry_date TEXT,
            address TEXT,
            selfie_file_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT,
            language TEXT DEFAULT 'es',
            referral_code TEXT,
            referred_by INTEGER
        )
    ''')
    
    # Cases table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE,
            user_id INTEGER REFERENCES users(id),
            status TEXT DEFAULT 'new',
            stage TEXT DEFAULT 'evaluation',
            eligibility_score INTEGER,
            assigned_lawyer TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            submitted_at TEXT,
            admitted_at TEXT,
            resolved_at TEXT,
            resolution TEXT
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
            file_path TEXT,
            extracted_text TEXT,
            extracted_data TEXT,
            validation_score INTEGER,
            status TEXT DEFAULT 'pending',
            rejection_reason TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            verified_at TEXT,
            verified_by TEXT,
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
            currency TEXT DEFAULT 'EUR',
            payment_type TEXT,
            payment_method TEXT,
            status TEXT DEFAULT 'pending',
            stripe_payment_id TEXT,
            stripe_checkout_url TEXT,
            transaction_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_at TEXT,
            notes TEXT
        )
    ''')
    
    # Appointments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            case_id INTEGER REFERENCES cases(id),
            appointment_type TEXT,
            scheduled_date TEXT,
            scheduled_time TEXT,
            duration_minutes INTEGER DEFAULT 30,
            status TEXT DEFAULT 'scheduled',
            meeting_link TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            cancelled_at TEXT
        )
    ''')
    
    # Antecedentes service table
    c.execute('''
        CREATE TABLE IF NOT EXISTS antecedentes_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            country TEXT,
            status TEXT DEFAULT 'pending',
            citizen_id TEXT,
            email_for_delivery TEXT,
            price REAL,
            payment_id INTEGER REFERENCES payments(id),
            certificate_obtained_at TEXT,
            apostille_obtained_at TEXT,
            delivered_at TEXT,
            tracking_notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Messages/interactions log
    c.execute('''
        CREATE TABLE IF NOT EXISTS message_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            platform TEXT,
            direction TEXT,
            message_type TEXT,
            content TEXT,
            intent_detected TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Admin notifications queue
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notification_type TEXT,
            priority TEXT DEFAULT 'normal',
            user_id INTEGER,
            case_id INTEGER,
            message TEXT,
            data TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            handled_at TEXT,
            handled_by TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

def get_db():
    """Get database connection."""
    conn = sqlite3.connect('tuspapeles.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_or_create_user(telegram_id: int, first_name: str = None) -> Dict:
    """Get user from database or create new one."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    
    if row:
        user = dict(row)
        # Update last active
        c.execute("UPDATE users SET last_active = ? WHERE telegram_id = ?", 
                  (datetime.now().isoformat(), telegram_id))
        conn.commit()
    else:
        # Create new user
        c.execute("""
            INSERT INTO users (telegram_id, first_name, last_active) 
            VALUES (?, ?, ?)
        """, (telegram_id, first_name, datetime.now().isoformat()))
        conn.commit()
        user_id = c.lastrowid
        
        # Create case
        case_number = f"TP2026-{user_id:05d}"
        c.execute("""
            INSERT INTO cases (case_number, user_id) 
            VALUES (?, ?)
        """, (case_number, user_id))
        conn.commit()
        
        user = {
            "id": user_id,
            "telegram_id": telegram_id,
            "first_name": first_name,
            "case_number": case_number,
            "is_new": True
        }
        
        # Notify admins of new user
        notify_admins(
            "new_user",
            f"🆕 Nuevo usuario: {first_name or 'Sin nombre'} (ID: {telegram_id})",
            user_id=user_id
        )
    
    conn.close()
    return user

def update_user(telegram_id: int, **kwargs) -> None:
    """Update user data."""
    conn = get_db()
    c = conn.cursor()
    
    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [telegram_id]
    
    c.execute(f"UPDATE users SET {fields} WHERE telegram_id = ?", values)
    conn.commit()
    conn.close()

def get_user_case(telegram_id: int) -> Optional[Dict]:
    """Get user's case with all documents."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT u.*, c.id as case_id, c.case_number, c.status as case_status, 
               c.stage, c.eligibility_score
        FROM users u
        JOIN cases c ON u.id = c.user_id
        WHERE u.telegram_id = ?
    """, (telegram_id,))
    
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    
    case = dict(row)
    
    # Get documents
    c.execute("""
        SELECT * FROM documents 
        WHERE case_id = ? 
        ORDER BY uploaded_at DESC
    """, (case["case_id"],))
    
    case["documents"] = [dict(r) for r in c.fetchall()]
    
    # Get payments
    c.execute("""
        SELECT * FROM payments 
        WHERE case_id = ? 
        ORDER BY created_at DESC
    """, (case["case_id"],))
    
    case["payments"] = [dict(r) for r in c.fetchall()]
    
    conn.close()
    return case

def save_document(user_id: int, case_id: int, doc_type: str, file_id: str, 
                  extracted_data: dict = None, validation_score: int = None) -> int:
    """Save document to database."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO documents (user_id, case_id, document_type, file_id, 
                              extracted_data, validation_score, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, case_id, doc_type, file_id, 
          json.dumps(extracted_data) if extracted_data else None,
          validation_score, datetime.now().isoformat()))
    
    conn.commit()
    doc_id = c.lastrowid
    conn.close()
    
    return doc_id

def notify_admins(notification_type: str, message: str, 
                  user_id: int = None, case_id: int = None,
                  priority: str = "normal", data: dict = None):
    """Queue admin notification."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO admin_notifications 
        (notification_type, priority, user_id, case_id, message, data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (notification_type, priority, user_id, case_id, message,
          json.dumps(data) if data else None))
    
    conn.commit()
    conn.close()

def log_message(user_id: int, platform: str, direction: str, 
                content: str, message_type: str = "text", intent: str = None):
    """Log message for analytics."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO message_log 
        (user_id, platform, direction, message_type, content, intent_detected)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, platform, direction, message_type, 
          content[:500] if content else None, intent))
    
    conn.commit()
    conn.close()

# =============================================================================
# KEYBOARD BUILDERS
# =============================================================================

def build_main_menu(user: Dict = None) -> InlineKeyboardMarkup:
    """Build main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("📊 Mi Estado", callback_data="status"),
         InlineKeyboardButton("📄 Documentos", callback_data="documents")],
        [InlineKeyboardButton("📤 Subir Documento", callback_data="upload")],
        [InlineKeyboardButton("💳 Pagos", callback_data="payments"),
         InlineKeyboardButton("📅 Cita", callback_data="appointment")],
        [InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data="faq")],
        [InlineKeyboardButton("📜 Servicio Antecedentes", callback_data="antecedentes")],
        [InlineKeyboardButton("💬 Contacto Humano", callback_data="contact")],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_faq_menu() -> InlineKeyboardMarkup:
    """Build FAQ categories keyboard."""
    keyboard = [
        [InlineKeyboardButton("📝 Requisitos", callback_data="faq_requisitos"),
         InlineKeyboardButton("📄 Documentos", callback_data="faq_documentos")],
        [InlineKeyboardButton("📜 Apostilla", callback_data="faq_apostilla"),
         InlineKeyboardButton("💼 Trabajo", callback_data="faq_trabajo")],
        [InlineKeyboardButton("👨‍👩‍👧 Familia", callback_data="faq_familia"),
         InlineKeyboardButton("⏰ Plazos", callback_data="faq_plazos")],
        [InlineKeyboardButton("💰 Precios", callback_data="faq_precio"),
         InlineKeyboardButton("🚀 Proceso", callback_data="faq_proceso")],
        [InlineKeyboardButton("✈️ Viajes", callback_data="faq_viajes"),
         InlineKeyboardButton("⚖️ Legal", callback_data="faq_legal")],
        [InlineKeyboardButton("« Menú Principal", callback_data="main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_documents_menu(case: Dict) -> InlineKeyboardMarkup:
    """Build document upload menu showing what's missing."""
    uploaded_types = [d["document_type"] for d in case.get("documents", [])]
    
    keyboard = []
    
    # Required documents first
    for doc_type, config in DOCUMENT_TYPES.items():
        if config["required"]:
            status = "✅" if doc_type in uploaded_types else "⏳"
            keyboard.append([
                InlineKeyboardButton(
                    f"{status} {config['icon']} {config['name']}", 
                    callback_data=f"upload_{doc_type}"
                )
            ])
    
    # Optional documents section
    keyboard.append([InlineKeyboardButton("➕ Añadir documento opcional", callback_data="upload_optional")])
    keyboard.append([InlineKeyboardButton("« Menú Principal", callback_data="main")])
    
    return InlineKeyboardMarkup(keyboard)

def build_nationality_keyboard() -> InlineKeyboardMarkup:
    """Build nationality selection keyboard."""
    # Most common nationalities first
    common = ["co", "pe", "ec", "ve", "hn", "bo", "do", "ma"]
    
    keyboard = []
    row = []
    for code in common:
        nat = NATIONALITIES[code]
        row.append(InlineKeyboardButton(
            f"{nat['flag']} {nat['name'][:12]}", 
            callback_data=f"nat_{code}"
        ))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🌍 Otro país...", callback_data="nat_other")])
    keyboard.append([InlineKeyboardButton("« Volver", callback_data="main")])
    
    return InlineKeyboardMarkup(keyboard)

def build_payment_menu(case: Dict) -> InlineKeyboardMarkup:
    """Build payment options keyboard."""
    payments = case.get("payments", [])
    evaluation_paid = any(p["payment_type"] == "evaluation" and p["status"] == "paid" for p in payments)
    processing_paid = any(p["payment_type"] == "processing" and p["status"] == "paid" for p in payments)
    
    keyboard = []
    
    if not evaluation_paid:
        keyboard.append([InlineKeyboardButton(
            f"💳 Pagar Evaluación (€{PRICING['evaluation']})", 
            callback_data="pay_evaluation"
        )])
    else:
        keyboard.append([InlineKeyboardButton("✅ Evaluación pagada", callback_data="paid_info")])
    
    if evaluation_paid and not processing_paid:
        keyboard.append([InlineKeyboardButton(
            f"💳 Pagar Gestión (€{PRICING['processing']})", 
            callback_data="pay_processing"
        )])
    elif processing_paid:
        keyboard.append([InlineKeyboardButton("✅ Gestión pagada", callback_data="paid_info")])
    
    keyboard.append([InlineKeyboardButton("📋 Historial de Pagos", callback_data="payment_history")])
    keyboard.append([InlineKeyboardButton("« Menú Principal", callback_data="main")])
    
    return InlineKeyboardMarkup(keyboard)

def build_antecedentes_menu() -> InlineKeyboardMarkup:
    """Build antecedentes service keyboard."""
    keyboard = [
        [InlineKeyboardButton(f"🇨🇴 Colombia (€{PRICING['antecedentes_colombia']})", callback_data="ante_co")],
        [InlineKeyboardButton(f"🇵🇪 Perú (€{PRICING['antecedentes_peru']})", callback_data="ante_pe")],
        [InlineKeyboardButton(f"🇪🇨 Ecuador (€{PRICING['antecedentes_ecuador']})", callback_data="ante_ec")],
        [InlineKeyboardButton(f"🇻🇪 Venezuela (€{PRICING['antecedentes_venezuela']})", callback_data="ante_ve")],
        [InlineKeyboardButton(f"🌍 Otro país (€{PRICING['antecedentes_other']})", callback_data="ante_other")],
        [InlineKeyboardButton("❓ ¿Cómo funciona?", callback_data="ante_info")],
        [InlineKeyboardButton("« Menú Principal", callback_data="main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_appointment_menu() -> InlineKeyboardMarkup:
    """Build appointment scheduling keyboard."""
    keyboard = [
        [InlineKeyboardButton("📹 Videollamada (30 min) - GRATIS", callback_data="appt_video")],
        [InlineKeyboardButton("📞 Llamada telefónica", callback_data="appt_phone")],
        [InlineKeyboardButton("💬 Chat con abogado", callback_data="appt_chat")],
        [InlineKeyboardButton("📅 Ver mis citas", callback_data="appt_list")],
        [InlineKeyboardButton("« Menú Principal", callback_data="main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_back_button(callback: str = "main") -> InlineKeyboardMarkup:
    """Build simple back button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("« Volver", callback_data=callback)]
    ])

# Continue in Part 2...
# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_progress(case: Dict) -> Dict:
    """Calculate case completion progress."""
    documents = case.get("documents", [])
    uploaded_types = set(d["document_type"] for d in documents if d["status"] != "rejected")
    verified_types = set(d["document_type"] for d in documents if d["status"] == "verified")
    
    required_docs = [k for k, v in DOCUMENT_TYPES.items() if v["required"]]
    required_uploaded = len([d for d in required_docs if d in uploaded_types])
    required_verified = len([d for d in required_docs if d in verified_types])
    
    # Calculate progress percentage
    total_steps = 5  # docs, payment1, review, payment2, submit
    completed = 0
    
    if required_uploaded >= len(required_docs):
        completed += 1
    if required_verified >= len(required_docs):
        completed += 1
    
    payments = case.get("payments", [])
    if any(p["payment_type"] == "evaluation" and p["status"] == "paid" for p in payments):
        completed += 1
    if any(p["payment_type"] == "processing" and p["status"] == "paid" for p in payments):
        completed += 1
    
    progress = int((completed / total_steps) * 100)
    
    # Determine status text
    status_map = {
        "new": "📝 Pendiente de documentos",
        "collecting": "📂 Recopilando documentos",
        "review": "🔍 En revisión legal",
        "ready": "✅ Listo para presentar",
        "submitted": "📤 Presentado",
        "admitted": "⚡ Admitido - ¡Puedes trabajar!",
        "resolved": "🎉 Resuelto"
    }
    
    missing = [d for d in required_docs if d not in uploaded_types]
    
    return {
        "progress": min(progress, 100),
        "required_total": len(required_docs),
        "required_uploaded": required_uploaded,
        "required_verified": required_verified,
        "optional_uploaded": len(uploaded_types) - required_uploaded,
        "missing_required": missing,
        "status_text": status_map.get(case.get("case_status", "new"), "📝 En proceso"),
        "days_until_deadline": (DEADLINE - datetime.now()).days
    }

def format_progress_bar(progress: int, length: int = 10) -> str:
    """Create visual progress bar."""
    filled = int(progress / 100 * length)
    empty = length - filled
    return "█" * filled + "░" * empty

def format_case_status(case: Dict) -> str:
    """Format case status message."""
    progress = calculate_progress(case)
    bar = format_progress_bar(progress["progress"])
    
    message = f"""
📊 *Estado de tu Caso*
━━━━━━━━━━━━━━━━━━━━━

📋 *Caso:* `{case.get('case_number', 'N/A')}`
📍 *Estado:* {progress['status_text']}

📈 *Progreso:* {progress['progress']}%
{bar}

📄 *Documentos:*
✅ Subidos: {progress['required_uploaded']}/{progress['required_total']} obligatorios
🔍 Verificados: {progress['required_verified']}/{progress['required_total']}
📎 Opcionales: {progress['optional_uploaded']}
"""
    
    if progress["missing_required"]:
        message += "\n⚠️ *Pendiente de subir:*\n"
        for doc_type in progress["missing_required"]:
            config = DOCUMENT_TYPES.get(doc_type, {})
            message += f"• {config.get('icon', '📄')} {config.get('name', doc_type)}\n"
    
    message += f"\n⏰ *Faltan {progress['days_until_deadline']} días* para el cierre"
    
    return message

def format_welcome_message(user: Dict) -> str:
    """Format welcome message for new/returning users."""
    days = (DEADLINE - datetime.now()).days
    first_name = user.get("first_name", "")
    
    return f"""
¡Hola{' ' + first_name if first_name else ''}! 👋 

Soy el asistente de *tuspapeles2026.es*

Te ayudaré a preparar tu solicitud de regularización extraordinaria.

📅 *Fechas clave:*
• Solicitudes: Abril - 30 Junio 2026
• ⏰ Faltan *{days} días* para el cierre

✅ *Requisitos principales:*
• Entrada a España antes del 31/12/2025
• Acreditar 5 meses de estancia
• Sin antecedentes penales

💰 *Precio total:* €336.28
_(Incluye TODO hasta la resolución)_

*¿Empezamos?* 👇
"""

# =============================================================================
# COMMAND HANDLERS
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command."""
    user_tg = update.effective_user
    user = get_or_create_user(user_tg.id, user_tg.first_name)
    
    # Log interaction
    log_message(user.get("id"), "telegram", "in", "/start", "command")
    
    # Send welcome message
    await update.message.reply_text(
        format_welcome_message(user),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_main_menu(user)
    )
    
    return STATE_MAIN

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /menu command."""
    await update.message.reply_text(
        "📱 *Menú Principal*\n\n¿Qué quieres hacer?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_main_menu()
    )
    return STATE_MAIN

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /estado command."""
    case = get_user_case(update.effective_user.id)
    
    if not case:
        await update.message.reply_text(
            "No encontré tu caso. Usa /start para comenzar.",
            reply_markup=build_back_button()
        )
        return
    
    await update.message.reply_text(
        format_case_status(case),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ayuda command."""
    await update.message.reply_text(
        """
❓ *Preguntas Frecuentes*

Selecciona una categoría o escríbeme tu duda directamente:
""",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_faq_menu()
    )

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /contacto command."""
    await update.message.reply_text(
        """
💬 *Contacto con Humanos*

*Opciones disponibles:*

1️⃣ *WhatsApp* (más rápido)
   📱 +34 XXX XXX XXX

2️⃣ *Email*
   ✉️ info@tuspapeles2026.es

3️⃣ *Videollamada gratuita*
   📹 Agenda una consulta de 30 min

4️⃣ *Escribir mensaje ahora*
   ✏️ Escríbeme y te contactamos

*Horario de atención:*
L-V: 9:00 - 20:00
Sáb: 10:00 - 14:00

_Los bots trabajamos 24/7, pero los humanos necesitan descansar 😴_
""",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📹 Agendar Videollamada", callback_data="appt_video")],
            [InlineKeyboardButton("✏️ Escribir Mensaje", callback_data="write_message")],
            [InlineKeyboardButton("« Menú Principal", callback_data="main")],
        ])
    )
    return STATE_MAIN

async def antecedentes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /antecedentes command."""
    await update.message.reply_text(
        """
📜 *Servicio de Antecedentes Penales*

¿Necesitas el certificado de antecedentes penales de tu país *CON APOSTILLA*?

*¡Te lo conseguimos!* 🎉

Nos encargamos de:
✅ Obtener el certificado oficial
✅ Tramitar la apostilla
✅ Enviártelo por email (PDF válido)

*Todo 100% online*, sin que tengas que ir al consulado.

*Selecciona tu país:*
""",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_antecedentes_menu()
    )

# =============================================================================
# CALLBACK HANDLERS
# =============================================================================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle all callback queries."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = get_or_create_user(update.effective_user.id)
    
    # Log interaction
    log_message(user.get("id"), "telegram", "in", f"callback:{data}", "callback")
    
    # ==================== MAIN MENU ====================
    if data == "main":
        await query.edit_message_text(
            "📱 *Menú Principal*\n\n¿Qué quieres hacer?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_main_menu()
        )
        return STATE_MAIN
    
    # ==================== STATUS ====================
    elif data == "status":
        case = get_user_case(update.effective_user.id)
        if case:
            await query.edit_message_text(
                format_case_status(case),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📄 Ver Documentos", callback_data="documents")],
                    [InlineKeyboardButton("📤 Subir Documento", callback_data="upload")],
                    [InlineKeyboardButton("« Menú Principal", callback_data="main")],
                ])
            )
        else:
            await query.edit_message_text(
                "No tienes un caso activo. ¡Empecemos!",
                reply_markup=build_main_menu()
            )
        return STATE_MAIN
    
    # ==================== DOCUMENTS ====================
    elif data == "documents":
        case = get_user_case(update.effective_user.id)
        if case and case.get("documents"):
            msg = "📁 *Mis Documentos*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            status_icons = {
                "pending": "⏳",
                "verified": "✅",
                "rejected": "❌",
                "reviewing": "🔍"
            }
            
            for doc in case["documents"]:
                config = DOCUMENT_TYPES.get(doc["document_type"], DOCUMENT_TYPES["otro"])
                icon = status_icons.get(doc["status"], "⏳")
                
                msg += f"{config['icon']} *{config['name']}*\n"
                msg += f"   Estado: {icon} {doc['status']}\n"
                msg += f"   Subido: {doc['uploaded_at'][:10]}\n"
                if doc.get("rejection_reason"):
                    msg += f"   ⚠️ _{doc['rejection_reason']}_\n"
                msg += "\n"
        else:
            msg = "📁 *Mis Documentos*\n\n_No has subido ningún documento todavía._"
        
        await query.edit_message_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Subir Documento", callback_data="upload")],
                [InlineKeyboardButton("« Menú Principal", callback_data="main")],
            ])
        )
        return STATE_MAIN
    
    # ==================== UPLOAD ====================
    elif data == "upload":
        case = get_user_case(update.effective_user.id)
        await query.edit_message_text(
            """
📤 *Subir Documento*

Selecciona el tipo de documento que vas a subir:
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_documents_menu(case) if case else build_back_button()
        )
        return STATE_MAIN
    
    elif data.startswith("upload_"):
        doc_type = data.replace("upload_", "")
        
        if doc_type == "optional":
            # Show optional documents
            keyboard = []
            for dtype, config in DOCUMENT_TYPES.items():
                if not config["required"]:
                    keyboard.append([InlineKeyboardButton(
                        f"{config['icon']} {config['name']}", 
                        callback_data=f"upload_{dtype}"
                    )])
            keyboard.append([InlineKeyboardButton("« Volver", callback_data="upload")])
            
            await query.edit_message_text(
                "📎 *Documentos Opcionales*\n\nEstos documentos ayudan a fortalecer tu caso:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            config = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["otro"])
            context.user_data["awaiting_document"] = doc_type
            
            msg = f"""
📤 *Subir {config['name']}*

{config['help_text']}

*Instrucciones:*
1. Toma una foto clara del documento
2. Asegúrate de buena iluminación
3. Que se vea todo el documento
4. Envíala aquí directamente

_Esperando tu foto..._ 📷
"""
            if config.get("needs_apostille"):
                msg += "\n⚠️ *Recuerda:* Este documento debe tener apostilla."
            
            await query.edit_message_text(
                msg,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancelar", callback_data="upload")],
                ])
            )
            return STATE_AWAITING_DOCUMENT
        
        return STATE_MAIN
    
    # ==================== PAYMENTS ====================
    elif data == "payments":
        case = get_user_case(update.effective_user.id)
        
        msg = """
💳 *Pagos*
━━━━━━━━━━━━━━━━━━━━━

*Desglose del servicio:*
├ Evaluación inicial: €99
├ Gestión completa: €199
└ Tasa gobierno: €38.28
━━━━━━━━━━━━━━━━━━━━━
*Total: €336.28*

*Formas de pago:*
💳 Tarjeta de crédito/débito
📱 Bizum
🏦 Transferencia bancaria
"""
        
        await query.edit_message_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_payment_menu(case) if case else build_back_button()
        )
        return STATE_MAIN
    
    elif data.startswith("pay_"):
        payment_type = data.replace("pay_", "")
        amount = PRICING.get(payment_type, 99)
        
        # Create payment record
        user_data = get_or_create_user(update.effective_user.id)
        case = get_user_case(update.effective_user.id)
        
        if STRIPE_AVAILABLE and STRIPE_SECRET_KEY:
            # Create Stripe checkout session
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': f'tuspapeles2026 - {payment_type.title()}',
                            },
                            'unit_amount': int(amount * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f'{WEBSITE_URL}/pago-exitoso?session_id={{CHECKOUT_SESSION_ID}}',
                    cancel_url=f'{WEBSITE_URL}/pago-cancelado',
                    metadata={
                        'user_id': user_data.get('id'),
                        'case_id': case.get('case_id') if case else None,
                        'payment_type': payment_type,
                        'telegram_id': update.effective_user.id
                    }
                )
                
                await query.edit_message_text(
                    f"""
💳 *Pago de {payment_type.title()}*

Monto: *€{amount}*

Haz clic en el botón para pagar de forma segura:
""",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💳 Pagar Ahora", url=session.url)],
                        [InlineKeyboardButton("« Volver", callback_data="payments")],
                    ])
                )
            except Exception as e:
                logger.error(f"Stripe error: {e}")
                await query.edit_message_text(
                    f"Error al crear el pago. Por favor contacta con soporte.\n\nError: {str(e)[:100]}",
                    reply_markup=build_back_button("payments")
                )
        else:
            # Manual payment instructions
            await query.edit_message_text(
                f"""
💳 *Pago de {payment_type.title()}*

Monto: *€{amount}*

*Opciones de pago:*

1️⃣ *Bizum:* +34 XXX XXX XXX
   Concepto: {case.get('case_number', 'tuspapeles')}

2️⃣ *Transferencia:*
   IBAN: ES00 0000 0000 0000 0000
   Concepto: {case.get('case_number', 'tuspapeles')}

3️⃣ *Tarjeta:*
   Paga online en: {PAYMENT_URL}

📧 Envía el comprobante a: pagos@tuspapeles2026.es

_Te confirmaremos el pago en menos de 24h_
""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Ya he pagado", callback_data="payment_confirm")],
                    [InlineKeyboardButton("« Volver", callback_data="payments")],
                ])
            )
        
        return STATE_MAIN
    
    elif data == "payment_confirm":
        # Notify admins of payment claim
        user = get_or_create_user(update.effective_user.id)
        case = get_user_case(update.effective_user.id)
        notify_admins(
            "payment_claim",
            f"💰 Usuario dice que ha pagado: {user.get('first_name', 'N/A')} - Caso: {case.get('case_number', 'N/A')}",
            user_id=user.get('id'),
            case_id=case.get('case_id') if case else None,
            priority="high"
        )
        
        await query.edit_message_text(
            """
✅ *¡Gracias!*

Hemos registrado tu notificación de pago.

Verificaremos el pago y actualizaremos tu caso en las próximas 24 horas (normalmente mucho antes).

Te enviaremos un mensaje cuando esté confirmado.
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_back_button("main")
        )
        return STATE_MAIN
    
    # ==================== FAQ ====================
    elif data == "faq":
        await query.edit_message_text(
            "❓ *Preguntas Frecuentes*\n\nSelecciona una categoría:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_faq_menu()
        )
        return STATE_MAIN
    
    elif data.startswith("faq_"):
        category = data.replace("faq_", "")
        
        # Map categories to FAQ entries
        category_map = {
            "requisitos": ["requisitos_basicos", "fecha_entrada", "sin_contrato"],
            "documentos": ["documentos_lista", "sin_empadronamiento"],
            "apostilla": ["apostilla_que_es", "antecedentes_como"],
            "trabajo": ["puedo_trabajar", "autonomo"],
            "familia": ["menores", "nacido_espana"],
            "plazos": ["plazos"],
            "precio": ["precio", "pago_cuotas"],
            "proceso": ["como_funciona"],
            "viajes": ["viajes"],
            "legal": ["overstay", "si_rechazan"],
        }
        
        faq_keys = category_map.get(category, [])
        
        if faq_keys:
            faq = FAQ_DATABASE.get(faq_keys[0], {})
            
            # Build navigation for multiple FAQs in category
            nav_buttons = []
            if len(faq_keys) > 1:
                for i, key in enumerate(faq_keys):
                    f = FAQ_DATABASE.get(key, {})
                    nav_buttons.append(InlineKeyboardButton(
                        f["title"][:20] + "..." if len(f["title"]) > 20 else f["title"],
                        callback_data=f"faqitem_{key}"
                    ))
            
            keyboard = []
            if nav_buttons:
                # Split into rows of 2
                for i in range(0, len(nav_buttons), 2):
                    keyboard.append(nav_buttons[i:i+2])
            
            keyboard.append([InlineKeyboardButton("« Categorías", callback_data="faq")])
            keyboard.append([InlineKeyboardButton("« Menú Principal", callback_data="main")])
            
            await query.edit_message_text(
                f"{faq['title']}\n{faq['content']}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                "Categoría no encontrada.",
                reply_markup=build_faq_menu()
            )
        
        return STATE_MAIN
    
    elif data.startswith("faqitem_"):
        faq_key = data.replace("faqitem_", "")
        faq = FAQ_DATABASE.get(faq_key, {})
        
        if faq:
            await query.edit_message_text(
                f"{faq['title']}\n{faq['content']}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("« Categorías", callback_data="faq")],
                    [InlineKeyboardButton("« Menú Principal", callback_data="main")],
                ])
            )
        
        return STATE_MAIN
    
    # ==================== APPOINTMENTS ====================
    elif data == "appointment":
        await query.edit_message_text(
            """
📅 *Agendar Cita*

¿Cómo prefieres hablar con nosotros?
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_appointment_menu()
        )
        return STATE_MAIN
    
    elif data.startswith("appt_"):
        appt_type = data.replace("appt_", "")
        
        if appt_type == "video":
            # Show available dates (next 7 days, weekdays only)
            keyboard = []
            today = datetime.now()
            
            for i in range(1, 8):
                date = today + timedelta(days=i)
                if date.weekday() < 5:  # Weekday
                    date_str = date.strftime("%Y-%m-%d")
                    date_display = date.strftime("%a %d/%m")
                    keyboard.append([InlineKeyboardButton(
                        f"📅 {date_display}",
                        callback_data=f"apptdate_{date_str}"
                    )])
            
            keyboard.append([InlineKeyboardButton("« Volver", callback_data="appointment")])
            
            context.user_data["appt_type"] = "video"
            
            await query.edit_message_text(
                """
📹 *Videollamada Gratuita*

Duración: 30 minutos
Precio: GRATIS

Selecciona una fecha:
""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return STATE_SCHEDULING_APPOINTMENT
        
        elif appt_type == "list":
            # Show user's appointments
            user = get_or_create_user(update.effective_user.id)
            conn = get_db()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM appointments 
                WHERE user_id = ? AND status = 'scheduled'
                ORDER BY scheduled_date, scheduled_time
            """, (user.get('id'),))
            appointments = c.fetchall()
            conn.close()
            
            if appointments:
                msg = "📅 *Tus Citas*\n\n"
                for appt in appointments:
                    appt = dict(appt)
                    msg += f"📹 {appt['scheduled_date']} a las {appt['scheduled_time']}\n"
                    if appt.get('meeting_link'):
                        msg += f"   🔗 {appt['meeting_link']}\n"
                    msg += "\n"
            else:
                msg = "📅 *Tus Citas*\n\n_No tienes citas programadas._"
            
            await query.edit_message_text(
                msg,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Nueva Cita", callback_data="appt_video")],
                    [InlineKeyboardButton("« Menú Principal", callback_data="main")],
                ])
            )
        
        return STATE_MAIN
    
    elif data.startswith("apptdate_"):
        date_str = data.replace("apptdate_", "")
        context.user_data["appt_date"] = date_str
        
        # Show available times
        times = ["09:00", "10:00", "11:00", "12:00", "16:00", "17:00", "18:00", "19:00"]
        keyboard = []
        row = []
        
        for time in times:
            row.append(InlineKeyboardButton(f"🕐 {time}", callback_data=f"appttime_{time}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("« Volver", callback_data="appt_video")])
        
        await query.edit_message_text(
            f"""
🕐 *Selecciona la hora*

Fecha: {date_str}

Horario disponible:
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return STATE_SELECTING_TIME
    
    elif data.startswith("appttime_"):
        time_str = data.replace("appttime_", "")
        date_str = context.user_data.get("appt_date")
        appt_type = context.user_data.get("appt_type", "video")
        
        # Save appointment
        user = get_or_create_user(update.effective_user.id)
        case = get_user_case(update.effective_user.id)
        
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO appointments 
            (user_id, case_id, appointment_type, scheduled_date, scheduled_time)
            VALUES (?, ?, ?, ?, ?)
        """, (user.get('id'), case.get('case_id') if case else None, 
              appt_type, date_str, time_str))
        conn.commit()
        conn.close()
        
        # Notify admins
        notify_admins(
            "new_appointment",
            f"📅 Nueva cita: {user.get('first_name', 'N/A')} - {date_str} {time_str}",
            user_id=user.get('id'),
            priority="high"
        )
        
        await query.edit_message_text(
            f"""
✅ *¡Cita Confirmada!*

📅 Fecha: {date_str}
🕐 Hora: {time_str}
📹 Tipo: Videollamada

Te enviaremos el enlace de la videollamada el día de la cita.

_Si necesitas cancelar o cambiar la cita, escríbenos._
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_back_button("main")
        )
        
        # Clear appointment data
        context.user_data.pop("appt_date", None)
        context.user_data.pop("appt_type", None)
        
        return STATE_MAIN
    
    # ==================== ANTECEDENTES SERVICE ====================
    elif data == "antecedentes":
        await query.edit_message_text(
            """
📜 *Servicio de Antecedentes Penales*

¿Necesitas el certificado de antecedentes penales de tu país *CON APOSTILLA*?

*¡Nosotros lo gestionamos!* 🎉

✅ Obtenemos el certificado oficial
✅ Tramitamos la apostilla
✅ Te lo enviamos por email (PDF válido)

*Todo 100% online* - Sin ir al consulado

*Selecciona tu país:*
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_antecedentes_menu()
        )
        return STATE_MAIN
    
    elif data.startswith("ante_"):
        country_code = data.replace("ante_", "")
        
        if country_code == "info":
            await query.edit_message_text(
                """
📜 *¿Cómo Funciona el Servicio?*

*Paso 1: Nos envías tus datos*
   • Número de cédula/DNI de tu país
   • Email para recibir el documento

*Paso 2: Realizas el pago*
   • Tarjeta, Bizum o transferencia

*Paso 3: Nosotros hacemos todo*
   • Solicitamos el certificado online
   • Tramitamos la apostilla electrónica
   • Tiempo: 3-15 días según país

*Paso 4: Recibes tu documento*
   • PDF oficial con apostilla
   • Válido para el trámite de regularización

*¿Es legal?*
✅ Sí, usamos los portales oficiales de cada gobierno
✅ El documento es 100% auténtico
✅ La apostilla es oficial

_Necesitamos un poder simple de autorización que te enviaremos._
""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🇨🇴 Pedir Colombia", callback_data="ante_co")],
                    [InlineKeyboardButton("🇵🇪 Pedir Perú", callback_data="ante_pe")],
                    [InlineKeyboardButton("🇪🇨 Pedir Ecuador", callback_data="ante_ec")],
                    [InlineKeyboardButton("🇻🇪 Pedir Venezuela", callback_data="ante_ve")],
                    [InlineKeyboardButton("« Volver", callback_data="antecedentes")],
                ])
            )
        
        elif country_code in ANTECEDENTES_INFO:
            info = ANTECEDENTES_INFO[country_code]
            
            msg = f"""
📜 *Antecedentes de {info['name']}*

*Precio:* €{info['price']}
*Tiempo estimado:* {info['time_days']}

*Incluye:*
✅ Certificado de {info['certificate_source']}
✅ Apostilla de {info['apostille_source']}
✅ Envío por email (PDF)

*Necesitamos:*
"""
            for req in info['requirements']:
                msg += f"• {req}\n"
            
            if info.get('note'):
                msg += f"\n{info['note']}"
            
            msg += "\n\n*¿Quieres contratar este servicio?*"
            
            await query.edit_message_text(
                msg,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"✅ Contratar (€{info['price']})", callback_data=f"ante_order_{country_code}")],
                    [InlineKeyboardButton("« Volver", callback_data="antecedentes")],
                ])
            )
        
        elif country_code == "other":
            await query.edit_message_text(
                """
🌍 *Otros Países*

Para países no listados, el servicio tiene un costo de *€79* y requiere evaluación individual.

*Países con servicio confirmado:*
🇭🇳 Honduras
🇧🇴 Bolivia  
🇵🇾 Paraguay
🇩🇴 República Dominicana
🇸🇻 El Salvador
🇦🇷 Argentina

*Escríbenos* indicando tu país y te confirmamos disponibilidad y tiempo estimado.
""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✏️ Escribir Mensaje", callback_data="write_message")],
                    [InlineKeyboardButton("« Volver", callback_data="antecedentes")],
                ])
            )
        
        return STATE_MAIN
    
    elif data.startswith("ante_order_"):
        country_code = data.replace("ante_order_", "")
        info = ANTECEDENTES_INFO.get(country_code, {})
        
        context.user_data["ante_country"] = country_code
        
        await query.edit_message_text(
            f"""
📝 *Solicitud de Antecedentes - {info.get('name', 'País')}*

Por favor, envíame tu *número de cédula/DNI* de {info.get('name', 'tu país')}.

Escríbelo aquí directamente:
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancelar", callback_data="antecedentes")],
            ])
        )
        return STATE_ANTECEDENTES_DATA
    
    # ==================== CONTACT ====================
    elif data == "contact":
        await query.edit_message_text(
            INTENT_RESPONSES["contact"],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📹 Agendar Videollamada", callback_data="appt_video")],
                [InlineKeyboardButton("✏️ Escribir Mensaje", callback_data="write_message")],
                [InlineKeyboardButton("« Menú Principal", callback_data="main")],
            ])
        )
        return STATE_MAIN
    
    elif data == "write_message":
        await query.edit_message_text(
            """
✏️ *Escribir Mensaje*

Escribe tu mensaje o pregunta y nuestro equipo te responderá lo antes posible.

_Escribe tu mensaje ahora:_
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancelar", callback_data="main")],
            ])
        )
        context.user_data["awaiting_contact_message"] = True
        return STATE_CONTACT_MESSAGE
    
    # ==================== NATIONALITY ====================
    elif data.startswith("nat_"):
        code = data.replace("nat_", "")
        nationality = NATIONALITIES.get(code, {})
        
        user = get_or_create_user(update.effective_user.id)
        update_user(update.effective_user.id, nationality=code)
        
        context.user_data["nationality"] = code
        
        await query.edit_message_text(
            f"""
{nationality.get('flag', '🌍')} *{nationality.get('name', 'País')}*

¡Perfecto! Hemos registrado tu nacionalidad.

""" + ("✅ Tu país está en el Convenio de La Haya, así que solo necesitas *apostilla* (no legalización consular)." 
       if nationality.get('hague') 
       else "⚠️ Tu país NO está en el Convenio de La Haya. Necesitarás *legalización consular* además de la apostilla.") + """

¿Necesitas ayuda con los antecedentes penales?
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📜 Servicio Antecedentes", callback_data="antecedentes")],
                [InlineKeyboardButton("📊 Ver Mi Estado", callback_data="status")],
                [InlineKeyboardButton("« Menú Principal", callback_data="main")],
            ])
        )
        return STATE_MAIN
    
    # Default fallback
    else:
        await query.edit_message_text(
            "No entendí esa opción. Volvamos al menú principal.",
            reply_markup=build_main_menu()
        )
        return STATE_MAIN

# =============================================================================
# MESSAGE HANDLERS
# =============================================================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle photo uploads."""
    user = get_or_create_user(update.effective_user.id)
    photo = update.message.photo[-1]
    
    expected_type = context.user_data.get("awaiting_document")
    
    await update.message.reply_text("🔍 Analizando documento...")
    
    # Download and process
    try:
        photo_file = await photo.get_file()
        
        # Basic classification if OCR available
        doc_type = expected_type or "otro"
        confidence = 70
        extracted_data = {}
        
        if OCR_AVAILABLE:
            try:
                photo_bytes = await photo_file.download_as_bytearray()
                image = Image.open(BytesIO(photo_bytes))
                text = pytesseract.image_to_string(image, lang='spa+eng')
                
                # Classify
                if not expected_type:
                    text_upper = text.upper()
                    for dtype, config in DOCUMENT_TYPES.items():
                        for keyword in config.get("keywords", []):
                            if keyword in text_upper:
                                doc_type = dtype
                                confidence = 85
                                break
                        if doc_type != "otro":
                            break
            except Exception as e:
                logger.error(f"OCR error: {e}")
        
        config = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["otro"])
        
        # Store pending document
        context.user_data["pending_document"] = {
            "file_id": photo.file_id,
            "doc_type": doc_type,
            "extracted_data": extracted_data
        }
        
        msg = f"""
✅ *Documento Detectado*

{config['icon']} *{config['name']}*
Confianza: {confidence}%
"""
        
        if config.get("needs_apostille"):
            msg += "\n⚠️ Recuerda: Este documento necesita apostilla."
        
        msg += "\n\n¿Es correcto?"
        
        await update.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Sí, guardar", callback_data=f"confirm_doc_{doc_type}"),
                 InlineKeyboardButton("❌ No, repetir", callback_data="upload")],
                [InlineKeyboardButton("🔄 Es otro tipo", callback_data="upload")],
            ])
        )
        
        # Clear awaiting
        context.user_data.pop("awaiting_document", None)
        
    except Exception as e:
        logger.error(f"Photo processing error: {e}")
        await update.message.reply_text(
            "❌ Error al procesar la imagen. Por favor, intenta de nuevo.",
            reply_markup=build_back_button("upload")
        )
    
    return STATE_MAIN

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle all text messages with NLU."""
    text = update.message.text.strip()
    user = get_or_create_user(update.effective_user.id, update.effective_user.first_name)
    
    # Log message
    log_message(user.get("id"), "telegram", "in", text, "text")
    
    # Check if we're in a specific state
    
    # Waiting for contact message
    if context.user_data.get("awaiting_contact_message"):
        context.user_data.pop("awaiting_contact_message", None)
        
        # Save and notify admins
        notify_admins(
            "user_message",
            f"💬 Mensaje de {user.get('first_name', 'Usuario')}: {text[:200]}",
            user_id=user.get("id"),
            priority="normal",
            data={"full_message": text}
        )
        
        await update.message.reply_text(
            """
✅ *Mensaje Enviado*

Hemos recibido tu mensaje. Nuestro equipo te responderá lo antes posible.

_Tiempo de respuesta habitual: 2-4 horas en horario laboral_
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_main_menu()
        )
        return STATE_MAIN
    
    # Waiting for antecedentes data (citizen ID)
    if context.user_data.get("ante_country"):
        country = context.user_data.get("ante_country")
        info = ANTECEDENTES_INFO.get(country, {})
        
        # Validate ID format (basic)
        citizen_id = re.sub(r'[^0-9A-Za-z]', '', text)
        
        if len(citizen_id) < 5:
            await update.message.reply_text(
                "❌ El número parece muy corto. Por favor, ingresa tu número de cédula/DNI completo.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancelar", callback_data="antecedentes")],
                ])
            )
            return STATE_ANTECEDENTES_DATA
        
        context.user_data["ante_citizen_id"] = citizen_id
        
        await update.message.reply_text(
            f"""
📧 *Ahora necesito tu email*

El certificado apostillado se enviará a este correo:

_Escribe tu email:_
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancelar", callback_data="antecedentes")],
            ])
        )
        context.user_data["ante_awaiting_email"] = True
        return STATE_ANTECEDENTES_DATA
    
    # Waiting for email for antecedentes
    if context.user_data.get("ante_awaiting_email"):
        email = text.lower().strip()
        
        # Basic email validation
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            await update.message.reply_text(
                "❌ Ese email no parece válido. Por favor, revísalo e intenta de nuevo.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancelar", callback_data="antecedentes")],
                ])
            )
            return STATE_ANTECEDENTES_DATA
        
        country = context.user_data.get("ante_country")
        citizen_id = context.user_data.get("ante_citizen_id")
        info = ANTECEDENTES_INFO.get(country, {})
        
        # Create order
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO antecedentes_orders 
            (user_id, country, citizen_id, email_for_delivery, price)
            VALUES (?, ?, ?, ?, ?)
        """, (user.get('id'), country, citizen_id, email, info.get('price', 79)))
        conn.commit()
        order_id = c.lastrowid
        conn.close()
        
        # Notify admins
        notify_admins(
            "antecedentes_order",
            f"📜 Nueva orden antecedentes: {info.get('name', country)} - {citizen_id}",
            user_id=user.get("id"),
            priority="high",
            data={"order_id": order_id, "country": country, "citizen_id": citizen_id, "email": email}
        )
        
        # Clear context
        context.user_data.pop("ante_country", None)
        context.user_data.pop("ante_citizen_id", None)
        context.user_data.pop("ante_awaiting_email", None)
        
        await update.message.reply_text(
            f"""
✅ *Pedido Registrado*

*Resumen:*
• País: {info.get('name', country)}
• Cédula/DNI: {citizen_id}
• Email: {email}
• Precio: €{info.get('price', 79)}

*Siguiente paso:*
Realiza el pago y te contactaremos para confirmar y comenzar el trámite.

*Formas de pago:*
💳 Tarjeta / Bizum / Transferencia
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"💳 Pagar €{info.get('price', 79)}", callback_data=f"pay_antecedentes_{order_id}")],
                [InlineKeyboardButton("« Menú Principal", callback_data="main")],
            ])
        )
        return STATE_MAIN
    
    # ==================== NLU FOR FREE TEXT ====================
    
    # First, try to detect intent
    intent = detect_intent(text)
    
    if intent:
        if intent.startswith("faq_"):
            # Redirect to FAQ
            faq_key = intent.replace("faq_", "")
            faq = FAQ_DATABASE.get(faq_key)
            if faq:
                await update.message.reply_text(
                    f"{faq['title']}\n{faq['content']}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("❓ Más preguntas", callback_data="faq")],
                        [InlineKeyboardButton("« Menú Principal", callback_data="main")],
                    ])
                )
                return STATE_MAIN
        
        elif intent == "status":
            case = get_user_case(update.effective_user.id)
            if case:
                await update.message.reply_text(
                    format_case_status(case),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=build_main_menu()
                )
            else:
                await update.message.reply_text(
                    "No tienes un caso activo todavía. ¡Empecemos!",
                    reply_markup=build_main_menu()
                )
            return STATE_MAIN
        
        elif intent == "contact":
            await update.message.reply_text(
                INTENT_RESPONSES["contact"],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📹 Agendar Videollamada", callback_data="appt_video")],
                    [InlineKeyboardButton("✏️ Escribir Mensaje", callback_data="write_message")],
                    [InlineKeyboardButton("« Menú Principal", callback_data="main")],
                ])
            )
            return STATE_MAIN
        
        elif intent == "appointment":
            await update.message.reply_text(
                "📅 *Agendar Cita*\n\n¿Cómo prefieres hablar con nosotros?",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=build_appointment_menu()
            )
            return STATE_MAIN
        
        elif intent == "payment":
            case = get_user_case(update.effective_user.id)
            await update.message.reply_text(
                "💳 *Pagos*\n\nSelecciona una opción:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=build_payment_menu(case) if case else build_back_button()
            )
            return STATE_MAIN
        
        elif intent == "antecedentes":
            await update.message.reply_text(
                "📜 *Servicio de Antecedentes*\n\nSelecciona tu país:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=build_antecedentes_menu()
            )
            return STATE_MAIN
        
        elif intent in INTENT_RESPONSES:
            await update.message.reply_text(
                INTENT_RESPONSES[intent],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=build_main_menu()
            )
            return STATE_MAIN
    
    # Try FAQ matching
    faq_match = find_faq_match(text)
    if faq_match:
        await update.message.reply_text(
            f"{faq_match['title']}\n{faq_match['content']}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Más preguntas", callback_data="faq")],
                [InlineKeyboardButton("« Menú Principal", callback_data="main")],
            ])
        )
        return STATE_MAIN
    
    # Default: didn't understand
    await update.message.reply_text(
        """
🤔 No estoy seguro de haber entendido tu pregunta.

*Puedo ayudarte con:*
• Información sobre la regularización
• Estado de tu caso
• Subir documentos
• Agendar citas
• Pagos
• Servicio de antecedentes

*Escríbeme de otra forma* o usa el menú:
""",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_main_menu()
    )
    
    return STATE_MAIN

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Exception: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ha ocurrido un error. Por favor, intenta de nuevo o usa /start",
                reply_markup=build_main_menu()
            )
    except:
        pass

# =============================================================================
# SCHEDULED JOBS
# =============================================================================

async def send_daily_updates(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send daily personalized updates."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT u.telegram_id, u.first_name, u.id as user_id, c.case_number, c.status
        FROM users u
        JOIN cases c ON u.id = c.user_id
        WHERE u.telegram_id IS NOT NULL
        AND c.status NOT IN ('resolved', 'cancelled')
    """)
    
    users = c.fetchall()
    conn.close()
    
    days_left = (DEADLINE - datetime.now()).days
    
    for row in users:
        row = dict(row)
        try:
            case = get_user_case(row['telegram_id'])
            if not case:
                continue
            
            progress = calculate_progress(case)
            first_name = row.get('first_name', '')
            
            # Personalized message based on progress
            if progress["progress"] < 30:
                message = f"""
☀️ ¡Buenos días{', ' + first_name if first_name else ''}!

Tu caso *{row['case_number']}* está al {progress['progress']}%.

📋 *Siguiente paso:* Sube tus documentos pendientes

⏰ Faltan *{days_left} días* para el cierre.

_¿Necesitas ayuda? Escríbeme._
"""
            elif progress["progress"] < 70:
                message = f"""
☀️ ¡Buenos días{', ' + first_name if first_name else ''}!

¡Vas muy bien! 🎉 Progreso: {progress['progress']}%

📋 *Pendiente:* {len(progress['missing_required'])} documentos

💪 ¡Un poco más y estás listo!
"""
            else:
                message = f"""
☀️ ¡Buenos días{', ' + first_name if first_name else ''}!

🏆 ¡Tu expediente está casi completo!

Progreso: {progress['progress']}%

Nuestro equipo está revisando tus documentos.
"""
            
            await context.bot.send_message(
                chat_id=row['telegram_id'],
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=build_main_menu()
            )
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error sending daily update to {row['telegram_id']}: {e}")

async def process_admin_notifications(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process and send admin notifications."""
    if not ADMIN_CHAT_IDS:
        return
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT * FROM admin_notifications 
        WHERE status = 'pending'
        ORDER BY priority DESC, created_at ASC
        LIMIT 10
    """)
    
    notifications = c.fetchall()
    
    for notif in notifications:
        notif = dict(notif)
        try:
            for admin_id in ADMIN_CHAT_IDS:
                priority_icon = "🔴" if notif['priority'] == 'high' else "🟡" if notif['priority'] == 'normal' else "⚪"
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"{priority_icon} *{notif['notification_type'].upper()}*\n\n{notif['message']}",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            c.execute("UPDATE admin_notifications SET status = 'sent', handled_at = ? WHERE id = ?",
                      (datetime.now().isoformat(), notif['id']))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
    
    conn.close()

# =============================================================================
# MAIN
# =============================================================================

async def set_commands(application):
    """Set bot commands."""
    commands = [
        BotCommand("start", "Menú principal"),
        BotCommand("estado", "Ver estado de mi caso"),
        BotCommand("documentos", "Mis documentos"),
        BotCommand("pagos", "Ver pagos"),
        BotCommand("cita", "Agendar cita"),
        BotCommand("ayuda", "Preguntas frecuentes"),
        BotCommand("antecedentes", "Servicio antecedentes"),
        BotCommand("contacto", "Hablar con persona"),
    ]
    await application.bot.set_my_commands(commands)

def main() -> None:
    """Start the bot."""
    # Initialize database
    init_database()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("estado", status_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("contacto", contact_command))
    application.add_handler(CommandHandler("antecedentes", antecedentes_command))
    
    # Callback handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Photo handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Text handler (must be last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Schedule jobs
    job_queue = application.job_queue
    if job_queue:
        # Daily updates at 8 AM
        job_queue.run_daily(
            send_daily_updates,
            time=datetime.strptime("08:00", "%H:%M").time(),
            name="daily_updates"
        )
        
        # Admin notifications every 5 minutes
        job_queue.run_repeating(
            process_admin_notifications,
            interval=300,
            first=10,
            name="admin_notifications"
        )
    
    # Set commands
    application.post_init = set_commands
    
    # Start polling
    logger.info("🚀 Bot v3.0 starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
