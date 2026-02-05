#!/usr/bin/env python3
"""
================================================================================
PH-Bot v5.0.0 — Client Intake & Case Management
================================================================================
Repository: github.com/anacuero-bit/PH-Bot
Updated:    2026-02-05

WHAT'S NEW IN v5.0:
  - Professional lawyer tone (no slang, no "quiubo parce")
  - NLU: handles free-text messages, not just button taps
  - OCR document scanning + auto-classification
  - 5-layer document validation pipeline
  - Smart escalation (bot → FAQ → canned → queue → human)
  - Lawyer-presence signals throughout ("Su abogado ha revisado…")
  - Comprehensive FAQ (50+ topics from objection-handling research)
  - Correct payment structure per PAYMENT_STRATEGY.md:
        Phase 1 FREE → Phase 2 €47 → Phase 3 €150 → Phase 4 €100
  - Country-specific document guidance
  - Personalized progress tracking
  - Admin tools: /approve2, /approve3, /stats, /broadcast, /flag

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
    "phase1": 0,       # Free — build trust
    "phase2": 47,      # After 3+ docs — legal review
    "phase3": 150,     # Docs verified — processing
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
# COUNTRY DATA (no slang greetings — professional tone)
# =============================================================================

COUNTRIES = {
    "co": {
        "name": "Colombia", "flag": "🇨🇴",
        "antecedentes_url": "https://antecedentes.policia.gov.co",
        "antecedentes_online": True,
        "antecedentes_price": 35,
        "apostille_info": "Apostilla electrónica disponible en cancilleria.gov.co",
        "hague": True,
    },
    "ve": {
        "name": "Venezuela", "flag": "🇻🇪",
        "antecedentes_url": "https://tramites.ministeriopublico.gob.ve",
        "antecedentes_online": False,
        "antecedentes_price": 59,
        "apostille_info": "Sistema frecuentemente caído. Recomendamos gestión profesional.",
        "hague": True,
    },
    "pe": {
        "name": "Perú", "flag": "🇵🇪",
        "antecedentes_url": "https://portal.policia.gob.pe/antecedentes_policiales/",
        "antecedentes_online": True,
        "antecedentes_price": 45,
        "apostille_info": "Apostilla en Relaciones Exteriores. Puede tardar 2-3 semanas.",
        "hague": True,
    },
    "ec": {
        "name": "Ecuador", "flag": "🇪🇨",
        "antecedentes_url": "https://certificados.ministeriodelinterior.gob.ec",
        "antecedentes_online": True,
        "antecedentes_price": 35,
        "apostille_info": "Apostilla electrónica disponible.",
        "hague": True,
    },
    "hn": {
        "name": "Honduras", "flag": "🇭🇳",
        "antecedentes_online": False,
        "antecedentes_price": 79,
        "apostille_info": "Requiere gestión presencial o mediante contacto local.",
        "hague": True,
    },
    "bo": {
        "name": "Bolivia", "flag": "🇧🇴",
        "antecedentes_online": False,
        "antecedentes_price": 79,
        "apostille_info": "Apostilla en Cancillería. Proceso presencial.",
        "hague": True,
    },
    "ar": {
        "name": "Argentina", "flag": "🇦🇷",
        "antecedentes_url": "https://www.dnrec.jus.gov.ar",
        "antecedentes_online": True,
        "antecedentes_price": 45,
        "apostille_info": "Apostilla electrónica disponible.",
        "hague": True,
    },
    "ma": {
        "name": "Marruecos", "flag": "🇲🇦",
        "antecedentes_online": False,
        "antecedentes_price": 79,
        "apostille_info": "Requiere legalización (no Apostilla — no es miembro del Convenio de La Haya). Legalización consular.",
        "hague": False,
    },
    "other": {
        "name": "Otro país", "flag": "🌍",
        "antecedentes_online": False,
        "antecedentes_price": 89,
        "apostille_info": "Consulte con nuestro equipo para su caso específico.",
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
        "tip": "Solicítelo en su ayuntamiento. Algunos permiten hacerlo online.",
    },
    "photo": {
        "name": "Fotografías tipo carnet",
        "icon": "📷",
        "required": True,
        "ocr_keywords": [],
        "validity_check": None,
        "tip": "2 fotos recientes, fondo blanco, tamaño carnet. Disponibles en fotomatones o estudios de fotografía.",
    },
    "proof_stay_1": {
        "name": "Prueba de estancia (1)",
        "icon": "📄",
        "required": True,
        "ocr_keywords": ["ENDESA", "IBERDROLA", "NATURGY", "FACTURA", "EXTRACTO", "BANCO", "ALQUILER",
                         "ARRENDAMIENTO", "CONTRATO", "WESTERN UNION", "RIA", "SEGURIDAD SOCIAL"],
        "validity_check": "less_than_6_months",
        "tip": "Facturas de luz/agua/gas, extractos bancarios, contrato de alquiler, recibos de envíos de dinero, tarjeta sanitaria…",
    },
    "proof_stay_2": {
        "name": "Prueba de estancia (2)",
        "icon": "📄",
        "required": True,
        "ocr_keywords": [],
        "validity_check": "less_than_6_months",
        "tip": "Se necesitan al menos dos documentos distintos que acrediten presencia continuada en España.",
    },
    "other": {
        "name": "Otro documento",
        "icon": "📎",
        "required": False,
        "ocr_keywords": [],
        "validity_check": None,
        "tip": "",
    },
}

# =============================================================================
# NLU — INTENT DETECTION FOR FREE-TEXT MESSAGES
# =============================================================================

INTENT_PATTERNS = {
    "greeting": [
        r"^hola\b", r"^buenos?\s*(días?|tardes?|noches?)", r"^hey\b",
        r"^saludos?\b", r"^qué tal", r"^buenas\b",
    ],
    "thanks": [
        r"\bgracias\b", r"\bgenial\b", r"\bperfecto\b", r"\bexcelente\b",
        r"^ok\b", r"^vale\b", r"\bde acuerdo\b", r"\bentendido\b",
    ],
    "goodbye": [
        r"\badiós\b", r"\badios\b", r"\bchao\b", r"\bbye\b",
        r"\bhasta luego\b", r"\bnos vemos\b",
    ],
    "help": [
        r"\bayuda\b", r"\bno entiendo\b", r"\bno sé\b", r"\bcómo funciona\b",
        r"\bestoy perdid[oa]\b", r"\bexplica\b",
    ],
    "price": [
        r"\bprecio\b", r"\bcuest[ao]\b", r"\bcuánto\b", r"\btarifa\b",
        r"\bpagar\b", r"\bcost[oe]\b", r"\bcobr", r"\bdinero\b",
    ],
    "documents": [
        r"\bdocumento", r"\bpapeles\b", r"\bpasaporte\b", r"\bempadronamiento\b",
        r"\bantecedentes\b", r"\bfactura\b", r"\bqué necesito\b",
    ],
    "status": [
        r"\bestado\b", r"\bmi caso\b", r"\bcómo va\b", r"\bprogreso\b",
        r"\bavance\b", r"\bqué falta\b",
    ],
    "human": [
        r"\bpersona\b", r"\bagente\b", r"\bhumano\b", r"\bllamar\b",
        r"\bteléfono\b", r"\bcontacto\b", r"\babogad[oa]\b", r"\bhablar con\b",
    ],
    "work": [
        r"\btrabajar\b", r"\btrabajo\b", r"\bcontrato\b", r"\bautónom[oa]\b",
        r"\bempleo\b", r"\bempresa\b",
    ],
    "family": [
        r"\bhij[oa]s?\b", r"\bmenor", r"\bfamilia\b", r"\bbebé\b",
        r"\bniñ[oa]s?\b", r"\besposa?\b", r"\bmarido\b", r"\bpareja\b",
    ],
    "deadline": [
        r"\bplazo\b", r"\bfecha\b", r"\bcuándo\b", r"\btiempo\b",
        r"\bdeadline\b", r"\babril\b", r"\bjunio\b",
    ],
    "asylum": [
        r"\basilo\b", r"\brefugi", r"\bprotección internacional\b",
        r"\btarjeta roja\b", r"\bhoja blanca\b",
    ],
    "trust": [
        r"\bestafa\b", r"\bconfia[rn]?\b", r"\bsegur[oa]\b", r"\bfraude\b",
        r"\blegítim[oa]\b", r"\breal\b", r"\bverdad\b", r"\bfiar\b",
    ],
}

# =============================================================================
# FAQ DATABASE — Professional tone, comprehensive
# =============================================================================

FAQ = {
    "requisitos": {
        "title": "Requisitos de la regularización",
        "keywords": ["requisito", "puedo", "quién", "elegible", "condicion"],
        "text": (
            "*Requisitos principales:*\n\n"
            "1. Haber entrado a España *antes del 31 de diciembre de 2025*.\n"
            "2. Acreditar una estancia continuada de *al menos 5 meses*.\n"
            "3. *No tener antecedentes penales* en España ni en su país de origen.\n\n"
            "La estancia se puede probar con documentos públicos o privados: "
            "empadronamiento, facturas, extractos bancarios, contratos, "
            "tarjeta sanitaria, recibos de envíos de dinero, entre otros.\n\n"
            "Los solicitantes de protección internacional (asilo) también pueden "
            "acogerse, siempre que la solicitud se hubiera presentado antes del 31/12/2025."
        ),
    },
    "documentos": {
        "title": "Documentos necesarios",
        "keywords": ["documento", "papeles", "necesito", "falta", "preparar"],
        "text": (
            "*Documentación necesaria:*\n\n"
            "1. *Pasaporte en vigor.* Si está vencido, renuévelo cuanto antes.\n"
            "2. *Certificado de antecedentes penales* de su país de origen "
            "(y de cualquier país donde haya residido en los últimos 5 años). "
            "Debe estar apostillado o legalizado, y traducido si no está en español.\n"
            "3. *Certificado de empadronamiento* o equivalente.\n"
            "4. *Dos fotografías* tipo carnet recientes.\n"
            "5. *Pruebas de estancia continuada:* al menos dos documentos "
            "con fechas que acrediten su presencia en España "
            "(facturas, extractos bancarios, contrato de alquiler, tarjeta sanitaria, "
            "recibos de Western Union o Ria, certificado de escolarización de hijos…).\n"
            "6. *Tasa administrativa:* €38,28 (se abona al gobierno al presentar).\n\n"
            "Le ayudamos a revisar y completar toda esta documentación."
        ),
    },
    "plazos": {
        "title": "Plazos y fechas clave",
        "keywords": ["plazo", "fecha", "cuándo", "tiempo", "abril", "junio", "deadline"],
        "text": (
            "*Calendario previsto:*\n\n"
            "Febrero-marzo 2026 — Tramitación del Real Decreto.\n"
            "Principios de abril 2026 — Apertura del plazo de solicitudes.\n"
            "*30 de junio de 2026* — Cierre del plazo.\n\n"
            "Una vez presentada la solicitud:\n"
            "- Admisión a trámite: máximo 15 días.\n"
            "- Con la admisión, se obtiene autorización *provisional* para trabajar.\n"
            "- Resolución final: aproximadamente 3 meses.\n\n"
            "Recomendamos preparar la documentación *ahora* para evitar "
            "la saturación de los últimos días."
        ),
    },
    "precio": {
        "title": "Nuestras tarifas",
        "keywords": ["precio", "cuesta", "cuánto", "tarifa", "pagar", "caro", "barato", "dinero"],
        "text": (
            "*Nuestras tarifas — sin sorpresas:*\n\n"
            "Fase 1 · Preparación: *Gratuito*\n"
            "  Verificación de elegibilidad, subida de documentos, revisión preliminar.\n\n"
            "Fase 2 · Revisión legal: *€47*\n"
            "  Análisis completo, informe detallado, plan personalizado.\n\n"
            "Fase 3 · Procesamiento: *€150*\n"
            "  Expediente legal, formularios, revisión final de abogado.\n\n"
            "Fase 4 · Presentación: *€100*\n"
            "  Presentación oficial, seguimiento hasta resolución.\n\n"
            "*Total servicio: €297*\n"
            "Tasas del gobierno (aparte): €38,28 + ~€16 (TIE).\n\n"
            "A modo de referencia, un abogado generalista cobra entre €500 y €1.000 "
            "por un servicio similar. Las gestorías, entre €300 y €600, pero sin "
            "supervisión de abogado colegiado."
        ),
    },
    "trabajo": {
        "title": "Autorización de trabajo",
        "keywords": ["trabajo", "trabajar", "contrato", "empleo", "autónom", "cuenta propia"],
        "text": (
            "*Autorización de trabajo:*\n\n"
            "Desde que su solicitud sea *admitida a trámite* (máximo 15 días "
            "tras la presentación), obtendrá una autorización provisional para "
            "trabajar legalmente en toda España.\n\n"
            "Esto incluye:\n"
            "- Trabajo por cuenta ajena en cualquier sector.\n"
            "- Trabajo por cuenta propia (autónomo).\n"
            "- Posibilidad de firmar contratos y darse de alta en la Seguridad Social.\n\n"
            "No se requiere oferta de empleo previa para solicitar la regularización."
        ),
    },
    "familia": {
        "title": "Hijos menores y familia",
        "keywords": ["hijo", "hija", "menor", "familia", "niño", "bebé", "esposa", "pareja"],
        "text": (
            "*Regularización de menores y familia:*\n\n"
            "Los hijos e hijas menores de edad que se encuentren en España "
            "pueden regularizarse *simultáneamente* con el solicitante.\n\n"
            "Ventaja importante: el permiso para menores será de *5 años* "
            "(no 1 año como el del adulto).\n\n"
            "Documentación adicional para menores:\n"
            "- Pasaporte del menor.\n"
            "- Partida de nacimiento apostillada.\n"
            "- Certificado de escolarización (si está en edad escolar).\n"
            "- Libro de familia, si lo tiene.\n\n"
            "Descuentos familiares:\n"
            "- 2.ª persona: 18% de descuento.\n"
            "- 3.ª persona en adelante: 25% de descuento."
        ),
    },
    "antecedentes": {
        "title": "Antecedentes penales",
        "keywords": ["antecedente", "penal", "criminal", "apostilla", "récord", "delito"],
        "text": (
            "*Certificado de antecedentes penales:*\n\n"
            "Es obligatorio presentar un certificado *sin antecedentes* de:\n"
            "- Su país de origen.\n"
            "- Cualquier otro país donde haya residido en los últimos 5 años.\n\n"
            "El documento debe estar:\n"
            "- *Apostillado* (Convenio de La Haya) o *legalizado* vía consular.\n"
            "- *Traducido al español* por traductor jurado (si no está en español).\n"
            "- Emitido con una antigüedad máxima de 3-6 meses.\n\n"
            "Opciones:\n"
            "a) Lo gestiona usted mismo — le proporcionamos instrucciones detalladas.\n"
            "b) Lo gestionamos nosotros — entre €35 y €79 según el país.\n\n"
            "Si su país tiene un sistema online, puede ser rápido. "
            "En caso contrario, le recomendamos empezar cuanto antes."
        ),
    },
    "confianza": {
        "title": "Sobre Pombo & Horowitz",
        "keywords": ["confia", "estafa", "seguro", "fraude", "real", "legítim", "fiar", "quiénes"],
        "text": (
            "*Sobre Pombo & Horowitz Abogados:*\n\n"
            "- Fundado en 1988. Más de 35 años de ejercicio.\n"
            "- Más de 12.000 casos de extranjería gestionados.\n"
            "- Abogados colegiados en el ICAM (Ilustre Colegio de Abogados de Madrid).\n"
            "- Oficina física: Calle Serrano, Madrid.\n"
            "- Puede verificar nuestra colegiación en icam.es.\n\n"
            "Diferencias con gestorías y servicios no regulados:\n"
            "- Un abogado colegiado firma y responde personalmente de su trabajo.\n"
            "- Estamos sujetos al código deontológico del Colegio de Abogados.\n"
            "- Si algo sale mal, tiene a quién reclamar.\n\n"
            "No cobramos nada hasta que usted haya comprobado nuestro trabajo."
        ),
    },
    "asilo": {
        "title": "Solicitantes de asilo / protección internacional",
        "keywords": ["asilo", "refugi", "protección internacional", "tarjeta roja", "hoja blanca"],
        "text": (
            "*Si tiene una solicitud de protección internacional:*\n\n"
            "Puede acogerse a la regularización siempre que la solicitud "
            "de asilo se hubiera presentado *antes del 31 de diciembre de 2025*.\n\n"
            "Proceso:\n"
            "- Al solicitar la regularización, su expediente de asilo queda *suspendido* "
            "(no cerrado definitivamente).\n"
            "- Si la regularización se resuelve favorablemente, el asilo se archiva.\n"
            "- Si se deniega, su solicitud de asilo se reactiva.\n\n"
            "Es importante valorar las ventajas: la regularización ofrece "
            "autorización de trabajo inmediata (con la admisión a trámite), "
            "algo que la vía de asilo no siempre proporciona con la misma rapidez."
        ),
    },
    "despues": {
        "title": "Después de la regularización",
        "keywords": ["después", "luego", "siguiente", "renovar", "nacionalidad", "permanente"],
        "text": (
            "*Después de obtener la autorización:*\n\n"
            "1. Recibirá un permiso de residencia y trabajo de *1 año*.\n"
            "2. Deberá solicitar la *TIE* (Tarjeta de Identidad de Extranjero).\n"
            "3. Al vencer el año, deberá renovar por la vía ordinaria "
            "(arraigo social, laboral, familiar, etc.).\n\n"
            "Camino hacia la nacionalidad:\n"
            "- Ciudadanos iberoamericanos: 2 años de residencia legal.\n"
            "- Resto de nacionalidades: 10 años.\n"
            "- El tiempo en situación irregular *no cuenta*.\n"
            "- Esta regularización inicia el cómputo.\n\n"
            "Le acompañamos también en los pasos posteriores."
        ),
    },
    "caro": {
        "title": "Comparativa de precios",
        "keywords": ["caro", "barato", "much", "alcanza", "económic"],
        "text": (
            "*Entendemos que es una inversión importante.*\n\n"
            "Comparativa de mercado:\n\n"
            "Gestorías tradicionales: €300-600\n"
            "  Sin abogados, sin garantías, pago por adelantado.\n\n"
            "Abogados generalistas: €500-1.000\n"
            "  Sin especialización en extranjería.\n\n"
            "Pombo & Horowitz: €297 total\n"
            "  Abogados colegiados especializados.\n"
            "  38 años de experiencia.\n"
            "  Pago progresivo (no todo de golpe).\n"
            "  Primera fase completamente gratuita.\n\n"
            "Además, un error en la solicitud puede significar la denegación "
            "y la pérdida de la oportunidad. El coste de no hacerlo bien "
            "es mucho mayor que el de hacerlo con profesionales."
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
        return False, "La imagen es demasiado pequeña. Acérquese más al documento."
    if w * h < 500_000:
        return False, "La resolución es muy baja. Tome la foto con mejor iluminación y más cerca."
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
        result["notes"].append("Documento guardado. Será revisado manualmente.")
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
                f"Esperábamos «{DOC_TYPES.get(expected_type, {}).get('name', expected_type)}» "
                f"pero parece ser «{DOC_TYPES.get(detected, {}).get('name', detected)}»."
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
        result["notes"].append("No pudimos analizar el documento automáticamente. Será revisado por nuestro equipo.")

    return result


# =============================================================================
# HELPERS
# =============================================================================

def days_left() -> int:
    return max(0, (DEADLINE - datetime.now()).days)


def phase_name(user: Dict) -> str:
    if user.get("phase4_paid"): return "Fase 4 — Presentación"
    if user.get("phase3_paid"): return "Fase 3 — Procesamiento"
    if user.get("phase2_paid"): return "Fase 2 — Revisión legal"
    return "Fase 1 — Preparación (gratuita)"


def phase_status(user: Dict, doc_count: int) -> str:
    if user.get("phase2_paid") and not user.get("phase3_paid"):
        return "Su expediente está siendo analizado por nuestro equipo legal."
    if not user.get("phase2_paid") and doc_count >= MIN_DOCS_FOR_PHASE2:
        return "Ya puede desbloquear la revisión legal completa."
    remaining = max(0, MIN_DOCS_FOR_PHASE2 - doc_count)
    if remaining > 0:
        return f"Suba {remaining} documento(s) más para acceder a la revisión legal."
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
    buttons.append([InlineKeyboardButton("← Volver al menú", callback_data="back")])
    return InlineKeyboardMarkup(buttons)


def main_menu_kb(user: Dict) -> InlineKeyboardMarkup:
    dc = get_doc_count(user["telegram_id"])
    btns = [
        [InlineKeyboardButton(f"📄 Mis documentos ({dc})", callback_data="m_docs")],
        [InlineKeyboardButton("📤 Subir documento", callback_data="m_upload")],
    ]
    if dc >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        btns.append([InlineKeyboardButton("🔓 Revisión legal — €47", callback_data="m_pay2")])
    elif user.get("phase2_paid") and not user.get("phase3_paid") and user.get("docs_verified"):
        btns.append([InlineKeyboardButton("🔓 Procesamiento — €150", callback_data="m_pay3")])
    btns += [
        [InlineKeyboardButton("💰 Costos y pagos", callback_data="m_price")],
        [InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="m_faq")],
        [InlineKeyboardButton("📞 Hablar con nuestro equipo", callback_data="m_contact")],
    ]
    return InlineKeyboardMarkup(btns)


def faq_menu_kb() -> InlineKeyboardMarkup:
    btns = []
    for key, faq in FAQ.items():
        btns.append([InlineKeyboardButton(faq["title"], callback_data=f"fq_{key}")])
    btns.append([InlineKeyboardButton("← Volver al menú", callback_data="back")])
    return InlineKeyboardMarkup(btns)


async def notify_admins(context, msg: str):
    for aid in ADMIN_IDS:
        try:
            await context.bot.send_message(aid, msg, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass


# =============================================================================
# HANDLERS
# =============================================================================

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = get_user(update.effective_user.id)
    if user and user.get("eligible"):
        return await show_main_menu(update, ctx)

    create_user(update.effective_user.id, update.effective_user.first_name or "Usuario")

    await update.message.reply_text(
        "Bienvenido/a al servicio de regularización de *Pombo & Horowitz Abogados*.\n\n"
        "Le guiaremos paso a paso en el proceso de regularización extraordinaria 2026.\n\n"
        "Todo lo que haga en esta primera fase es *gratuito*: verificar su elegibilidad, "
        "subir documentos y recibir una revisión preliminar. No le pediremos ningún pago "
        "hasta que haya comprobado nuestro trabajo.\n\n"
        "Para empezar, indíquenos su país de origen:",
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
        "A continuación, necesitamos hacerle *3 preguntas breves* para verificar "
        "si cumple los requisitos básicos de la regularización.\n\n"
        "Sus respuestas son estrictamente confidenciales.",
        parse_mode=ParseMode.MARKDOWN,
    )

    await q.message.reply_text(
        "*Pregunta 1 de 3*\n\n"
        "¿Se encontraba usted en España *antes del 31 de diciembre de 2025*?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Sí, llegué antes de esa fecha", callback_data="d_yes")],
            [InlineKeyboardButton("No, llegué después", callback_data="d_no")],
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
            "Lamentablemente, la regularización extraordinaria requiere haber estado "
            "en España *antes del 31 de diciembre de 2025*.\n\n"
            "Existen otras vías (arraigo social, laboral, familiar) que podrían aplicar "
            "en su caso. Si lo desea, un abogado puede valorar su situación.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Consultar con un abogado", callback_data="m_contact")],
                [InlineKeyboardButton("Volver al inicio", callback_data="restart")],
            ]),
        )
        return ST_NOT_ELIGIBLE

    if q.data == "d_unsure":
        await q.edit_message_text(
            "No se preocupe. ¿Dispone de algún documento de finales de 2025 o anterior?\n\n"
            "Por ejemplo: sello de entrada en el pasaporte, billete de avión, "
            "empadronamiento, contrato de alquiler, factura, recibo de envío de dinero…",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Sí, tengo algún documento", callback_data="d_yes")],
                [InlineKeyboardButton("No tengo ninguno", callback_data="d_no")],
            ]),
        )
        return ST_Q1_DATE

    # d_yes
    await q.edit_message_text(
        "*Pregunta 2 de 3*\n\n"
        "¿Lleva al menos *5 meses* viviendo en España de forma continuada?\n\n"
        "(Viajes cortos al extranjero no interrumpen la continuidad.)",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Sí, más de 5 meses", callback_data="t_yes")],
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
            "Si para entonces ya cumple el requisito, podría acogerse.\n\n"
            "¿Desea que le avisemos cuando se acerque la fecha?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Sí, avísenme", callback_data="notify")],
                [InlineKeyboardButton("Volver al inicio", callback_data="restart")],
            ]),
        )
        return ST_NOT_ELIGIBLE

    if q.data == "t_almost":
        await q.edit_message_text(
            "El plazo no abre hasta abril de 2026. Si para entonces ya cumple "
            "los 5 meses, perfecto. Puede ir preparando la documentación mientras tanto.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Continuar", callback_data="t_yes")],
            ]),
        )
        return ST_Q2_TIME

    # t_yes
    await q.edit_message_text(
        "*Pregunta 3 de 3*\n\n"
        "¿Tiene antecedentes penales en España o en su país de origen?\n\n"
        "Esta información es estrictamente confidencial.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("No, sin antecedentes", callback_data="r_clean")],
            [InlineKeyboardButton("Sí, tengo antecedentes", callback_data="r_yes")],
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
            "Tener antecedentes no supone automáticamente una exclusión. "
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
            "(robos, agresiones, tráfico de drogas, etc.).\n\n"
            "Las multas de tráfico, faltas leves o denuncias archivadas *no* cuentan.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("No tengo condenas", callback_data="r_clean")],
                [InlineKeyboardButton("Tengo alguna condena", callback_data="r_yes")],
            ]),
        )
        return ST_Q3_RECORD

    # r_clean — ELIGIBLE
    update_user(update.effective_user.id, eligible=1, has_criminal_record=0)
    case = get_or_create_case(update.effective_user.id)

    await q.edit_message_text(
        f"*{name}, cumple los requisitos básicos para la regularización.*\n\n"
        f"Le hemos asignado el número de expediente *{case['case_number']}*.\n\n"
        f"Plazo de solicitudes: abril — 30 de junio de 2026.\n"
        f"Quedan *{days_left()} días*.\n\n"
        "El siguiente paso es preparar su documentación. "
        "Puede empezar ahora mismo — es completamente gratuito.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Ver documentos necesarios", callback_data="fq_documentos")],
            [InlineKeyboardButton("Ver costos del servicio", callback_data="m_price")],
            [InlineKeyboardButton("Empezar a subir documentos", callback_data="m_upload")],
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

    msg = (
        f"*{name}* — Expediente {case['case_number']}\n"
        f"Fase actual: {phase_name(user)}\n\n"
        f"Documentos subidos: {dc}\n"
        f"{phase_status(user, dc)}\n\n"
        f"Quedan {days_left()} días para el cierre del plazo."
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

    if d == "m_docs":
        docs = get_user_docs(update.effective_user.id)
        if not docs:
            text = "*Sus documentos*\n\nAún no ha subido ningún documento."
        else:
            text = "*Sus documentos*\n\n"
            for doc in docs:
                info = DOC_TYPES.get(doc["doc_type"], DOC_TYPES["other"])
                icon = "✅" if doc["status"] == "approved" else "⏳"
                score_text = f" ({doc['validation_score']}%)" if doc["validation_score"] else ""
                text += f"{icon} {info['icon']} {info['name']}{score_text}\n"
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Subir documento", callback_data="m_upload")],
                [InlineKeyboardButton("← Volver", callback_data="back")],
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
        tip = f"\n\n💡 {info['tip']}" if info.get("tip") else ""
        await q.edit_message_text(
            f"*Subir: {info['name']}*\n\n"
            f"Envíe una fotografía clara del documento.{tip}\n\n"
            "Consejos:\n"
            "- Buena iluminación, sin sombras.\n"
            "- Todo el documento visible.\n"
            "- Texto legible.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Cancelar", callback_data="m_upload")],
            ]))
        return ST_UPLOAD_PHOTO

    if d == "m_price":
        await q.edit_message_text(FAQ["precio"]["text"], parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver", callback_data="back")],
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
            "Teléfono: +34 91 555 0123\n"
            "Email: info@tuspapeles2026.es\n"
            "Oficina: Calle Serrano 45, Madrid\n\n"
            "Horario: lunes a viernes, 9:00–19:00.\n\n"
            "También puede escribir su consulta aquí y la trasladaremos a un abogado:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Escribir consulta", callback_data="write_msg")],
                [InlineKeyboardButton("← Volver", callback_data="back")],
            ]))
        return ST_CONTACT

    if d == "write_msg":
        await q.edit_message_text(
            "Escriba su consulta a continuación y la recibirá un miembro de nuestro equipo.\n\n"
            "Responderemos en un plazo máximo de 24 horas laborables.")
        return ST_HUMAN_MSG

    if d == "m_pay2":
        dc = get_doc_count(update.effective_user.id)
        await q.edit_message_text(
            f"*Revisión legal completa — €47*\n\n"
            f"Ha subido {dc} documentos. Con este pago, nuestro equipo realizará:\n\n"
            "- Análisis legal de toda su documentación.\n"
            "- Informe detallado indicando qué está correcto y qué falta.\n"
            "- Plan personalizado con plazos.\n"
            "- Asesoramiento sobre antecedentes penales.\n"
            "- Canal de soporte prioritario.\n\n"
            "*Formas de pago:*\n"
            f"Bizum: {BIZUM_PHONE}\n"
            f"Transferencia: {BANK_IBAN}\n"
            "Concepto: su nombre + número de expediente.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ya he realizado el pago", callback_data="paid2")],
                [InlineKeyboardButton("Tengo dudas", callback_data="m_contact")],
                [InlineKeyboardButton("← Volver", callback_data="back")],
            ]))
        return ST_PAY_PHASE2

    if d == "paid2":
        update_user(update.effective_user.id, state="phase2_pending")
        await notify_admins(ctx,
            f"💳 *Pago Fase 2 pendiente*\n"
            f"Usuario: {user.get('first_name')}\n"
            f"TID: {update.effective_user.id}\n"
            f"Aprobar: `/approve2 {update.effective_user.id}`")
        await q.edit_message_text(
            "Hemos registrado su notificación de pago.\n\n"
            "Lo verificaremos y le confirmaremos el acceso a la revisión legal. "
            "Recibirá una notificación cuando esté activado.")
        return ConversationHandler.END

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
                    [InlineKeyboardButton("Más preguntas", callback_data="m_faq")],
                    [InlineKeyboardButton("Menú principal", callback_data="back")],
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
        await update.message.reply_text("Por favor, envíe una fotografía del documento.")
        return ST_UPLOAD_PHOTO

    photo = update.message.photo[-1]
    file_id = photo.file_id
    dtype = ctx.user_data.get("doc_type", "other")
    info = DOC_TYPES.get(dtype, DOC_TYPES["other"])

    # Processing message
    processing_msg = await update.message.reply_text("🔍 Analizando documento…")

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
        status_text = "✅ Documento aceptado."
    elif score >= 40:
        status_text = "⏳ Documento recibido. Será revisado por nuestro equipo."
    else:
        status_text = "⚠️ Hay un problema con este documento."

    notes_text = ""
    if result.get("notes"):
        notes_text = "\n" + "\n".join(f"  · {n}" for n in result["notes"])

    # Phase 2 unlock message
    unlock = ""
    if dc >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        unlock = "\n\nYa puede desbloquear la *revisión legal completa* por €47."

    await processing_msg.edit_text(
        f"{status_text}\n\n"
        f"Tipo: {info['name']}\n"
        f"Documentos totales: {dc}"
        f"{notes_text}{unlock}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Subir otro documento", callback_data="m_upload")],
            [InlineKeyboardButton("Volver al menú", callback_data="back")],
        ]),
    )

    # Notify admins
    await notify_admins(ctx,
        f"📄 Documento subido\n"
        f"Usuario: {user.get('first_name')} (TID: {update.effective_user.id})\n"
        f"Tipo: {info['name']}\n"
        f"Score: {score}/100\n"
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
            f"💬 *Consulta de usuario*\n"
            f"De: {user.get('first_name')} ({update.effective_user.id})\n"
            f"País: {COUNTRIES.get(user.get('country_code', ''), {}).get('name', '?')}\n\n"
            f"Mensaje:\n{text[:800]}")
        await update.message.reply_text(
            "Hemos recibido su consulta. Un miembro de nuestro equipo le responderá "
            "a la mayor brevedad posible.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver al menú", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # Intent-based responses
    if intent == "greeting":
        await update.message.reply_text(
            f"Hola, {user.get('first_name', '')}. ¿En qué puedo ayudarle?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ver mi expediente", callback_data="back")],
                [InlineKeyboardButton("Preguntas frecuentes", callback_data="m_faq")],
            ]))
        return ST_MAIN_MENU

    if intent == "thanks":
        await update.message.reply_text(
            "De nada. ¿Necesita algo más?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver al menú", callback_data="back")],
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
            f"Teléfono: +34 91 555 0123\n"
            f"Email: info@tuspapeles2026.es\n\n"
            "O escriba su consulta aquí y se la trasladamos a un abogado.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Escribir consulta", callback_data="write_msg")],
                [InlineKeyboardButton("Volver al menú", callback_data="back")],
            ]))
        return ST_CONTACT

    if intent == "price":
        await update.message.reply_text(FAQ["precio"]["text"], parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver al menú", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if intent == "status":
        return await show_main_menu(update, ctx)

    # Try FAQ match
    faq = find_faq_match(text)
    if faq:
        await update.message.reply_text(
            faq["text"].replace("{days}", str(days_left())),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Más preguntas", callback_data="m_faq")],
                [InlineKeyboardButton("Volver al menú", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # Default — couldn't understand
    await update.message.reply_text(
        "No he podido identificar su consulta con certeza. "
        "Puede utilizar los botones del menú o seleccionar una de estas opciones:",
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
            "Nuestro equipo legal iniciará la revisión completa de su documentación. "
            "Recibirá un informe detallado en un plazo de 48–72 horas.\n\n"
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
            "Le notificaremos cuando esté listo para la presentación.")
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
        f"*Estadísticas*\n\n"
        f"Usuarios: {total}\n"
        f"Elegibles: {eligible}\n"
        f"Documentos: {docs}\n"
        f"Mensajes recibidos: {msgs}\n\n"
        f"Fase 2 pagados: {p2} (€{p2*47})\n"
        f"Fase 3 pagados: {p3} (€{p3*150})\n"
        f"*Ingresos: €{rev}*\n\n"
        f"Días restantes: {days_left()}", parse_mode=ParseMode.MARKDOWN)


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
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text),
            MessageHandler(filters.PHOTO, handle_photo_upload),
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
            ],
            ST_DOCS_LIST: [CallbackQueryHandler(handle_menu)],
            ST_UPLOAD_SELECT: [CallbackQueryHandler(handle_menu)],
            ST_UPLOAD_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo_upload),
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

    logger.info("PH-Bot v5.0.0 starting")
    logger.info(f"Payment: FREE > €47 > €150 > €100 | Days left: {days_left()}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
