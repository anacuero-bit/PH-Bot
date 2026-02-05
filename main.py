#!/usr/bin/env python3
"""
================================================================================
PH-Bot v5.1.0 â€” Client Intake & Case Management
================================================================================
Repository: github.com/anacuero-bit/PH-Bot
Updated:    2026-02-05

CHANGELOG:
----------
v5.1.0 (2026-02-05)
  - FULL AUDIT + CONVERSION OPTIMIZATION:
  - FIXED: fq_ callbacks from eligibility screen (broken button did nothing)
  - FIXED: Progress bar now dynamic (was always 0%)
  - FIXED: 6 orphaned NLU intents now route to FAQ
  - ADDED: PDF/file upload support (not just photos)
  - ADDED: 13 document upload categories (was 7)
  - ADDED: Expanded OCR keywords (fintech, phone, transport, delivery)
  - ADDED: Debit cards, vet visits, social media etc in residency FAQ
  - ADDED: 5 new FAQ entries (no empadronamiento, travel, expired passport, arraigo, denial)
  - ADDED: Stripe payment link support (env var)
  - ADDED: Improved Phase 2 trigger message (urgency + social proof)
  - ADDED: Name collection in registration
  - ADDED: Social proof counter in main menu

v5.0.2 (2026-02-05)
  - GROK RESEARCH INTEGRATION:
  - Added vulnerability clause FAQ (no job offer needed)
  - Added expanded proof of residency FAQ (40+ doc types, 8 categories)
  - Added approval rate messaging FAQ (80-90% with caveats)
  - Added digital submission FAQ (100% online)
  - Added 2005 comparison FAQ
  - Added detailed timeline FAQ
  - Updated eligibility result screen with vulnerability + approval info
  - New NLU intents: online_submission, approval_rate, comparison_2005
  - Expanded 'work' intent to catch vulnerability-related queries
  - Intent-to-FAQ routing for direct responses

v5.0.3 (2026-02-05)
  - BUGFIXES from full audit:
  - FIXED: /reset now in entry_points (was only in fallbacks â€” didn't work mid-conversation)
  - FIXED: m_pay3 handler added (button existed but did nothing)
  - FIXED: paid3 handler + admin notification for Phase 3 payments
  - REMOVED: dead contact_lawyer/contact_help handlers (no buttons used them)
  - NOTE: ST_SERVICE_INFO kept in states dict for future use but currently unreachable

v5.0.1 (2026-02-05)
  - Restored from v4: progress bar visual in main menu
  - Restored from v4: demonyms in country data
  - Restored from v4: contact_lawyer / contact_help callbacks
  - Fixed: /reset now works (entry_points matched v4 pattern)

v5.0.0 (2026-02-05)
  - Professional lawyer tone (no slang, no "quiubo parce")
  - NLU: handles free-text messages, not just button taps
  - OCR document scanning + auto-classification
  - 5-layer document validation pipeline
  - Smart escalation (bot â†’ FAQ â†’ canned â†’ queue â†’ human)
  - Comprehensive FAQ (11 topics vs 6 in v4)
  - Correct payment structure per PAYMENT_STRATEGY.md:
        Phase 1 FREE â†’ Phase 2 â‚¬47 â†’ Phase 3 â‚¬150 â†’ Phase 4 â‚¬100
  - Country-specific antecedentes guidance
  - Message logging database
  - Admin tools: /approve2, /approve3, /reply, /stats, /broadcast

v4.0.0 (2026-02-04)
  - Country selection with flags
  - Progressive payment (wrong amounts: â‚¬9.99 â†’ â‚¬89.01 â†’ â‚¬199 â†’ â‚¬38.28)
  - FAQ carousel, /reset command
  - Carried from v3: NLU, document scanning (lost in v4 rewrite, restored in v5)

ENV VARS:
  TELEGRAM_BOT_TOKEN  (required)
  ADMIN_CHAT_IDS      comma-separated Telegram IDs
  SUPPORT_PHONE       WhatsApp number
  BIZUM_PHONE         Bizum number
  BANK_IBAN           Transfer IBAN
  ANTHROPIC_API_KEY   (optional, for AI escalation)
================================================================================
"""

import os
import re
import sqlite3
import logging
import hashlib
from io import BytesIO
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

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

# Optional: OCR
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Optional: image quality
try:
    from PIL import ImageFilter, ImageStat
    IMAGE_ANALYSIS = True
except ImportError:
    IMAGE_ANALYSIS = False

# =============================================================================
# CONFIGURATION
# =============================================================================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_CHAT_IDS", "").split(",") if x.strip()]
SUPPORT_PHONE = os.environ.get("SUPPORT_PHONE", "+34 600 000 000")
BIZUM_PHONE = os.environ.get("BIZUM_PHONE", "+34 600 000 000")
BANK_IBAN = os.environ.get("BANK_IBAN", "ES00 0000 0000 0000 0000 0000")
STRIPE_PHASE2_LINK = os.environ.get("STRIPE_PHASE2_LINK", "")  # Stripe payment link for €47
STRIPE_PHASE3_LINK = os.environ.get("STRIPE_PHASE3_LINK", "")  # Stripe payment link for €150
STRIPE_PHASE4_LINK = os.environ.get("STRIPE_PHASE4_LINK", "")  # Stripe payment link for €100

DEADLINE = datetime(2026, 6, 30, 23, 59, 59)
DB_PATH = "tuspapeles.db"
MIN_DOCS_FOR_PHASE2 = 3

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("ph-bot")

# =============================================================================
# PRICING (per PAYMENT_STRATEGY.md)
# =============================================================================

PRICING = {
    "phase1": 0,       # Free â€” build trust
    "phase2": 47,      # After 3+ docs â€” legal review
    "phase3": 150,     # Docs verified â€” processing
    "phase4": 100,     # Filing window opens
    "total_service": 297,
    "gov_fee": 38.28,
    "tie_card": 16,
}

# =============================================================================
# CONVERSATION STATES
# =============================================================================

(
    ST_WELCOME,
    ST_COUNTRY,
    ST_Q1_DATE,
    ST_Q2_TIME,
    ST_Q3_RECORD,
    ST_ELIGIBLE,
    ST_NOT_ELIGIBLE,
    ST_SERVICE_INFO,
    ST_FAQ_MENU,
    ST_FAQ_ITEM,
    ST_MAIN_MENU,
    ST_DOCS_LIST,
    ST_UPLOAD_SELECT,
    ST_UPLOAD_PHOTO,
    ST_PAY_PHASE2,
    ST_PAY_PHASE3,
    ST_CONTACT,
    ST_HUMAN_MSG,
) = range(18)

# =============================================================================
# COUNTRY DATA (no slang greetings â€” professional tone)
# =============================================================================

COUNTRIES = {
    "co": {
        "name": "Colombia", "flag": "ðŸ‡¨ðŸ‡´", "demonym": "colombiano/a",
        "antecedentes_url": "https://antecedentes.policia.gov.co",
        "antecedentes_online": True,
        "antecedentes_price": 35,
        "apostille_info": "Apostilla electrÃ³nica disponible en cancilleria.gov.co",
        "hague": True,
    },
    "ve": {
        "name": "Venezuela", "flag": "ðŸ‡»ðŸ‡ª", "demonym": "venezolano/a",
        "antecedentes_url": "https://tramites.ministeriopublico.gob.ve",
        "antecedentes_online": False,
        "antecedentes_price": 59,
        "apostille_info": "Sistema frecuentemente caÃ­do. Recomendamos gestiÃ³n profesional.",
        "hague": True,
    },
    "pe": {
        "name": "PerÃº", "flag": "ðŸ‡µðŸ‡ª", "demonym": "peruano/a",
        "antecedentes_url": "https://portal.policia.gob.pe/antecedentes_policiales/",
        "antecedentes_online": True,
        "antecedentes_price": 45,
        "apostille_info": "Apostilla en Relaciones Exteriores. Puede tardar 2-3 semanas.",
        "hague": True,
    },
    "ec": {
        "name": "Ecuador", "flag": "ðŸ‡ªðŸ‡¨", "demonym": "ecuatoriano/a",
        "antecedentes_url": "https://certificados.ministeriodelinterior.gob.ec",
        "antecedentes_online": True,
        "antecedentes_price": 35,
        "apostille_info": "Apostilla electrÃ³nica disponible.",
        "hague": True,
    },
    "hn": {
        "name": "Honduras", "flag": "ðŸ‡­ðŸ‡³", "demonym": "hondureÃ±o/a",
        "antecedentes_online": False,
        "antecedentes_price": 79,
        "apostille_info": "Requiere gestiÃ³n presencial o mediante contacto local.",
        "hague": True,
    },
    "bo": {
        "name": "Bolivia", "flag": "ðŸ‡§ðŸ‡´", "demonym": "boliviano/a",
        "antecedentes_online": False,
        "antecedentes_price": 79,
        "apostille_info": "Apostilla en CancillerÃ­a. Proceso presencial.",
        "hague": True,
    },
    "ar": {
        "name": "Argentina", "flag": "ðŸ‡¦ðŸ‡·", "demonym": "argentino/a",
        "antecedentes_url": "https://www.dnrec.jus.gov.ar",
        "antecedentes_online": True,
        "antecedentes_price": 45,
        "apostille_info": "Apostilla electrÃ³nica disponible.",
        "hague": True,
    },
    "ma": {
        "name": "Marruecos", "flag": "ðŸ‡²ðŸ‡¦", "demonym": "marroquÃ­",
        "antecedentes_online": False,
        "antecedentes_price": 79,
        "apostille_info": "Requiere legalizaciÃ³n (no Apostilla â€” no es miembro del Convenio de La Haya). LegalizaciÃ³n consular.",
        "hague": False,
    },
    "other": {
        "name": "Otro paÃ­s", "flag": "ðŸŒ", "demonym": "",
        "antecedentes_online": False,
        "antecedentes_price": 89,
        "apostille_info": "Consulte con nuestro equipo para su caso especÃ­fico.",
        "hague": False,
    },
}

# =============================================================================
# DOCUMENT TYPES + VALIDATION CONFIG
# =============================================================================

DOC_TYPES = {
    "passport": {
        "name": "Pasaporte",
        "icon": "🪪",
        "required": True,
        "ocr_keywords": ["PASAPORTE", "PASSPORT", "REPÚBLICA", "TRAVEL DOCUMENT"],
        "validity_check": "not_expired",
        "tip": "Asegúrese de que esté vigente. Si está vencido, renuévelo antes de solicitar.",
    },
    "antecedentes": {
        "name": "Antecedentes penales",
        "icon": "📜",
        "required": True,
        "ocr_keywords": ["ANTECEDENTES", "PENALES", "CRIMINAL", "RECORD", "POLICÍA"],
        "validity_check": "less_than_3_months",
        "tip": "Debe estar apostillado (o legalizado) y, si no está en español, traducido por traductor jurado.",
    },
    "empadronamiento": {
        "name": "Empadronamiento / Certificado de residencia",
        "icon": "📍",
        "required": True,
        "ocr_keywords": ["PADRÓN", "EMPADRONAMIENTO", "AYUNTAMIENTO", "CERTIFICADO", "MUNICIPAL"],
        "validity_check": "less_than_3_months",
        "tip": "Solícitelo en su ayuntamiento. Algunos permiten hacerlo online.",
    },
    "photo": {
        "name": "Fotografías tipo carnet",
        "icon": "📷",
        "required": True,
        "ocr_keywords": [],
        "validity_check": None,
        "tip": "2 fotos recientes, fondo blanco, tamaño carnet.",
    },
    "rental": {
        "name": "Contrato de alquiler / recibos de alquiler",
        "icon": "🏠",
        "required": False,
        "ocr_keywords": ["ALQUILER", "ARRENDAMIENTO", "CONTRATO", "ARRENDADOR", "INQUILINO", "RENTA MENSUAL"],
        "validity_check": "less_than_6_months",
        "tip": "Contrato de alquiler y/o recibos de pago de alquiler (transferencia, Bizum, efectivo con recibo).",
    },
    "utility_bill": {
        "name": "Facturas de suministros (luz, agua, gas, internet)",
        "icon": "💡",
        "required": False,
        "ocr_keywords": ["ENDESA", "IBERDROLA", "NATURGY", "REPSOL", "FACTURA", "SUMINISTRO",
                         "MOVISTAR", "VODAFONE", "ORANGE", "YOIGO", "MASMOVIL", "DIGI",
                         "CANAL DE ISABEL", "AGUAS DE"],
        "validity_check": "less_than_6_months",
        "tip": "Facturas a su nombre o del domicilio donde reside. Incluye telefonía móvil.",
    },
    "bank_statement": {
        "name": "Extracto bancario / tarjeta de débito",
        "icon": "🏦",
        "required": False,
        "ocr_keywords": ["EXTRACTO", "BANCO", "BANKINTER", "CAIXABANK", "SANTANDER", "BBVA", "SABADELL",
                         "REVOLUT", "N26", "WISE", "BNEXT", "OPENBANK", "ING",
                         "SALDO", "MOVIMIENTOS", "TRANSFERENCIA"],
        "validity_check": "less_than_6_months",
        "tip": "Extractos con actividad en España. Sirven bancos tradicionales Y fintechs (Revolut, N26, Wise, Bnext).",
    },
    "remittance": {
        "name": "Envíos de dinero (Western Union, Ria, etc.)",
        "icon": "💸",
        "required": False,
        "ocr_keywords": ["WESTERN UNION", "RIA", "MONEYGRAM", "REMESA", "SMALL WORLD",
                         "TRANSFERENCIA INTERNACIONAL", "ENVÍO"],
        "validity_check": "less_than_6_months",
        "tip": "Recibos de envíos de dinero al extranjero realizados desde España. Muy buena prueba de estancia.",
    },
    "medical": {
        "name": "Documentos médicos (citas, recetas, tarjeta sanitaria)",
        "icon": "🏥",
        "required": False,
        "ocr_keywords": ["TARJETA SANITARIA", "SIP", "CITA MÉDICA", "RECETA", "HOSPITAL",
                         "CENTRO DE SALUD", "URGENCIAS", "PRESCRIPCIÓN", "SERVICIO DE SALUD",
                         "VACUNACIÓN", "FARMACIA"],
        "validity_check": "less_than_6_months",
        "tip": "Citas médicas, recetas, informes de hospital, tarjeta sanitaria, vacunaciones, visitas al dentista.",
    },
    "transport": {
        "name": "Transporte (abono, billetes, Cabify/Uber)",
        "icon": "🚌",
        "required": False,
        "ocr_keywords": ["ABONO TRANSPORTE", "RENFE", "CERCANÍAS", "EMT", "TMB", "METRO",
                         "CABIFY", "UBER", "BOLT", "BICIMAD", "BICING"],
        "validity_check": "less_than_6_months",
        "tip": "Abono transporte, billetes de tren/bus, recibos de Cabify, Uber, BiciMad. Con fechas.",
    },
    "work_informal": {
        "name": "Trabajo / apps de reparto (Glovo, Uber Eats...)",
        "icon": "💼",
        "required": False,
        "ocr_keywords": ["NÓMINA", "GLOVO", "UBER EATS", "DELIVEROO", "JUST EAT",
                         "SEGURIDAD SOCIAL", "CONTRATO TRABAJO", "SALARIO"],
        "validity_check": "less_than_6_months",
        "tip": "Nóminas, contratos, capturas de apps de delivery (Glovo, Uber Eats), facturas de trabajo autónomo.",
    },
    "education": {
        "name": "Educación (matrícula, cursos, guardería)",
        "icon": "📚",
        "required": False,
        "ocr_keywords": ["MATRÍCULA", "CERTIFICADO ESCOLAR", "CURSO", "ACADEMIA",
                         "GUARDERÍA", "COLEGIO", "INSTITUTO", "UNIVERSIDAD"],
        "validity_check": "less_than_12_months",
        "tip": "Matrícula escolar (suya o de sus hijos), cursos de español, formación profesional, guardería.",
    },
    "other": {
        "name": "Otro documento",
        "icon": "🔎",
        "required": False,
        "ocr_keywords": [],
        "validity_check": None,
        "tip": "Cualquier otro documento con fecha: gym, correo postal, vet, iglesia, eventos, seguros...",
    },
}

# =============================================================================
# NLU â€” INTENT DETECTION FOR FREE-TEXT MESSAGES
# =============================================================================

INTENT_PATTERNS = {
    "greeting": [
        r"^hola\b", r"^buenos?\s*(dÃ­as?|tardes?|noches?)", r"^hey\b",
        r"^saludos?\b", r"^quÃ© tal", r"^buenas\b",
    ],
    "thanks": [
        r"\bgracias\b", r"\bgenial\b", r"\bperfecto\b", r"\bexcelente\b",
        r"^ok\b", r"^vale\b", r"\bde acuerdo\b", r"\bentendido\b",
    ],
    "goodbye": [
        r"\badiÃ³s\b", r"\badios\b", r"\bchao\b", r"\bbye\b",
        r"\bhasta luego\b", r"\bnos vemos\b",
    ],
    "help": [
        r"\bayuda\b", r"\bno entiendo\b", r"\bno sÃ©\b", r"\bcÃ³mo funciona\b",
        r"\bestoy perdid[oa]\b", r"\bexplica\b",
    ],
    "price": [
        r"\bprecio\b", r"\bcuest[ao]\b", r"\bcuÃ¡nto\b", r"\btarifa\b",
        r"\bpagar\b", r"\bcost[oe]\b", r"\bcobr", r"\bdinero\b",
    ],
    "documents": [
        r"\bdocumento", r"\bpapeles\b", r"\bpasaporte\b", r"\bempadronamiento\b",
        r"\bantecedentes\b", r"\bfactura\b", r"\bquÃ© necesito\b",
    ],
    "status": [
        r"\bestado\b", r"\bmi caso\b", r"\bcÃ³mo va\b", r"\bprogreso\b",
        r"\bavance\b", r"\bquÃ© falta\b",
    ],
    "human": [
        r"\bpersona\b", r"\bagente\b", r"\bhumano\b", r"\bllamar\b",
        r"\btelÃ©fono\b", r"\bcontacto\b", r"\babogad[oa]\b", r"\bhablar con\b",
    ],
    "work": [
        r"\btrabajar\b", r"\btrabajo\b", r"\bcontrato\b", r"\bautÃ³nom[oa]\b",
        r"\bempleo\b", r"\bempresa\b", r"\bempleador\b", r"\bpatrÃ³n\b",
        r"\boferta de trabajo\b", r"\bvulnerab",
    ],
    "family": [
        r"\bhij[oa]s?\b", r"\bmenor", r"\bfamilia\b", r"\bbebÃ©\b",
        r"\bniÃ±[oa]s?\b", r"\besposa?\b", r"\bmarido\b", r"\bpareja\b",
    ],
    "deadline": [
        r"\bplazo\b", r"\bfecha\b", r"\bcuÃ¡ndo\b", r"\btiempo\b",
        r"\bdeadline\b", r"\babril\b", r"\bjunio\b",
    ],
    "asylum": [
        r"\basilo\b", r"\brefugi", r"\bprotecciÃ³n internacional\b",
        r"\btarjeta roja\b", r"\bhoja blanca\b",
    ],
    "trust": [
        r"\bestafa\b", r"\bconfia[rn]?\b", r"\bsegur[oa]\b", r"\bfraude\b",
        r"\blegÃ­tim[oa]\b", r"\breal\b", r"\bverdad\b", r"\bfiar\b",
    ],
    "online_submission": [
        r"\bpresencial\b", r"\boficina\b", r"\btelemÃ¡tic", r"\bonline\b",
        r"\bcita previa\b", r"\bcola\b", r"\bhay que ir\b",
    ],
    "approval_rate": [
        r"\bprobabilidad\b", r"\bme van a aprobar\b", r"\brechaz",
        r"\bposibilidades\b", r"\bfunciona esto\b", r"\bquÃ© posibilidad",
    ],
    "comparison_2005": [
        r"\b2005\b", r"\banterior\b", r"\bla Ãºltima vez\b",
        r"\bproceso anterior\b",
    ],
    "no_empadronamiento": [
        r"\bno tengo empadronamiento\b", r"\bsin empadronamiento\b",
        r"\bno.*empadronad[oa]\b", r"\bno me quieren empadronar\b",
    ],
    "travel": [
        r"\bviajar\b", r"\bsalir de espa\xf1a\b", r"\bvuelo\b",
        r"\bir a mi pa\xeds\b", r"\bvolver a mi pa\xeds\b",
    ],
    "expired_passport": [
        r"\bpasaporte vencido\b", r"\bpasaporte caducado\b",
        r"\brenovar pasaporte\b", r"\bsin pasaporte\b",
    ],
    "arraigo": [
        r"\barraigo\b", r"\bya tengo expediente\b",
        r"\botra solicitud\b",
    ],
    "denial": [
        r"\bdeneg", r"\brecurso\b", r"\bsi me dicen que no\b",
        r"\bqu\xe9 pasa si no\b",
    ],

}

# =============================================================================
# FAQ DATABASE â€” Professional tone, comprehensive
# =============================================================================

FAQ = {
    "requisitos": {
        "title": "Requisitos de la regularizaciÃ³n",
        "keywords": ["requisito", "puedo", "quiÃ©n", "elegible", "condicion"],
        "text": (
            "*Requisitos principales:*\n\n"
            "1. Haber entrado a EspaÃ±a *antes del 31 de diciembre de 2025*.\n"
            "2. Acreditar una estancia continuada de *al menos 5 meses*.\n"
            "3. *No tener antecedentes penales* en EspaÃ±a ni en su paÃ­s de origen.\n\n"
            "La estancia se puede probar con documentos pÃºblicos o privados: "
            "empadronamiento, facturas, extractos bancarios, contratos, "
            "tarjeta sanitaria, recibos de envÃ­os de dinero, entre otros.\n\n"
            "Los solicitantes de protecciÃ³n internacional (asilo) tambiÃ©n pueden "
            "acogerse, siempre que la solicitud se hubiera presentado antes del 31/12/2025."
        ),
    },
    "documentos": {
        "title": "Documentos necesarios",
        "keywords": ["documento", "papeles", "necesito", "falta", "preparar"],
        "text": (
            "*DocumentaciÃ³n necesaria:*\n\n"
            "1. *Pasaporte en vigor.* Si estÃ¡ vencido, renuÃ©velo cuanto antes.\n"
            "2. *Certificado de antecedentes penales* de su paÃ­s de origen "
            "(y de cualquier paÃ­s donde haya residido en los Ãºltimos 5 aÃ±os). "
            "Debe estar apostillado o legalizado, y traducido si no estÃ¡ en espaÃ±ol.\n"
            "3. *Certificado de empadronamiento* o equivalente.\n"
            "4. *Dos fotografÃ­as* tipo carnet recientes.\n"
            "5. *Pruebas de estancia continuada:* al menos dos documentos "
            "con fechas que acrediten su presencia en EspaÃ±a "
            "(facturas, extractos bancarios, contrato de alquiler, tarjeta sanitaria, "
            "recibos de Western Union o Ria, certificado de escolarizaciÃ³n de hijosâ€¦).\n"
            "6. *Tasa administrativa:* â‚¬38,28 (se abona al gobierno al presentar).\n\n"
            "Le ayudamos a revisar y completar toda esta documentaciÃ³n."
        ),
    },
    "plazos": {
        "title": "Plazos y fechas clave",
        "keywords": ["plazo", "fecha", "cuÃ¡ndo", "tiempo", "abril", "junio", "deadline"],
        "text": (
            "*Calendario previsto:*\n\n"
            "Febrero-marzo 2026 â€” TramitaciÃ³n del Real Decreto.\n"
            "Principios de abril 2026 â€” Apertura del plazo de solicitudes.\n"
            "*30 de junio de 2026* â€” Cierre del plazo.\n\n"
            "Una vez presentada la solicitud:\n"
            "- AdmisiÃ³n a trÃ¡mite: mÃ¡ximo 15 dÃ­as.\n"
            "- Con la admisiÃ³n, se obtiene autorizaciÃ³n *provisional* para trabajar.\n"
            "- ResoluciÃ³n final: aproximadamente 3 meses.\n\n"
            "Recomendamos preparar la documentaciÃ³n *ahora* para evitar "
            "la saturaciÃ³n de los Ãºltimos dÃ­as."
        ),
    },
    "precio": {
        "title": "Nuestras tarifas",
        "keywords": ["precio", "cuesta", "cuÃ¡nto", "tarifa", "pagar", "caro", "barato", "dinero"],
        "text": (
            "*Nuestras tarifas â€” sin sorpresas:*\n\n"
            "Fase 1 Â· PreparaciÃ³n: *Gratuito*\n"
            "  VerificaciÃ³n de elegibilidad, subida de documentos, revisiÃ³n preliminar.\n\n"
            "Fase 2 Â· RevisiÃ³n legal: *â‚¬47*\n"
            "  AnÃ¡lisis completo, informe detallado, plan personalizado.\n\n"
            "Fase 3 Â· Procesamiento: *â‚¬150*\n"
            "  Expediente legal, formularios, revisiÃ³n final de abogado.\n\n"
            "Fase 4 Â· PresentaciÃ³n: *â‚¬100*\n"
            "  PresentaciÃ³n oficial, seguimiento hasta resoluciÃ³n.\n\n"
            "*Total servicio: â‚¬297*\n"
            "Tasas del gobierno (aparte): â‚¬38,28 + ~â‚¬16 (TIE).\n\n"
            "A modo de referencia, un abogado generalista cobra entre â‚¬500 y â‚¬1.000 "
            "por un servicio similar. Las gestorÃ­as, entre â‚¬300 y â‚¬600, pero sin "
            "supervisiÃ³n de abogado colegiado."
        ),
    },
    "trabajo": {
        "title": "AutorizaciÃ³n de trabajo",
        "keywords": ["trabajo", "trabajar", "contrato", "empleo", "autÃ³nom", "cuenta propia"],
        "text": (
            "*AutorizaciÃ³n de trabajo:*\n\n"
            "Desde que su solicitud sea *admitida a trÃ¡mite* (mÃ¡ximo 15 dÃ­as "
            "tras la presentaciÃ³n), obtendrÃ¡ una autorizaciÃ³n provisional para "
            "trabajar legalmente en toda EspaÃ±a.\n\n"
            "Esto incluye:\n"
            "- Trabajo por cuenta ajena en cualquier sector.\n"
            "- Trabajo por cuenta propia (autÃ³nomo).\n"
            "- Posibilidad de firmar contratos y darse de alta en la Seguridad Social.\n\n"
            "No se requiere oferta de empleo previa para solicitar la regularizaciÃ³n."
        ),
    },
    "familia": {
        "title": "Hijos menores y familia",
        "keywords": ["hijo", "hija", "menor", "familia", "niÃ±o", "bebÃ©", "esposa", "pareja"],
        "text": (
            "*RegularizaciÃ³n de menores y familia:*\n\n"
            "Los hijos e hijas menores de edad que se encuentren en EspaÃ±a "
            "pueden regularizarse *simultÃ¡neamente* con el solicitante.\n\n"
            "Ventaja importante: el permiso para menores serÃ¡ de *5 aÃ±os* "
            "(no 1 aÃ±o como el del adulto).\n\n"
            "DocumentaciÃ³n adicional para menores:\n"
            "- Pasaporte del menor.\n"
            "- Partida de nacimiento apostillada.\n"
            "- Certificado de escolarizaciÃ³n (si estÃ¡ en edad escolar).\n"
            "- Libro de familia, si lo tiene.\n\n"
            "Descuentos familiares:\n"
            "- 2.Âª persona: 18% de descuento.\n"
            "- 3.Âª persona en adelante: 25% de descuento."
        ),
    },
    "antecedentes": {
        "title": "Antecedentes penales",
        "keywords": ["antecedente", "penal", "criminal", "apostilla", "rÃ©cord", "delito"],
        "text": (
            "*Certificado de antecedentes penales:*\n\n"
            "Es obligatorio presentar un certificado *sin antecedentes* de:\n"
            "- Su paÃ­s de origen.\n"
            "- Cualquier otro paÃ­s donde haya residido en los Ãºltimos 5 aÃ±os.\n\n"
            "El documento debe estar:\n"
            "- *Apostillado* (Convenio de La Haya) o *legalizado* vÃ­a consular.\n"
            "- *Traducido al espaÃ±ol* por traductor jurado (si no estÃ¡ en espaÃ±ol).\n"
            "- Emitido con una antigÃ¼edad mÃ¡xima de 3-6 meses.\n\n"
            "Opciones:\n"
            "a) Lo gestiona usted mismo â€” le proporcionamos instrucciones detalladas.\n"
            "b) Lo gestionamos nosotros â€” entre â‚¬35 y â‚¬79 segÃºn el paÃ­s.\n\n"
            "Si su paÃ­s tiene un sistema online, puede ser rÃ¡pido. "
            "En caso contrario, le recomendamos empezar cuanto antes."
        ),
    },
    "confianza": {
        "title": "Sobre Pombo & Horowitz",
        "keywords": ["confia", "estafa", "seguro", "fraude", "real", "legÃ­tim", "fiar", "quiÃ©nes"],
        "text": (
            "*Sobre Pombo & Horowitz Abogados:*\n\n"
            "- Fundado en 1988. MÃ¡s de 35 aÃ±os de ejercicio.\n"
            "- MÃ¡s de 12.000 casos de extranjerÃ­a gestionados.\n"
            "- Abogados colegiados en el ICAM (Ilustre Colegio de Abogados de Madrid).\n"
            "- Oficina fÃ­sica: Calle Serrano, Madrid.\n"
            "- Puede verificar nuestra colegiaciÃ³n en icam.es.\n\n"
            "Diferencias con gestorÃ­as y servicios no regulados:\n"
            "- Un abogado colegiado firma y responde personalmente de su trabajo.\n"
            "- Estamos sujetos al cÃ³digo deontolÃ³gico del Colegio de Abogados.\n"
            "- Si algo sale mal, tiene a quiÃ©n reclamar.\n\n"
            "No cobramos nada hasta que usted haya comprobado nuestro trabajo."
        ),
    },
    "asilo": {
        "title": "Solicitantes de asilo / protecciÃ³n internacional",
        "keywords": ["asilo", "refugi", "protecciÃ³n internacional", "tarjeta roja", "hoja blanca"],
        "text": (
            "*Si tiene una solicitud de protecciÃ³n internacional:*\n\n"
            "Puede acogerse a la regularizaciÃ³n siempre que la solicitud "
            "de asilo se hubiera presentado *antes del 31 de diciembre de 2025*.\n\n"
            "Proceso:\n"
            "- Al solicitar la regularizaciÃ³n, su expediente de asilo queda *suspendido* "
            "(no cerrado definitivamente).\n"
            "- Si la regularizaciÃ³n se resuelve favorablemente, el asilo se archiva.\n"
            "- Si se deniega, su solicitud de asilo se reactiva.\n\n"
            "Es importante valorar las ventajas: la regularizaciÃ³n ofrece "
            "autorizaciÃ³n de trabajo inmediata (con la admisiÃ³n a trÃ¡mite), "
            "algo que la vÃ­a de asilo no siempre proporciona con la misma rapidez."
        ),
    },
    "despues": {
        "title": "DespuÃ©s de la regularizaciÃ³n",
        "keywords": ["despuÃ©s", "luego", "siguiente", "renovar", "nacionalidad", "permanente"],
        "text": (
            "*DespuÃ©s de obtener la autorizaciÃ³n:*\n\n"
            "1. RecibirÃ¡ un permiso de residencia y trabajo de *1 aÃ±o*.\n"
            "2. DeberÃ¡ solicitar la *TIE* (Tarjeta de Identidad de Extranjero).\n"
            "3. Al vencer el aÃ±o, deberÃ¡ renovar por la vÃ­a ordinaria "
            "(arraigo social, laboral, familiar, etc.).\n\n"
            "Camino hacia la nacionalidad:\n"
            "- Ciudadanos iberoamericanos: 2 aÃ±os de residencia legal.\n"
            "- Resto de nacionalidades: 10 aÃ±os.\n"
            "- El tiempo en situaciÃ³n irregular *no cuenta*.\n"
            "- Esta regularizaciÃ³n inicia el cÃ³mputo.\n\n"
            "Le acompaÃ±amos tambiÃ©n en los pasos posteriores."
        ),
    },
    "caro": {
        "title": "Comparativa de precios",
        "keywords": ["caro", "barato", "much", "alcanza", "econÃ³mic"],
        "text": (
            "*Entendemos que es una inversiÃ³n importante.*\n\n"
            "Comparativa de mercado:\n\n"
            "GestorÃ­as tradicionales: â‚¬300-600\n"
            "  Sin abogados, sin garantÃ­as, pago por adelantado.\n\n"
            "Abogados generalistas: â‚¬500-1.000\n"
            "  Sin especializaciÃ³n en extranjerÃ­a.\n\n"
            "Pombo & Horowitz: â‚¬297 total\n"
            "  Abogados colegiados especializados.\n"
            "  38 aÃ±os de experiencia.\n"
            "  Pago progresivo (no todo de golpe).\n"
            "  Primera fase completamente gratuita.\n\n"
            "AdemÃ¡s, un error en la solicitud puede significar la denegaciÃ³n "
            "y la pÃ©rdida de la oportunidad. El coste de no hacerlo bien "
            "es mucho mayor que el de hacerlo con profesionales."
        ),
    },
    # === GROK RESEARCH ADDITIONS (2026-02-05) ===
    "vulnerabilidad": {
        "title": "No necesitas contrato de trabajo",
        "keywords": ["contrato", "oferta", "empleador", "vulnerable", "vulnerabilidad",
                     "patron", "sin empleo", "trabajo necesito", "me piden contrato"],
        "text": (
            "*No necesitas oferta de trabajo.*\n\n"
            "A diferencia del proceso de 2005, este decreto presume "
            "*vulnerabilidad* por estar en situaciÃ³n irregular.\n\n"
            "Esto significa:\n"
            "- NO necesita un contrato de trabajo.\n"
            "- NO necesita un empleador que le patrocine.\n"
            "- NO necesita demostrar ingresos mÃ­nimos.\n\n"
            "El decreto reconoce que estar sin papeles ya es una situaciÃ³n "
            "de vulnerabilidad. Es la diferencia mÃ¡s grande con procesos anteriores.\n\n"
            "Solo necesita demostrar:\n"
            "1. Que llegÃ³ antes del 31/12/2025.\n"
            "2. Que lleva 5+ meses en EspaÃ±a.\n"
            "3. Que no tiene antecedentes penales graves."
        ),
    },
    "pruebas_residencia": {
        "title": "Documentos que sirven como prueba",
        "keywords": ["prueba", "demostrar", "no tengo empadronamiento", "quÃ© sirve",
                     "prueba de residencia", "cÃ³mo demuestro", "quÃ© documentos sirven"],
        "text": (
            "*El decreto acepta CUALQUIER documento pÃºblico o privado.*\n\n"
            "No necesita empadronamiento obligatoriamente. Sirven combinaciones de:\n\n"
            "ðŸ  Vivienda: facturas de luz/agua/gas, contrato de alquiler.\n"
            "ðŸ¥ MÃ©dicos: citas mÃ©dicas, recetas, tarjeta sanitaria (SIP), vacunaciones.\n"
            "ðŸ¦ Bancarios: extractos bancarios, recibos de Western Union o Ria.\n"
            "ðŸšŒ Transporte: abono transporte, billetes de tren/bus, recibos de Cabify.\n"
            "ðŸ“š EducaciÃ³n: matrÃ­cula escolar (suya o de sus hijos), cursos de espaÃ±ol.\n"
            "ðŸ’¼ Trabajo: nÃ³minas, registros de Glovo/Uber Eats, facturas autÃ³nomo.\n"
            "ðŸ“± Vida diaria: facturas de mÃ³vil, abono de gimnasio, correo postal.\n"
            "â›ª Comunidad: iglesia/mezquita, voluntariado en ONGs.\n\n"
            "Combinar 3-5 documentos de diferentes categorÃ­as es lo ideal. "
            "MÃ¡s documentos = menos riesgo de rechazo."
        ),
    },
    "aprobacion": {
        "title": "Probabilidades de aprobaciÃ³n",
        "keywords": ["probabilidad", "aprobar", "rechazar", "funciona", "posibilidades",
                     "me van a aprobar", "van a rechazar", "quÃ© posibilidades"],
        "text": (
            "*Basado en el proceso de 2005 (el Ãºltimo en EspaÃ±a):*\n\n"
            "- Se aprobaron entre el 80-90% de las solicitudes.\n"
            "- El gobierno ha diseÃ±ado este decreto para ser flexible.\n"
            "- Los expertos esperan un umbral bajo de exigencia.\n\n"
            "No podemos garantizar la aprobaciÃ³n de ningÃºn caso individual. "
            "Pero si cumple los requisitos bÃ¡sicos y presenta documentaciÃ³n "
            "razonable, las probabilidades estÃ¡n muy a su favor.\n\n"
            "El gobierno quiere regularizar â€” ha diseÃ±ado el proceso para "
            "aprobar, no para rechazar. Nuestro trabajo es asegurarnos de que "
            "su solicitud sea lo mÃ¡s fuerte posible."
        ),
    },
    "presentacion_online": {
        "title": "La presentaciÃ³n es 100% online",
        "keywords": ["presencial", "oficina", "telemÃ¡tico", "online", "internet",
                     "hay que ir", "cita previa", "cÃ³mo se presenta"],
        "text": (
            "*Las solicitudes se presentan de forma telemÃ¡tica.*\n\n"
            "No necesita ir a ninguna oficina:\n"
            "- No necesita cita previa.\n"
            "- No necesita hacer cola.\n"
            "- AutorizaciÃ³n provisional de trabajo inmediata al presentar.\n\n"
            "Nosotros nos encargamos de:\n"
            "- Preparar toda la documentaciÃ³n.\n"
            "- Revisarla legalmente.\n"
            "- Presentarla por usted de forma digital.\n"
            "- Dar seguimiento hasta la resoluciÃ³n."
        ),
    },
    "diferencia_2005": {
        "title": "Diferencias con el proceso de 2005",
        "keywords": ["2005", "anterior", "diferencia", "la Ãºltima vez", "proceso anterior"],
        "text": (
            "*Diferencias con el proceso de 2005:*\n\n"
            "2005: Necesitaba contrato de trabajo.\n"
            "2026: NO necesita contrato. âœ…\n\n"
            "2005: Solo trabajadores.\n"
            "2026: Incluye vulnerabilidad. âœ…\n\n"
            "2005: Presencial.\n"
            "2026: 100% online. âœ…\n\n"
            "2005: MÃ¡s documentaciÃ³n exigida.\n"
            "2026: MÃ¡s flexible en pruebas. âœ…\n\n"
            "2005: 80-90% aprobaciÃ³n.\n"
            "2026: Expectativa similar o mejor. âœ…\n\n"
            "La diferencia mÃ¡s importante: en 2005 necesitaba un empleador. "
            "En 2026, NO."
        ),
    },
    "plazos_detalle": {
        "title": "Fechas clave detalladas",
        "keywords": ["plazo detalle", "calendario", "cuÃ¡nto tarda", "resoluciÃ³n",
                     "admisiÃ³n", "provisional"],
        "text": (
            "*Calendario completo:*\n\n"
            "AprobaciÃ³n del decreto: 27 de enero de 2026. âœ…\n"
            "Plazo de solicitud: 1 de abril â€” 30 de junio de 2026.\n"
            "DuraciÃ³n: 3 meses exactos, sin prÃ³rroga confirmada.\n\n"
            "Tras presentar la solicitud:\n"
            "- AdmisiÃ³n inicial: mÃ¡ximo 15 dÃ­as.\n"
            "- AutorizaciÃ³n provisional de trabajo: inmediata.\n"
            "- ResoluciÃ³n final: mÃ¡ximo 3 meses.\n\n"
            "RecomendaciÃ³n: no espere al Ãºltimo momento. Prepare sus documentos "
            "AHORA para presentar en abril. Los primeros en presentar = "
            "primeros en recibir respuesta."
        ),
    },
    # === v5.1.0 ADDITIONS ===
    "sin_empadronamiento": {
        "title": "No tengo empadronamiento",
        "keywords": ["no tengo empadronamiento", "sin empadronamiento", "no estoy empadronado",
                     "no me quieren empadronar", "empadronamiento imposible"],
        "text": (
            "*¿No tiene empadronamiento? No se preocupe.*\n\n"
            "El empadronamiento es la prueba más fuerte, pero *NO es obligatorio*. "
            "El decreto acepta cualquier combinación de documentos.\n\n"
            "Alternativas igual de válidas:\n"
            "- Contrato o recibos de alquiler\n"
            "- Facturas de luz, agua, gas o internet\n"
            "- Extractos bancarios con actividad en España\n"
            "- Tarjetas Revolut, N26, Wise con transacciones locales\n"
            "- Recibos de Western Union o Ria\n"
            "- Citas médicas o tarjeta sanitaria\n"
            "- Abono transporte con cargas\n"
            "- Registros de Glovo, Uber Eats, Deliveroo\n\n"
            "Con 3-5 documentos de diferentes categorías tiene opciones sólidas. "
            "Muchas personas han conseguido el arraigo sin empadronamiento.\n\n"
            "¿Quiere que le ayudemos a identificar qué documentos puede tener?"
        ),
    },
    "viajar_pendiente": {
        "title": "¿Puedo viajar con la solicitud pendiente?",
        "keywords": ["viajar", "salir de españa", "vuelo", "ir a mi país", "vacaciones"],
        "text": (
            "*Viajar durante el proceso:*\n\n"
            "⚠️ *Antes de presentar la solicitud:* puede viajar dentro de España "
            "sin problema. Salir de España es arriesgado — podría tener "
            "dificultades para regresar.\n\n"
            "✅ *Después de la admisión a trámite:* recibirá una autorización "
            "provisional. Consulte con su abogado antes de viajar al extranjero "
            "durante este período.\n\n"
            "Recomendación: no viaje fuera de España hasta tener la resolución favorable."
        ),
    },
    "pasaporte_vencido": {
        "title": "¿Qué hago si mi pasaporte está vencido?",
        "keywords": ["pasaporte vencido", "pasaporte caducado", "renovar pasaporte",
                     "sin pasaporte", "pasaporte expirado"],
        "text": (
            "*Pasaporte vencido:*\n\n"
            "Necesita un pasaporte *en vigor* para la solicitud. Si está vencido:\n\n"
            "1. Contacte con el consulado de su país en España para renovarlo.\n"
            "2. Pida cita lo antes posible — los consulados pueden saturarse.\n"
            "3. Mientras tanto, puede ir preparando el resto de documentación.\n\n"
            "El plazo de solicitud no abre hasta abril. Tiene tiempo, pero "
            "no lo deje para el último momento.\n\n"
            "¿Necesita datos de contacto de su consulado?"
        ),
    },
    "arraigo_en_curso": {
        "title": "Ya tengo un arraigo en curso",
        "keywords": ["arraigo", "arraigo social", "arraigo laboral", "ya tengo expediente",
                     "otra solicitud", "en trámite"],
        "text": (
            "*Si ya tiene un arraigo en curso:*\n\n"
            "Puede acogerse a la regularización extraordinaria aunque tenga "
            "otra solicitud pendiente. Ventajas:\n\n"
            "- La regularización es más rápida (resolución en ~3 meses).\n"
            "- NO necesita contrato de trabajo.\n"
            "- Autorización provisional de trabajo inmediata.\n\n"
            "Su solicitud de arraigo quedaría suspendida (no cerrada). "
            "Si la regularización se aprueba, el arraigo se archiva. "
            "Si se deniega, el arraigo se reactiva.\n\n"
            "Le recomendamos valorar ambas vías con un abogado."
        ),
    },
    "denegacion": {
        "title": "¿Qué pasa si me deniegan?",
        "keywords": ["denegar", "denegación", "rechazo", "recurso", "si me dicen que no",
                     "qué pasa si no"],
        "text": (
            "*En caso de denegación:*\n\n"
            "1. Tiene derecho a *recurso* (incluido en nuestro servicio).\n"
            "2. La denegación NO implica expulsión automática.\n"
            "3. Puede seguir optando a otras vías (arraigo social, laboral, etc.).\n\n"
            "Basado en 2005, el 80-90% de solicitudes fueron aprobadas. "
            "Las denegaciones suelen ser por:\n"
            "- Antecedentes penales no declarados\n"
            "- Documentación insuficiente (evitable con buena preparación)\n"
            "- Entrada posterior al 31/12/2025\n\n"
            "Nuestro trabajo es minimizar el riesgo de rechazo. "
            "Y si ocurre, el recurso está incluido."
        ),
    },
}

# =============================================================================
# DATABASE
# =============================================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        first_name TEXT,
        full_name TEXT,
        phone TEXT,
        country_code TEXT,
        eligible INTEGER DEFAULT 0,
        current_phase INTEGER DEFAULT 1,
        phase2_paid INTEGER DEFAULT 0,
        phase3_paid INTEGER DEFAULT 0,
        phase4_paid INTEGER DEFAULT 0,
        has_criminal_record INTEGER DEFAULT 0,
        preliminary_review_sent INTEGER DEFAULT 0,
        docs_verified INTEGER DEFAULT 0,
        state TEXT DEFAULT 'new',
        escalation_queue TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        case_number TEXT UNIQUE,
        status TEXT DEFAULT 'onboarding',
        progress INTEGER DEFAULT 0,
        assigned_lawyer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        doc_type TEXT,
        file_id TEXT,
        ocr_text TEXT,
        detected_type TEXT,
        validation_score INTEGER DEFAULT 0,
        validation_notes TEXT,
        status TEXT DEFAULT 'pending',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        direction TEXT,
        content TEXT,
        intent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    conn.commit()
    conn.close()


def get_user(tid: int) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (tid,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(tid: int, first_name: str) -> Dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (telegram_id, first_name) VALUES (?, ?)", (tid, first_name))
    conn.commit()
    conn.close()
    return get_user(tid)


def update_user(tid: int, **kw):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fields = ", ".join(f"{k} = ?" for k in kw)
    vals = list(kw.values()) + [tid]
    c.execute(f"UPDATE users SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?", vals)
    conn.commit()
    conn.close()


def delete_user(tid: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE telegram_id = ?", (tid,))
    row = c.fetchone()
    if row:
        uid = row[0]
        c.execute("DELETE FROM documents WHERE user_id = ?", (uid,))
        c.execute("DELETE FROM cases WHERE user_id = ?", (uid,))
        c.execute("DELETE FROM messages WHERE user_id = ?", (uid,))
        c.execute("DELETE FROM users WHERE id = ?", (uid,))
    conn.commit()
    conn.close()


def get_doc_count(tid: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM documents d JOIN users u ON d.user_id=u.id WHERE u.telegram_id=?", (tid,))
    n = c.fetchone()[0]
    conn.close()
    return n


def get_user_docs(tid: int) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT d.* FROM documents d JOIN users u ON d.user_id=u.id WHERE u.telegram_id=? ORDER BY d.uploaded_at DESC", (tid,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_document(tid: int, doc_type: str, file_id: str, ocr_text: str = "", detected_type: str = "", score: int = 0, notes: str = ""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO documents (user_id, doc_type, file_id, ocr_text, detected_type, validation_score, validation_notes)
        SELECT id, ?, ?, ?, ?, ?, ? FROM users WHERE telegram_id = ?""",
        (doc_type, file_id, ocr_text, detected_type, score, notes, tid))
    conn.commit()
    conn.close()


def save_message(tid: int, direction: str, content: str, intent: str = ""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO messages (user_id, direction, content, intent)
        SELECT id, ?, ?, ? FROM users WHERE telegram_id = ?""",
        (direction, content[:500], intent, tid))
    conn.commit()
    conn.close()


def get_or_create_case(tid: int) -> Dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT c.* FROM cases c JOIN users u ON c.user_id=u.id WHERE u.telegram_id=?", (tid,))
    case = c.fetchone()
    if not case:
        import random
        cn = f"PH-2026-{random.randint(1000, 9999)}"
        c.execute("INSERT INTO cases (user_id, case_number) SELECT id, ? FROM users WHERE telegram_id=?", (cn, tid))
        conn.commit()
        c.execute("SELECT * FROM cases WHERE case_number=?", (cn,))
        case = c.fetchone()
    conn.close()
    return dict(case)


# =============================================================================
# NLU ENGINE
# =============================================================================

def detect_intent(text: str) -> Optional[str]:
    """Detect the user's intent from free text."""
    t = text.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, t):
                return intent
    return None


def find_faq_match(text: str) -> Optional[Dict]:
    """Find the best FAQ entry for the user's message."""
    t = text.lower()
    best, best_score = None, 0
    for key, faq in FAQ.items():
        score = 0
        for kw in faq["keywords"]:
            if kw in t:
                score += len(kw)
        if score > best_score:
            best_score = score
            best = faq
    return best if best_score >= 4 else None


# =============================================================================
# DOCUMENT PROCESSING
# =============================================================================

def check_image_quality(image) -> Tuple[bool, str]:
    """Layer 1: Basic image quality check."""
    w, h = image.size
    if w < 600 or h < 400:
        return False, "La imagen es demasiado pequeÃ±a. AcÃ©rquese mÃ¡s al documento."
    if w * h < 500_000:
        return False, "La resoluciÃ³n es muy baja. Tome la foto con mejor iluminaciÃ³n y mÃ¡s cerca."
    return True, "ok"


def classify_document_ocr(text: str) -> str:
    """Layer 2: Classify document from OCR text."""
    upper = text.upper()
    for dtype, config in DOC_TYPES.items():
        if config["ocr_keywords"]:
            matches = sum(1 for kw in config["ocr_keywords"] if kw in upper)
            if matches >= 1:
                return dtype
    return "other"


def extract_dates(text: str) -> List[str]:
    """Extract dates from OCR text."""
    return re.findall(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)


def extract_passport_number(text: str) -> Optional[str]:
    """Extract passport number."""
    m = re.search(r'\b[A-Z]{1,3}\d{5,9}\b', text.upper())
    return m.group() if m else None


async def process_document(photo_file, expected_type: str) -> Dict:
    """Full document processing pipeline."""
    result = {
        "success": False,
        "detected_type": "other",
        "ocr_text": "",
        "score": 0,
        "notes": [],
    }

    if not OCR_AVAILABLE:
        result["success"] = True
        result["score"] = 50
        result["notes"].append("Documento guardado. SerÃ¡ revisado manualmente.")
        return result

    try:
        photo_bytes = await photo_file.download_as_bytearray()
        image = Image.open(BytesIO(photo_bytes))

        # Layer 1: Image quality
        ok, msg = check_image_quality(image)
        if not ok:
            result["notes"].append(msg)
            result["score"] = 10
            return result

        result["score"] += 20  # Image quality passed

        # Layer 2: OCR + classification
        text = pytesseract.image_to_string(image, lang="spa+eng")
        result["ocr_text"] = text[:2000]
        detected = classify_document_ocr(text)
        result["detected_type"] = detected

        if detected != "other":
            result["score"] += 20  # Document classified

        # Layer 3: Type match
        if detected == expected_type or expected_type == "other":
            result["score"] += 20
        else:
            result["notes"].append(
                f"EsperÃ¡bamos Â«{DOC_TYPES.get(expected_type, {}).get('name', expected_type)}Â» "
                f"pero parece ser Â«{DOC_TYPES.get(detected, {}).get('name', detected)}Â»."
            )

        # Layer 4: Data extraction
        dates = extract_dates(text)
        if dates:
            result["score"] += 10
        passport_num = extract_passport_number(text)
        if passport_num:
            result["score"] += 10

        result["success"] = True

    except Exception as e:
        logger.error(f"Document processing error: {e}")
        result["success"] = True
        result["score"] = 40
        result["notes"].append("No pudimos analizar el documento automÃ¡ticamente. SerÃ¡ revisado por nuestro equipo.")

    return result


# =============================================================================
# HELPERS
# =============================================================================

def days_left() -> int:
    return max(0, (DEADLINE - datetime.now()).days)


def phase_name(user: Dict) -> str:
    if user.get("phase4_paid"): return "Fase 4 â€” PresentaciÃ³n"
    if user.get("phase3_paid"): return "Fase 3 â€” Procesamiento"
    if user.get("phase2_paid"): return "Fase 2 â€” RevisiÃ³n legal"
    return "Fase 1 â€” PreparaciÃ³n (gratuita)"


def phase_status(user: Dict, doc_count: int) -> str:
    if user.get("phase2_paid") and not user.get("phase3_paid"):
        return "Su expediente estÃ¡ siendo analizado por nuestro equipo legal."
    if not user.get("phase2_paid") and doc_count >= MIN_DOCS_FOR_PHASE2:
        return "Ya puede desbloquear la revisiÃ³n legal completa."
    remaining = max(0, MIN_DOCS_FOR_PHASE2 - doc_count)
    if remaining > 0:
        return f"Suba {remaining} documento(s) mÃ¡s para acceder a la revisiÃ³n legal."
    return ""


def country_kb() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for code, d in COUNTRIES.items():
        row.append(InlineKeyboardButton(f"{d['flag']} {d['name']}", callback_data=f"c_{code}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def doc_type_kb() -> InlineKeyboardMarkup:
    buttons = []
    for code, d in DOC_TYPES.items():
        buttons.append([InlineKeyboardButton(f"{d['icon']} {d['name']}", callback_data=f"dt_{code}")])
    buttons.append([InlineKeyboardButton("â† Volver al menÃº", callback_data="back")])
    return InlineKeyboardMarkup(buttons)


def main_menu_kb(user: Dict) -> InlineKeyboardMarkup:
    dc = get_doc_count(user["telegram_id"])
    btns = [
        [InlineKeyboardButton(f"ðŸ“„ Mis documentos ({dc})", callback_data="m_docs")],
        [InlineKeyboardButton("ðŸ“¤ Subir documento", callback_data="m_upload")],
    ]
    if dc >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        btns.append([InlineKeyboardButton("ðŸ”“ RevisiÃ³n legal â€” â‚¬47", callback_data="m_pay2")])
    elif user.get("phase2_paid") and not user.get("phase3_paid") and user.get("docs_verified"):
        btns.append([InlineKeyboardButton("ðŸ”“ Procesamiento â€” â‚¬150", callback_data="m_pay3")])
    btns += [
        [InlineKeyboardButton("ðŸ’° Costos y pagos", callback_data="m_price")],
        [InlineKeyboardButton("â“ Preguntas frecuentes", callback_data="m_faq")],
        [InlineKeyboardButton("ðŸ“ž Hablar con nuestro equipo", callback_data="m_contact")],
    ]
    return InlineKeyboardMarkup(btns)


def faq_menu_kb() -> InlineKeyboardMarkup:
    btns = []
    for key, faq in FAQ.items():
        btns.append([InlineKeyboardButton(faq["title"], callback_data=f"fq_{key}")])
    btns.append([InlineKeyboardButton("â† Volver al menÃº", callback_data="back")])
    return InlineKeyboardMarkup(btns)


async def notify_admins(context, msg: str):
    for aid in ADMIN_IDS:
        try:
            await context.bot.send_message(aid, msg, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass


# =============================================================================
# PAYMENT HELPERS
# =============================================================================

def _payment_buttons(paid_callback: str, stripe_link: str = "") -> InlineKeyboardMarkup:
    """Build payment buttons with optional Stripe link."""
    btns = []
    if stripe_link:
        btns.append([InlineKeyboardButton("💳 Pagar con tarjeta", url=stripe_link)])
    btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
    btns.append([InlineKeyboardButton("Ya he realizado el pago", callback_data=paid_callback)])
    btns.append([InlineKeyboardButton("Tengo dudas", callback_data="m_contact")])
    btns.append([InlineKeyboardButton("← Volver", callback_data="back")])
    return InlineKeyboardMarkup(btns)


def _user_doc_summary(tid: int) -> str:
    """Build a summary of user's uploaded docs for conversion messaging."""
    docs = get_user_docs(tid)
    if not docs:
        return ""
    lines = []
    for doc in docs[:6]:
        info = DOC_TYPES.get(doc["doc_type"], DOC_TYPES["other"])
        lines.append(f"✅ {info['name']}")
    return "\n".join(lines)


# =============================================================================
# HANDLERS
# =============================================================================

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = get_user(update.effective_user.id)
    if user and user.get("eligible"):
        return await show_main_menu(update, ctx)

    create_user(update.effective_user.id, update.effective_user.first_name or "Usuario")

    await update.message.reply_text(
        "Bienvenido/a al servicio de regularizaciÃ³n de *Pombo & Horowitz Abogados*.\n\n"
        "Le guiaremos paso a paso en el proceso de regularizaciÃ³n extraordinaria 2026.\n\n"
        "Todo lo que haga en esta primera fase es *gratuito*: verificar su elegibilidad, "
        "subir documentos y recibir una revisiÃ³n preliminar. No le pediremos ningÃºn pago "
        "hasta que haya comprobado nuestro trabajo.\n\n"
        "Para empezar, indÃ­quenos su paÃ­s de origen:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=country_kb(),
    )
    return ST_COUNTRY


async def cmd_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    delete_user(update.effective_user.id)
    await update.message.reply_text(
        "Su cuenta ha sido reiniciada.\nEscriba /start para comenzar de nuevo."
    )
    return ConversationHandler.END


async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    return await show_main_menu(update, ctx)


# --- Country selection ---

async def handle_country(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    code = q.data.replace("c_", "")
    country = COUNTRIES.get(code, COUNTRIES["other"])
    update_user(update.effective_user.id, country_code=code)

    await q.edit_message_text(
        f"Gracias. Hemos registrado su nacionalidad: {country['flag']} {country['name']}.\n\n"
        "A continuaciÃ³n, necesitamos hacerle *3 preguntas breves* para verificar "
        "si cumple los requisitos bÃ¡sicos de la regularizaciÃ³n.\n\n"
        "Sus respuestas son estrictamente confidenciales.",
        parse_mode=ParseMode.MARKDOWN,
    )

    await q.message.reply_text(
        "*Pregunta 1 de 3*\n\n"
        "Â¿Se encontraba usted en EspaÃ±a *antes del 31 de diciembre de 2025*?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("SÃ­, lleguÃ© antes de esa fecha", callback_data="d_yes")],
            [InlineKeyboardButton("No, lleguÃ© despuÃ©s", callback_data="d_no")],
            [InlineKeyboardButton("No estoy seguro/a", callback_data="d_unsure")],
        ]),
    )
    return ST_Q1_DATE


# --- Eligibility questions ---

async def handle_q1(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()

    if q.data == "d_no":
        await q.edit_message_text(
            "Lamentablemente, la regularizaciÃ³n extraordinaria requiere haber estado "
            "en EspaÃ±a *antes del 31 de diciembre de 2025*.\n\n"
            "Existen otras vÃ­as (arraigo social, laboral, familiar) que podrÃ­an aplicar "
            "en su caso. Si lo desea, un abogado puede valorar su situaciÃ³n.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Consultar con un abogado", callback_data="m_contact")],
                [InlineKeyboardButton("Volver al inicio", callback_data="restart")],
            ]),
        )
        return ST_NOT_ELIGIBLE

    if q.data == "d_unsure":
        await q.edit_message_text(
            "No se preocupe. Â¿Dispone de algÃºn documento de finales de 2025 o anterior?\n\n"
            "Por ejemplo: sello de entrada en el pasaporte, billete de aviÃ³n, "
            "empadronamiento, contrato de alquiler, factura, recibo de envÃ­o de dineroâ€¦",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("SÃ­, tengo algÃºn documento", callback_data="d_yes")],
                [InlineKeyboardButton("No tengo ninguno", callback_data="d_no")],
            ]),
        )
        return ST_Q1_DATE

    # d_yes
    await q.edit_message_text(
        "*Pregunta 2 de 3*\n\n"
        "Â¿Lleva al menos *5 meses* viviendo en EspaÃ±a de forma continuada?\n\n"
        "(Viajes cortos al extranjero no interrumpen la continuidad.)",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("SÃ­, mÃ¡s de 5 meses", callback_data="t_yes")],
            [InlineKeyboardButton("Casi, me faltan unas semanas", callback_data="t_almost")],
            [InlineKeyboardButton("No, menos de 5 meses", callback_data="t_no")],
        ]),
    )
    return ST_Q2_TIME


async def handle_q2(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()

    if q.data == "t_no":
        await q.edit_message_text(
            "Se requieren al menos 5 meses de estancia continuada. "
            "El plazo de solicitudes abre en abril de 2026. "
            "Si para entonces ya cumple el requisito, podrÃ­a acogerse.\n\n"
            "Â¿Desea que le avisemos cuando se acerque la fecha?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("SÃ­, avÃ­senme", callback_data="notify")],
                [InlineKeyboardButton("Volver al inicio", callback_data="restart")],
            ]),
        )
        return ST_NOT_ELIGIBLE

    if q.data == "t_almost":
        await q.edit_message_text(
            "El plazo no abre hasta abril de 2026. Si para entonces ya cumple "
            "los 5 meses, perfecto. Puede ir preparando la documentaciÃ³n mientras tanto.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Continuar", callback_data="t_yes")],
            ]),
        )
        return ST_Q2_TIME

    # t_yes
    await q.edit_message_text(
        "*Pregunta 3 de 3*\n\n"
        "Â¿Tiene antecedentes penales en EspaÃ±a o en su paÃ­s de origen?\n\n"
        "Esta informaciÃ³n es estrictamente confidencial.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("No, sin antecedentes", callback_data="r_clean")],
            [InlineKeyboardButton("SÃ­, tengo antecedentes", callback_data="r_yes")],
            [InlineKeyboardButton("No estoy seguro/a", callback_data="r_unsure")],
        ]),
    )
    return ST_Q3_RECORD


async def handle_q3(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    user = get_user(update.effective_user.id)
    name = user.get("first_name", "")

    if q.data == "r_yes":
        update_user(update.effective_user.id, has_criminal_record=1)
        await q.edit_message_text(
            "Tener antecedentes no supone automÃ¡ticamente una exclusiÃ³n. "
            "Depende del tipo de delito y las circunstancias.\n\n"
            "Le recomendamos que un abogado valore su caso concreto.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Consultar con un abogado", callback_data="m_contact")],
                [InlineKeyboardButton("Volver al inicio", callback_data="restart")],
            ]),
        )
        return ST_NOT_ELIGIBLE

    if q.data == "r_unsure":
        await q.edit_message_text(
            "Los antecedentes penales se refieren a condenas firmes por delitos "
            "(robos, agresiones, trÃ¡fico de drogas, etc.).\n\n"
            "Las multas de trÃ¡fico, faltas leves o denuncias archivadas *no* cuentan.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("No tengo condenas", callback_data="r_clean")],
                [InlineKeyboardButton("Tengo alguna condena", callback_data="r_yes")],
            ]),
        )
        return ST_Q3_RECORD

    # r_clean â€” ELIGIBLE
    update_user(update.effective_user.id, eligible=1, has_criminal_record=0)
    case = get_or_create_case(update.effective_user.id)

    await q.edit_message_text(
        f"*{name}, cumple los requisitos bÃ¡sicos para la regularizaciÃ³n.*\n\n"
        f"Le hemos asignado el nÃºmero de expediente *{case['case_number']}*.\n\n"
        "ðŸ’¡ *Â¿SabÃ­a que?* Este decreto NO requiere contrato de trabajo. "
        "Se presume vulnerabilidad por estar en situaciÃ³n irregular.\n\n"
        "ðŸ“Š En el proceso de 2005, se aprobaron el 80-90% de solicitudes. "
        "Este decreto es aÃºn mÃ¡s flexible.\n\n"
        f"ðŸ“… Plazo: 1 abril â€” 30 junio 2026 ({days_left()} dÃ­as).\n"
        "ðŸ’» PresentaciÃ³n: 100% online.\n\n"
        "El siguiente paso es preparar su documentaciÃ³n. "
        "Puede empezar ahora mismo â€” es completamente gratuito.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ðŸ“„ Ver quÃ© documentos necesito", callback_data="fq_pruebas_residencia")],
            [InlineKeyboardButton("ðŸ’° Ver precios del servicio", callback_data="m_price")],
            [InlineKeyboardButton("ðŸ“¤ Empezar a subir documentos", callback_data="m_upload")],
            [InlineKeyboardButton("â“ Tengo mÃ¡s preguntas", callback_data="m_faq")],
        ]),
    )
    return ST_ELIGIBLE


# --- Main menu ---

async def show_main_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = get_user(update.effective_user.id)
    if not user:
        user = create_user(update.effective_user.id, update.effective_user.first_name or "Usuario")

    name = user.get("full_name") or user.get("first_name", "Usuario")
    case = get_or_create_case(update.effective_user.id)
    dc = get_doc_count(update.effective_user.id)

    # Dynamic progress bar
    dc_temp = get_doc_count(update.effective_user.id)
    if user.get("phase4_paid"):
        progress = 95
    elif user.get("phase3_paid"):
        progress = 85
    elif user.get("phase2_paid"):
        progress = min(75, 65 + dc_temp)
    elif dc_temp >= MIN_DOCS_FOR_PHASE2:
        progress = 50 + min(15, dc_temp * 2)
    elif dc_temp > 0:
        progress = 15 + (dc_temp * 10)
    else:
        progress = 10
    bar = "â–ˆ" * (progress // 10) + "â–‘" * (10 - progress // 10)

    msg = (
        f"*{name}* â€” Expediente {case['case_number']}\n"
        f"Fase actual: {phase_name(user)}\n\n"
        f"Progreso: {bar} {progress}%\n"
        f"Documentos subidos: {dc}\n"
        f"{phase_status(user, dc)}\n\n"
        f"Quedan {days_left()} dÃ­as para el cierre del plazo."
    )

    kb = main_menu_kb(user)
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    else:
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    return ST_MAIN_MENU


# --- Menu actions ---

async def handle_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data
    user = get_user(update.effective_user.id)

    # FAQ callback routing (from eligibility screen and other places)
    if d.startswith("fq_"):
        key = d[3:]
        faq = FAQ.get(key)
        if faq:
            text = faq["text"].replace("{days}", str(days_left()))
            await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Más preguntas", callback_data="m_faq")],
                    [InlineKeyboardButton("Menú principal", callback_data="back")],
                ]))
            return ST_FAQ_ITEM
        return ST_MAIN_MENU

    if d == "m_docs":
        docs = get_user_docs(update.effective_user.id)
        if not docs:
            text = "*Sus documentos*\n\nAÃºn no ha subido ningÃºn documento."
        else:
            text = "*Sus documentos*\n\n"
            for doc in docs:
                info = DOC_TYPES.get(doc["doc_type"], DOC_TYPES["other"])
                icon = "âœ…" if doc["status"] == "approved" else "â³"
                score_text = f" ({doc['validation_score']}%)" if doc["validation_score"] else ""
                text += f"{icon} {info['icon']} {info['name']}{score_text}\n"
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ðŸ“¤ Subir documento", callback_data="m_upload")],
                [InlineKeyboardButton("â† Volver", callback_data="back")],
            ]))
        return ST_DOCS_LIST

    if d == "m_upload":
        await q.edit_message_text(
            "*Subir documento*\n\nSeleccione el tipo de documento que desea subir:",
            parse_mode=ParseMode.MARKDOWN, reply_markup=doc_type_kb())
        return ST_UPLOAD_SELECT

    if d.startswith("dt_"):
        dtype = d[3:]
        info = DOC_TYPES.get(dtype, DOC_TYPES["other"])
        ctx.user_data["doc_type"] = dtype
        tip = f"\n\nðŸ’¡ {info['tip']}" if info.get("tip") else ""
        await q.edit_message_text(
            f"*Subir: {info['name']}*\n\n"
            f"EnvÃ­e una fotografÃ­a clara del documento.{tip}\n\n"
            "Consejos:\n"
            "- Buena iluminaciÃ³n, sin sombras.\n"
            "- Todo el documento visible.\n"
            "- Texto legible.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("â† Cancelar", callback_data="m_upload")],
            ]))
        return ST_UPLOAD_PHOTO

    if d == "m_price":
        await q.edit_message_text(FAQ["precio"]["text"], parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("â† Volver", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if d == "m_faq":
        await q.edit_message_text("*Preguntas frecuentes*\n\nSeleccione un tema:",
            parse_mode=ParseMode.MARKDOWN, reply_markup=faq_menu_kb())
        return ST_FAQ_MENU

    if d == "m_contact":
        await q.edit_message_text(
            "*Contacto con nuestro equipo*\n\n"
            f"WhatsApp: {SUPPORT_PHONE}\n"
            "TelÃ©fono: +34 91 555 0123\n"
            "Email: info@tuspapeles2026.es\n"
            "Oficina: Calle Serrano 45, Madrid\n\n"
            "Horario: lunes a viernes, 9:00â€“19:00.\n\n"
            "TambiÃ©n puede escribir su consulta aquÃ­ y la trasladaremos a un abogado:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Escribir consulta", callback_data="write_msg")],
                [InlineKeyboardButton("â† Volver", callback_data="back")],
            ]))
        return ST_CONTACT

    if d == "write_msg":
        await q.edit_message_text(
            "Escriba su consulta a continuaciÃ³n y la recibirÃ¡ un miembro de nuestro equipo.\n\n"
            "Responderemos en un plazo mÃ¡ximo de 24 horas laborables.")
        return ST_HUMAN_MSG

    if d == "m_pay2":
        dc = get_doc_count(update.effective_user.id)
        await q.edit_message_text(
            f"*RevisiÃ³n legal completa â€” â‚¬47*\n\n"
            f"Ha subido {dc} documentos. Con este pago, nuestro equipo realizarÃ¡:\n\n"
            "- AnÃ¡lisis legal de toda su documentaciÃ³n.\n"
            "- Informe detallado indicando quÃ© estÃ¡ correcto y quÃ© falta.\n"
            "- Plan personalizado con plazos.\n"
            "- Asesoramiento sobre antecedentes penales.\n"
            "- Canal de soporte prioritario.\n\n"
            "*Formas de pago:*\n"
            f"Bizum: {BIZUM_PHONE}\n"
            f"Transferencia: {BANK_IBAN}\n"
            "Concepto: su nombre + nÃºmero de expediente.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ya he realizado el pago", callback_data="paid2")],
                [InlineKeyboardButton("Tengo dudas", callback_data="m_contact")],
                [InlineKeyboardButton("â† Volver", callback_data="back")],
            ]))
        return ST_PAY_PHASE2

    if d == "paid2":
        update_user(update.effective_user.id, state="phase2_pending")
        await notify_admins(ctx,
            f"ðŸ’³ *Pago Fase 2 pendiente*\n"
            f"Usuario: {user.get('first_name')}\n"
            f"TID: {update.effective_user.id}\n"
            f"Aprobar: `/approve2 {update.effective_user.id}`")
        await q.edit_message_text(
            "Hemos registrado su notificaciÃ³n de pago.\n\n"
            "Lo verificaremos y le confirmaremos el acceso a la revisiÃ³n legal. "
            "RecibirÃ¡ una notificaciÃ³n cuando estÃ© activado.")
        return ConversationHandler.END

    if d == "m_pay3":
        await q.edit_message_text(
            f"*PreparaciÃ³n del expediente â€” â‚¬150*\n\n"
            "Sus documentos han sido verificados. Con este pago, nuestro equipo realizarÃ¡:\n\n"
            "- Expediente legal completo.\n"
            "- Todos los formularios completados y revisados.\n"
            "- RevisiÃ³n final por abogado.\n"
            "- Puesto reservado en cola de presentaciÃ³n.\n\n"
            "*Formas de pago:*\n"
            f"Bizum: {BIZUM_PHONE}\n"
            f"Transferencia: {BANK_IBAN}\n"
            "Concepto: su nombre + nÃºmero de expediente.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ya he realizado el pago", callback_data="paid3")],
                [InlineKeyboardButton("Tengo dudas", callback_data="m_contact")],
                [InlineKeyboardButton("â† Volver", callback_data="back")],
            ]))
        return ST_PAY_PHASE3

    if d == "paid3":
        update_user(update.effective_user.id, state="phase3_pending")
        await notify_admins(ctx,
            f"ðŸ’³ *Pago Fase 3 pendiente*\n"
            f"Usuario: {user.get('first_name')}\n"
            f"TID: {update.effective_user.id}\n"
            f"Aprobar: `/approve3 {update.effective_user.id}`")
        await q.edit_message_text(
            "Hemos registrado su notificaciÃ³n de pago.\n\n"
            "Lo verificaremos y comenzaremos la preparaciÃ³n de su expediente. "
            "RecibirÃ¡ una notificaciÃ³n cuando estÃ© activado.")
        return ConversationHandler.END

    if d == "show_bizum":
        await q.edit_message_text(
            "*Datos para el pago:*\n\n"
            f"*Bizum:* {BIZUM_PHONE}\n"
            f"*Transferencia:* {BANK_IBAN}\n\n"
            "Concepto: su nombre + número de expediente.\n\n"
            "Cuando haya realizado el pago, pulse el botón de confirmación.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ya he realizado el pago", callback_data="paid2")],
                [InlineKeyboardButton("← Volver", callback_data="back")],
            ]))
        return ST_PAY_PHASE2

    if d == "back":
        return await show_main_menu(update, ctx)

    if d == "restart":
        await q.message.reply_text(
            "Escriba /start para comenzar de nuevo.")
        return ConversationHandler.END

    if d == "notify":
        await q.edit_message_text(
            "Le avisaremos cuando se acerque la apertura del plazo. "
            "Puede volver a escribirnos en cualquier momento.")
        return ConversationHandler.END

    return ST_MAIN_MENU


# --- FAQ ---

async def handle_faq_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    d = q.data

    if d.startswith("fq_"):
        key = d[3:]
        faq = FAQ.get(key)
        if faq:
            text = faq["text"].replace("{days}", str(days_left()))
            await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("MÃ¡s preguntas", callback_data="m_faq")],
                    [InlineKeyboardButton("MenÃº principal", callback_data="back")],
                ]))
        return ST_FAQ_ITEM

    if d == "m_faq":
        await q.edit_message_text("*Preguntas frecuentes*\n\nSeleccione un tema:",
            parse_mode=ParseMode.MARKDOWN, reply_markup=faq_menu_kb())
        return ST_FAQ_MENU

    if d == "back":
        return await show_main_menu(update, ctx)

    return ST_FAQ_MENU


# --- Document upload ---

async def handle_photo_upload(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.photo:
        await update.message.reply_text("Por favor, envÃ­e una fotografÃ­a del documento.")
        return ST_UPLOAD_PHOTO

    photo = update.message.photo[-1]
    file_id = photo.file_id
    dtype = ctx.user_data.get("doc_type", "other")
    info = DOC_TYPES.get(dtype, DOC_TYPES["other"])

    # Processing message
    processing_msg = await update.message.reply_text("ðŸ” Analizando documentoâ€¦")

    # Process document
    try:
        file = await ctx.bot.get_file(photo.file_id)
        result = await process_document(file, dtype)
    except Exception as e:
        logger.error(f"Doc processing failed: {e}")
        result = {"success": True, "detected_type": dtype, "ocr_text": "", "score": 40, "notes": ["Documento guardado."]}

    # Save
    save_document(
        update.effective_user.id, dtype, file_id,
        ocr_text=result.get("ocr_text", ""),
        detected_type=result.get("detected_type", ""),
        score=result.get("score", 0),
        notes="; ".join(result.get("notes", [])),
    )

    dc = get_doc_count(update.effective_user.id)
    user = get_user(update.effective_user.id)

    # Build response
    score = result.get("score", 0)
    if score >= 70:
        status_text = "âœ… Documento aceptado."
    elif score >= 40:
        status_text = "â³ Documento recibido. SerÃ¡ revisado por nuestro equipo."
    else:
        status_text = "âš ï¸ Hay un problema con este documento."

    notes_text = ""
    if result.get("notes"):
        notes_text = "\n" + "\n".join(f"  Â· {n}" for n in result["notes"])

    # Phase 2 unlock message
    unlock = ""
    if dc >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        unlock = "\n\nYa puede desbloquear la *revisiÃ³n legal completa* por â‚¬47."

    await processing_msg.edit_text(
        f"{status_text}\n\n"
        f"Tipo: {info['name']}\n"
        f"Documentos totales: {dc}"
        f"{notes_text}{unlock}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Subir otro documento", callback_data="m_upload")],
            [InlineKeyboardButton("Volver al menÃº", callback_data="back")],
        ]),
    )

    # Notify admins
    await notify_admins(ctx,
        f"ðŸ“„ Documento subido\n"
        f"Usuario: {user.get('first_name')} (TID: {update.effective_user.id})\n"
        f"Tipo: {info['name']}\n"
        f"Score: {score}/100\n"
        f"Total docs: {dc}")

    return ST_MAIN_MENU


# --- File/PDF upload handler ---

async def handle_file_upload(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle document/PDF uploads (not photos)."""
    doc = update.message.document
    if not doc:
        await update.message.reply_text("Por favor, envíe un documento o fotografía.")
        return ST_UPLOAD_PHOTO

    file_id = doc.file_id
    file_name = doc.file_name or "documento"
    dtype = ctx.user_data.get("doc_type", "other")
    info = DOC_TYPES.get(dtype, DOC_TYPES["other"])

    # Save document
    save_document(
        update.effective_user.id, dtype, file_id,
        ocr_text=f"[PDF/File: {file_name}]",
        detected_type=dtype,
        score=50,
        notes="Documento recibido como archivo. Será revisado por nuestro equipo.",
    )

    dc = get_doc_count(update.effective_user.id)
    user = get_user(update.effective_user.id)

    unlock = ""
    if dc >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        unlock = "\n\nYa puede desbloquear la *revisión legal completa* por €47."

    await update.message.reply_text(
        f"✅ Documento recibido: {info['name']}\n"
        f"Archivo: {file_name}\n"
        f"Documentos totales: {dc}\n\n"
        f"Será revisado por nuestro equipo legal.{unlock}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Subir otro documento", callback_data="m_upload")],
            [InlineKeyboardButton("Volver al menú", callback_data="back")],
        ]),
    )

    await notify_admins(ctx,
        f"📎 Archivo subido\n"
        f"Usuario: {user.get('first_name')} (TID: {update.effective_user.id})\n"
        f"Tipo: {info['name']}\n"
        f"Archivo: {file_name}\n"
        f"Total docs: {dc}")

    return ST_MAIN_MENU


# --- Free-text handler (NLU) ---

async def handle_free_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle any text that isn't a button press."""
    text = update.message.text or ""
    user = get_user(update.effective_user.id)
    if not user:
        user = create_user(update.effective_user.id, update.effective_user.first_name or "Usuario")

    # Log message
    intent = detect_intent(text)
    save_message(update.effective_user.id, "in", text, intent or "")

    # If in human-message mode, forward to admins
    if ctx.user_data.get("awaiting_human_msg"):
        ctx.user_data["awaiting_human_msg"] = False
        await notify_admins(ctx,
            f"ðŸ’¬ *Consulta de usuario*\n"
            f"De: {user.get('first_name')} ({update.effective_user.id})\n"
            f"PaÃ­s: {COUNTRIES.get(user.get('country_code', ''), {}).get('name', '?')}\n\n"
            f"Mensaje:\n{text[:800]}")
        await update.message.reply_text(
            "Hemos recibido su consulta. Un miembro de nuestro equipo le responderÃ¡ "
            "a la mayor brevedad posible.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver al menÃº", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # Intent-based responses
    if intent == "greeting":
        await update.message.reply_text(
            f"Hola, {user.get('first_name', '')}. Â¿En quÃ© puedo ayudarle?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ver mi expediente", callback_data="back")],
                [InlineKeyboardButton("Preguntas frecuentes", callback_data="m_faq")],
            ]))
        return ST_MAIN_MENU

    if intent == "thanks":
        await update.message.reply_text(
            "De nada. Â¿Necesita algo mÃ¡s?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver al menÃº", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if intent == "goodbye":
        await update.message.reply_text(
            "Hasta pronto. Puede escribirnos en cualquier momento. Estamos disponibles 24/7.")
        return ST_MAIN_MENU

    if intent == "human":
        await update.message.reply_text(
            f"Por supuesto. Puede contactar con nuestro equipo:\n\n"
            f"WhatsApp: {SUPPORT_PHONE}\n"
            f"TelÃ©fono: +34 91 555 0123\n"
            f"Email: info@tuspapeles2026.es\n\n"
            "O escriba su consulta aquÃ­ y se la trasladamos a un abogado.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Escribir consulta", callback_data="write_msg")],
                [InlineKeyboardButton("Volver al menÃº", callback_data="back")],
            ]))
        return ST_CONTACT

    if intent == "price":
        await update.message.reply_text(FAQ["precio"]["text"], parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver al menÃº", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if intent == "status":
        return await show_main_menu(update, ctx)

    # Route all intents to their FAQ entries
    intent_faq_map = {
        "work": "vulnerabilidad",
        "online_submission": "presentacion_online",
        "approval_rate": "aprobacion",
        "comparison_2005": "diferencia_2005",
        "help": "requisitos",
        "family": "familia",
        "deadline": "plazos_detalle",
        "asylum": "asilo",
        "trust": "confianza",
        "documents": "pruebas_residencia",
        "no_empadronamiento": "sin_empadronamiento",
        "travel": "viajar_pendiente",
        "expired_passport": "pasaporte_vencido",
        "arraigo": "arraigo_en_curso",
        "denial": "denegacion",
    }
    if intent in intent_faq_map:
        faq = FAQ.get(intent_faq_map[intent])
        if faq:
            await update.message.reply_text(
                faq["text"],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Verificar mi elegibilidad", callback_data="back")],
                    [InlineKeyboardButton("MÃ¡s preguntas", callback_data="m_faq")],
                ]))
            return ST_MAIN_MENU

    # Try FAQ match
    faq = find_faq_match(text)
    if faq:
        await update.message.reply_text(
            faq["text"].replace("{days}", str(days_left())),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("MÃ¡s preguntas", callback_data="m_faq")],
                [InlineKeyboardButton("Volver al menÃº", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # Default â€” couldn't understand
    await update.message.reply_text(
        "No he podido identificar su consulta con certeza. "
        "Puede utilizar los botones del menÃº o seleccionar una de estas opciones:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Ver mi expediente", callback_data="back")],
            [InlineKeyboardButton("Preguntas frecuentes", callback_data="m_faq")],
            [InlineKeyboardButton("Hablar con nuestro equipo", callback_data="m_contact")],
        ]))
    return ST_MAIN_MENU


# --- Human message state ---

async def handle_human_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["awaiting_human_msg"] = True
    return await handle_free_text(update, ctx)


# =============================================================================
# ADMIN COMMANDS
# =============================================================================

async def cmd_approve2(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not ctx.args:
        await update.message.reply_text("Uso: /approve2 <telegram_id>"); return
    try:
        tid = int(ctx.args[0])
        update_user(tid, phase2_paid=1, current_phase=2, state="phase2_active")
        await ctx.bot.send_message(tid,
            "Su pago ha sido confirmado.\n\n"
            "Nuestro equipo legal iniciarÃ¡ la revisiÃ³n completa de su documentaciÃ³n. "
            "RecibirÃ¡ un informe detallado en un plazo de 48â€“72 horas.\n\n"
            "Escriba /menu para ver su panel.", parse_mode=ParseMode.MARKDOWN)
        await update.message.reply_text(f"Fase 2 aprobada para {tid}.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_approve3(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not ctx.args:
        await update.message.reply_text("Uso: /approve3 <telegram_id>"); return
    try:
        tid = int(ctx.args[0])
        update_user(tid, phase3_paid=1, current_phase=3, state="phase3_active")
        await ctx.bot.send_message(tid,
            "Pago de la Fase 3 confirmado.\n\n"
            "Estamos preparando su expediente legal completo. "
            "Le notificaremos cuando estÃ© listo para la presentaciÃ³n.")
        await update.message.reply_text(f"Fase 3 aprobada para {tid}.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin replies to user: /reply <tid> <message>"""
    if update.effective_user.id not in ADMIN_IDS: return
    if len(ctx.args) < 2:
        await update.message.reply_text("Uso: /reply <telegram_id> <mensaje>"); return
    try:
        tid = int(ctx.args[0])
        msg = " ".join(ctx.args[1:])
        await ctx.bot.send_message(tid,
            f"*Mensaje de su abogado:*\n\n{msg}", parse_mode=ParseMode.MARKDOWN)
        await update.message.reply_text(f"Enviado a {tid}.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users"); total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE eligible=1"); eligible = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE phase2_paid=1"); p2 = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE phase3_paid=1"); p3 = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM documents"); docs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM messages WHERE direction='in'"); msgs = c.fetchone()[0]
    conn.close()
    rev = (p2 * 47) + (p3 * 150)
    await update.message.reply_text(
        f"*EstadÃ­sticas*\n\n"
        f"Usuarios: {total}\n"
        f"Elegibles: {eligible}\n"
        f"Documentos: {docs}\n"
        f"Mensajes recibidos: {msgs}\n\n"
        f"Fase 2 pagados: {p2} (â‚¬{p2*47})\n"
        f"Fase 3 pagados: {p3} (â‚¬{p3*150})\n"
        f"*Ingresos: â‚¬{rev}*\n\n"
        f"DÃ­as restantes: {days_left()}", parse_mode=ParseMode.MARKDOWN)


async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin broadcasts to all users: /broadcast <message>"""
    if update.effective_user.id not in ADMIN_IDS: return
    if not ctx.args:
        await update.message.reply_text("Uso: /broadcast <mensaje>"); return
    msg = " ".join(ctx.args)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT telegram_id FROM users")
    users = [r[0] for r in c.fetchall()]
    conn.close()
    sent, failed = 0, 0
    for tid in users:
        try:
            await ctx.bot.send_message(tid, msg, parse_mode=ParseMode.MARKDOWN)
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(f"Enviado: {sent} | Fallido: {failed}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set.")
        return

    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
            CommandHandler("menu", cmd_menu),
            CommandHandler("reset", cmd_reset),
        ],
        states={
            ST_COUNTRY: [CallbackQueryHandler(handle_country, pattern="^c_")],
            ST_Q1_DATE: [CallbackQueryHandler(handle_q1)],
            ST_Q2_TIME: [CallbackQueryHandler(handle_q2)],
            ST_Q3_RECORD: [CallbackQueryHandler(handle_q3)],
            ST_ELIGIBLE: [CallbackQueryHandler(handle_menu)],
            ST_NOT_ELIGIBLE: [CallbackQueryHandler(handle_menu)],
            ST_SERVICE_INFO: [CallbackQueryHandler(handle_menu)],
            ST_FAQ_MENU: [CallbackQueryHandler(handle_faq_menu)],
            ST_FAQ_ITEM: [CallbackQueryHandler(handle_faq_menu)],
            ST_MAIN_MENU: [
                CallbackQueryHandler(handle_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text),
                MessageHandler(filters.PHOTO, handle_photo_upload),
                MessageHandler(filters.Document.ALL, handle_file_upload),
            ],
            ST_DOCS_LIST: [CallbackQueryHandler(handle_menu)],
            ST_UPLOAD_SELECT: [CallbackQueryHandler(handle_menu)],
            ST_UPLOAD_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo_upload),
                MessageHandler(filters.Document.ALL, handle_file_upload),
                CallbackQueryHandler(handle_menu),
            ],
            ST_PAY_PHASE2: [CallbackQueryHandler(handle_menu)],
            ST_PAY_PHASE3: [CallbackQueryHandler(handle_menu)],
            ST_CONTACT: [
                CallbackQueryHandler(handle_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text),
            ],
            ST_HUMAN_MSG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_human_msg),
                CallbackQueryHandler(handle_menu),
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CommandHandler("reset", cmd_reset),
            CommandHandler("menu", cmd_menu),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text),
            MessageHandler(filters.PHOTO, handle_photo_upload),
            MessageHandler(filters.Document.ALL, handle_file_upload),
            CallbackQueryHandler(handle_menu),
        ],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("approve2", cmd_approve2))
    app.add_handler(CommandHandler("approve3", cmd_approve3))
    app.add_handler(CommandHandler("reply", cmd_reply))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))

    logger.info("PH-Bot v5.1.0 starting")
    logger.info(f"Payment: FREE > â‚¬47 > â‚¬150 > â‚¬100 | Days left: {days_left()}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
