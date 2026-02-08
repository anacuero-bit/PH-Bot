#!/usr/bin/env python3
"""
================================================================================
PH-Bot v5.6.0 — Client Intake & Case Management
================================================================================
Repository: github.com/anacuero-bit/PH-Bot
Updated:    2026-02-08

CHANGELOG:
----------
v5.4.0 (2026-02-08)
  - EXPANDED COUNTRIES: 25 countries (was 9) with verified antecedentes info
  - ADDED: /antecedentes command — country-specific criminal record instructions
  - ADDED: Country-specific antecedentes info in NLU (criminal_cert intent)
  - UPDATED: Country keyboard — 5x5 flag grid for top non-EU nationalities in Spain
  - UPDATED: Referidos screen — PAID vs UNPAID templates with full explanation
  - UPDATED: Share buttons — WhatsApp, Telegram, Facebook, Copy for IG/TikTok
  - UPDATED: Share URLs use tuspapeles2026.es/r.html?code= referral landing page
  - UPDATED: copy_ref_ handler sends copyable text for Instagram/TikTok sharing
  - UPDATED: Pricing FAQ — comprehensive breakdown with govt fees, phases, discounts
  - UPDATED: Antecedentes FAQ references /antecedentes for country-specific info
  - REMOVED: Broken antecedentes_url links from COUNTRIES dict
  - REMOVED: antecedentes_price upsell (replaced with /antecedentes command)

v5.3.1 (2026-02-07)
  - BUGFIXES:
  - FIXED: AI confidence always showing 0% - improved JSON parsing with:
      - Better markdown code block stripping (```json, etc.)
      - Robust JSON extraction from response text
      - Explicit float conversion for confidence values
      - Detailed logging for debugging
  - FIXED: /pendientes now shows documents with inline action buttons:
      - [✓ Aprobar] [✗ Rechazar] buttons for quick actions
      - [🔄 Pedir nueva foto] for resubmission requests
      - [⏭ Siguiente] to skip to next document
      - Document image sent with each pending item
      - Rejection reason selection with predefined options
      - Auto-advance to next pending doc after action
  - FIXED: Admin notification missing user name - now shows:
      - full_name (if set) or first_name or Telegram name as fallback

v5.3.0 (2026-02-07)
  - AI DOCUMENT ANALYSIS:
  - ADDED: Claude Vision API integration for document classification
  - ADDED: Auto-processing logic based on confidence levels:
      - High (≥85%): Auto-approved
      - Medium (60-85%): Pending admin review
      - Low (<60%): User prompted to re-upload
  - ADDED: /pendientes admin command - view pending documents
  - ADDED: /aprobar <doc_id> - approve a document
  - ADDED: /rechazar <doc_id> [reason] - reject a document
  - ADDED: /ver <doc_id> - view document with AI analysis details
  - ADDED: New document columns: ai_analysis, ai_confidence, ai_type,
      extracted_name, extracted_address, extracted_date, approved,
      document_country, expiry_date, issues
  - UPDATED: Progress bar now counts only approved documents
  - UPDATED: Phase 2 unlock based on approved doc count
  - ADDED: User notifications when documents are approved/rejected

v5.2.0 (2026-02-06)
  - INFRASTRUCTURE & FEATURES:
  - FIXED: UTF-8 encoding corruption (mojibake) - all Spanish chars now display correctly
  - ADDED: Stripe payment links integrated into Phase 2/3/4 payment screens
  - ADDED: Phase 4 payment flow (€110 filing fee) with m_pay4, paid4 handlers
  - ADDED: /approve4 and /ready admin commands for Phase 4 management
  - ADDED: expediente_ready field for Phase 4 eligibility
  - ADDED: PostgreSQL support for Railway (persistent DB via DATABASE_URL)
  - ADDED: Re-engagement reminders (24h, 72h, 1week) via job queue
  - ADDED: Database type shown in /stats output
  - UPDATED: All database functions support both PostgreSQL and SQLite

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
  - FIXED: /reset now in entry_points (was only in fallbacks — didn't work mid-conversation)
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
  - Smart escalation (bot → FAQ → canned → queue → human)
  - Comprehensive FAQ (11 topics vs 6 in v4)
  - Correct payment structure per PAYMENT_STRATEGY.md:
        Phase 1 FREE → Phase 2 €39 → Phase 3 €150 → Phase 4 €110
  - Country-specific antecedentes guidance
  - Message logging database
  - Admin tools: /approve2, /approve3, /reply, /stats, /broadcast

v4.0.0 (2026-02-04)
  - Country selection with flags
  - Progressive payment (wrong amounts: €9.99 → €89.01 → €199 → €38.28)
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

# Optional: PostgreSQL (for Railway production)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Optional: Anthropic Claude API for document analysis
try:
    import anthropic
    import base64
    import json
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_CHAT_IDS", "").split(",") if x.strip()]
SUPPORT_PHONE = os.environ.get("SUPPORT_PHONE", "+34 600 000 000")
BIZUM_PHONE = os.environ.get("BIZUM_PHONE", "+34 600 000 000")
BANK_IBAN = os.environ.get("BANK_IBAN", "ES00 0000 0000 0000 0000 0000")
STRIPE_PHASE2_LINK = os.environ.get("STRIPE_PHASE2_LINK", "")  # Stripe payment link for €39
STRIPE_PHASE3_LINK = os.environ.get("STRIPE_PHASE3_LINK", "")  # Stripe payment link for €150
STRIPE_PHASE4_LINK = os.environ.get("STRIPE_PHASE4_LINK", "")  # Stripe payment link for €110
STRIPE_PREPAY_LINK = os.environ.get("STRIPE_PREPAY_LINK", "")  # Stripe payment link for €254 full prepay
STRIPE_ANTECEDENTES_LINK = os.environ.get("STRIPE_ANTECEDENTES_LINK", "")  # Stripe for €49 antecedentes
STRIPE_GOVT_FEES_LINK = os.environ.get("STRIPE_GOVT_FEES_LINK", "")  # Stripe for €29 govt fees
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")  # Claude API for document analysis
# Debug: log API key availability at startup (never log the key itself)
logging.getLogger("ph-bot").info(
    "ANTHROPIC config: AVAILABLE=%s, API_KEY set=%s, KEY length=%d",
    ANTHROPIC_AVAILABLE, bool(ANTHROPIC_API_KEY), len(ANTHROPIC_API_KEY)
)

# Database: Use PostgreSQL if DATABASE_URL is set and connection works, otherwise SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = False  # Will be set to True after successful connection test

def _test_postgres_connection() -> bool:
    """Test if PostgreSQL connection works."""
    if not DATABASE_URL or not POSTGRES_AVAILABLE:
        return False
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
        conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL connection failed, falling back to SQLite: {e}")
        return False

USE_POSTGRES = _test_postgres_connection()

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
    "phase2": 39,      # After 3+ docs — legal review
    "phase3": 150,     # Docs verified — processing
    "phase4": 110,     # Filing window opens
    "total_service": 299,
    "prepay": 254,     # 15% discount for full upfront payment
    "prepay_savings": 45,
    "antecedentes_service": 49,   # We handle certificate + apostille + translation
    "govt_fees_service": 29,      # We handle 790 tax form payments
    "gov_fee": 38.28,
    "tie_card": 16,
}

# =============================================================================
# CONVERSATION STATES
# =============================================================================

(
    ST_WELCOME,
    ST_COUNTRY,
    ST_FULL_NAME,
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
    ST_PAY_PHASE4,
    ST_CONTACT,
    ST_HUMAN_MSG,
    ST_ENTER_REFERRAL_CODE,
    ST_FAQ_CATEGORY,
) = range(22)

# =============================================================================
# REFERRAL SYSTEM
# =============================================================================

REFERRAL_CREDIT_AMOUNT = 25      # €25 per referral
REFERRAL_CREDIT_CAP = 299        # Max credits (full service)
REFERRAL_CASH_PERCENT = 0.10     # 10% cash after cap
REFERRAL_FRIEND_DISCOUNT = 25    # €25 off for friend

# =============================================================================
# COUNTRY DATA (no slang greetings — professional tone)
# =============================================================================

COUNTRIES = {
    "ma": {"name": "Marruecos", "flag": "🇲🇦", "demonym": "marroquí"},
    "co": {"name": "Colombia", "flag": "🇨🇴", "demonym": "colombiano/a"},
    "ve": {"name": "Venezuela", "flag": "🇻🇪", "demonym": "venezolano/a"},
    "pe": {"name": "Perú", "flag": "🇵🇪", "demonym": "peruano/a"},
    "ec": {"name": "Ecuador", "flag": "🇪🇨", "demonym": "ecuatoriano/a"},
    "ar": {"name": "Argentina", "flag": "🇦🇷", "demonym": "argentino/a"},
    "cn": {"name": "China", "flag": "🇨🇳", "demonym": "chino/a"},
    "ua": {"name": "Ucrania", "flag": "🇺🇦", "demonym": "ucraniano/a"},
    "hn": {"name": "Honduras", "flag": "🇭🇳", "demonym": "hondureño/a"},
    "do": {"name": "Rep. Dominicana", "flag": "🇩🇴", "demonym": "dominicano/a"},
    "pk": {"name": "Pakistán", "flag": "🇵🇰", "demonym": "pakistaní"},
    "bo": {"name": "Bolivia", "flag": "🇧🇴", "demonym": "boliviano/a"},
    "br": {"name": "Brasil", "flag": "🇧🇷", "demonym": "brasileño/a"},
    "py": {"name": "Paraguay", "flag": "🇵🇾", "demonym": "paraguayo/a"},
    "ni": {"name": "Nicaragua", "flag": "🇳🇮", "demonym": "nicaragüense"},
    "cu": {"name": "Cuba", "flag": "🇨🇺", "demonym": "cubano/a"},
    "ng": {"name": "Nigeria", "flag": "🇳🇬", "demonym": "nigeriano/a"},
    "sn": {"name": "Senegal", "flag": "🇸🇳", "demonym": "senegalés/a"},
    "gt": {"name": "Guatemala", "flag": "🇬🇹", "demonym": "guatemalteco/a"},
    "sv": {"name": "El Salvador", "flag": "🇸🇻", "demonym": "salvadoreño/a"},
    "in": {"name": "India", "flag": "🇮🇳", "demonym": "indio/a"},
    "bd": {"name": "Bangladesh", "flag": "🇧🇩", "demonym": "bangladesí"},
    "ph": {"name": "Filipinas", "flag": "🇵🇭", "demonym": "filipino/a"},
    "gh": {"name": "Ghana", "flag": "🇬🇭", "demonym": "ghanés/a"},
    "other": {"name": "Otro país", "flag": "🌍", "demonym": ""},
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
        r"\bprecio\b", r"\bcuest[ao]\b", r"\bcuánto cuesta\b", r"\btarifa\b",
        r"\bcost[oe]\b", r"\bcobr", r"\bdinero\b",
    ],
    "documents": [
        r"\bdocumento", r"\bpapeles\b", r"\bqué necesito\b",
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
        r"\bcontrato\b", r"\bempleo\b", r"\boferta de trabajo\b",
        r"\bempleador\b", r"\bpatrón\b", r"\bvulnerab",
    ],
    "family": [
        r"\bhij[oa]s?\b", r"\bmenor", r"\bfamilia\b", r"\bbebé\b",
        r"\bniñ[oa]s?\b", r"\besposa?\b", r"\bmarido\b", r"\bpareja\b",
        r"\breagrupación\b",
    ],
    "deadline": [
        r"\bplazo\b", r"\bfecha\b", r"\bcuándo\b", r"\bdeadline\b",
        r"\babril\b", r"\bjunio\b",
    ],
    "asylum": [
        r"\basilo\b", r"\brefugi", r"\bprotección internacional\b",
        r"\btarjeta roja\b",
    ],
    "trust": [
        r"\bestafa\b", r"\breal\b", r"\bverdad\b", r"\bmentira\b",
        r"\blegítim[oa]\b",
    ],
    "online_submission": [
        r"\bpresencial\b", r"\btelemátic", r"\bonline\b",
        r"\bcómo presento\b", r"\bdónde presento\b",
    ],
    "no_empadronamiento": [
        r"\bno tengo empadronamiento\b", r"\bsin empadronamiento\b",
        r"\bno.*empadronad[oa]\b", r"\bpadrón\b",
    ],
    "travel": [
        r"\bviajar\b", r"\bsalir de espa\xf1a\b", r"\bsalir.*mientras\b",
        r"\bviajar.*mientras\b",
    ],
    "expired_passport": [
        r"\bpasaporte.*vencido\b", r"\bpasaporte.*caducado\b",
        r"\brenovar pasaporte\b", r"\bsin pasaporte\b",
    ],
    "denial": [
        r"\bdeneg", r"\brecurso\b", r"\bsi me dicen que no\b",
        r"\bqu\xe9 pasa si no\b",
    ],
    "nationality": [
        r"\bnacionalidad\b", r"\bcolombian[oa]\b", r"\bvenezolan[oa]\b",
        r"\bperuan[oa]\b", r"\bpa\xeds\b",
    ],
    "tourist_entry": [
        r"\bturista\b", r"\bvisa\b", r"\bme qued[eé]\b", r"\bquedado\b",
    ],
    "prior_denial": [
        r"\bdenegaron\b", r"\bdenegado\b", r"\brechazaron\b", r"\bnegaron\b",
        r"\barraigo\b",
    ],
    "expulsion": [
        r"\bexpulsi\xf3n\b", r"\bexpulsar\b", r"\bdeportar\b",
    ],
    "criminal_cert": [
        r"\bcertificado.*antecedentes\b", r"\bapostilla\b",
        r"\bantecedentes\b",
    ],
    "response_time": [
        r"\bcu\xe1nto tarda\b", r"\brespuesta\b", r"\bresoluci\xf3n\b",
    ],
    "work_while_waiting": [
        r"\btrabajar.*mientras\b", r"\bprovisional\b",
        r"\btrabajar\b", r"\btrabajo\b", r"\bautónom[oa]\b",
    ],
    "payment_phases": [
        r"\bfases?\b", r"\bfase 1\b", r"\bfase 2\b", r"\bfase 3\b",
        r"\bfase 4\b", r"\bpagar\b",
    ],
    "permit_type": [
        r"\bqu\xe9 permiso\b", r"\bresidencia\b", r"\btarjeta\b", r"\bTIE\b",
    ],
    "spanish_nationality": [
        r"\bnacionalidad espa\xf1ola\b", r"\bciudadan\xeda\b",
    ],
    "safety": [
        r"\bsegur[oa]\b", r"\bmiedo\b", r"\briesgo\b",
    ],
    "scam_accelerate": [
        r"\bacelerar\b", r"\brápido\b", r"\bpagar.*más\b", r"\burgente\b",
    ],
    "why_now": [
        r"\bpor qu\xe9 ahora\b", r"\bpor qu\xe9 no antes\b",
    ],
    "tiempo_espana": [
        r"\bcuánto tiempo\b", r"\baños\b", r"\bmeses\b", r"\bllevo\b",
    ],
}

# =============================================================================
# FAQ CATEGORIES — Accordion/collapsible navigation
# =============================================================================

FAQ_CATEGORIES = {
    "cat_req": {
        "title": "📋 Requisitos Básicos",
        "keys": [
            "requisitos", "contrato_trabajo", "nacionalidad", "tiempo_espana",
            "turista", "denegacion_previa", "orden_expulsion", "solicitantes_asilo",
        ],
    },
    "cat_ant": {
        "title": "🔍 Antecedentes Penales",
        "keys": [
            "antecedentes", "certificado_antecedentes",
            "antecedentes_dificil", "validez_antecedentes",
        ],
    },
    "cat_doc": {
        "title": "📄 Documentos Necesarios",
        "keys": [
            "documentos_necesarios", "prueba_llegada", "prueba_permanencia",
            "sin_empadronamiento", "documentos_otro_nombre", "traduccion",
            "pasaporte_vencido", "pasaporte_perdido",
        ],
    },
    "cat_pro": {
        "title": "⏰ Proceso y Plazos",
        "keys": [
            "plazos", "como_presentar", "presentar_antes", "plazo_vencido",
            "tiempo_respuesta", "trabajar_mientras_espero",
            "salir_espana", "denegacion",
        ],
    },
    "cat_cos": {
        "title": "💰 Costos y Pagos",
        "keys": [
            "costo", "por_que_pagar", "solo_sin_abogado", "fases_pago",
        ],
    },
    "cat_dep": {
        "title": "✅ Después de la Solicitud",
        "keys": [
            "que_permiso", "trabajar_legal", "viajar",
            "traer_familia", "nacionalidad_espanola",
        ],
    },
    "cat_mie": {
        "title": "🛡 Miedos Comunes",
        "keys": [
            "seguridad_datos", "es_real", "por_que_ahora", "estafa_acelerar",
        ],
    },
}

# =============================================================================
# FAQ DATABASE — 41 entries, professional tone
# =============================================================================

FAQ = {
    # === REQUISITOS BÁSICOS ===
    "requisitos": {
        "title": "¿Cuáles son los requisitos?",
        "keywords": ["requisito", "necesito", "califico", "puedo aplicar", "elegible", "condicion"],
        "text": (
            "*¿Cuáles son los requisitos para la regularización 2026?*\n\n"
            "Debes demostrar:\n"
            "1. Estar en España *antes del 31 de diciembre de 2025*.\n"
            "2. Al menos *5 meses de permanencia continuada*.\n"
            "3. *No tener antecedentes penales graves* en España ni en tu país de origen.\n"
            "4. No representar una amenaza para el orden público."
        ),
    },
    "contrato_trabajo": {
        "title": "¿Necesito contrato de trabajo?",
        "keywords": ["contrato", "oferta", "empleador", "vulnerable", "vulnerabilidad",
                     "patron", "sin empleo", "me piden contrato"],
        "text": (
            "*¿Necesito un contrato de trabajo para aplicar?*\n\n"
            "*NO.* Este decreto incluye una \"cláusula de vulnerabilidad\" — "
            "se presume que cualquier persona en situación irregular es vulnerable. "
            "*No necesitas oferta de empleo* ni contrato para aplicar."
        ),
    },
    "nacionalidad": {
        "title": "¿Importa mi nacionalidad?",
        "keywords": ["nacionalidad", "país", "colombiano", "venezolano", "peruano",
                     "cualquier país"],
        "text": (
            "*¿Importa mi nacionalidad?*\n\n"
            "No. El decreto aplica a *todas las nacionalidades* sin distinción. "
            "Aunque la mayoría serán latinoamericanos (~90%), cualquier persona "
            "que cumpla los requisitos puede aplicar."
        ),
    },
    "tiempo_espana": {
        "title": "¿Cuánto tiempo debo llevar en España?",
        "keywords": ["cuánto tiempo", "años", "meses", "llevo", "permanencia"],
        "text": (
            "*¿Cuánto tiempo debo llevar en España?*\n\n"
            "Debes haber llegado a España *antes del 31 de diciembre de 2025* "
            "y demostrar al menos *5 meses de permanencia continuada* al momento "
            "de presentar tu solicitud."
        ),
    },
    "turista": {
        "title": "¿Puedo aplicar si entré como turista?",
        "keywords": ["turista", "visa", "me quedé", "quedado", "overstay"],
        "text": (
            "*¿Puedo aplicar si entré como turista y me quedé?*\n\n"
            "Sí. La forma de entrada *no importa*. Lo que importa es demostrar "
            "que estabas en España antes del 31/12/2025 y que has permanecido "
            "de forma continuada."
        ),
    },
    "denegacion_previa": {
        "title": "¿Puedo aplicar si me denegaron antes?",
        "keywords": ["denegaron", "denegado", "rechazaron", "negaron",
                     "denegación previa", "me rechazaron"],
        "text": (
            "*¿Puedo aplicar si ya me denegaron un permiso antes?*\n\n"
            "Sí, puedes aplicar. Una denegación previa de arraigo u otro permiso "
            "*no te descalifica* automáticamente. Incluso puedes tener un arraigo "
            "en trámite y solicitar esta regularización en paralelo."
        ),
    },
    "orden_expulsion": {
        "title": "¿Puedo aplicar con orden de expulsión?",
        "keywords": ["expulsión", "deportación", "orden", "expulsar", "deportar"],
        "text": (
            "*¿Puedo aplicar si tengo una orden de expulsión?*\n\n"
            "Depende. Si la orden está en vigor y activa, probablemente no. "
            "Consulta tu caso específico con un abogado antes de presentar."
        ),
    },
    "solicitantes_asilo": {
        "title": "¿Qué pasa con solicitantes de asilo?",
        "keywords": ["asilo", "refugi", "protección internacional", "tarjeta roja"],
        "text": (
            "*¿Qué pasa con los solicitantes de asilo?*\n\n"
            "Los solicitantes de protección internacional que hayan presentado "
            "su solicitud antes del 31/12/2025 también pueden acogerse a esta "
            "regularización, con requisitos específicos."
        ),
    },

    # === ANTECEDENTES PENALES ===
    "antecedentes": {
        "title": "¿Qué pasa si tengo antecedentes?",
        "keywords": ["antecedente", "penal", "criminal", "delito", "récord"],
        "text": (
            "*¿Qué pasa si tengo antecedentes penales?*\n\n"
            "Depende de la gravedad. Delitos menores generalmente no descalifican. "
            "Delitos graves (violencia, narcotráfico, delitos sexuales) sí pueden "
            "descalificarte. También se revisará que no tengas problemas graves "
            "con la policía u otros cuerpos de seguridad."
        ),
    },
    "certificado_antecedentes": {
        "title": "¿Necesito certificado de mi país?",
        "keywords": ["certificado antecedentes", "apostilla", "legalizado", "traducido",
                     "obtener antecedentes", "cómo consigo", "pedir antecedentes"],
        "text": (
            "*¿Necesito certificado de antecedentes de mi país?*\n\n"
            "Sí. Necesitas certificado de antecedentes penales de tu país de origen, "
            "debidamente *legalizado o apostillado* y traducido si no está en español.\n\n"
            "Solicítalo *YA* — los consulados se saturarán cerca de abril.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📌 *IMPORTANTE*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "• El certificado debe tener menos de 3 meses de antigüedad\n"
            "• Debe estar apostillado o legalizado\n"
            "• Si está en otro idioma, necesita traducción jurada en España\n\n"
            "Usa /antecedentes para ver instrucciones específicas para tu país.\n\n"
            "¿Tienes dudas? Escríbenos y te ayudamos."
        ),
    },
    "antecedentes_dificil": {
        "title": "¿Si es difícil obtener el certificado?",
        "keywords": ["difícil obtener", "tarda", "consulado saturado", "no llega",
                     "más de un mes"],
        "text": (
            "*¿Y si en mi país es difícil obtener el certificado?*\n\n"
            "Solicítalo con anticipación. Si tras solicitarlo pasa más de un mes "
            "sin recibirlo, podrás acreditarlo con el justificante de solicitud. "
            "Consulta con tu consulado las opciones disponibles."
        ),
    },
    "validez_antecedentes": {
        "title": "¿Cuánto tiempo de validez tienen?",
        "keywords": ["validez", "vigencia certificado", "caduca", "3 meses"],
        "text": (
            "*¿Cuánto tiempo de validez tienen los certificados de antecedentes?*\n\n"
            "Generalmente tienen validez de *3 meses*. Recomendamos solicitarlos "
            "en marzo 2026 para que estén vigentes al momento de presentar tu "
            "solicitud en abril-junio."
        ),
    },

    # === DOCUMENTOS NECESARIOS ===
    "documentos_necesarios": {
        "title": "¿Qué documentos necesito?",
        "keywords": ["documento", "papeles", "necesito", "falta", "preparar",
                     "qué necesito"],
        "text": (
            "*¿Qué documentos necesito para aplicar?*\n\n"
            "Documentos básicos:\n"
            "1. *Pasaporte vigente.*\n"
            "2. *Certificado de antecedentes penales* de tu país "
            "(legalizado y traducido).\n"
            "3. *Pruebas de presencia* en España antes del 31/12/2025.\n"
            "4. *Pruebas de permanencia continuada* de 5 meses."
        ),
    },
    "prueba_llegada": {
        "title": "¿Cómo demuestro presencia antes del 31/12?",
        "keywords": ["demostrar presencia", "sello entrada", "billete avión",
                     "31 diciembre", "primer documento"],
        "text": (
            "*¿Cómo demuestro que estaba en España antes del 31/12/2025?*\n\n"
            "El primer documento es clave: pasaporte con sello de entrada, "
            "billete de avión, o cualquier factura/recibo con tu nombre y "
            "fecha anterior al 31 de diciembre de 2025."
        ),
    },
    "prueba_permanencia": {
        "title": "¿Cómo demuestro los 5 meses?",
        "keywords": ["prueba residencia", "demostrar permanencia", "qué sirve",
                     "cómo demuestro", "qué documentos sirven", "5 meses"],
        "text": (
            "*¿Cómo demuestro los 5 meses de permanencia continuada?*\n\n"
            "Cualquier documento con tu nombre, dirección en España, y fecha: "
            "facturas de luz/agua/internet, contratos de alquiler, empadronamiento, "
            "recibos de envío de dinero, extractos bancarios, citas médicas, "
            "recibos de compras, recargas de abono transporte, recibos de paquetería "
            "(NACEX, SEUR, etc.), membresías de gimnasio, y más de 40 tipos de "
            "documentos públicos o privados."
        ),
    },
    "sin_empadronamiento": {
        "title": "¿Qué pasa si no tengo empadronamiento?",
        "keywords": ["no tengo empadronamiento", "sin empadronamiento", "no estoy empadronado",
                     "no me quieren empadronar", "padrón"],
        "text": (
            "*¿No tienes empadronamiento? No te preocupes.*\n\n"
            "El empadronamiento *NO es obligatorio*. Puedes demostrar residencia "
            "con: facturas de suministros, contrato de alquiler, extractos bancarios "
            "con dirección, cartas oficiales, recibos de paquetería, informes "
            "médicos, etc."
        ),
    },
    "documentos_otro_nombre": {
        "title": "¿Sirven documentos a nombre de otro?",
        "keywords": ["otro nombre", "nombre de otra persona", "factura no es mía",
                     "compañero"],
        "text": (
            "*¿Sirven los documentos a nombre de otra persona?*\n\n"
            "Parcialmente. Si vives con alguien y las facturas están a su nombre, "
            "necesitas documentos adicionales que te vinculen a esa dirección "
            "(contrato de subarrendamiento, declaración del titular, documentos "
            "propios con esa dirección)."
        ),
    },
    "traduccion": {
        "title": "¿Necesito traducir mis documentos?",
        "keywords": ["traducir", "traducción", "traductor jurado", "idioma", "otro idioma"],
        "text": (
            "*¿Necesito traducir mis documentos?*\n\n"
            "Los documentos en español no necesitan traducción. Los documentos "
            "en otros idiomas deben traducirse por *traductor jurado*."
        ),
    },
    "pasaporte_vencido": {
        "title": "¿Mi pasaporte puede estar vencido?",
        "keywords": ["pasaporte vencido", "pasaporte caducado", "renovar pasaporte",
                     "pasaporte expirado"],
        "text": (
            "*¿Mi pasaporte puede estar vencido?*\n\n"
            "*NO.* Tu pasaporte *DEBE* estar vigente. Si está vencido o próximo a "
            "vencer, renuévalo *AHORA* en tu consulado. No esperes a abril."
        ),
    },
    "pasaporte_perdido": {
        "title": "¿Qué hago si perdí mi pasaporte?",
        "keywords": ["perdí pasaporte", "sin pasaporte", "robaron pasaporte"],
        "text": (
            "*¿Qué pasa si perdí mi pasaporte?*\n\n"
            "Solicita uno nuevo en tu consulado *INMEDIATAMENTE*. Sin pasaporte "
            "vigente no podrás completar la solicitud."
        ),
    },

    # === PROCESO Y PLAZOS ===
    "plazos": {
        "title": "¿Cuándo puedo presentar?",
        "keywords": ["plazo", "fecha", "cuándo", "abril", "junio", "deadline"],
        "text": (
            "*¿Cuándo puedo presentar mi solicitud?*\n\n"
            "El plazo abre a principios de *abril de 2026* (fecha exacta por confirmar) "
            "y cierra el *30 de junio de 2026*. Son aproximadamente 3 meses. "
            "Es *improrrogable*."
        ),
    },
    "como_presentar": {
        "title": "¿Cómo se presenta la solicitud?",
        "keywords": ["cómo presento", "dónde presento", "presencial", "telemática",
                     "online", "internet"],
        "text": (
            "*¿Cómo se presenta la solicitud?*\n\n"
            "Se podrá presentar de forma *telemática (online)* o presencial. "
            "El gobierno recomienda la vía telemática para evitar colas y retrasos."
        ),
    },
    "presentar_antes": {
        "title": "¿Puedo presentar antes de abril?",
        "keywords": ["antes de abril", "adelantar", "ya presentar"],
        "text": (
            "*¿Puedo presentar antes de abril?*\n\n"
            "No. El sistema no aceptará solicitudes hasta que abra el plazo oficial. "
            "Pero debes tener tu documentación lista *ANTES* de abril."
        ),
    },
    "plazo_vencido": {
        "title": "¿Qué pasa si no llego a junio?",
        "keywords": ["no llego", "tarde", "después de junio", "improrrogable",
                     "último momento"],
        "text": (
            "*¿Qué pasa si no llego a presentar antes del 30 de junio?*\n\n"
            "Pierdes la oportunidad. Es un plazo *cerrado e improrrogable*. "
            "No esperes al último momento — prepara todo ahora."
        ),
    },
    "tiempo_respuesta": {
        "title": "¿Cuánto tardan en responder?",
        "keywords": ["tardan", "resolución", "respuesta", "cuánto esperar",
                     "cuánto tarda"],
        "text": (
            "*¿Cuánto tardan en responder?*\n\n"
            "El plazo máximo de tramitación es de *3 meses*. Pero con la mera "
            "admisión a trámite (máximo 15 días), ya podrás residir y trabajar "
            "provisionalmente."
        ),
    },
    "trabajar_mientras_espero": {
        "title": "¿Puedo trabajar mientras espero?",
        "keywords": ["trabajar mientras", "provisional", "trabajar legalmente",
                     "permiso trabajo"],
        "text": (
            "*¿Puedo trabajar mientras espero la resolución?*\n\n"
            "*SÍ.* Desde que tu solicitud sea admitida a trámite (máximo 15 días), "
            "podrás trabajar legalmente en cualquier sector y en cualquier parte "
            "de España."
        ),
    },
    "salir_espana": {
        "title": "¿Puedo salir de España mientras espero?",
        "keywords": ["salir de españa", "viajar mientras", "ir a mi país",
                     "vuelo", "salir"],
        "text": (
            "*¿Puedo salir de España mientras espero la resolución?*\n\n"
            "*NO recomendado.* Salir podría interpretarse como abandono de tu "
            "solicitud o romper la continuidad de residencia. Espera hasta tener "
            "el permiso en mano."
        ),
    },
    "denegacion": {
        "title": "¿Qué pasa si me niegan?",
        "keywords": ["denegar", "denegación", "rechazo", "recurso", "si me dicen que no",
                     "qué pasa si no"],
        "text": (
            "*¿Qué pasa si me niegan la solicitud?*\n\n"
            "Puedes recurrir la decisión. Tendrás plazo para presentar "
            "alegaciones o recurso. Un abogado puede ayudarte con esto."
        ),
    },

    # === COSTOS Y PAGOS ===
    "costo": {
        "title": "¿Cuánto cuesta la regularización?",
        "keywords": ["precio", "cuesta", "cuánto cuesta", "tarifa", "caro", "barato",
                     "dinero", "costo", "tasas", "modelo 790", "gobierno"],
        "text": (
            "💰 *¿Cuánto Cuesta la Regularización?*\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 NUESTRO SERVICIO\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "*Pago por fases:* €299 total\n"
            "*Pago único:* €254 (ahorras €45) ⭐\n\n"
            "📌 *Fase 1 — GRATIS*\n"
            "• Verificación de elegibilidad\n"
            "• Subida de documentos\n\n"
            "📌 *Fase 2 — €39*\n"
            "• Revisión legal completa\n"
            "• Verificación de documentos\n\n"
            "📌 *Fase 3 — €150*\n"
            "• Preparación del expediente\n"
            "• Redacción de escritos legales\n\n"
            "📌 *Fase 4 — €110*\n"
            "• Presentación de solicitud\n"
            "• Seguimiento hasta resolución\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💳 OPCIONES DE PAGO\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "*⭐ Pago único: €254*\n"
            "Ahorras €45 (15% descuento)\n\n"
            "*Por fases: €299*\n"
            "Paga cada fase cuando estés listo.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 DESCUENTOS\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "• €25 con código de amigo\n"
            "• Hasta €299 por referir amigos\n"
            "• 15% si pagas todo de una vez\n\n"
            "_Los descuentos son acumulables._\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 SERVICIOS ADICIONALES\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "*Antecedentes penales: +€49*\n"
            "Solicitud + apostilla + traducción\n\n"
            "*Gestión tasas gobierno: +€29*\n"
            "Pagamos las tasas 790 por ti\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🏛️ TASAS DEL GOBIERNO\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "El gobierno cobra tasas adicionales:\n\n"
            "• Tasa 790-052: ~€16-20\n"
            "• Tasa 790-012 (TIE): ~€16-21\n"
            "• Antecedentes España: ~€3.86\n\n"
            "*Total gobierno: ~€40-50*\n\n"
            "Estas se pagan directamente al gobierno.\n"
            "💡 Por €29, las gestionamos por ti.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ IMPORTANTE\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "En 2005, el *10-20% de solicitudes fueron DENEGADAS* por errores "
            "en documentación.\n\n"
            "Nuestros abogados revisan cada detalle."
        ),
    },
    "por_que_pagar": {
        "title": "¿Por qué usar un servicio?",
        "keywords": ["por qué servicio", "gratis", "necesito abogado", "por qué pagar"],
        "text": (
            "*¿Por qué usar un servicio si el trámite es \"gratuito\"?*\n\n"
            "Nuestro servicio cubre: verificación de elegibilidad, revisión legal "
            "de documentos, preparación del expediente, presentación telemática, "
            "y seguimiento hasta la resolución.\n\n"
            "Un expediente mal preparado puede causar denegación — en 2005, el "
            "10-20% fueron denegados, muchos por errores evitables."
        ),
    },
    "solo_sin_abogado": {
        "title": "¿Puedo hacerlo yo solo?",
        "keywords": ["yo solo", "sin abogado", "hacer yo", "necesario abogado"],
        "text": (
            "*¿Puedo hacerlo yo solo sin abogado?*\n\n"
            "Técnicamente sí. Pero un solo día de \"vacío\" en tu prueba de "
            "permanencia, un documento mal presentado, o un error en el formulario "
            "puede significar denegación. Cada caso es distinto."
        ),
    },
    "fases_pago": {
        "title": "¿Qué incluye cada fase?",
        "keywords": ["fase", "etapa", "incluye", "paso"],
        "text": (
            "*¿Qué incluye cada fase de pago?*\n\n"
            "*Fase 1 (GRATIS):* Verificación de elegibilidad + subir documentos.\n"
            "*Fase 2 (€39):* Revisión legal completa.\n"
            "*Fase 3 (€150):* Preparación del expediente.\n"
            "*Fase 4 (€110):* Presentación y seguimiento."
        ),
    },

    # === DESPUÉS DE LA SOLICITUD ===
    "que_permiso": {
        "title": "¿Qué permiso voy a recibir?",
        "keywords": ["qué permiso", "autorización", "residencia temporal", "TIE"],
        "text": (
            "*¿Qué permiso voy a recibir?*\n\n"
            "Autorización de residencia temporal con vigencia inicial de "
            "*1 año*, renovable. Después te incorporas a las figuras ordinarias "
            "del Reglamento de Extranjería."
        ),
    },
    "trabajar_legal": {
        "title": "¿Podré trabajar legalmente?",
        "keywords": ["trabajar legalmente", "permiso trabajo", "autónomo", "alta"],
        "text": (
            "*¿Podré trabajar legalmente?*\n\n"
            "Sí. La autorización incluye *permiso de trabajo desde el primer día*, "
            "en cualquier sector y en cualquier parte de España. También puedes "
            "darte de alta como autónomo."
        ),
    },
    "viajar": {
        "title": "¿Podré viajar fuera de España?",
        "keywords": ["viajar después", "salir después", "TIE viajar"],
        "text": (
            "*¿Podré viajar fuera de España?*\n\n"
            "Sí, una vez tengas el permiso (tarjeta TIE) en mano. Durante el "
            "proceso de solicitud, no recomendamos salir del país."
        ),
    },
    "traer_familia": {
        "title": "¿Podré traer a mi familia?",
        "keywords": ["familia", "hijo", "hija", "menor", "esposa", "pareja",
                     "reagrupación"],
        "text": (
            "*¿Podré traer a mi familia?*\n\n"
            "Los hijos menores que estén en España pueden regularizarse "
            "simultáneamente. Para otros familiares, después podrás solicitar "
            "*reagrupación familiar* (proceso separado con requisitos adicionales)."
        ),
    },
    "nacionalidad_espanola": {
        "title": "¿Me lleva a la nacionalidad española?",
        "keywords": ["nacionalidad española", "ciudadanía", "iberoamericano",
                     "cuántos años"],
        "text": (
            "*¿Este permiso me lleva a la nacionalidad española?*\n\n"
            "Sí, eventualmente. Para ciudadanos de países iberoamericanos "
            "(Colombia, Venezuela, Perú, etc.): tras *2 años* de residencia legal. "
            "Para otras nacionalidades: generalmente 10 años."
        ),
    },

    # === MIEDOS COMUNES ===
    "seguridad_datos": {
        "title": "¿Es seguro dar mis datos?",
        "keywords": ["seguro", "datos", "deportar", "perseguir", "miedo", "riesgo"],
        "text": (
            "*¿Es seguro dar mis datos? ¿Me pueden deportar si me rechazan?*\n\n"
            "El proceso está diseñado para proteger, no para perseguir. Una "
            "denegación *NO activa automáticamente* un proceso de expulsión. "
            "Miles de personas aplicaron en regularizaciones anteriores sin "
            "consecuencias negativas por intentar."
        ),
    },
    "es_real": {
        "title": "¿Esto es real o es una estafa?",
        "keywords": ["estafa", "real", "fraude", "verdad", "legítimo", "mentira"],
        "text": (
            "*¿Esto es real o es una estafa?*\n\n"
            "Es 100% real. El Consejo de Ministros aprobó la tramitación del "
            "Real Decreto el 27 de enero de 2026. Puedes verificarlo en "
            "lamoncloa.gob.es y en el BOE cuando se publique el texto definitivo."
        ),
    },
    "por_que_ahora": {
        "title": "¿Por qué ahora y no antes?",
        "keywords": ["por qué ahora", "por qué no antes", "1986", "historia"],
        "text": (
            "*¿Por qué ahora y no antes?*\n\n"
            "Gobiernos de distintos colores políticos han realizado "
            "regularizaciones desde 1986 hasta 2005. Esta retoma una "
            "iniciativa ciudadana respaldada por más de 700.000 firmas "
            "y apoyada por una amplia mayoría del Congreso."
        ),
    },
    "estafa_acelerar": {
        "title": "¿Puedo pagar para \"acelerar\"?",
        "keywords": ["acelerar", "rápido", "urgente", "pagar más"],
        "text": (
            "*¿Qué pasa si alguien me cobra por \"acelerar\" el trámite?*\n\n"
            "⚠️ *CUIDADO.* No existe forma de \"acelerar\" el proceso oficial. "
            "Desconfía de quien te ofrezca esto. Trabaja solo con profesionales "
            "registrados y verifica sus credenciales."
        ),
    },

    # === REFERRAL (kept for /referidos command) ===
    "referidos": {
        "title": "Programa de referidos",
        "keywords": ["referido", "código", "amigo", "descuento", "compartir", "ganar", "crédito"],
        "text": (
            "*Programa de referidos:*\n\n"
            "*Para tu amigo:*\n"
            "Si alguien usa tu código al registrarse, recibe €25 de descuento "
            "en su primer pago.\n\n"
            "*Para ti:*\n"
            "Cuando pagues tu Fase 2 (€39) y tu amigo también pague, "
            "ganas €25 de crédito que se aplica a tus siguientes pagos.\n\n"
            "Puedes ver tu código y estadísticas con el comando /referidos."
        ),
    },
}

# =============================================================================
# DATABASE
# =============================================================================

def get_connection():
    """Get database connection (PostgreSQL if DATABASE_URL set, else SQLite)."""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def db_param(index: int = 1) -> str:
    """Return the parameter placeholder for the current database."""
    return "%s" if USE_POSTGRES else "?"


def init_db():
    conn = get_connection()
    c = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL schema
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
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
            expediente_ready INTEGER DEFAULT 0,
            state TEXT DEFAULT 'new',
            escalation_queue TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS cases (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            case_number TEXT UNIQUE,
            status TEXT DEFAULT 'onboarding',
            progress INTEGER DEFAULT 0,
            assigned_lawyer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            doc_type TEXT,
            file_id TEXT,
            ocr_text TEXT,
            detected_type TEXT,
            validation_score INTEGER DEFAULT 0,
            validation_notes TEXT,
            status TEXT DEFAULT 'pending',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            direction TEXT,
            content TEXT,
            intent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        logger.info("Database: PostgreSQL initialized")
    else:
        # SQLite schema
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
            expediente_ready INTEGER DEFAULT 0,
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
        logger.info("Database: SQLite initialized")

    # Add referral columns to users table (both PostgreSQL and SQLite)
    referral_columns = [
        ("referral_code", "VARCHAR(20)"),
        ("referred_by_code", "VARCHAR(20)"),
        ("referred_by_user_id", "BIGINT"),
        ("referral_count", "INTEGER DEFAULT 0"),
        ("referral_credits_earned", "REAL DEFAULT 0"),
        ("referral_credits_used", "REAL DEFAULT 0"),
        ("referral_cash_earned", "REAL DEFAULT 0"),
        ("friend_discount_applied", "INTEGER DEFAULT 0"),
    ]
    for col_name, col_type in referral_columns:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            conn.commit()
        except Exception:
            conn.rollback()  # Reset transaction state for PostgreSQL

    # Create referrals table
    if USE_POSTGRES:
        c.execute("""CREATE TABLE IF NOT EXISTS referrals (
            id SERIAL PRIMARY KEY,
            referrer_user_id BIGINT NOT NULL,
            referrer_code VARCHAR(20) NOT NULL,
            referred_user_id BIGINT NOT NULL,
            status VARCHAR(20) DEFAULT 'registered',
            credit_amount REAL DEFAULT 0,
            credit_awarded_at TIMESTAMP,
            cash_amount REAL DEFAULT 0,
            friend_total_paid REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(referrer_user_id, referred_user_id)
        )""")
    else:
        c.execute("""CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_user_id INTEGER NOT NULL,
            referrer_code VARCHAR(20) NOT NULL,
            referred_user_id INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'registered',
            credit_amount REAL DEFAULT 0,
            credit_awarded_at TIMESTAMP,
            cash_amount REAL DEFAULT 0,
            friend_total_paid REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(referrer_user_id, referred_user_id)
        )""")
    conn.commit()

    # Create referral_events table for audit
    if USE_POSTGRES:
        c.execute("""CREATE TABLE IF NOT EXISTS referral_events (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            event_type VARCHAR(30) NOT NULL,
            amount REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    else:
        c.execute("""CREATE TABLE IF NOT EXISTS referral_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_type VARCHAR(30) NOT NULL,
            amount REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    conn.commit()

    # Create indexes for referral system
    try:
        c.execute("CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referrer_code)")
        conn.commit()
    except Exception:
        conn.rollback()

    # Add AI analysis columns to documents table
    doc_columns = [
        ("ai_analysis", "TEXT"),
        ("ai_confidence", "REAL DEFAULT 0"),
        ("ai_type", "VARCHAR(50)"),
        ("extracted_name", "VARCHAR(255)"),
        ("extracted_address", "TEXT"),
        ("extracted_date", "VARCHAR(50)"),
        ("approved", "INTEGER DEFAULT 0"),  # 0=pending, 1=approved, -1=rejected
        ("document_country", "VARCHAR(50)"),
        ("expiry_date", "VARCHAR(50)"),
        ("issues", "TEXT"),
    ]
    for col_name, col_type in doc_columns:
        try:
            c.execute(f"ALTER TABLE documents ADD COLUMN {col_name} {col_type}")
            conn.commit()
        except Exception:
            conn.rollback()

    conn.commit()
    conn.close()


# =============================================================================
# CLAUDE VISION API DOCUMENT ANALYSIS
# =============================================================================

def extract_json_from_response(text: str) -> str:
    """Extract JSON from response, handling markdown code blocks."""
    text = text.strip()

    # Handle markdown code blocks: ```json, ```JSON, ``` etc.
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```)
        lines = lines[1:]
        # Remove last line if it's just ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    # Also try to find JSON object if there's text before/after
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]

    return text.strip()


async def analyze_document_with_claude(image_bytes: bytes) -> Dict:
    """
    Analyze a document image using Claude Vision API.
    Returns structured analysis with type, confidence, and extracted data.
    """
    if not ANTHROPIC_AVAILABLE or not ANTHROPIC_API_KEY:
        logger.warning("Claude Vision API not available: ANTHROPIC_AVAILABLE=%s, API_KEY set=%s",
                      ANTHROPIC_AVAILABLE, bool(ANTHROPIC_API_KEY))
        return {
            "success": False,
            "error": "Claude Vision API not available",
            "type": "unknown",
            "confidence": 0.0,
        }

    response_text = ""
    try:
        logger.info("DEBUG: Creating Anthropic client (key length=%d, starts_with=%s)",
                     len(ANTHROPIC_API_KEY), ANTHROPIC_API_KEY[:8] + "..." if len(ANTHROPIC_API_KEY) > 8 else "SHORT")
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        logger.info("DEBUG: Sending image to Claude Vision API (%d bytes, base64 length=%d)",
                     len(image_bytes), len(image_base64))

        # Determine media type (assume JPEG for photos from Telegram)
        media_type = "image/jpeg"

        prompt = """Analiza este documento y devuelve SOLO un objeto JSON válido, sin texto adicional ni bloques de código:

{
    "type": "passport|nie|dni|utility_bill|bank_statement|rental_contract|work_contract|antecedentes|empadronamiento|other",
    "confidence": 0.85,
    "is_identity_document": true,
    "is_proof_of_residency": false,
    "extracted_name": "Juan García López",
    "extracted_address": null,
    "extracted_date": "2024-01-15",
    "document_country": "ES",
    "expiry_date": "2030-01-15",
    "issues": []
}

IMPORTANTE: El campo "confidence" debe ser un número decimal entre 0.0 y 1.0 (ejemplo: 0.85, 0.92, 0.75).

Tipos de documento:
- passport: Pasaporte
- nie: Número de Identidad de Extranjero (tarjeta verde)
- dni: Documento Nacional de Identidad español
- utility_bill: Factura de luz, agua, gas, internet, teléfono
- bank_statement: Extracto bancario o carta del banco
- rental_contract: Contrato de alquiler
- work_contract: Contrato de trabajo o nóminas
- antecedentes: Certificado de antecedentes penales
- empadronamiento: Certificado de empadronamiento
- other: Otro documento

Problemas comunes a detectar:
- Documento borroso o ilegible
- Documento vencido
- Documento recortado o incompleto
- No se ve el nombre claramente
- No se ve la fecha claramente"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ],
                }
            ],
        )

        # Parse the response
        logger.info("DEBUG: API response received. stop_reason=%s, content_blocks=%d",
                     message.stop_reason, len(message.content))
        response_text = message.content[0].text.strip()
        logger.info("DEBUG: Raw response text (%d chars): %s", len(response_text), response_text[:800])

        # Extract JSON from response
        json_text = extract_json_from_response(response_text)
        logger.info("DEBUG: Extracted JSON (%d chars): %s", len(json_text), json_text[:500])

        try:
            analysis = json.loads(json_text)
        except json.JSONDecodeError as je:
            logger.error("DEBUG: JSON parse FAILED at pos %d: %s", je.pos, je.msg)
            logger.error("DEBUG: JSON text around error: ...%s...", json_text[max(0, je.pos-50):je.pos+50])
            raise

        logger.info("DEBUG: Parsed analysis keys: %s", list(analysis.keys()))

        # Ensure confidence is a float
        raw_confidence = analysis.get("confidence", 0)
        logger.info("DEBUG: Raw confidence value: %r (type: %s)", raw_confidence, type(raw_confidence).__name__)

        if isinstance(raw_confidence, str):
            # Handle string like "0.85" or "85%"
            raw_confidence = raw_confidence.replace("%", "").strip()
            try:
                raw_confidence = float(raw_confidence)
                if raw_confidence > 1:
                    raw_confidence = raw_confidence / 100  # Convert 85 to 0.85
            except ValueError:
                raw_confidence = 0.0
        elif isinstance(raw_confidence, (int, float)):
            raw_confidence = float(raw_confidence)
            if raw_confidence > 1:
                raw_confidence = raw_confidence / 100  # Convert 85 to 0.85
        else:
            raw_confidence = 0.0

        analysis["confidence"] = raw_confidence
        analysis["success"] = True
        analysis["raw_response"] = response_text

        logger.info("DEBUG: Final confidence after conversion: %f (type: %s)",
                     analysis["confidence"], type(analysis["confidence"]).__name__)
        logger.info("Claude Vision analysis: type=%s, confidence=%.2f, name=%s",
                     analysis.get('type'), analysis['confidence'],
                     analysis.get('extracted_name', 'N/A'))
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Claude Vision JSON parse error: {e}")
        logger.error(f"Raw response was: {response_text[:1000]}")
        return {
            "success": False,
            "error": f"JSON parse error: {str(e)}",
            "type": "unknown",
            "confidence": 0.0,
            "raw_response": response_text,
        }
    except Exception as e:
        logger.error(f"Claude Vision API error: {e}")
        logger.error(f"Response text: {response_text[:500] if response_text else 'empty'}")
        return {
            "success": False,
            "error": str(e),
            "type": "unknown",
            "confidence": 0.0,
        }


def get_doc_type_from_ai(ai_type: str) -> str:
    """Map AI-detected document type to our internal doc_type codes."""
    mapping = {
        "passport": "passport",
        "nie": "nie",
        "dni": "dni",
        "utility_bill": "utility",
        "bank_statement": "bank",
        "rental_contract": "rent",
        "work_contract": "work",
        "antecedentes": "antecedentes",
        "empadronamiento": "empadronamiento",
        "other": "other",
    }
    return mapping.get(ai_type, "other")


def _row_to_dict(row, cursor) -> Optional[Dict]:
    """Convert a database row to a dictionary."""
    if row is None:
        return None
    if USE_POSTGRES:
        cols = [desc[0] for desc in cursor.description]
        return dict(zip(cols, row))
    return dict(row)


def get_user(tid: int) -> Optional[Dict]:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT * FROM users WHERE telegram_id = {p}", (tid,))
    row = c.fetchone()
    result = _row_to_dict(row, c)
    conn.close()
    return result


def create_user(tid: int, first_name: str) -> Dict:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    if USE_POSTGRES:
        c.execute(f"INSERT INTO users (telegram_id, first_name) VALUES ({p}, {p}) ON CONFLICT (telegram_id) DO NOTHING", (tid, first_name))
    else:
        c.execute(f"INSERT OR IGNORE INTO users (telegram_id, first_name) VALUES ({p}, {p})", (tid, first_name))
    conn.commit()
    conn.close()
    return get_user(tid)


def update_user(tid: int, **kw):
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    fields = ", ".join(f"{k} = {p}" for k in kw)
    vals = list(kw.values()) + [tid]
    c.execute(f"UPDATE users SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = {p}", vals)
    conn.commit()
    conn.close()


def delete_user(tid: int):
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT id FROM users WHERE telegram_id = {p}", (tid,))
    row = c.fetchone()
    if row:
        uid = row[0]
        c.execute(f"DELETE FROM documents WHERE user_id = {p}", (uid,))
        c.execute(f"DELETE FROM cases WHERE user_id = {p}", (uid,))
        c.execute(f"DELETE FROM messages WHERE user_id = {p}", (uid,))
        c.execute(f"DELETE FROM users WHERE id = {p}", (uid,))
    conn.commit()
    conn.close()


def get_doc_count(tid: int) -> int:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT COUNT(*) FROM documents d JOIN users u ON d.user_id=u.id WHERE u.telegram_id={p}", (tid,))
    n = c.fetchone()[0]
    conn.close()
    return n


def get_approved_doc_count(tid: int) -> int:
    """Count only approved documents for a user."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT COUNT(*) FROM documents d JOIN users u ON d.user_id=u.id WHERE u.telegram_id={p} AND d.approved=1", (tid,))
    n = c.fetchone()[0]
    conn.close()
    return n


def get_pending_documents(limit: int = 20) -> List[Dict]:
    """Get documents pending admin review (approved=0)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"""
        SELECT d.*, u.telegram_id, u.first_name
        FROM documents d
        JOIN users u ON d.user_id = u.id
        WHERE d.approved = 0
        ORDER BY d.uploaded_at DESC
        LIMIT {limit}
    """)
    rows = c.fetchall()
    result = [_row_to_dict(r, c) for r in rows]
    conn.close()
    return result


def update_document_approval(doc_id: int, approved: int) -> bool:
    """Update document approval status. approved: 1=approved, -1=rejected"""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"UPDATE documents SET approved={p} WHERE id={p}", (approved, doc_id))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_document_by_id(doc_id: int) -> Optional[Dict]:
    """Get a document by its ID."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"""
        SELECT d.*, u.telegram_id, u.first_name
        FROM documents d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = {p}
    """, (doc_id,))
    row = c.fetchone()
    result = _row_to_dict(row, c)
    conn.close()
    return result


def get_user_docs(tid: int) -> List[Dict]:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT d.* FROM documents d JOIN users u ON d.user_id=u.id WHERE u.telegram_id={p} ORDER BY d.uploaded_at DESC", (tid,))
    rows = c.fetchall()
    result = [_row_to_dict(r, c) for r in rows]
    conn.close()
    return result


def get_user_doc_by_type(tid: int, doc_type: str) -> Optional[Dict]:
    """Get a user's existing document of a specific type, if any."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(
        f"SELECT d.* FROM documents d JOIN users u ON d.user_id=u.id "
        f"WHERE u.telegram_id={p} AND d.doc_type={p} ORDER BY d.uploaded_at DESC LIMIT 1",
        (tid, doc_type))
    row = c.fetchone()
    result = _row_to_dict(row, c)
    conn.close()
    return result


def delete_document(doc_id: int):
    """Delete a document by ID."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"DELETE FROM documents WHERE id={p}", (doc_id,))
    conn.commit()
    conn.close()


def save_document(
    tid: int,
    doc_type: str,
    file_id: str,
    ocr_text: str = "",
    detected_type: str = "",
    score: int = 0,
    notes: str = "",
    ai_analysis: str = "",
    ai_confidence: float = 0.0,
    ai_type: str = "",
    extracted_name: str = "",
    extracted_address: str = "",
    extracted_date: str = "",
    approved: int = 0,
    document_country: str = "",
    expiry_date: str = "",
    issues: str = "",
) -> int:
    """Save document and return the document ID."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"""INSERT INTO documents (
        user_id, doc_type, file_id, ocr_text, detected_type, validation_score, validation_notes,
        ai_analysis, ai_confidence, ai_type, extracted_name, extracted_address, extracted_date,
        approved, document_country, expiry_date, issues
    ) SELECT id, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}
    FROM users WHERE telegram_id = {p}""",
        (doc_type, file_id, ocr_text, detected_type, score, notes,
         ai_analysis, ai_confidence, ai_type, extracted_name, extracted_address, extracted_date,
         approved, document_country, expiry_date, issues, tid))
    conn.commit()

    # Get the inserted document ID
    if USE_POSTGRES:
        c.execute("SELECT lastval()")
    else:
        c.execute("SELECT last_insert_rowid()")
    doc_id = c.fetchone()[0]
    conn.close()
    return doc_id


def save_message(tid: int, direction: str, content: str, intent: str = ""):
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"""INSERT INTO messages (user_id, direction, content, intent)
        SELECT id, {p}, {p}, {p} FROM users WHERE telegram_id = {p}""",
        (direction, content[:500], intent, tid))
    conn.commit()
    conn.close()


def get_or_create_case(tid: int) -> Dict:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT c.* FROM cases c JOIN users u ON c.user_id=u.id WHERE u.telegram_id={p}", (tid,))
    case = c.fetchone()
    if not case:
        import random
        cn = f"PH-2026-{random.randint(1000, 9999)}"
        c.execute(f"INSERT INTO cases (user_id, case_number) SELECT id, {p} FROM users WHERE telegram_id={p}", (cn, tid))
        conn.commit()
        c.execute(f"SELECT * FROM cases WHERE case_number={p}", (cn,))
        case = c.fetchone()
    result = _row_to_dict(case, c)
    conn.close()
    return result


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
# REFERRAL FUNCTIONS
# =============================================================================

import random
import string

def generate_referral_code(user_id: int) -> str:
    """Generate unique referral code: NAME-XXXX

    Checks in order: full_name, first_name, Telegram first_name, "USER"
    """
    # Get user data to find the best name
    user = get_user(user_id)

    # Priority: full_name -> first_name -> "USER"
    name = None
    if user.get('full_name'):
        # Use first word of full name
        name = user['full_name'].split()[0]
    elif user.get('first_name'):
        name = user['first_name']

    clean_name = ''.join(c for c in (name or '').upper() if c.isalpha())[:8]
    if not clean_name:
        clean_name = "USER"

    conn = get_connection()
    c = conn.cursor()
    p = db_param()

    for _ in range(10):
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code = f"{clean_name}-{suffix}"
        c.execute(f"SELECT 1 FROM users WHERE referral_code = {p}", (code,))
        if not c.fetchone():
            conn.close()
            return code

    conn.close()
    return f"{clean_name}-{random.randint(10000, 99999)}"


def validate_referral_code(code: str) -> dict:
    """Validate referral code and return referrer info."""
    if not code or len(code) < 3:
        return {'valid': False, 'error': 'invalid_format'}

    code = code.upper().strip()

    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT telegram_id, first_name FROM users WHERE referral_code = {p}", (code,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {'valid': False, 'error': 'not_found'}

    return {
        'valid': True,
        'referrer_id': row[0],
        'referrer_name': row[1],
        'code': code
    }


def apply_referral_code_to_user(user_id: int, code: str, referrer_id: int) -> bool:
    """Store referral relationship."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()

    try:
        c.execute(f"""
            UPDATE users
            SET referred_by_code = {p}, referred_by_user_id = {p}
            WHERE telegram_id = {p} AND referred_by_code IS NULL
        """, (code, referrer_id, user_id))

        c.execute(f"""
            INSERT OR IGNORE INTO referrals (referrer_user_id, referrer_code, referred_user_id)
            VALUES ({p}, {p}, {p})
        """, (referrer_id, code, user_id))

        c.execute(f"""
            INSERT INTO referral_events (user_id, event_type, description)
            VALUES ({p}, 'code_used', {p})
        """, (user_id, f"Used code {code}"))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error applying referral: {e}")
        return False
    finally:
        conn.close()


def get_referral_stats(user_id: int) -> dict:
    """Get referral statistics for a user."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()

    c.execute(f"SELECT * FROM users WHERE telegram_id = {p}", (user_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return None

    user = _row_to_dict(row, c)

    c.execute(f"""
        SELECT r.*, u.first_name as referred_name
        FROM referrals r
        JOIN users u ON r.referred_user_id = u.telegram_id
        WHERE r.referrer_user_id = {p}
        ORDER BY r.created_at DESC LIMIT 10
    """, (user_id,))
    referrals = [_row_to_dict(r, c) for r in c.fetchall()]

    conn.close()

    earned = float(user.get('referral_credits_earned') or 0)
    used = float(user.get('referral_credits_used') or 0)

    return {
        'code': user.get('referral_code'),
        'count': user.get('referral_count') or 0,
        'credits_earned': earned,
        'credits_used': used,
        'credits_available': max(0, earned - used),
        'cash_earned': user.get('referral_cash_earned') or 0,
        'can_earn': user.get('phase2_paid') == 1,
        'referrals': referrals
    }


def credit_referrer(referred_user_id: int, payment_amount: float) -> dict:
    """Credit referrer when friend pays."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()

    try:
        c.execute(f"""
            SELECT r.referrer_user_id, r.credit_amount,
                   u.phase2_paid, u.referral_credits_earned
            FROM referrals r
            JOIN users u ON r.referrer_user_id = u.telegram_id
            WHERE r.referred_user_id = {p}
        """, (referred_user_id,))

        row = c.fetchone()
        if not row:
            conn.close()
            return {'credited': False, 'reason': 'no_referrer'}

        referrer_id = row[0]
        existing_credit = row[1] or 0
        phase2_paid = row[2] == 1
        credits_earned = float(row[3] or 0)

        if not phase2_paid:
            conn.close()
            return {'credited': False, 'reason': 'referrer_not_eligible'}

        if existing_credit > 0:
            conn.close()
            return {'credited': False, 'reason': 'already_credited'}

        if credits_earned >= REFERRAL_CREDIT_CAP:
            conn.close()
            return {'credited': False, 'reason': 'cap_reached'}

        credit_amount = min(REFERRAL_CREDIT_AMOUNT, REFERRAL_CREDIT_CAP - credits_earned)

        c.execute(f"""
            UPDATE referrals
            SET credit_amount = {p}, status = 'paid_phase2',
                credit_awarded_at = CURRENT_TIMESTAMP,
                friend_total_paid = {p}
            WHERE referred_user_id = {p}
        """, (credit_amount, payment_amount, referred_user_id))

        c.execute(f"""
            UPDATE users
            SET referral_credits_earned = referral_credits_earned + {p},
                referral_count = referral_count + 1
            WHERE telegram_id = {p}
        """, (credit_amount, referrer_id))

        c.execute(f"""
            INSERT INTO referral_events (user_id, event_type, amount, description)
            VALUES ({p}, 'credit_earned', {p}, 'Friend paid')
        """, (referrer_id, credit_amount))

        conn.commit()
        return {'credited': True, 'amount': credit_amount, 'referrer_id': referrer_id}

    except Exception as e:
        conn.rollback()
        logger.error(f"Error crediting referrer: {e}")
        return {'credited': False, 'reason': 'error'}
    finally:
        conn.close()


def get_friend_discount(user_id: int) -> dict:
    """Check if user has friend discount available."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()

    c.execute(f"""
        SELECT u1.referred_by_code, u1.friend_discount_applied,
               u2.first_name as referrer_name
        FROM users u1
        LEFT JOIN users u2 ON u1.referred_by_user_id = u2.telegram_id
        WHERE u1.telegram_id = {p}
    """, (user_id,))

    row = c.fetchone()
    conn.close()

    if not row or not row[0] or row[1]:
        return {'has_discount': False}

    return {
        'has_discount': True,
        'amount': REFERRAL_FRIEND_DISCOUNT,
        'referrer_name': row[2] or 'un amigo'
    }


def apply_friend_discount(user_id: int) -> bool:
    """Mark friend discount as used."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"UPDATE users SET friend_discount_applied = 1 WHERE telegram_id = {p}", (user_id,))
    conn.commit()
    conn.close()
    return True


def apply_credits_to_payment(user_id: int, price: float) -> dict:
    """Calculate price after applying credits."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()

    c.execute(f"SELECT referral_credits_earned, referral_credits_used FROM users WHERE telegram_id = {p}", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {'original': price, 'credits_applied': 0, 'final_price': price, 'credits_remaining': 0}

    earned = float(row[0] or 0)
    used = float(row[1] or 0)
    available = earned - used

    if available <= 0:
        return {'original': price, 'credits_applied': 0, 'final_price': price, 'credits_remaining': 0}

    to_apply = min(available, price)
    final = price - to_apply

    return {
        'original': price,
        'credits_applied': to_apply,
        'final_price': final,
        'credits_remaining': available - to_apply
    }


def mark_credits_used(user_id: int, amount: float):
    """Mark credits as used after payment."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"UPDATE users SET referral_credits_used = referral_credits_used + {p} WHERE telegram_id = {p}", (amount, user_id))
    c.execute(f"INSERT INTO referral_events (user_id, event_type, amount, description) VALUES ({p}, 'credit_applied', {p}, 'Payment')", (user_id, amount))
    conn.commit()
    conn.close()


def get_share_text(code: str) -> str:
    """Standard share message text for all platforms."""
    return (
        f"¡Hola! 👋 Te comparto mi código para la regularización 2026 en España. "
        f"Con el código {code} tienes €25 de descuento. Es 100% online y muy fácil. "
        f"👉 tuspapeles2026.es/r.html?code={code}"
    )


def get_whatsapp_share_url(code: str) -> str:
    """Generate WhatsApp share URL with referral code."""
    import urllib.parse
    return f"https://wa.me/?text={urllib.parse.quote(get_share_text(code))}"


def get_telegram_share_url(code: str) -> str:
    """Generate Telegram share URL with referral code."""
    import urllib.parse
    return (
        f"https://t.me/share/url?"
        f"url={urllib.parse.quote(f'https://t.me/TusPapeles2026Bot?start={code}')}"
        f"&text={urllib.parse.quote('Usa mi código para €25 de descuento')}"
    )


def get_facebook_share_url(code: str) -> str:
    """Generate Facebook share URL with referral link."""
    import urllib.parse
    return f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(f'https://tuspapeles2026.es/r.html?code={code}')}"


def referral_share_keyboard(code: str) -> InlineKeyboardMarkup:
    """Generate share buttons for multiple platforms."""
    wa_url = get_whatsapp_share_url(code)
    tg_url = get_telegram_share_url(code)
    fb_url = get_facebook_share_url(code)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 WhatsApp", url=wa_url),
         InlineKeyboardButton("📲 Telegram", url=tg_url)],
        [InlineKeyboardButton("📘 Facebook", url=fb_url),
         InlineKeyboardButton("📋 Copiar", callback_data=f"copy_ref_{code}")],
        [InlineKeyboardButton("← Volver", callback_data="back")],
    ])


def get_share_buttons(code: str) -> list:
    """Generate social media share button rows (without back button)."""
    wa_url = get_whatsapp_share_url(code)
    tg_url = get_telegram_share_url(code)
    fb_url = get_facebook_share_url(code)
    return [
        [InlineKeyboardButton("📱 WhatsApp", url=wa_url),
         InlineKeyboardButton("📲 Telegram", url=tg_url)],
        [InlineKeyboardButton("📘 Facebook", url=fb_url),
         InlineKeyboardButton("📋 Copiar", callback_data=f"copy_ref_{code}")],
    ]


def build_referidos_text(stats: dict) -> str:
    """Build the comprehensive referidos screen text — different for paid vs unpaid."""
    code = stats['code']
    count = stats['count']
    earned = stats['credits_earned']
    used = stats['credits_used']
    available = stats['credits_available']
    can_earn = stats['can_earn']

    stats_block = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 TUS ESTADÍSTICAS\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Amigos referidos: {count}\n"
        f"Crédito ganado: €{earned}\n"
        f"Crédito usado: €{used}\n"
        f"Crédito disponible: €{available}"
    )

    how_block = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 ¿CÓMO FUNCIONA?\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ *COMPARTE* tu código con amigos que necesiten regularizarse\n\n"
        "2️⃣ *ELLOS RECIBEN* €25 de descuento en su primer pago\n\n"
        "3️⃣ *TÚ GANAS* €25 de crédito por cada amigo que pague"
    )

    if can_earn:
        activation_block = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✅ TU CÓDIGO ESTÁ *ACTIVO*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Cada vez que un amigo pague usando tu código, ganas €25 de crédito "
            "que se aplica automáticamente a tus próximos pagos.\n\n"
            "🎯 *Con 12 amigos = tu servicio completo es GRATIS*\n\n"
            "¡Comparte ahora!"
        )
    else:
        activation_block = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔓 ACTIVAR TUS GANANCIAS\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Para empezar a ganar créditos, primero debes pagar tu Fase 2 (€39).\n\n"
            "*¿Por qué?* Queremos asegurar que solo usuarios comprometidos con el "
            "proceso puedan ganar créditos. Esto evita fraudes y garantiza un sistema "
            "justo para todos.\n\n"
            "Una vez pagues tu €39:\n"
            "• Tu código se activa permanentemente\n"
            "• Empiezas a ganar €25 por cada amigo que pague\n"
            "• Puedes acumular hasta €299 en créditos (¡servicio completo gratis!)\n\n"
            "🎯 *Con 12 amigos = tu servicio completo es GRATIS*"
        )

    text = (
        f"👥 *Tus Referidos*\n\n"
        f"Tu código personal: `{code}`\n\n"
        f"{stats_block}\n\n"
        f"{how_block}\n\n"
        f"{activation_block}"
    )
    return text


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


def get_country_checklist(country_code: str) -> str:
    """Generate a document checklist with clear mandatory vs optional grouping."""
    country = COUNTRIES.get(country_code, COUNTRIES["other"])
    name = country.get("name", "su país")

    return (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 OBLIGATORIOS (todos necesarios)\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ *Pasaporte completo*\n"
        "   Todas las páginas, incluyendo vacías.\n\n"
        "2️⃣ *Antecedentes penales - España*\n"
        "   Certificado del Ministerio de Justicia.\n\n"
        f"3️⃣ *Antecedentes penales - {name}*\n"
        "   Apostillado y traducido si no está en español.\n"
        "   Usa /antecedentes para más información.\n\n"
        "4️⃣ *Empadronamiento*\n"
        "   Certificado de tu ayuntamiento.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🏠 PRUEBA DE RESIDENCIA (elige UNA opción)\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Debes demostrar presencia en España antes del 10 noviembre 2024.\n\n"
        "*Opción A:* Empadronamiento histórico\n"
        "*Opción B:* Contrato de trabajo anterior a nov 2024\n"
        "*Opción C:* Historial médico (cita o informe)\n"
        "*Opción D:* Envíos de dinero (Western Union, Ria, etc.)\n"
        "*Opción E:* Otros (facturas, extractos bancarios, billetes)\n\n"
        "💡 _Cuantos más documentos de prueba, mejor._\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📎 OPCIONALES (refuerzan tu caso)\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "• Contrato de trabajo actual\n"
        "• Nóminas recientes\n"
        "• Vida laboral\n"
        "• Certificado de estudios en España\n"
        "• Certificado de idioma español\n"
        "• Cartas de apoyo de empleador/vecinos"
    )


def calculate_progress(user: Dict, dc_approved: int) -> int:
    """Calculate progress percentage — single source of truth for all screens."""
    if user.get("phase4_paid"):
        return 95
    elif user.get("phase3_paid"):
        return 85
    elif user.get("phase2_paid"):
        return min(75, 65 + dc_approved)
    elif dc_approved >= MIN_DOCS_FOR_PHASE2:
        return 50 + min(15, dc_approved * 2)
    elif dc_approved > 0:
        return 15 + (dc_approved * 10)
    else:
        return 10


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
    """Generate country selection keyboard — top 25 non-EU nationalities in Spain."""
    countries_order = [
        "ma", "co", "ve", "pe", "ec",
        "ar", "cn", "ua", "hn", "do",
        "pk", "bo", "br", "py", "ni",
        "cu", "ng", "sn", "gt", "sv",
        "in", "bd", "ph", "gh", "other",
    ]
    rows = []
    for i in range(0, len(countries_order), 2):
        row = []
        for code in countries_order[i:i + 2]:
            c = COUNTRIES[code]
            row.append(InlineKeyboardButton(
                f"{c['flag']} {c['name']}", callback_data=f"c_{code}"))
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
        [InlineKeyboardButton("📋 Mi checklist de documentos", callback_data="m_checklist")],
        [InlineKeyboardButton(f"📄 Mis documentos ({dc})", callback_data="m_docs")],
        [InlineKeyboardButton("📤 Subir documento", callback_data="m_upload")],
    ]
    # Payment progression: Phase 2 → Phase 3 → Phase 4
    if dc >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        btns.append([InlineKeyboardButton("🔓 Revisión legal — €39", callback_data="m_pay2")])
    elif user.get("phase2_paid") and not user.get("phase3_paid") and user.get("docs_verified"):
        btns.append([InlineKeyboardButton("🔓 Procesamiento — €150", callback_data="m_pay3")])
    elif user.get("phase3_paid") and not user.get("phase4_paid") and user.get("expediente_ready"):
        btns.append([InlineKeyboardButton("🔓 Presentación — €110", callback_data="m_pay4")])
    btns += [
        [InlineKeyboardButton("📣 Invitar amigos", callback_data="m_referidos"),
         InlineKeyboardButton("👥 Mis referidos", callback_data="m_referidos")],
        [InlineKeyboardButton("💰 Costos y pagos", callback_data="m_price")],
        [InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="m_faq")],
        [InlineKeyboardButton("💬 Consultar con abogado", callback_data="m_contact")],
    ]
    return InlineKeyboardMarkup(btns)


def faq_menu_kb() -> InlineKeyboardMarkup:
    """Show FAQ category buttons (accordion top level)."""
    btns = []
    for cat_key, cat in FAQ_CATEGORIES.items():
        btns.append([InlineKeyboardButton(cat["title"], callback_data=f"fcat_{cat_key}")])
    btns.append([InlineKeyboardButton("← Volver al menú", callback_data="back")])
    return InlineKeyboardMarkup(btns)


def faq_category_kb(cat_key: str) -> InlineKeyboardMarkup:
    """Show question buttons within a FAQ category."""
    cat = FAQ_CATEGORIES.get(cat_key, {})
    btns = []
    for faq_key in cat.get("keys", []):
        faq = FAQ.get(faq_key)
        if faq:
            btns.append([InlineKeyboardButton(faq["title"], callback_data=f"fq_{faq_key}")])
    btns.append([InlineKeyboardButton("← Todas las categorías", callback_data="m_faq")])
    btns.append([InlineKeyboardButton("← Menú principal", callback_data="back")])
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


def docs_ready_payment_kb(has_referral_discount: bool = False) -> InlineKeyboardMarkup:
    """Payment options shown AFTER documents are uploaded (not at eligibility)."""
    prepay_price = PRICING["prepay"] - REFERRAL_FRIEND_DISCOUNT if has_referral_discount else PRICING["prepay"]
    phase2_price = PRICING["phase2"] - REFERRAL_FRIEND_DISCOUNT if has_referral_discount else PRICING["phase2"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"⭐ Pagar TODO — €{prepay_price} (ahorra €{PRICING['prepay_savings']})",
            callback_data="pay_full")],
        [InlineKeyboardButton(
            f"💳 Pagar revisión — €{phase2_price}",
            callback_data="m_pay2")],
        [InlineKeyboardButton(
            "📄 Subir más documentos",
            callback_data="m_upload")],
        [InlineKeyboardButton("← Menú", callback_data="back")],
    ])


ANTECEDENTES_HELP_TEXT = (
    "🌍 *Antecedentes Penales del País de Origen*\n\n"
    "Necesitas un certificado de antecedentes penales de tu país, "
    "apostillado (o legalizado) y traducido al español si es necesario.\n\n"
    "⚠️ *Esto puede ser complicado:*\n"
    "• Cada país tiene su propio proceso\n"
    "• Algunos requieren gestiones presenciales\n"
    "• Los tiempos varían de días a meses\n"
    "• Errores pueden retrasar tu solicitud\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "💼 NUESTRO SERVICIO DE ANTECEDENTES\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    f"Por *€{PRICING['antecedentes_service']}* nos encargamos de todo:\n\n"
    "✅ Investigamos el proceso de tu país\n"
    "✅ Solicitamos el certificado\n"
    "✅ Gestionamos apostilla/legalización\n"
    "✅ Traducción jurada si necesario\n"
    "✅ Te lo entregamos listo\n\n"
    "⏱️ Tiempo: 2-4 semanas (varía por país)\n\n"
    "⚠️ _Nota: Algunos países tienen procesos muy complejos o lentos. "
    "Te informaremos antes de empezar si tu país presenta dificultades especiales._"
)


def antecedentes_service_kb() -> InlineKeyboardMarkup:
    """Buttons for antecedentes service offer — direct payment."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💼 Contratar servicio — €{PRICING['antecedentes_service']}", callback_data="buy_antecedentes")],
        [InlineKeyboardButton("📋 Lo hago yo mismo", callback_data="back")],
    ])


def antecedentes_help_kb() -> InlineKeyboardMarkup:
    """Buttons for antecedentes help — request support flow."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Solicitar ayuda con antecedentes", callback_data="request_antecedentes_help")],
        [InlineKeyboardButton("📋 Lo gestiono yo mismo", callback_data="m_checklist")],
        [InlineKeyboardButton("← Menú", callback_data="back")],
    ])


def govt_fees_service_kb() -> InlineKeyboardMarkup:
    """Buttons for government fees service offer."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💼 Añadir servicio — €{PRICING['govt_fees_service']}", callback_data="buy_govt_fees")],
        [InlineKeyboardButton("📋 Las pago yo mismo", callback_data="back")],
    ])


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
    """Handle /start, including referral codes from deep links."""
    tid = update.effective_user.id
    user = get_user(tid)

    # Existing user with eligibility → main menu
    if user and user.get("eligible"):
        return await show_main_menu(update, ctx)

    # Create user if new
    if not user:
        create_user(tid, update.effective_user.first_name or "Usuario")

    # Check for referral code in start param (deep link: t.me/bot?start=CODE)
    if ctx.args and len(ctx.args) > 0:
        code = ctx.args[0].upper().strip()
        result = validate_referral_code(code)

        if result['valid'] and result['referrer_id'] != tid:
            apply_referral_code_to_user(tid, result['code'], result['referrer_id'])

            await update.message.reply_text(
                f"🎉 ¡Código aplicado! Tienes *€{REFERRAL_FRIEND_DISCOUNT} de descuento* en tu primer pago.\n\n"
                "🇪🇸 *¡Bienvenido/a a tuspapeles2026!*\n\n"
                "Esta plataforma ha sido desarrollada por los abogados de "
                "*Pombo, Horowitz & Espinosa* para optimizar el proceso de regularización, "
                "reduciendo el riesgo de error humano y de peticiones denegadas.\n\n"
                "✅ Te guiamos paso a paso en todo el proceso\n"
                "✅ Revisamos y verificamos cada documento\n"
                "✅ Preparamos tu expediente completo\n"
                "✅ Presentamos tu solicitud en abril-junio\n"
                "✅ Seguimiento hasta resolución favorable\n\n"
                "Empecemos verificando si cumples los requisitos básicos.\n\n"
                "Para empezar, indícanos tu país de origen:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=country_kb(),
            )
            return ST_COUNTRY

    # Normal start - ask if they have a referral code
    await update.message.reply_text(
        "🇪🇸 *¡Bienvenido/a a tuspapeles2026!*\n\n"
        "Sabemos que este momento es importante para ti y tu familia. "
        "La regularización extraordinaria de 2026 es una oportunidad histórica, "
        "y estamos aquí para ayudarte a aprovecharla.\n\n"
        "Esta plataforma ha sido desarrollada por los abogados de "
        "*Pombo, Horowitz & Espinosa* para optimizar el proceso de regularización "
        "de cientos de clientes, reduciendo el riesgo de error humano y de "
        "peticiones de regularización denegadas.\n\n"
        "Combinando nuestra experiencia en la regularización del año 2005 con los "
        "avances en inteligencia artificial, aseguramos que nuestros clientes se "
        "benefician de un proceso eficiente, seguro y transparente.\n\n"
        "*Nuestro servicio completo incluye:*\n\n"
        "✅ Te guiamos paso a paso en todo el proceso\n"
        "✅ Revisamos y verificamos cada documento\n"
        "✅ Preparamos tu expediente completo\n"
        "✅ Presentamos tu solicitud en abril-junio\n"
        "✅ Hacemos seguimiento con la administración\n"
        "✅ Gestionamos recursos si fuera necesario\n"
        "✅ Te entregamos tu resolución favorable\n\n"
        "El proceso es 100% por este chat. Sin citas, sin colas, sin complicaciones.\n\n"
        "📅 El plazo de solicitudes abre en abril y cierra el *30 de junio de 2026*.\n\n"
        "Empecemos verificando si cumples los requisitos básicos...\n\n"
        "¿Tienes un código de un amigo? Si lo tienes, escríbelo ahora para €25 de descuento.\n\n"
        "Ejemplo: `MARIA-7K2P`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("No tengo código — continuar", callback_data="ref_skip")]
        ]),
    )
    return ST_ENTER_REFERRAL_CODE


async def cmd_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Reset user account - ADMIN ONLY. Usage: /reset or /reset <telegram_id>"""
    tid = update.effective_user.id
    chat_id = update.effective_chat.id

    # Admin-only command
    if tid not in ADMIN_IDS:
        await update.message.reply_text(
            "Este comando está reservado para administradores.\n\n"
            "Si necesita ayuda con su cuenta, escriba /start o contacte con soporte."
        )
        return ConversationHandler.END

    # Check if admin wants to reset another user: /reset 123456789
    target_tid = tid  # Default: reset own account
    if update.message and update.message.text:
        parts = update.message.text.split()
        if len(parts) > 1:
            try:
                target_tid = int(parts[1])
            except ValueError:
                await update.message.reply_text("Uso: /reset o /reset <telegram_id>")
                return ConversationHandler.END

    logger.info(f"RESET requested by admin {tid} for user {target_tid}")

    # Delete from database
    delete_user(target_tid)

    # Clear context data if resetting own account
    if target_tid == tid:
        ctx.user_data.clear()
        if hasattr(ctx, 'chat_data') and ctx.chat_data:
            ctx.chat_data.clear()

    # Send confirmation
    if target_tid == tid:
        confirmation = (
            "✅ Su cuenta ha sido eliminada completamente.\n\n"
            "Todos sus datos, documentos y progreso han sido borrados.\n"
            "Escriba /start para comenzar de nuevo."
        )
    else:
        confirmation = f"✅ Usuario {target_tid} eliminado de la base de datos."

    try:
        if update.message:
            await update.message.reply_text(confirmation)
        else:
            await ctx.bot.send_message(chat_id=chat_id, text=confirmation)
    except Exception as e:
        logger.error(f"Error sending reset confirmation: {e}")

    logger.info(f"RESET completed for user {target_tid}")
    return ConversationHandler.END


async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    return await show_main_menu(update, ctx)


# --- Referral code entry ---

async def handle_referral_code_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user typing a referral code."""
    tid = update.effective_user.id
    code = update.message.text.upper().strip()

    # Validate
    result = validate_referral_code(code)

    if not result['valid']:
        await update.message.reply_text(
            "Código no encontrado. Verifica que esté bien escrito o continúa sin código.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Intentar de nuevo", callback_data="ref_retry")],
                [InlineKeyboardButton("Continuar sin código", callback_data="ref_skip")]
            ]),
        )
        return ST_ENTER_REFERRAL_CODE

    # Can't use own code
    if result['referrer_id'] == tid:
        await update.message.reply_text(
            "No puedes usar tu propio código.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Continuar sin código", callback_data="ref_skip")]
            ]),
        )
        return ST_ENTER_REFERRAL_CODE

    # Apply code
    apply_referral_code_to_user(tid, result['code'], result['referrer_id'])

    await update.message.reply_text(
        f"Código aplicado. Tienes €{REFERRAL_FRIEND_DISCOUNT} de descuento en tu primer pago.\n\n"
        "Para empezar, indíquenos su país de origen:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=country_kb(),
    )
    return ST_COUNTRY


async def handle_referral_callbacks(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle referral-related buttons."""
    q = update.callback_query
    await q.answer()

    if q.data == "ref_skip":
        await q.edit_message_text(
            "Para empezar, indícanos tu país de origen:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=country_kb(),
        )
        return ST_COUNTRY

    elif q.data == "ref_retry":
        await q.edit_message_text(
            "Escribe el código de referido:\n\nEjemplo: `MARIA-7K2P`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("No tengo código", callback_data="ref_skip")]
            ]),
        )
        return ST_ENTER_REFERRAL_CODE

    elif q.data == "ref_copy":
        user = get_user(update.effective_user.id)
        code = user.get('referral_code', '')
        await q.answer(f"Tu código: {code}", show_alert=True)
        return ST_MAIN_MENU

    return ST_ENTER_REFERRAL_CODE


# --- Country selection ---

async def handle_country(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    code = q.data.replace("c_", "")
    country = COUNTRIES.get(code, COUNTRIES["other"])
    update_user(update.effective_user.id, country_code=code)

    await q.edit_message_text(
        f"✅ Registrado: {country['flag']} *{country['name']}*\n\n"
        "Continuemos con la verificación de requisitos...\n\n"
        "¿Cómo te llamas? Escribe tu nombre completo:",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ST_FULL_NAME


async def handle_full_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's full name input."""
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("Por favor, escribe tu nombre completo:")
        return ST_FULL_NAME

    update_user(update.effective_user.id, full_name=name)

    await update.message.reply_text(
        f"Gracias, {name.split()[0]}.\n\n"
        "A continuación, necesitamos hacerte *3 preguntas breves* para verificar "
        "si cumples los requisitos básicos de la regularización.\n\n"
        "Tus respuestas son estrictamente confidenciales.",
        parse_mode=ParseMode.MARKDOWN,
    )

    await update.message.reply_text(
        "*Pregunta 1 de 3*\n\n"
        "¿Te encontrabas en España *antes del 31 de diciembre de 2025*?",
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
    tid = update.effective_user.id
    update_user(tid, eligible=1, has_criminal_record=0)
    case = get_or_create_case(tid)

    # Generate referral code for user
    user = get_user(tid)
    if not user.get('referral_code'):
        code = generate_referral_code(tid)
        update_user(tid, referral_code=code)
    else:
        code = user['referral_code']

    await q.edit_message_text(
        f"✅ *¡Buenas noticias, {name}!*\n\n"
        "Según tus respuestas, cumples los requisitos básicos para la "
        "regularización extraordinaria de 2026.\n\n"
        f"Expediente: *{case['case_number']}*\n"
        f"Plazo: 1 abril — 30 junio 2026 ({days_left()} días)\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📋 SIGUIENTE PASO\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Sube tus documentos para que podamos verificarlos.\n\n"
        "*Esta fase es 100% gratis:*\n"
        "• Verificamos tu elegibilidad ✓ (completado)\n"
        "• Subes tus documentos\n"
        "• Te indicamos si falta algo\n\n"
        "Cuando estén listos, un abogado los revisará en detalle (Fase 2, €39).\n\n"
        f"💡 Tu código: `{code}`\n"
        "_Más info en \"Invitar amigos\" del menú._",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Subir documentos", callback_data="m_upload")],
            [InlineKeyboardButton("📋 Ver checklist de documentos", callback_data="m_checklist")],
            [InlineKeyboardButton("❓ Tengo preguntas", callback_data="m_faq")],
        ]),
    )
    return ST_ELIGIBLE


# --- Main menu ---

async def show_main_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = get_user(update.effective_user.id)
    if not user or not user.get("eligible"):
        # User doesn't exist or hasn't completed eligibility - redirect to start
        msg = "Escriba /start para comenzar el proceso de regularización."
        if update.callback_query:
            await update.callback_query.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
        return ConversationHandler.END

    name = user.get("full_name") or user.get("first_name", "Usuario")
    case = get_or_create_case(update.effective_user.id)
    tid = update.effective_user.id
    dc_total = get_doc_count(tid)
    dc_approved = get_approved_doc_count(tid)

    # Dynamic progress bar (shared calculation)
    progress = calculate_progress(user, dc_approved)
    bar = "█" * (progress // 10) + "░" * (10 - progress // 10)

    # Document status line
    doc_status = f"Documentos aprobados: {dc_approved}"
    if dc_total > dc_approved:
        pending = dc_total - dc_approved
        doc_status += f" (+ {pending} en revisión)"

    msg = (
        f"*{name}* — Expediente {case['case_number']}\n"
        f"Fase actual: {phase_name(user)}\n\n"
        f"Progreso: {bar} {progress}%\n"
        f"{doc_status}\n"
        f"{phase_status(user, dc_approved)}\n\n"
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

    # If user was deleted (via /reset), redirect to start
    if not user:
        await q.edit_message_text(
            "Su sesión ha expirado o su cuenta fue eliminada.\n\n"
            "Escriba /start para comenzar de nuevo."
        )
        return ConversationHandler.END

    # Route country selection callbacks (fallback if state handler misses)
    if d.startswith("c_"):
        return await handle_country(update, ctx)

    # Route eligibility Q1 callbacks
    if d.startswith("d_"):
        return await handle_q1(update, ctx)

    # Route eligibility Q2 callbacks
    if d.startswith("t_"):
        return await handle_q2(update, ctx)

    # Route eligibility Q3 callbacks
    if d.startswith("r_"):
        return await handle_q3(update, ctx)

    # FAQ callback routing (from eligibility screen and other places)
    if d.startswith("fq_"):
        key = d[3:]
        faq = FAQ.get(key)
        if faq:
            text = faq["text"].replace("{days}", str(days_left()))
            await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📋 Todas las categorías", callback_data="m_faq")],
                    [InlineKeyboardButton("← Menú principal", callback_data="back")],
                ]))
            return ST_FAQ_ITEM
        return ST_MAIN_MENU

    # FAQ category callback routing
    if d.startswith("fcat_"):
        cat_key = d[5:]
        cat = FAQ_CATEGORIES.get(cat_key)
        if cat:
            ctx.user_data["faq_cat"] = cat_key
            await q.edit_message_text(
                f"*{cat['title']}*\n\nSeleccione una pregunta:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=faq_category_kb(cat_key))
            return ST_FAQ_CATEGORY
        return ST_MAIN_MENU

    if d == "m_checklist":
        country_code = user.get("country_code", "other")
        country = COUNTRIES.get(country_code, COUNTRIES["other"])
        checklist = get_country_checklist(country_code)

        await q.edit_message_text(
            f"📋 *Checklist de documentos para {country['flag']} {country['name']}*\n\n"
            f"{checklist}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 Subir documentos", callback_data="m_upload")],
                [InlineKeyboardButton("🌍 Ayuda con antecedentes", callback_data="antecedentes_help")],
                [InlineKeyboardButton("← Volver al menú", callback_data="back")],
            ]))
        return ST_MAIN_MENU

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
        # Check for duplicate document (passport, nie, dni, antecedentes)
        if dtype in ("passport", "nie", "dni", "antecedentes"):
            existing = get_user_doc_by_type(update.effective_user.id, dtype)
            if existing:
                ctx.user_data["replace_doc_id"] = existing["id"]
                await q.edit_message_text(
                    f"Ya tienes un *{info['name']}* subido. ¿Quieres reemplazarlo?",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Sí, reemplazar", callback_data=f"repl_yes_{dtype}")],
                        [InlineKeyboardButton("No, cancelar", callback_data="m_upload")],
                    ]))
                return ST_UPLOAD_SELECT
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

    if d.startswith("repl_yes_"):
        dtype = d[9:]
        info = DOC_TYPES.get(dtype, DOC_TYPES["other"])
        old_id = ctx.user_data.pop("replace_doc_id", None)
        if old_id:
            delete_document(old_id)
        ctx.user_data["doc_type"] = dtype
        tip = f"\n\n💡 {info['tip']}" if info.get("tip") else ""
        await q.edit_message_text(
            f"*Subir: {info['name']}* (reemplazo)\n\n"
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
        await q.edit_message_text(FAQ["costo"]["text"], parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"⭐ Pagar TODO — €{PRICING['prepay']}", callback_data="pay_full")],
                [InlineKeyboardButton(f"💳 Pagar Fase 2 — €{PRICING['phase2']}", callback_data="m_pay2")],
                [InlineKeyboardButton("📦 Ver servicios adicionales", callback_data="extra_services")],
                [InlineKeyboardButton("← Volver", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if d == "m_referidos":
        tid = update.effective_user.id
        stats = get_referral_stats(tid)

        if not stats or not stats['code']:
            await q.edit_message_text(
                "Aún no tienes código de referidos.\n"
                "Completa la verificación de elegibilidad primero.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("← Volver", callback_data="back")],
                ]),
            )
            return ST_MAIN_MENU

        text = build_referidos_text(stats)
        buttons = get_share_buttons(stats['code'])
        buttons.append([InlineKeyboardButton("← Volver", callback_data="back")])

        await q.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return ST_MAIN_MENU

    if d.startswith("copy_ref_"):
        code = d[len("copy_ref_"):]
        copy_text = f"🇪🇸 ¿Necesitas regularizarte en España? Usa mi código {code} para €25 de descuento en tuspapeles2026.es"
        await q.answer("Texto copiado — pégalo en Instagram o TikTok", show_alert=True)
        await q.message.reply_text(
            f"📋 *Copia este texto:*\n\n`{copy_text}`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ST_MAIN_MENU

    if d == "m_faq":
        await q.edit_message_text("*Preguntas frecuentes*\n\nSeleccione una categoría:",
            parse_mode=ParseMode.MARKDOWN, reply_markup=faq_menu_kb())
        return ST_FAQ_MENU

    if d == "m_contact":
        await q.edit_message_text(
            "*¿Tienes una consulta para nuestro equipo legal?*\n\n"
            "Escribe tu mensaje aquí y lo trasladaremos a un abogado:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver", callback_data="back")],
            ]))
        ctx.user_data["awaiting_human_msg"] = True
        return ST_HUMAN_MSG

    if d == "write_msg":
        await q.edit_message_text(
            "*¿Tienes una consulta para nuestro equipo legal?*\n\n"
            "Escribe tu mensaje aquí y lo trasladaremos a un abogado:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver", callback_data="back")],
            ]))
        ctx.user_data["awaiting_human_msg"] = True
        return ST_HUMAN_MSG

    if d == "m_pay2":
        tid = update.effective_user.id
        dc = get_doc_count(tid)
        base_price = 39  # Phase 2 price

        # Check friend discount
        friend_disc = get_friend_discount(tid)
        discount = friend_disc['amount'] if friend_disc['has_discount'] else 0

        # Check referral credits
        price_after_discount = base_price - discount
        credit_calc = apply_credits_to_payment(tid, price_after_discount)

        final_price = credit_calc['final_price']

        # Store for payment confirmation
        ctx.user_data['payment_discount'] = discount
        ctx.user_data['payment_credits'] = credit_calc['credits_applied']
        ctx.user_data['payment_final'] = final_price

        # Build price breakdown (simple math)
        lines = [f"*Revisión legal completa*\n"]
        lines.append(f"Precio: €{base_price}")

        if discount > 0:
            lines.append(f"Descuento amigo: -€{discount}")

        if credit_calc['credits_applied'] > 0:
            lines.append(f"Tu crédito: -€{credit_calc['credits_applied']}")

        lines.append(f"*Total: €{final_price}*\n")

        if final_price <= 0:
            lines.append("Esta fase es gratis gracias a tus referidos.")
            if credit_calc['credits_remaining'] > 0:
                lines.append(f"Crédito restante: €{credit_calc['credits_remaining']}")

            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("Continuar gratis", callback_data="paid2_free")],
                [InlineKeyboardButton("Volver", callback_data="m_menu")],
            ])
        else:
            lines.append(f"Ha subido {dc} documentos. Con este pago:\n")
            lines.append("• Análisis legal de su documentación.")
            lines.append("• Informe de qué está correcto y qué falta.")
            lines.append("• Plan personalizado con plazos.")

            kb = _payment_buttons("paid2", STRIPE_PHASE2_LINK)

        await q.edit_message_text(
            "\n".join(lines),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb)
        return ST_PAY_PHASE2

    if d == "paid2" or d == "paid2_free":
        tid = update.effective_user.id

        # Apply discounts
        discount = ctx.user_data.get('payment_discount', 0)
        credits_used = ctx.user_data.get('payment_credits', 0)

        if discount > 0:
            apply_friend_discount(tid)

        if credits_used > 0:
            mark_credits_used(tid, credits_used)

        # Update user status
        update_user(tid, phase2_paid=1, current_phase=2, state="phase2_active")

        # Credit the referrer
        result = credit_referrer(tid, 39)

        if result.get('credited'):
            # Minimal notification to referrer
            try:
                user_data = get_user(tid)
                await ctx.bot.send_message(
                    result['referrer_id'],
                    f"Tu amigo {user_data.get('first_name', 'alguien')} usó tu código. +€{result['amount']} crédito.",
                )
            except Exception as e:
                logger.error(f"Failed to notify referrer: {e}")

        # Notify admins
        await notify_admins(ctx,
            f"Pago Fase 2: User {tid}\n"
            f"Descuento: €{discount} | Créditos: €{credits_used}")

        # Get user's referral code for activation message
        user = get_user(tid)
        code = user.get('referral_code', '')
        share_btns = get_share_buttons(code)

        await q.edit_message_text(
            "Pago recibido.\n\n"
            "Nuestro equipo revisará su documentación en las próximas 24-48 horas.\n"
            "Le notificaremos cuando esté listo para la siguiente fase.\n\n"
            f"✅ Tu código está activo: `{code}`\n"
            "Ganas €25 de crédito por cada amigo que pague.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                share_btns + [[InlineKeyboardButton("Ver mi progreso", callback_data="m_menu")]]
            ),
        )
        return ST_MAIN_MENU

    if d == "m_pay3":
        text = (
            "*Preparación del expediente — €150*\n\n"
            "Sus documentos han sido verificados. Con este pago, nuestro equipo realizará:\n\n"
            "• Expediente legal completo.\n"
            "• Todos los formularios completados y revisados.\n"
            "• Revisión final por abogado.\n"
            "• Puesto reservado en cola de presentación.\n\n"
        )
        if STRIPE_PHASE3_LINK:
            text += "Pulse *Pagar con tarjeta* para un pago seguro instantáneo."
        else:
            text += (
                "*Formas de pago:*\n"
                f"Bizum: {BIZUM_PHONE}\n"
                f"Transferencia: {BANK_IBAN}\n"
                "Concepto: su nombre + número de expediente."
            )
        await q.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_payment_buttons("paid3", STRIPE_PHASE3_LINK))
        return ST_PAY_PHASE3

    if d == "paid3":
        update_user(update.effective_user.id, state="phase3_pending")
        await notify_admins(ctx,
            f"💳 *Pago Fase 3 pendiente*\n"
            f"Usuario: {user.get('first_name')}\n"
            f"TID: {update.effective_user.id}\n"
            f"Aprobar: `/approve3 {update.effective_user.id}`")
        await q.edit_message_text(
            "Hemos registrado su notificación de pago.\n\n"
            "Lo verificaremos y comenzaremos la preparación de su expediente. "
            "Recibirá una notificación cuando esté activado.")
        return ConversationHandler.END

    if d == "m_pay4":
        dl = days_left()
        text = (
            "*Presentación de solicitud — €110*\n\n"
            f"Su expediente está listo. Quedan *{dl} días* hasta el cierre del plazo.\n\n"
            "Con este pago final, realizaremos:\n\n"
            "• Presentación telemática oficial ante Extranjería.\n"
            "• Seguimiento del estado de su solicitud.\n"
            "• Notificación inmediata de resolución.\n"
            "• Asistencia para recogida de TIE.\n\n"
        )
        if STRIPE_PHASE4_LINK:
            text += "Pulse *Pagar con tarjeta* para un pago seguro instantáneo."
        else:
            text += (
                "*Formas de pago:*\n"
                f"Bizum: {BIZUM_PHONE}\n"
                f"Transferencia: {BANK_IBAN}\n"
                "Concepto: su nombre + número de expediente."
            )
        await q.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_payment_buttons("paid4", STRIPE_PHASE4_LINK))
        return ST_PAY_PHASE4

    if d == "paid4":
        update_user(update.effective_user.id, state="phase4_pending")
        await notify_admins(ctx,
            f"💳 *Pago Fase 4 pendiente*\n"
            f"Usuario: {user.get('first_name')}\n"
            f"TID: {update.effective_user.id}\n"
            f"Aprobar: `/approve4 {update.effective_user.id}`")
        await q.edit_message_text(
            "Hemos registrado su notificación de pago.\n\n"
            "Lo verificaremos y procederemos a presentar su solicitud. "
            "Recibirá una confirmación con el número de registro.")
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

    if d == "pay_full":
        tid = update.effective_user.id
        u = get_user(tid)
        has_referral = u.get("used_referral_code") is not None
        price = PRICING["prepay"] - REFERRAL_FRIEND_DISCOUNT if has_referral else PRICING["prepay"]
        referral_line = "\n🎁 _Descuento de €25 aplicado por usar código de amigo._\n" if has_referral else ""
        btns = []
        if STRIPE_PREPAY_LINK:
            btns.append([InlineKeyboardButton(f"💳 Pagar €{price}", url=STRIPE_PREPAY_LINK)])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Tengo dudas", callback_data="m_contact")])
        btns.append([InlineKeyboardButton("← Volver", callback_data="back")])
        await q.edit_message_text(
            f"💳 *Pago Único — €{price}*\n\n"
            "Incluye todas las fases hasta tu resolución:\n"
            "✅ Revisión legal completa\n"
            "✅ Preparación del expediente\n"
            "✅ Presentación de solicitud\n"
            "✅ Seguimiento hasta resolución\n"
            f"{referral_line}\n"
            "Haz clic en el botón para pagar de forma segura:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    if d == "antecedentes_help":
        await q.edit_message_text(
            ANTECEDENTES_HELP_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=antecedentes_help_kb())
        return ST_MAIN_MENU

    if d == "request_antecedentes_help":
        country_code = user.get("country_code", "other") if user else "other"
        country = COUNTRIES.get(country_code, COUNTRIES["other"])
        country_name = country.get("name", "No especificado")
        await q.edit_message_text(
            f"📩 *Solicitud de Ayuda con Antecedentes*\n\n"
            f"País de origen: *{country_name}*\n\n"
            "Para darte un presupuesto exacto y tiempo estimado, "
            "necesitamos confirmar algunos datos.\n\n"
            "Un miembro de nuestro equipo te contactará en las "
            "próximas 24 horas para:\n"
            "• Confirmar el proceso de tu país\n"
            "• Explicarte los pasos\n"
            "• Darte precio y tiempo exacto\n\n"
            "¿Quieres que te contactemos?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Sí, contactadme", callback_data="confirm_antecedentes_request")],
                [InlineKeyboardButton("← Volver", callback_data="antecedentes_help")],
            ]))
        return ST_MAIN_MENU

    if d == "confirm_antecedentes_request":
        tid = update.effective_user.id
        u = get_user(tid)
        country_code = u.get("country_code", "other") if u else "other"
        uname = update.effective_user.username or "N/A"
        admin_msg = (
            "🌍 *SOLICITUD ANTECEDENTES*\n\n"
            f"Usuario: {u.get('name', 'N/A')}\n"
            f"Telegram: @{uname}\n"
            f"ID: {tid}\n"
            f"País: {country_code}\n\n"
            f"Contactar para dar presupuesto de servicio antecedentes (€{PRICING['antecedentes_service']} estándar)."
        )
        for admin_id in ADMIN_IDS:
            try:
                await ctx.bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                pass
        await q.edit_message_text(
            "✅ *Solicitud Enviada*\n\n"
            "Hemos recibido tu solicitud. Un miembro del equipo "
            "te contactará en las próximas 24 horas.\n\n"
            "Mientras tanto, puedes seguir subiendo otros documentos.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 Subir documentos", callback_data="m_upload")],
                [InlineKeyboardButton("← Menú", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if d == "buy_antecedentes":
        tid = update.effective_user.id
        btns = []
        if STRIPE_ANTECEDENTES_LINK:
            btns.append([InlineKeyboardButton(f"💳 Pagar €{PRICING['antecedentes_service']}", url=STRIPE_ANTECEDENTES_LINK)])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("← Volver", callback_data="back")])
        await q.edit_message_text(
            f"💼 *Servicio de Antecedentes Penales — €{PRICING['antecedentes_service']}*\n\n"
            "Nos encargamos de todo:\n\n"
            "✅ Solicitar el certificado en tu país de origen\n"
            "✅ Gestionar la apostilla o legalización\n"
            "✅ Traducción jurada al español (si necesario)\n"
            "✅ Entrega en formato digital, listo para presentar\n\n"
            "⏱️ Tiempo estimado: 2-4 semanas (varía por país)\n\n"
            "Necesitaremos algunos datos adicionales después del pago.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    if d == "buy_govt_fees":
        tid = update.effective_user.id
        btns = []
        if STRIPE_GOVT_FEES_LINK:
            btns.append([InlineKeyboardButton(f"💳 Pagar €{PRICING['govt_fees_service']}", url=STRIPE_GOVT_FEES_LINK)])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("← Volver", callback_data="back")])
        await q.edit_message_text(
            f"🏛️ *Gestión de Tasas Gubernamentales — €{PRICING['govt_fees_service']}*\n\n"
            "Nos encargamos de:\n\n"
            "✅ Pagar la Tasa 790-052 (tramitación)\n"
            "✅ Pagar la Tasa 790-012 (TIE)\n"
            "✅ Enviarte los justificantes de pago\n"
            "✅ Incluirlos en tu expediente\n\n"
            "💰 Las tasas en sí (~€40-50) las pagas aparte.\n"
            f"Nosotros cobramos €{PRICING['govt_fees_service']} por el servicio de gestión.\n\n"
            "_Así no tienes que preocuparte de formularios ni plazos._",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    if d == "extra_services":
        await q.edit_message_text(
            "📦 *Servicios Adicionales*\n\n"
            "Estos servicios son opcionales. Te ayudan a simplificar el proceso.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌍 *Antecedentes Penales — €{PRICING['antecedentes_service']}*\n"
            "Nos encargamos de solicitar, apostillar y traducir tu certificado "
            "de antecedentes del país de origen.\n\n"
            f"🏛️ *Gestión de Tasas — €{PRICING['govt_fees_service']}*\n"
            "Pagamos y gestionamos las tasas gubernamentales "
            "(790-052, 790-012) por ti.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "_Puedes añadir estos servicios en cualquier momento._",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"🌍 Antecedentes — €{PRICING['antecedentes_service']}", callback_data="buy_antecedentes")],
                [InlineKeyboardButton(f"🏛️ Tasas gobierno — €{PRICING['govt_fees_service']}", callback_data="buy_govt_fees")],
                [InlineKeyboardButton("← Volver", callback_data="back")],
            ]))
        return ST_MAIN_MENU

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

    # Category selected → show questions in that category
    if d.startswith("fcat_"):
        cat_key = d[5:]
        cat = FAQ_CATEGORIES.get(cat_key)
        if cat:
            ctx.user_data["faq_cat"] = cat_key
            await q.edit_message_text(
                f"*{cat['title']}*\n\nSeleccione una pregunta:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=faq_category_kb(cat_key))
            return ST_FAQ_CATEGORY

    # Question selected → show answer
    if d.startswith("fq_"):
        key = d[3:]
        faq = FAQ.get(key)
        if faq:
            text = faq["text"].replace("{days}", str(days_left()))
            # Build back buttons — include back-to-category if available
            btns = []
            cat_key = ctx.user_data.get("faq_cat")
            if cat_key and cat_key in FAQ_CATEGORIES:
                btns.append([InlineKeyboardButton(
                    f"← {FAQ_CATEGORIES[cat_key]['title']}",
                    callback_data=f"fcat_{cat_key}")])
            btns.append([InlineKeyboardButton("📋 Todas las categorías", callback_data="m_faq")])
            btns.append([InlineKeyboardButton("← Menú principal", callback_data="back")])
            await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(btns))
        return ST_FAQ_ITEM

    if d == "m_faq":
        await q.edit_message_text(
            "*Preguntas frecuentes*\n\nSeleccione una categoría:",
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
    tid = update.effective_user.id

    # Save document immediately — always accept, admin reviews later
    doc_id = save_document(
        tid=tid,
        doc_type=dtype,
        file_id=file_id,
        ocr_text="",
        detected_type=dtype,
        score=50,
        notes="pending_review",
        approved=0,
    )

    dc = get_doc_count(tid)
    user = get_user(tid)

    # Phase 2 unlock check
    unlock = ""
    if dc >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        unlock = "\n\n🎉 Ya puedes desbloquear la *revisión legal completa* por €39."

    # Always show success to user
    share_hint = ""
    if dc >= 3:
        share_hint = "\n\n💡 ¿Conoces a alguien en tu misma situación? Invítalo y gana €25 de crédito."

    await update.message.reply_text(
        f"✅ *¡Documento recibido!*\n\n"
        f"Tu *{info['name']}* ha sido guardado y será revisado por nuestro equipo "
        f"legal en las próximas horas.\n\n"
        f"Te notificaremos cuando esté verificado. Mientras tanto, puedes seguir "
        f"subiendo más documentos.\n\n"
        f"📄 Documentos subidos: {dc}{unlock}{share_hint}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Subir otro documento", callback_data="m_upload")],
            [InlineKeyboardButton("📣 Invitar amigos", callback_data="m_referidos")],
            [InlineKeyboardButton("Volver al menú", callback_data="back")],
        ]),
    )

    # Notify admins with photo for review
    user_name = user.get('full_name') or user.get('first_name') or update.effective_user.first_name or f"Usuario {tid}"

    for aid in ADMIN_IDS:
        try:
            await ctx.bot.send_photo(
                aid,
                file_id,
                caption=(
                    f"📄 *Nuevo documento para revisar*\n"
                    f"Usuario: {user_name} (TID: {tid})\n"
                    f"Tipo: {info['name']}\n"
                    f"DocID: {doc_id}\n"
                    f"Total docs: {dc}\n\n"
                    f"Use /pendientes para revisar"
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            logger.error(f"Failed to send admin photo notification to {aid}: {e}")

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
    tid = update.effective_user.id
    dtype = ctx.user_data.get("doc_type", "other")
    info = DOC_TYPES.get(dtype, DOC_TYPES["other"])

    # Save document immediately — always accept, admin reviews later
    doc_id = save_document(
        tid, dtype, file_id,
        ocr_text=f"[PDF/File: {file_name}]",
        detected_type=dtype,
        score=50,
        notes="pending_review",
        approved=0,
    )

    dc = get_doc_count(tid)
    user = get_user(tid)

    unlock = ""
    if dc >= MIN_DOCS_FOR_PHASE2 and not user.get("phase2_paid"):
        unlock = "\n\n🎉 Ya puedes desbloquear la *revisión legal completa* por €39."

    # Always show success to user
    share_hint = ""
    if dc >= 3:
        share_hint = "\n\n💡 ¿Conoces a alguien en tu misma situación? Invítalo y gana €25 de crédito."

    await update.message.reply_text(
        f"✅ *¡Documento recibido!*\n\n"
        f"Tu *{info['name']}* ha sido guardado y será revisado por nuestro equipo "
        f"legal en las próximas horas.\n\n"
        f"Te notificaremos cuando esté verificado. Mientras tanto, puedes seguir "
        f"subiendo más documentos.\n\n"
        f"📄 Documentos subidos: {dc}{unlock}{share_hint}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Subir otro documento", callback_data="m_upload")],
            [InlineKeyboardButton("📣 Invitar amigos", callback_data="m_referidos")],
            [InlineKeyboardButton("Volver al menú", callback_data="back")],
        ]),
    )

    # Notify admins
    user_name = user.get('full_name') or user.get('first_name') or update.effective_user.first_name or f"Usuario {tid}"

    for aid in ADMIN_IDS:
        try:
            await ctx.bot.send_document(
                aid,
                file_id,
                caption=(
                    f"📎 *Nuevo documento para revisar*\n"
                    f"Usuario: {user_name} (TID: {tid})\n"
                    f"Tipo: {info['name']}\n"
                    f"Archivo: {file_name}\n"
                    f"DocID: {doc_id}\n"
                    f"Total docs: {dc}\n\n"
                    f"Use /pendientes para revisar"
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            logger.error(f"Failed to send admin file notification to {aid}: {e}")

    return ST_MAIN_MENU


# --- Free-text handler (NLU) ---

async def handle_free_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle any text that isn't a button press."""
    text = update.message.text or ""

    # Catch commands that somehow got through
    if text.startswith("/"):
        if text.lower().startswith("/reset"):
            return await cmd_reset(update, ctx)
        elif text.lower().startswith("/start"):
            return await cmd_start(update, ctx)
        elif text.lower().startswith("/menu"):
            return await cmd_menu(update, ctx)
        elif text.lower().startswith("/referidos"):
            return await cmd_referidos(update, ctx)
        # Unknown command - ignore
        return ST_MAIN_MENU

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
            "✓ Tu consulta ha sido enviada. Te responderemos pronto.",
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
            "*¿Tienes una consulta para nuestro equipo legal?*\n\n"
            "Escribe tu mensaje aquí y lo trasladaremos a un abogado:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("← Volver al menú", callback_data="back")],
            ]))
        ctx.user_data["awaiting_human_msg"] = True
        return ST_HUMAN_MSG

    if intent == "price":
        await update.message.reply_text(FAQ["costo"]["text"], parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver al menú", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if intent == "status":
        return await show_main_menu(update, ctx)

    # Route all intents to their FAQ entries
    intent_faq_map = {
        "work": "contrato_trabajo",
        "online_submission": "como_presentar",
        "help": "requisitos",
        "family": "traer_familia",
        "deadline": "plazos",
        "asylum": "solicitantes_asilo",
        "trust": "es_real",
        "documents": "documentos_necesarios",
        "no_empadronamiento": "sin_empadronamiento",
        "travel": "salir_espana",
        "expired_passport": "pasaporte_vencido",
        "denial": "denegacion",
        "nationality": "nacionalidad",
        "tourist_entry": "turista",
        "prior_denial": "denegacion_previa",
        "expulsion": "orden_expulsion",
        "criminal_cert": "certificado_antecedentes",
        "response_time": "tiempo_respuesta",
        "work_while_waiting": "trabajar_mientras_espero",
        "payment_phases": "fases_pago",
        "permit_type": "que_permiso",
        "spanish_nationality": "nacionalidad_espanola",
        "safety": "seguridad_datos",
        "scam_accelerate": "estafa_acelerar",
        "why_now": "por_que_ahora",
        "tiempo_espana": "tiempo_espana",
    }
    # Special handling for antecedentes — show country-specific info
    if intent == "criminal_cert":
        await update.message.reply_text(
            ANTECEDENTES_HELP_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=antecedentes_help_kb(),
        )
        return ST_MAIN_MENU

    if intent in intent_faq_map:
        faq = FAQ.get(intent_faq_map[intent])
        if faq:
            await update.message.reply_text(
                faq["text"],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Verificar mi elegibilidad", callback_data="back")],
                    [InlineKeyboardButton("Más preguntas", callback_data="m_faq")],
                ]))
            return ST_MAIN_MENU

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


async def cmd_approve4(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not ctx.args:
        await update.message.reply_text("Uso: /approve4 <telegram_id>"); return
    try:
        tid = int(ctx.args[0])
        update_user(tid, phase4_paid=1, current_phase=4, state="phase4_active")
        await ctx.bot.send_message(tid,
            "Pago de la Fase 4 confirmado.\n\n"
            "Procederemos a presentar su solicitud ante Extranjería. "
            "Le enviaremos el número de registro y justificante de presentación.")
        await update.message.reply_text(f"Fase 4 aprobada para {tid}.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_ready(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Mark user's expediente as ready for Phase 4: /ready <telegram_id>"""
    if update.effective_user.id not in ADMIN_IDS: return
    if not ctx.args:
        await update.message.reply_text("Uso: /ready <telegram_id>"); return
    try:
        tid = int(ctx.args[0])
        update_user(tid, expediente_ready=1)
        await ctx.bot.send_message(tid,
            "Su expediente está completo y listo para presentar.\n\n"
            "Cuando desee proceder con la presentación oficial, "
            "acceda a su menú con /menu y pulse el botón de *Presentación*.",
            parse_mode=ParseMode.MARKDOWN)
        await update.message.reply_text(f"Expediente marcado como listo para {tid}.")
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
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users"); total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE eligible=1"); eligible = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE phase2_paid=1"); p2 = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE phase3_paid=1"); p3 = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE phase4_paid=1"); p4 = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM documents"); docs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM messages WHERE direction='in'"); msgs = c.fetchone()[0]
    conn.close()
    rev = (p2 * 39) + (p3 * 150) + (p4 * 110)
    db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
    await update.message.reply_text(
        f"*Estadísticas*\n\n"
        f"Usuarios: {total}\n"
        f"Elegibles: {eligible}\n"
        f"Documentos: {docs}\n"
        f"Mensajes recibidos: {msgs}\n\n"
        f"Fase 2 pagados: {p2} (€{p2*47})\n"
        f"Fase 3 pagados: {p3} (€{p3*150})\n"
        f"Fase 4 pagados: {p4} (€{p4*100})\n"
        f"*Ingresos: €{rev}*\n\n"
        f"DB: {db_type}\n"
        f"Días restantes: {days_left()}", parse_mode=ParseMode.MARKDOWN)


async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin broadcasts to all users: /broadcast <message>"""
    if update.effective_user.id not in ADMIN_IDS: return
    if not ctx.args:
        await update.message.reply_text("Uso: /broadcast <mensaje>"); return
    msg = " ".join(ctx.args)
    conn = get_connection()
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


async def cmd_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin views user profile: /user <telegram_id>"""
    caller_id = update.effective_user.id
    logger.info(f"/user called by {caller_id}, ADMIN_IDS={ADMIN_IDS}")
    if caller_id not in ADMIN_IDS:
        logger.warning(f"/user denied for {caller_id} - not in ADMIN_IDS")
        await update.message.reply_text(f"No autorizado. Tu ID: {caller_id}")
        return
    if not ctx.args:
        await update.message.reply_text("Uso: /user <telegram_id>")
        return
    try:
        tid = int(ctx.args[0])
        user = get_user(tid)
        if not user:
            await update.message.reply_text(f"Usuario {tid} no encontrado.")
            return

        # Get case info
        case = get_or_create_case(tid)
        docs = get_user_docs(tid)

        # Get country name
        country_code = user.get('country_code', '')
        country = COUNTRIES.get(country_code, {})
        country_name = f"{country.get('flag', '')} {country.get('name', country_code)}" if country else country_code

        # Build status text
        phases = []
        if user.get('phase2_paid'):
            phases.append("P2 ✓")
        if user.get('phase3_paid'):
            phases.append("P3 ✓")
        if user.get('phase4_paid'):
            phases.append("P4 ✓")
        phase_status = " | ".join(phases) if phases else "Sin pagos"

        # Referral info
        ref_code = user.get('referral_code', 'N/A')
        referred_by = user.get('referred_by_code', 'N/A')
        credits_earned = float(user.get('referral_credits_earned') or 0)
        credits_used = float(user.get('referral_credits_used') or 0)

        msg = (
            f"*Usuario: {tid}*\n\n"
            f"Nombre: {user.get('full_name') or user.get('first_name') or 'N/A'}\n"
            f"País: {country_name}\n"
            f"Elegible: {'Sí' if user.get('eligible') else 'No'}\n"
            f"Fase actual: {user.get('current_phase', 1)}\n"
            f"Pagos: {phase_status}\n"
            f"Expediente listo: {'Sí' if user.get('expediente_ready') else 'No'}\n\n"
            f"*Expediente:* {case.get('case_number', 'N/A')}\n"
            f"Estado: {case.get('status', 'N/A')}\n"
            f"Progreso: {case.get('progress', 0)}%\n\n"
            f"*Referidos:*\n"
            f"Código: `{ref_code}`\n"
            f"Referido por: {referred_by}\n"
            f"Créditos: €{credits_earned:.0f} ganados, €{credits_used:.0f} usados\n\n"
            f"*Documentos:* {len(docs)} subidos\n"
            f"Creado: {str(user.get('created_at', 'N/A'))[:19]}"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("ID inválido. Uso: /user <telegram_id>")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_docs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin views user documents: /docs <telegram_id>"""
    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        await update.message.reply_text(f"No autorizado. Tu ID: {caller_id}")
        return
    if not ctx.args:
        await update.message.reply_text("Uso: /docs <telegram_id>")
        return
    try:
        tid = int(ctx.args[0])
        user = get_user(tid)
        if not user:
            await update.message.reply_text(f"Usuario {tid} no encontrado.")
            return

        docs = get_user_docs(tid)
        if not docs:
            await update.message.reply_text(f"Usuario {tid} no tiene documentos.")
            return

        # Store docs for callback retrieval
        if 'admin_docs' not in ctx.user_data:
            ctx.user_data['admin_docs'] = {}
        ctx.user_data['admin_docs'][tid] = docs

        # Build document list with buttons
        msg = f"*Documentos de {tid}*\n({len(docs)} total)\n\n"
        buttons = []
        for i, doc in enumerate(docs):
            doc_type = doc.get('doc_type', 'unknown')
            detected = doc.get('detected_type', '')
            status = doc.get('status', 'pending')
            uploaded = str(doc.get('uploaded_at', ''))[:10]

            status_icon = "✓" if status == 'approved' else ("✗" if status == 'rejected' else "○")
            detected_str = f" → {detected}" if detected and detected != doc_type else ""

            msg += f"{i+1}. {status_icon} *{doc_type}*{detected_str}\n"
            msg += f"   {uploaded}\n\n"

            # Add button for this document
            buttons.append([InlineKeyboardButton(
                f"📄 {i+1}. {doc_type[:20]}",
                callback_data=f"adoc_{tid}_{i}"
            )])

        await update.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except ValueError:
        await update.message.reply_text("ID inválido. Uso: /docs <telegram_id>")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_doc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin views a specific document file: /doc <file_id>"""
    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        await update.message.reply_text(f"No autorizado. Tu ID: {caller_id}")
        return
    if not ctx.args:
        await update.message.reply_text("Uso: /doc <file_id>")
        return
    try:
        file_id = ctx.args[0]
        # Try to send the file back to admin
        try:
            await ctx.bot.send_document(update.effective_chat.id, file_id)
        except Exception:
            # If not a document, try as photo
            try:
                await ctx.bot.send_photo(update.effective_chat.id, file_id)
            except Exception as e:
                await update.message.reply_text(f"No se pudo enviar el archivo: {e}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def handle_admin_doc_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle admin document retrieval button clicks: adoc_{tid}_{index}"""
    q = update.callback_query
    await q.answer()

    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        return

    try:
        # Parse callback data: adoc_{tid}_{index}
        parts = q.data.split("_")
        tid = int(parts[1])
        idx = int(parts[2])

        # Get docs from stored data or fetch fresh
        docs = None
        if 'admin_docs' in ctx.user_data and tid in ctx.user_data['admin_docs']:
            docs = ctx.user_data['admin_docs'][tid]
        else:
            docs = get_user_docs(tid)

        if not docs or idx >= len(docs):
            await q.message.reply_text("Documento no encontrado. Use /docs de nuevo.")
            return

        doc = docs[idx]
        file_id = doc.get('file_id')
        doc_type = doc.get('doc_type', 'unknown')

        if not file_id:
            await q.message.reply_text("No hay file_id para este documento.")
            return

        # Try to send the file
        try:
            await ctx.bot.send_document(
                q.message.chat_id,
                file_id,
                caption=f"📄 {doc_type} - Usuario {tid}"
            )
        except Exception:
            # If not a document, try as photo
            try:
                await ctx.bot.send_photo(
                    q.message.chat_id,
                    file_id,
                    caption=f"📄 {doc_type} - Usuario {tid}"
                )
            except Exception as e:
                await q.message.reply_text(f"Error enviando archivo: {e}")
    except Exception as e:
        logger.error(f"Error in handle_admin_doc_callback: {e}")


async def cmd_pendientes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin command to view pending documents: /pendientes"""
    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        await update.message.reply_text(f"No autorizado. Tu ID: {caller_id}")
        return

    pending = get_pending_documents(limit=20)

    if not pending:
        await update.message.reply_text("✅ No hay documentos pendientes de revisión.")
        return

    # Show count summary
    await update.message.reply_text(f"📋 *{len(pending)} documentos pendientes de revisión*", parse_mode=ParseMode.MARKDOWN)

    # Show first document
    await show_pending_document(update, ctx, pending[0])


async def show_pending_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE, doc: Dict):
    """Show a pending document with action buttons."""
    doc_id = doc.get('id')
    tid = doc.get('telegram_id')
    first_name = doc.get('first_name') or 'Usuario'
    doc_type = doc.get('doc_type', 'unknown')
    ai_type = doc.get('ai_type', '')
    confidence = doc.get('ai_confidence', 0) or 0
    issues = doc.get('issues', '')
    extracted_name = doc.get('extracted_name', '')
    extracted_date = doc.get('extracted_date', '')
    file_id = doc.get('file_id')

    type_name = DOC_TYPES.get(doc_type, {}).get('name', doc_type)

    # Confidence indicator
    if confidence >= 0.6:
        conf_icon = "🟡 Media"
    else:
        conf_icon = "🔴 Baja"

    # Build info message
    msg = f"*📄 Documento #{doc_id}*\n\n"
    msg += f"*Usuario:* {first_name} (TID: {tid})\n"
    msg += f"*Tipo esperado:* {type_name}\n"
    msg += f"*Tipo detectado:* {ai_type or 'N/A'}\n"
    msg += f"*Confianza:* {conf_icon} ({int(confidence * 100)}%)\n"

    if extracted_name:
        msg += f"*Nombre extraído:* {extracted_name}\n"
    if extracted_date:
        msg += f"*Fecha:* {extracted_date}\n"
    if issues:
        msg += f"\n⚠️ *Problemas:* {issues}\n"

    # Action buttons
    buttons = [
        [
            InlineKeyboardButton("✓ Aprobar", callback_data=f"pdoc_approve_{doc_id}"),
            InlineKeyboardButton("✗ Rechazar", callback_data=f"pdoc_reject_{doc_id}"),
        ],
        [
            InlineKeyboardButton("🔄 Pedir nueva foto", callback_data=f"pdoc_resubmit_{doc_id}"),
            InlineKeyboardButton("⏭ Siguiente", callback_data="pdoc_next"),
        ],
    ]

    # Send the document image first
    chat_id = update.effective_chat.id
    if file_id:
        try:
            await ctx.bot.send_photo(
                chat_id,
                file_id,
                caption=f"📄 {type_name} - Doc #{doc_id} - {first_name}"
            )
        except Exception:
            try:
                await ctx.bot.send_document(
                    chat_id,
                    file_id,
                    caption=f"📄 {type_name} - Doc #{doc_id} - {first_name}"
                )
            except Exception as e:
                msg += f"\n\n❌ No se pudo cargar el archivo: {e}"

    # Send info message with buttons
    if update.callback_query:
        await ctx.bot.send_message(
            chat_id,
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


async def handle_pending_doc_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle pending document action callbacks: pdoc_approve_{id}, pdoc_reject_{id}, etc."""
    q = update.callback_query
    await q.answer()

    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        return

    data = q.data

    if data == "pdoc_next":
        pending = get_pending_documents(limit=1)
        if pending:
            await show_pending_document(update, ctx, pending[0])
        else:
            await q.message.reply_text("✅ No hay más documentos pendientes.")
        return

    # Parse action and doc_id
    parts = data.split("_")
    if len(parts) < 3:
        return

    action = parts[1]  # approve, reject, resubmit
    doc_id = int(parts[2])

    doc = get_document_by_id(doc_id)
    if not doc:
        await q.message.reply_text(f"Documento {doc_id} no encontrado.")
        return

    tid = doc.get('telegram_id')
    doc_type = doc.get('doc_type', 'unknown')
    type_name = DOC_TYPES.get(doc_type, {}).get('name', doc_type)

    if action == "approve":
        success = update_document_approval(doc_id, 1)
        if success:
            await q.message.reply_text(f"✅ Documento #{doc_id} aprobado.")
            try:
                await ctx.bot.send_message(
                    tid,
                    f"✅ *Documento aprobado*\n\n"
                    f"Tu documento «{type_name}» ha sido revisado y aprobado por nuestro equipo.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to notify user {tid}: {e}")

        # Auto-advance to next
        pending = get_pending_documents(limit=1)
        if pending:
            await show_pending_document(update, ctx, pending[0])
        else:
            await q.message.reply_text("✅ No hay más documentos pendientes.")
        return

    elif action == "reject":
        # Show rejection reason buttons
        buttons = [
            [InlineKeyboardButton("📷 Borroso/ilegible", callback_data=f"prej_blur_{doc_id}")],
            [InlineKeyboardButton("✂️ Incompleto/recortado", callback_data=f"prej_inc_{doc_id}")],
            [InlineKeyboardButton("📅 Documento vencido", callback_data=f"prej_exp_{doc_id}")],
            [InlineKeyboardButton("❓ Tipo incorrecto", callback_data=f"prej_wrong_{doc_id}")],
            [InlineKeyboardButton("🚫 No es documento válido", callback_data=f"prej_invalid_{doc_id}")],
            [InlineKeyboardButton("✏️ Otro motivo", callback_data=f"prej_other_{doc_id}")],
        ]
        await q.message.reply_text(
            f"*Seleccione el motivo del rechazo:*\nDocumento #{doc_id}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    elif action == "resubmit":
        # Show specific re-upload reason buttons
        ctx.user_data["resubmit_doc_id"] = doc_id
        buttons = [
            [InlineKeyboardButton("💡 Flash/reflejo", callback_data=f"pres_flash_{doc_id}")],
            [InlineKeyboardButton("🌑 Poca luz", callback_data=f"pres_dark_{doc_id}")],
            [InlineKeyboardButton("🔍 Borroso", callback_data=f"pres_blur_{doc_id}")],
            [InlineKeyboardButton("✂️ Cortado", callback_data=f"pres_cut_{doc_id}")],
            [InlineKeyboardButton("📐 Ángulo incorrecto", callback_data=f"pres_angle_{doc_id}")],
            [InlineKeyboardButton("📄 Sube frente/reverso", callback_data=f"pres_flip_{doc_id}")],
            [InlineKeyboardButton("✏️ Escribir mensaje personalizado", callback_data=f"pres_custom_{doc_id}")],
        ]
        await q.message.reply_text(
            f"*¿Por qué necesita nueva foto?*\nDocumento #{doc_id}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return


async def handle_rejection_reason_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle rejection reason callbacks: prej_*_{id}"""
    q = update.callback_query
    await q.answer()

    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        return

    # Parse reason and doc_id
    parts = q.data.split("_")
    if len(parts) < 3:
        return

    reason_code = parts[1]
    doc_id = int(parts[2])

    reasons = {
        "blur": "El documento está borroso o ilegible. Por favor, envía una foto más clara.",
        "inc": "El documento está incompleto o recortado. Por favor, incluye todo el documento en la foto.",
        "exp": "El documento parece estar vencido. Por favor, proporciona un documento vigente.",
        "wrong": "El tipo de documento no corresponde al solicitado. Verifica y envía el documento correcto.",
        "invalid": "El archivo enviado no es un documento válido. Sube una foto o PDF de un documento oficial.",
        "other": "El documento no puede ser aceptado. Contacta con soporte para más información.",
    }

    reason = reasons.get(reason_code, reasons["other"])

    doc = get_document_by_id(doc_id)
    if not doc:
        await q.message.reply_text(f"Documento {doc_id} no encontrado.")
        return

    tid = doc.get('telegram_id')
    doc_type = doc.get('doc_type', 'unknown')
    type_name = DOC_TYPES.get(doc_type, {}).get('name', doc_type)

    success = update_document_approval(doc_id, -1)  # -1 = rejected
    if success:
        await q.message.reply_text(f"❌ Documento #{doc_id} rechazado: {reason_code}")
        try:
            await ctx.bot.send_message(
                tid,
                f"❌ *Documento rechazado*\n\n"
                f"Tu documento «{type_name}» no ha podido ser aceptado.\n\n"
                f"*Motivo:* {reason}\n\n"
                f"Por favor, sube una nueva versión del documento.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to notify user {tid}: {e}")

    # Auto-advance to next
    pending = get_pending_documents(limit=1)
    if pending:
        await show_pending_document(update, ctx, pending[0])
    else:
        await q.message.reply_text("✅ No hay más documentos pendientes.")


async def handle_resubmit_reason_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle resubmit reason callbacks: pres_*_{id}"""
    q = update.callback_query
    await q.answer()

    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        return

    parts = q.data.split("_")
    if len(parts) < 3:
        return

    reason_code = parts[1]
    doc_id = int(parts[2])

    doc = get_document_by_id(doc_id)
    if not doc:
        await q.message.reply_text(f"Documento {doc_id} no encontrado.")
        return

    tid = doc.get('telegram_id')
    doc_type = doc.get('doc_type', 'unknown')
    type_name = DOC_TYPES.get(doc_type, {}).get('name', doc_type)

    # Custom message flow
    if reason_code == "custom":
        ctx.user_data["custom_resubmit_doc_id"] = doc_id
        ctx.user_data["custom_resubmit_tid"] = tid
        ctx.user_data["custom_resubmit_type"] = type_name
        await q.message.reply_text(
            f"Escribe el mensaje que quieres enviar al usuario sobre su *{type_name}* (Doc #{doc_id}):",
            parse_mode=ParseMode.MARKDOWN
        )
        return  # Wait for admin text input

    # Template messages
    templates = {
        "flash": "📸 Tu documento tiene reflejo o brillo, probablemente por el flash. Por favor, toma otra foto con luz natural, sin flash.",
        "dark": "🌑 La imagen está muy oscura. Busca un lugar con mejor iluminación y vuelve a intentarlo.",
        "blur": "🔍 La imagen está borrosa. Asegúrate de que la cámara enfoque bien antes de tomar la foto.",
        "cut": "✂️ El documento aparece cortado. Asegúrate de que se vea completo, incluyendo todos los bordes.",
        "angle": "📐 El documento está en ángulo. Colócalo sobre una superficie plana y toma la foto desde arriba.",
        "flip": "📄 Necesitamos ver el otro lado del documento. Por favor, sube una foto del frente/reverso.",
    }

    message = templates.get(reason_code, "Por favor, envía una nueva foto de este documento.")

    success = update_document_approval(doc_id, -2)  # -2 = needs resubmission
    if success:
        await q.message.reply_text(f"🔄 Pedida nueva foto para documento #{doc_id}: {reason_code}")
        try:
            await ctx.bot.send_message(
                tid,
                f"🔄 *Nueva foto necesaria*\n\n"
                f"Sobre tu «{type_name}»:\n\n"
                f"{message}",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to notify user {tid}: {e}")

    # Auto-advance to next
    pending = get_pending_documents(limit=1)
    if pending:
        await show_pending_document(update, ctx, pending[0])
    else:
        await q.message.reply_text("✅ No hay más documentos pendientes.")


async def handle_admin_custom_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle admin custom message for document resubmission requests."""
    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        return  # Not admin, let other handlers process this
    doc_id = ctx.user_data.get("custom_resubmit_doc_id")
    if not doc_id:
        return  # No pending custom message, let other handlers process
    tid = ctx.user_data.pop("custom_resubmit_tid", None)
    type_name = ctx.user_data.pop("custom_resubmit_type", "documento")
    ctx.user_data.pop("custom_resubmit_doc_id", None)

    custom_msg = update.message.text.strip()

    success = update_document_approval(doc_id, -2)  # -2 = needs resubmission
    if success:
        await update.message.reply_text(f"🔄 Mensaje personalizado enviado para documento #{doc_id}.")
        try:
            await ctx.bot.send_message(
                tid,
                f"📝 *Sobre tu {type_name}:*\n\n{custom_msg}",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to send custom message to user {tid}: {e}")

    # Auto-advance to next
    pending = get_pending_documents(limit=1)
    if pending:
        await show_pending_document(update, ctx, pending[0])
    else:
        await update.message.reply_text("✅ No hay más documentos pendientes.")


async def cmd_aprobar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin command to approve a document: /aprobar <doc_id>"""
    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        await update.message.reply_text(f"No autorizado. Tu ID: {caller_id}")
        return

    if not ctx.args:
        await update.message.reply_text("Uso: /aprobar <doc_id>")
        return

    try:
        doc_id = int(ctx.args[0])
        doc = get_document_by_id(doc_id)

        if not doc:
            await update.message.reply_text(f"Documento {doc_id} no encontrado.")
            return

        if doc.get('approved') == 1:
            await update.message.reply_text(f"Documento {doc_id} ya está aprobado.")
            return

        success = update_document_approval(doc_id, 1)
        if success:
            tid = doc.get('telegram_id')
            doc_type = doc.get('doc_type', 'unknown')
            type_name = DOC_TYPES.get(doc_type, {}).get('name', doc_type)

            await update.message.reply_text(f"✅ Documento {doc_id} aprobado.\nTipo: {type_name}\nUsuario: {tid}")

            # Notify user that their document was approved
            try:
                await ctx.bot.send_message(
                    tid,
                    f"✅ *Documento aprobado*\n\n"
                    f"Su documento «{type_name}» ha sido revisado y aprobado por nuestro equipo.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to notify user {tid} of approval: {e}")
        else:
            await update.message.reply_text(f"Error al aprobar documento {doc_id}.")

    except ValueError:
        await update.message.reply_text("ID inválido. Uso: /aprobar <doc_id>")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_rechazar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin command to reject a document: /rechazar <doc_id> [motivo]"""
    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        await update.message.reply_text(f"No autorizado. Tu ID: {caller_id}")
        return

    if not ctx.args:
        await update.message.reply_text("Uso: /rechazar <doc_id> [motivo]")
        return

    try:
        doc_id = int(ctx.args[0])
        reason = " ".join(ctx.args[1:]) if len(ctx.args) > 1 else "Documento no válido o ilegible"

        doc = get_document_by_id(doc_id)

        if not doc:
            await update.message.reply_text(f"Documento {doc_id} no encontrado.")
            return

        if doc.get('approved') == -1:
            await update.message.reply_text(f"Documento {doc_id} ya está rechazado.")
            return

        success = update_document_approval(doc_id, -1)
        if success:
            tid = doc.get('telegram_id')
            doc_type = doc.get('doc_type', 'unknown')
            type_name = DOC_TYPES.get(doc_type, {}).get('name', doc_type)

            await update.message.reply_text(f"❌ Documento {doc_id} rechazado.\nTipo: {type_name}\nUsuario: {tid}\nMotivo: {reason}")

            # Notify user that their document was rejected
            try:
                await ctx.bot.send_message(
                    tid,
                    f"❌ *Documento rechazado*\n\n"
                    f"Su documento «{type_name}» ha sido revisado y no puede ser aceptado.\n\n"
                    f"*Motivo:* {reason}\n\n"
                    f"Por favor, suba una nueva versión del documento.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to notify user {tid} of rejection: {e}")
        else:
            await update.message.reply_text(f"Error al rechazar documento {doc_id}.")

    except ValueError:
        await update.message.reply_text("ID inválido. Uso: /rechazar <doc_id> [motivo]")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_ver(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin command to view a document by ID: /ver <doc_id>"""
    caller_id = update.effective_user.id
    if caller_id not in ADMIN_IDS:
        await update.message.reply_text(f"No autorizado. Tu ID: {caller_id}")
        return

    if not ctx.args:
        await update.message.reply_text("Uso: /ver <doc_id>")
        return

    try:
        doc_id = int(ctx.args[0])
        doc = get_document_by_id(doc_id)

        if not doc:
            await update.message.reply_text(f"Documento {doc_id} no encontrado.")
            return

        # Build info message
        tid = doc.get('telegram_id')
        first_name = doc.get('first_name', 'Usuario')
        doc_type = doc.get('doc_type', 'unknown')
        type_name = DOC_TYPES.get(doc_type, {}).get('name', doc_type)
        ai_type = doc.get('ai_type', 'N/A')
        confidence = doc.get('ai_confidence', 0) or 0
        extracted_name = doc.get('extracted_name', '')
        extracted_address = doc.get('extracted_address', '')
        extracted_date = doc.get('extracted_date', '')
        issues = doc.get('issues', '')
        approved = doc.get('approved', 0)

        status_text = "✅ Aprobado" if approved == 1 else ("❌ Rechazado" if approved == -1 else "⏳ Pendiente")

        msg = f"*📄 Documento #{doc_id}*\n\n"
        msg += f"*Usuario:* {first_name} (TID: {tid})\n"
        msg += f"*Tipo esperado:* {type_name}\n"
        msg += f"*Tipo detectado:* {ai_type}\n"
        msg += f"*Confianza IA:* {int(confidence * 100)}%\n"
        msg += f"*Estado:* {status_text}\n\n"

        if extracted_name:
            msg += f"*Nombre extraído:* {extracted_name}\n"
        if extracted_address:
            msg += f"*Dirección:* {extracted_address[:100]}\n"
        if extracted_date:
            msg += f"*Fecha:* {extracted_date}\n"
        if issues:
            msg += f"\n⚠️ *Problemas:* {issues}\n"

        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

        # Send the actual file
        file_id = doc.get('file_id')
        if file_id:
            try:
                await ctx.bot.send_document(
                    update.effective_chat.id,
                    file_id,
                    caption=f"📄 {type_name} - Doc #{doc_id}"
                )
            except Exception:
                try:
                    await ctx.bot.send_photo(
                        update.effective_chat.id,
                        file_id,
                        caption=f"📄 {type_name} - Doc #{doc_id}"
                    )
                except Exception as e:
                    await update.message.reply_text(f"Error enviando archivo: {e}")

    except ValueError:
        await update.message.reply_text("ID inválido. Uso: /ver <doc_id>")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_referidos(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show referral stats for user."""
    tid = update.effective_user.id
    stats = get_referral_stats(tid)

    if not stats or not stats['code']:
        await update.message.reply_text(
            "Aún no tienes código de referidos.\n"
            "Completa la verificación de elegibilidad primero.",
        )
        return ConversationHandler.END

    text = build_referidos_text(stats)
    buttons = get_share_buttons(stats['code'])
    buttons.append([InlineKeyboardButton("← Menú", callback_data="back")])

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return ST_MAIN_MENU


async def cmd_estado(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's case status: /estado"""
    tid = update.effective_user.id
    user = get_user(tid)

    if not user:
        await update.message.reply_text(
            "No tiene una cuenta registrada.\n"
            "Escriba /start para comenzar.",
        )
        return ConversationHandler.END

    # Get case and docs info
    case = get_or_create_case(tid)
    docs = get_user_docs(tid)

    # Determine phase status
    phase = user.get('current_phase', 1)
    phase_names = {
        1: "Registro",
        2: "Revisión de documentos",
        3: "Preparación de expediente",
        4: "Presentación",
    }
    phase_name = phase_names.get(phase, "Registro")

    # Payment status
    payments = []
    if user.get('phase2_paid'):
        payments.append("Fase 2 ✓")
    if user.get('phase3_paid'):
        payments.append("Fase 3 ✓")
    if user.get('phase4_paid'):
        payments.append("Fase 4 ✓")
    payment_status = " | ".join(payments) if payments else "Sin pagos realizados"

    # Progress bar (shared calculation)
    dc_approved = get_approved_doc_count(tid)
    progress = calculate_progress(user, dc_approved)
    filled = progress // 10
    bar = "█" * filled + "░" * (10 - filled)

    # Doc summary
    doc_status = f"📄 Documentos: {len(docs)} subidos"
    if dc_approved < len(docs):
        pending = len(docs) - dc_approved
        doc_status += f" ({dc_approved} aprobados, {pending} en revisión)"
    elif dc_approved > 0:
        doc_status += f" ({dc_approved} aprobados)"

    await update.message.reply_text(
        f"*Estado de su expediente*\n\n"
        f"📋 Expediente: `{case.get('case_number', 'N/A')}`\n"
        f"📊 Fase actual: {phase_name(user)}\n"
        f"💳 Pagos: {payment_status}\n"
        f"{doc_status}\n"
        f"📈 Progreso: {bar} {progress}%\n\n"
        f"{'✅ Expediente listo para presentar' if user.get('expediente_ready') else '⏳ En proceso'}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Ver documentos", callback_data="m_docs")],
            [InlineKeyboardButton("📤 Subir documento", callback_data="m_upload")],
            [InlineKeyboardButton("📣 Compartir mi código", callback_data="m_referidos")],
            [InlineKeyboardButton("← Menú", callback_data="back")],
        ]),
    )
    return ST_MAIN_MENU


async def cmd_documentos(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's uploaded documents: /documentos"""
    tid = update.effective_user.id
    user = get_user(tid)

    if not user:
        await update.message.reply_text(
            "No tiene una cuenta registrada.\n"
            "Escriba /start para comenzar.",
        )
        return ConversationHandler.END

    docs = get_user_docs(tid)

    if not docs:
        await update.message.reply_text(
            "No ha subido ningún documento todavía.\n\n"
            "Use el menú para subir sus documentos.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 Subir documentos", callback_data="m_docs")],
                [InlineKeyboardButton("← Menú", callback_data="m_menu")],
            ]),
        )
        return ST_MAIN_MENU

    # Build document list
    msg = f"*Sus documentos* ({len(docs)} total)\n\n"
    for i, doc in enumerate(docs, 1):
        doc_type = doc.get('doc_type', 'Documento')
        status = doc.get('status', 'pending')
        status_icon = "✅" if status == 'approved' else ("❌" if status == 'rejected' else "⏳")
        status_text = "Aprobado" if status == 'approved' else ("Rechazado" if status == 'rejected' else "Pendiente")
        uploaded = str(doc.get('uploaded_at', ''))[:10]

        msg += f"{i}. {status_icon} *{doc_type}*\n"
        msg += f"   Estado: {status_text} | {uploaded}\n\n"

    await update.message.reply_text(
        msg,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Subir más documentos", callback_data="m_docs")],
            [InlineKeyboardButton("← Menú", callback_data="m_menu")],
        ]),
    )
    return ST_MAIN_MENU


async def cmd_ayuda(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show FAQ menu: /ayuda"""
    await update.message.reply_text(
        "*Preguntas frecuentes*\n\nSeleccione una categoría:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=faq_menu_kb(),
    )
    return ST_FAQ_MENU


async def cmd_antecedentes(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show generic antecedentes help + service offer: /antecedentes"""
    tid = update.effective_user.id
    user = get_user(tid)

    if not user:
        await update.message.reply_text(
            "No tiene una cuenta registrada.\n"
            "Escriba /start para comenzar.",
        )
        return ConversationHandler.END

    await update.message.reply_text(
        ANTECEDENTES_HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=antecedentes_help_kb(),
    )
    return ST_MAIN_MENU


async def cmd_contacto(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Start human contact flow: /contacto"""
    await update.message.reply_text(
        "*¿Tienes una consulta para nuestro equipo legal?*\n\n"
        "Escribe tu mensaje aquí y lo trasladaremos a un abogado:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("← Menú", callback_data="m_menu")],
        ]),
    )
    ctx.user_data["awaiting_human_msg"] = True
    return ST_HUMAN_MSG


# =============================================================================
# RE-ENGAGEMENT REMINDERS (Job Queue)
# =============================================================================

def get_users_for_reminder(hours_since_update: int, phase_filter: str = None) -> List[Dict]:
    """Get users who haven't interacted in X hours and haven't paid phase2 yet."""
    conn = get_connection()
    c = conn.cursor()
    p = db_param()

    if USE_POSTGRES:
        query = f"""
            SELECT telegram_id, first_name, country_code
            FROM users
            WHERE phase2_paid = 0
            AND eligible = 1
            AND updated_at < NOW() - INTERVAL '{hours_since_update} hours'
            AND updated_at > NOW() - INTERVAL '{hours_since_update + 24} hours'
        """
    else:
        query = f"""
            SELECT telegram_id, first_name, country_code
            FROM users
            WHERE phase2_paid = 0
            AND eligible = 1
            AND updated_at < datetime('now', '-{hours_since_update} hours')
            AND updated_at > datetime('now', '-{hours_since_update + 24} hours')
        """

    c.execute(query)
    rows = c.fetchall()
    result = [{"telegram_id": r[0], "first_name": r[1], "country_code": r[2]} for r in rows]
    conn.close()
    return result


async def send_reminder_24h(context: ContextTypes.DEFAULT_TYPE):
    """Send 24h reminder to users who started but haven't uploaded enough docs."""
    users = get_users_for_reminder(24)
    dl = days_left()

    for user in users:
        try:
            dc = get_doc_count(user["telegram_id"])
            if dc < MIN_DOCS_FOR_PHASE2:
                await context.bot.send_message(
                    user["telegram_id"],
                    f"Hola {user['first_name']},\n\n"
                    f"Vimos que comenzó su proceso de regularización pero aún no ha subido todos sus documentos.\n\n"
                    f"📄 Documentos subidos: {dc}\n"
                    f"📋 Mínimo recomendado: {MIN_DOCS_FOR_PHASE2}\n"
                    f"⏰ Días restantes: {dl}\n\n"
                    "Cuanto antes suba su documentación, antes podremos revisarla y asegurar que todo esté correcto.\n\n"
                    "Escriba /menu para continuar.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"24h reminder sent to {user['telegram_id']}")
        except Exception as e:
            logger.warning(f"Failed to send 24h reminder to {user['telegram_id']}: {e}")


async def send_reminder_72h(context: ContextTypes.DEFAULT_TYPE):
    """Send 72h reminder with urgency."""
    users = get_users_for_reminder(72)
    dl = days_left()

    for user in users:
        try:
            dc = get_doc_count(user["telegram_id"])
            if dc < MIN_DOCS_FOR_PHASE2:
                await context.bot.send_message(
                    user["telegram_id"],
                    f"Hola {user['first_name']},\n\n"
                    f"Han pasado 3 días desde que inició su proceso. El plazo de regularización cierra en *{dl} días*.\n\n"
                    "No pierda esta oportunidad única de regularizar su situación. "
                    "Más de 500 personas ya han completado su documentación con nosotros.\n\n"
                    "Recuerde: todo lo que haga en esta fase es *gratuito*. "
                    "Solo le pediremos un pago cuando hayamos revisado su caso.\n\n"
                    "Escriba /menu para retomar su proceso.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"72h reminder sent to {user['telegram_id']}")
        except Exception as e:
            logger.warning(f"Failed to send 72h reminder to {user['telegram_id']}: {e}")


async def send_reminder_1week(context: ContextTypes.DEFAULT_TYPE):
    """Send 1 week reminder - last chance."""
    users = get_users_for_reminder(168)  # 7 days * 24 hours
    dl = days_left()

    for user in users:
        try:
            await context.bot.send_message(
                user["telegram_id"],
                f"Hola {user['first_name']},\n\n"
                f"Ha pasado una semana desde que comenzó su proceso de regularización.\n\n"
                f"⚠️ *Solo quedan {dl} días* para presentar su solicitud.\n\n"
                "Entendemos que puede tener dudas o dificultades. "
                "Nuestro equipo está disponible para ayudarle en cada paso.\n\n"
                "Si necesita hablar con alguien, escriba /menu y pulse *Hablar con nuestro equipo*.\n\n"
                "No deje pasar esta oportunidad histórica.",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"1week reminder sent to {user['telegram_id']}")
        except Exception as e:
            logger.warning(f"Failed to send 1week reminder to {user['telegram_id']}: {e}")


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
            CommandHandler("estado", cmd_estado),
            CommandHandler("documentos", cmd_documentos),
            CommandHandler("referidos", cmd_referidos),
            CommandHandler("ayuda", cmd_ayuda),
            CommandHandler("contacto", cmd_contacto),
            CommandHandler("antecedentes", cmd_antecedentes),
        ],
        states={
            ST_ENTER_REFERRAL_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_referral_code_text),
                CallbackQueryHandler(handle_referral_callbacks, pattern="^ref_"),
            ],
            ST_COUNTRY: [
                CallbackQueryHandler(handle_country, pattern="^c_"),
            ],
            ST_FULL_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_full_name),
            ],
            ST_Q1_DATE: [
                CallbackQueryHandler(handle_q1),
            ],
            ST_Q2_TIME: [
                CallbackQueryHandler(handle_q2),
            ],
            ST_Q3_RECORD: [
                CallbackQueryHandler(handle_q3),
            ],
            ST_ELIGIBLE: [
                CallbackQueryHandler(handle_menu),
            ],
            ST_NOT_ELIGIBLE: [
                CallbackQueryHandler(handle_menu),
            ],
            ST_SERVICE_INFO: [
                CallbackQueryHandler(handle_menu),
            ],
            ST_FAQ_MENU: [
                CallbackQueryHandler(handle_faq_menu),
            ],
            ST_FAQ_CATEGORY: [
                CallbackQueryHandler(handle_faq_menu),
            ],
            ST_FAQ_ITEM: [
                CallbackQueryHandler(handle_faq_menu),
            ],
            ST_MAIN_MENU: [
                CallbackQueryHandler(handle_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text),
                MessageHandler(filters.PHOTO, handle_photo_upload),
                MessageHandler(filters.Document.ALL, handle_file_upload),
            ],
            ST_DOCS_LIST: [
                CallbackQueryHandler(handle_menu),
            ],
            ST_UPLOAD_SELECT: [
                CallbackQueryHandler(handle_menu),
            ],
            ST_UPLOAD_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo_upload),
                MessageHandler(filters.Document.ALL, handle_file_upload),
                CallbackQueryHandler(handle_menu),
            ],
            ST_PAY_PHASE2: [
                CallbackQueryHandler(handle_menu),
            ],
            ST_PAY_PHASE3: [
                CallbackQueryHandler(handle_menu),
            ],
            ST_PAY_PHASE4: [
                CallbackQueryHandler(handle_menu),
            ],
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
            CommandHandler("menu", cmd_menu),
            CommandHandler("estado", cmd_estado),
            CommandHandler("documentos", cmd_documentos),
            CommandHandler("referidos", cmd_referidos),
            CommandHandler("ayuda", cmd_ayuda),
            CommandHandler("contacto", cmd_contacto),
            CommandHandler("antecedentes", cmd_antecedentes),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text),
            MessageHandler(filters.PHOTO, handle_photo_upload),
            MessageHandler(filters.Document.ALL, handle_file_upload),
            CallbackQueryHandler(handle_menu),
        ],
    )

    app.add_handler(conv)

    # Public commands
    app.add_handler(CommandHandler("referidos", cmd_referidos))
    app.add_handler(CommandHandler("estado", cmd_estado))
    app.add_handler(CommandHandler("documentos", cmd_documentos))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))
    app.add_handler(CommandHandler("contacto", cmd_contacto))

    # Admin commands - use group=-1 for higher priority than ConversationHandler
    app.add_handler(CommandHandler("reset", cmd_reset), group=-1)
    app.add_handler(CommandHandler("approve2", cmd_approve2), group=-1)
    app.add_handler(CommandHandler("approve3", cmd_approve3), group=-1)
    app.add_handler(CommandHandler("approve4", cmd_approve4), group=-1)
    app.add_handler(CommandHandler("ready", cmd_ready), group=-1)
    app.add_handler(CommandHandler("reply", cmd_reply), group=-1)
    app.add_handler(CommandHandler("stats", cmd_stats), group=-1)
    app.add_handler(CommandHandler("broadcast", cmd_broadcast), group=-1)
    app.add_handler(CommandHandler("user", cmd_user), group=-1)
    app.add_handler(CommandHandler("docs", cmd_docs), group=-1)
    app.add_handler(CommandHandler("doc", cmd_doc), group=-1)
    app.add_handler(CommandHandler("pendientes", cmd_pendientes), group=-1)
    app.add_handler(CommandHandler("aprobar", cmd_aprobar), group=-1)
    app.add_handler(CommandHandler("rechazar", cmd_rechazar), group=-1)
    app.add_handler(CommandHandler("ver", cmd_ver), group=-1)
    app.add_handler(CallbackQueryHandler(handle_admin_doc_callback, pattern="^adoc_"), group=-1)
    app.add_handler(CallbackQueryHandler(handle_pending_doc_callback, pattern="^pdoc_"), group=-1)
    app.add_handler(CallbackQueryHandler(handle_rejection_reason_callback, pattern="^prej_"), group=-1)
    app.add_handler(CallbackQueryHandler(handle_resubmit_reason_callback, pattern="^pres_"), group=-1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_custom_message), group=-2)

    # Schedule re-engagement reminders (runs every 6 hours)
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(send_reminder_24h, interval=timedelta(hours=6), first=timedelta(minutes=5))
        job_queue.run_repeating(send_reminder_72h, interval=timedelta(hours=6), first=timedelta(minutes=10))
        job_queue.run_repeating(send_reminder_1week, interval=timedelta(hours=6), first=timedelta(minutes=15))
        logger.info("Re-engagement reminders scheduled (24h, 72h, 1week)")

    logger.info("PH-Bot v5.6.0 starting")
    logger.info(f"ADMIN_IDS: {ADMIN_IDS}")
    logger.info(f"Payment: FREE > €39 > €150 > €110 | Days left: {days_left()}")
    logger.info(f"Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
