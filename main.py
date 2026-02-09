#!/usr/bin/env python3
"""
================================================================================
PH-Bot v6.0.0 — Client Intake & Case Management
================================================================================
Repository: github.com/anacuero-bit/PH-Bot
Updated:    2026-02-09

CHANGELOG:
----------
v6.0.0 (2026-02-09)
  - MVP overhaul for pre-BOE launch
  - Added waitlist wall (blocks Phase 2+ until BOE publishes)
  - New pricing: €199 prepay / €247 by phases (€29 + €89 + €129)
  - Waitlist counter with deterministic fake growth
  - Professional Spanish tone, minimal emojis
  - Payment flows disabled until BOE publishes

v5.10.0 (2026-02-08)
  - NEW: Live capacity counter ("X de 1,000 plazas")
  - NEW: Waitlist system — triggers at Phase 2 when capacity full
  - NEW: Bypass waitlist with €254 prepay
  - NEW: waitlist DB table (PostgreSQL + SQLite)
  - NEW: /waitlist admin command (view capacity + waitlist stats)
  - NEW: /release admin command (notify waitlist users)
  - FIX: Referral credit triggers on friend's Phase 3 (was Phase 2, anti-gaming)
  - FIX: Referral discount applies to Phase 3 messaging
  - UPDATED: Eligibility message shows capacity counter
  - UPDATED: request_phase2 checks capacity before showing payment
  - UPDATED: /stats includes capacity + waitlist info

v5.9.0 (2026-02-08)
  - NEW: Phase 3 questionnaire (30 questions: personal data, address, employment, family, submission)
  - NEW: phase3_answers DB column + migration (PostgreSQL + SQLite)
  - NEW: Phase 3 handlers (handle_phase3_questionnaire, handle_phase3_text_answer)
  - NEW: 3 FAQ entries (¿Por qué tantas preguntas?, ¿Por qué sois más baratos?, ¿Por qué pagar si puedo hacerlo yo?)
  - NEW: Foreign antecedentes upsell after country selection (country-specific difficulty/time)
  - FIX: Referral code shown at paid3, paid4, m_pay3, m_pay4 (was only at paid2)
  - FIX: paid3 now starts Phase 3 questionnaire flow
  - UPDATED: paid4 shows referral info after payment

v5.8.0 (2026-02-08)
  - NEW: Phase 2 deep questionnaire (20 questions across 5 sections)
  - NEW: Personalized audit report generator (generate_phase2_report)
  - NEW: Competitive pricing messaging (PRICING_EXPLANATION)
  - NEW: Spain antecedentes upsell (€15 with DIY instructions)
  - NEW: Translation service upsell (€35/doc)
  - NEW: Priority processing upsell (€50)
  - NEW: VIP bundle (€320) and Phase 4 bundle (€175)
  - NEW: Country-specific antecedentes difficulty info
  - NEW: Phase 2 pitch after 3+ docs uploaded
  - NEW: Centralized STRIPE_LINKS dict
  - UPDATED: Welcome message with competitive pricing angle
  - UPDATED: Doc upload response with audit CTA
  - UPDATED: Extra services menu (5 services from 2)
  - UPDATED: All Stripe references use STRIPE_LINKS dict
  - UPDATED: All pricing references use PRICING dict consistently

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
import json
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
SUPPORT_PHONE_WA = os.environ.get("SUPPORT_PHONE_WA", SUPPORT_PHONE)  # WhatsApp number (may differ)
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

# =============================================================================
# CAPACITY MANAGEMENT
# =============================================================================
# MVP Launch Config
TOTAL_CAPACITY = 1000
BOE_PUBLISHED = False  # Flip to True when BOE publishes and payments open
PREPAY_BYPASS_PRICE = 199


def is_payments_enabled() -> bool:
    """Returns True only after BOE publishes."""
    return BOE_PUBLISHED

# =============================================================================
# CRITICAL DATES — USE THESE CONSTANTS EVERYWHERE
# =============================================================================
CUTOFF_DATE = "31 de diciembre de 2025"
CUTOFF_DATE_SHORT = "31/12/2025"
APPLICATION_START = "1 de abril de 2026"
APPLICATION_END = "30 de junio de 2026"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("ph-bot")

# =============================================================================
# PRICING (per PAYMENT_STRATEGY.md)
# =============================================================================

PRICING = {
    "phase1": 0,       # FREE — upload docs, get comfortable
    "phase2": 29,      # Audit + personalized strategy
    "phase3": 89,      # Tailored expediente preparation
    "phase4": 129,     # Submission + tracking
    "total_phases": 247,
    "prepay_discount": 48,
    "prepay_total": 199,
    # Extra services
    "antecedentes_spain": 29,      # Spain criminal record (we handle Cl@ve)
    "antecedentes_foreign": 49,    # Foreign certificate + apostille + translation
    "govt_fees_service": 29,       # We handle 790 tax form payments
    "translation_per_doc": 35,     # Sworn translation per document
    "urgent_processing": 50,       # Priority queue
    # Government fees (external — paid to government)
    "gov_fee": 38.28,
    "tie_card": 16,
    # Bundles
    "vip_bundle": 320,             # Phase 2+3+4 + antec Spain + govt fees
    "phase4_bundle": 175,          # Phase 4 + govt fees service + govt taxes
    # Referral
    "referral_discount": 25,
    "referral_credit": 25,
    "referral_max": 247,
}

# Stripe payment links (env vars — set in Railway)
STRIPE_LINKS = {
    "phase2": os.environ.get("STRIPE_PHASE2_LINK", ""),
    "phase3": os.environ.get("STRIPE_PHASE3_LINK", ""),
    "phase4": os.environ.get("STRIPE_PHASE4_LINK", ""),
    "prepay": os.environ.get("STRIPE_PREPAY_LINK", ""),
    "antecedentes_spain": os.environ.get("STRIPE_ANTEC_SPAIN_LINK", ""),
    "antecedentes_foreign": os.environ.get("STRIPE_ANTEC_FOREIGN_LINK", ""),
    "govt_fees": os.environ.get("STRIPE_GOVT_FEES_LINK", ""),
    "translation": os.environ.get("STRIPE_TRANSLATION_LINK", ""),
    "vip_bundle": os.environ.get("STRIPE_VIP_BUNDLE_LINK", ""),
    "phase4_bundle": os.environ.get("STRIPE_PHASE4_BUNDLE_LINK", ""),
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
    ST_PHASE2_QUESTIONNAIRE,
    ST_PHASE2_TEXT_ANSWER,
    ST_PHASE3_QUESTIONNAIRE,
    ST_PHASE3_TEXT_ANSWER,
    ST_WAITLIST,
) = range(27)

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
# COUNTRY-SPECIFIC ANTECEDENTES INFO (for upsell messaging)
# =============================================================================

COUNTRIES_ANTECEDENTES_INFO = {
    "co": {"difficulty": "media", "time": "2-3 semanas", "process": "Online + apostilla presencial", "notes": "Apostilla en Cancillería puede demorar"},
    "ve": {"difficulty": "alta", "time": "3-6 semanas", "process": "Presencial en Venezuela o consulado", "notes": "Proceso complicado por situación del país"},
    "pe": {"difficulty": "media", "time": "2-4 semanas", "process": "Online + apostilla", "notes": "Relativamente sencillo si tienes DNI peruano"},
    "ec": {"difficulty": "media", "time": "2-3 semanas", "process": "Online + apostilla en Cancillería", "notes": "Apostilla puede hacerse online"},
    "hn": {"difficulty": "alta", "time": "3-5 semanas", "process": "Presencial + apostilla", "notes": "Requiere gestiones locales"},
    "ma": {"difficulty": "alta", "time": "4-6 semanas", "process": "Consulado + legalización", "notes": "No es país Convenio de La Haya (sin apostilla)"},
    "sn": {"difficulty": "alta", "time": "4-8 semanas", "process": "Consulado + legalización", "notes": "No es país Convenio de La Haya"},
    "ar": {"difficulty": "baja", "time": "1-2 semanas", "process": "Online + apostilla electrónica", "notes": "Proceso relativamente rápido"},
    "bo": {"difficulty": "media", "time": "2-4 semanas", "process": "Presencial + apostilla", "notes": "Gestión en consulado o Bolivia"},
    "br": {"difficulty": "media", "time": "2-3 semanas", "process": "Online + apostilla", "notes": "Certificado digital disponible online"},
    "do": {"difficulty": "media", "time": "2-3 semanas", "process": "Online + apostilla", "notes": "Procuraduría General emite online"},
    "cu": {"difficulty": "alta", "time": "4-8 semanas", "process": "Consulado exclusivamente", "notes": "Solo se gestiona vía consulado en España"},
    "cn": {"difficulty": "alta", "time": "4-6 semanas", "process": "Consulado + legalización", "notes": "Proceso largo, requiere documentación china"},
    "pk": {"difficulty": "alta", "time": "4-6 semanas", "process": "Consulado + legalización", "notes": "Requiere verificación adicional"},
    "ng": {"difficulty": "alta", "time": "4-8 semanas", "process": "Consulado + legalización", "notes": "Tiempos variables por situación local"},
}

# =============================================================================
# PHASE 2 DEEP QUESTIONNAIRE
# =============================================================================

PHASE2_QUESTIONS = [
    # SECTION 1: History in Spain
    {"id": "arrival_date", "text": "📅 *¿Cuándo llegaste a España?*\n\nSi no recuerdas la fecha exacta, pon aproximada.", "type": "text", "section": "Historia en España"},
    {"id": "left_spain", "text": "✈️ *¿Has salido de España desde que llegaste?*", "type": "buttons",
     "options": [("No, nunca", "left_never"), ("Sí, una vez", "left_once"), ("Sí, varias veces", "left_multiple")],
     "section": "Historia en España"},
    {"id": "left_spain_details", "text": "¿Cuándo saliste y por cuánto tiempo?\n\n(Ejemplo: 'Diciembre 2024, 2 semanas')", "type": "text",
     "condition_field": "left_spain", "condition_values": ["left_once", "left_multiple"], "section": "Historia en España"},
    {"id": "arrival_proof", "text": "📄 *¿Tienes algún documento de tu llegada a España?*", "type": "buttons",
     "options": [("Billete de avión", "arrival_ticket"), ("Sello en pasaporte", "arrival_stamp"), ("Ambos", "arrival_both"), ("No tengo nada", "arrival_none")],
     "section": "Historia en España"},
    # SECTION 2: Current Situation
    {"id": "housing", "text": "🏠 *¿Dónde vives actualmente?*", "type": "buttons",
     "options": [("Piso alquilado a mi nombre", "housing_own"), ("Piso a nombre de otro", "housing_other"),
                 ("Habitación subarrendada", "housing_room"), ("Con familiares/amigos", "housing_family"), ("Otro", "housing_other_situation")],
     "section": "Situación Actual"},
    {"id": "employment", "text": "💼 *¿Trabajas actualmente?*", "type": "buttons",
     "options": [("Sí, con contrato", "work_contract"), ("Sí, sin contrato", "work_informal"),
                 ("Trabajo por apps (Glovo, etc)", "work_apps"), ("No trabajo", "work_none")],
     "section": "Situación Actual"},
    {"id": "employment_details", "text": "¿En qué sector trabajas y cuánto tiempo llevas?", "type": "text",
     "condition_field": "employment", "condition_values": ["work_contract", "work_informal", "work_apps"], "section": "Situación Actual"},
    {"id": "bank_account", "text": "🏦 *¿Tienes cuenta bancaria en España?*", "type": "buttons",
     "options": [("Sí, banco tradicional", "bank_traditional"), ("Sí, solo Revolut/N26/Wise", "bank_fintech"),
                 ("Ambos", "bank_both"), ("No tengo cuenta", "bank_none")],
     "section": "Situación Actual"},
    # SECTION 3: Family & Ties
    {"id": "children", "text": "👶 *¿Tienes hijos menores en España?*", "type": "buttons",
     "options": [("Sí", "children_yes"), ("No", "children_no")], "section": "Familia y Vínculos"},
    {"id": "children_details", "text": "¿Cuántos hijos? ¿Edades? ¿Nacieron aquí o llegaron contigo?", "type": "text",
     "condition_field": "children", "condition_values": ["children_yes"], "section": "Familia y Vínculos"},
    {"id": "partner", "text": "💑 *¿Tienes pareja en España?*", "type": "buttons",
     "options": [("Sí, con papeles (española/o o residente)", "partner_legal"), ("Sí, también irregular", "partner_irregular"), ("No", "partner_none")],
     "section": "Familia y Vínculos"},
    {"id": "other_family", "text": "👨‍👩‍👧 *¿Tienes otros familiares en España con papeles?*\n\n(Padres, hermanos, tíos...)", "type": "buttons",
     "options": [("Sí", "family_yes"), ("No", "family_no")], "section": "Familia y Vínculos"},
    {"id": "other_family_details", "text": "¿Qué familiar y qué tipo de permiso tiene?", "type": "text",
     "condition_field": "other_family", "condition_values": ["family_yes"], "section": "Familia y Vínculos"},
    # SECTION 4: Legal History
    {"id": "police_spain", "text": "👮 *¿Has tenido algún problema con la policía en España?*\n\n_Esto es confidencial y nos ayuda a preparar tu caso._", "type": "buttons",
     "options": [("No, nunca", "police_never"), ("Sí, algo menor", "police_minor"), ("Sí, algo serio", "police_serious")],
     "section": "Historial Legal"},
    {"id": "police_details", "text": "Cuéntanos brevemente qué pasó.\n\n_Esta información es confidencial y nos ayuda a preparar tu defensa._", "type": "text",
     "condition_field": "police_spain", "condition_values": ["police_minor", "police_serious"], "section": "Historial Legal"},
    {"id": "antecedentes_origin", "text": "📜 *¿Tienes antecedentes penales en tu país de origen?*", "type": "buttons",
     "options": [("No", "antecedentes_none"), ("Sí, pero cancelados", "antecedentes_cancelled"),
                 ("Sí, vigentes", "antecedentes_active"), ("No estoy seguro", "antecedentes_unsure")],
     "section": "Historial Legal"},
    {"id": "asylum", "text": "🛡️ *¿Has solicitado asilo en España?*", "type": "buttons",
     "options": [("No", "asylum_no"), ("Sí, pendiente (tarjeta roja)", "asylum_pending"),
                 ("Sí, denegado", "asylum_denied"), ("Sí, aprobado", "asylum_approved")],
     "section": "Historial Legal"},
    # SECTION 5: Documentation Status
    {"id": "passport_status", "text": "🛂 *¿Tu pasaporte está vigente?*", "type": "buttons",
     "options": [("Sí, vigente", "passport_valid"), ("Sí, pero caduca pronto", "passport_expiring"),
                 ("No, está caducado", "passport_expired"), ("Lo perdí", "passport_lost")],
     "section": "Documentación"},
    {"id": "antecedentes_foreign_status", "text": "📜 *¿Ya tienes tus antecedentes penales de tu país?*", "type": "buttons",
     "options": [("Sí, apostillados y traducidos", "antec_ready"), ("Sí, pero sin apostillar/traducir", "antec_partial"),
                 ("No, todavía no los pedí", "antec_none"), ("Es muy difícil conseguirlos", "antec_difficult")],
     "section": "Documentación"},
    {"id": "empadronamiento_status", "text": "📍 *¿Tienes empadronamiento?*", "type": "buttons",
     "options": [("Sí, actualizado", "empad_current"), ("Sí, pero antiguo", "empad_old"),
                 ("Nunca me empadroné", "empad_never"), ("Me quitaron del padrón", "empad_removed")],
     "section": "Documentación"},
]

# =============================================================================
# PHASE 3 QUESTIONNAIRE — Official form data collection
# =============================================================================

PHASE3_INTRO = (
    "📝 *Preparación de tu Expediente*\n\n"
    "Ahora necesitamos datos exactos para los formularios oficiales.\n"
    "Por favor, responde con cuidado — estos datos van en tu solicitud."
)

PHASE3_COMPLETION = (
    "✅ *Datos recibidos*\n\n"
    "Ahora nuestro equipo:\n"
    "1. Organizará tus documentos estratégicamente\n"
    "2. Completará todos los formularios oficiales\n"
    "3. Preparará la memoria de tu caso\n\n"
    "Te avisaremos cuando tu expediente esté listo para revisión final.\n\n"
    "⏱️ Tiempo estimado: 3-5 días laborables"
)

PHASE3_QUESTIONS = [
    # SECTION 1: Personal Data
    {"id": "p3_full_name", "text": "Nombre completo *exactamente* como aparece en tu pasaporte:", "type": "text",
     "required": True, "section": "👤 Datos Personales"},
    {"id": "p3_other_names", "text": "¿Has usado otros nombres o apellidos?", "type": "buttons",
     "options": [("No", "no"), ("Sí", "yes")], "section": "👤 Datos Personales"},
    {"id": "p3_other_names_detail", "text": "¿Cuáles?", "type": "text",
     "condition_field": "p3_other_names", "condition_values": ["yes"], "section": "👤 Datos Personales"},
    {"id": "p3_birth_date", "text": "Fecha de nacimiento (DD/MM/AAAA):", "type": "text",
     "required": True, "section": "👤 Datos Personales"},
    {"id": "p3_birth_place", "text": "Lugar de nacimiento (ciudad y país):", "type": "text",
     "required": True, "section": "👤 Datos Personales"},
    {"id": "p3_nationality", "text": "Nacionalidad:", "type": "text",
     "required": True, "section": "👤 Datos Personales"},
    {"id": "p3_passport_number", "text": "Número de pasaporte:", "type": "text",
     "required": True, "section": "👤 Datos Personales"},
    {"id": "p3_passport_expiry", "text": "Fecha de caducidad del pasaporte (DD/MM/AAAA):", "type": "text",
     "required": True, "section": "👤 Datos Personales"},

    # SECTION 2: Address & Contact
    {"id": "p3_street", "text": "Calle y número:", "type": "text",
     "required": True, "section": "📍 Dirección y Contacto"},
    {"id": "p3_floor_door", "text": "Piso y puerta (si aplica):", "type": "text",
     "section": "📍 Dirección y Contacto"},
    {"id": "p3_postal_code", "text": "Código postal:", "type": "text",
     "required": True, "section": "📍 Dirección y Contacto"},
    {"id": "p3_city", "text": "Municipio:", "type": "text",
     "required": True, "section": "📍 Dirección y Contacto"},
    {"id": "p3_province", "text": "Provincia:", "type": "text",
     "required": True, "section": "📍 Dirección y Contacto"},
    {"id": "p3_same_address_card", "text": "¿Quieres recibir tu tarjeta en esta dirección?", "type": "buttons",
     "options": [("Sí", "yes"), ("No, otra dirección", "no")], "section": "📍 Dirección y Contacto"},
    {"id": "p3_card_address", "text": "Dirección para recibir la tarjeta:", "type": "text",
     "condition_field": "p3_same_address_card", "condition_values": ["no"], "section": "📍 Dirección y Contacto"},
    {"id": "p3_phone", "text": "Teléfono móvil:", "type": "text",
     "required": True, "section": "📍 Dirección y Contacto"},
    {"id": "p3_email", "text": "Email:", "type": "text",
     "required": True, "section": "📍 Dirección y Contacto"},

    # SECTION 3: Employment
    {"id": "p3_currently_working", "text": "¿Trabajas actualmente con contrato?", "type": "buttons",
     "options": [("Sí", "yes"), ("No", "no")], "section": "💼 Datos Laborales"},
    {"id": "p3_employer_name", "text": "Nombre de la empresa:", "type": "text",
     "condition_field": "p3_currently_working", "condition_values": ["yes"], "section": "💼 Datos Laborales"},
    {"id": "p3_employer_cif", "text": "CIF de la empresa (si lo sabes):", "type": "text",
     "condition_field": "p3_currently_working", "condition_values": ["yes"], "section": "💼 Datos Laborales"},
    {"id": "p3_employer_address", "text": "Dirección de la empresa:", "type": "text",
     "condition_field": "p3_currently_working", "condition_values": ["yes"], "section": "💼 Datos Laborales"},
    {"id": "p3_employer_phone", "text": "Teléfono de la empresa:", "type": "text",
     "condition_field": "p3_currently_working", "condition_values": ["yes"], "section": "💼 Datos Laborales"},
    {"id": "p3_job_title", "text": "Tu puesto de trabajo:", "type": "text",
     "condition_field": "p3_currently_working", "condition_values": ["yes"], "section": "💼 Datos Laborales"},
    {"id": "p3_employer_aware", "text": "¿Tu empleador sabe que estás regularizándote?", "type": "buttons",
     "options": [("Sí, me apoya", "yes_support"), ("Sí, pero prefiere no involucrarse", "yes_neutral"), ("No sabe", "no")],
     "condition_field": "p3_currently_working", "condition_values": ["yes"], "section": "💼 Datos Laborales"},

    # SECTION 4: Family in application
    {"id": "p3_include_family", "text": "¿Vas a incluir familiares en tu solicitud?", "type": "buttons",
     "options": [("Sí, hijos menores", "children"), ("Sí, pareja", "partner"),
                 ("Sí, hijos y pareja", "both"), ("No, solo yo", "none")],
     "section": "👨‍👩‍👧 Familiares en la Solicitud"},
    {"id": "p3_family_details", "text": "Por cada familiar, indica:\n- Nombre completo\n- Fecha nacimiento\n- Parentesco\n- Nº pasaporte", "type": "text",
     "condition_field": "p3_include_family", "condition_values": ["children", "partner", "both"],
     "section": "👨‍👩‍👧 Familiares en la Solicitud"},
    {"id": "p3_coordinate_applications", "text": "¿Quieres que coordinemos las solicitudes para presentarlas juntas?", "type": "buttons",
     "options": [("Sí", "yes"), ("No", "no")],
     "condition_field": "p3_include_family", "condition_values": ["children", "partner", "both"],
     "section": "👨‍👩‍👧 Familiares en la Solicitud"},

    # SECTION 5: Submission preferences
    {"id": "p3_priority_submission", "text": "¿Quieres presentación prioritaria (primeros días de abril)?", "type": "buttons",
     "options": [("Sí, quiero ser de los primeros", "yes"), ("No me importa, cuando esté listo", "no")],
     "section": "📤 Preferencias de Presentación"},
    {"id": "p3_anything_else", "text": "¿Hay algo más que debamos saber sobre tu caso?", "type": "text",
     "section": "📤 Preferencias de Presentación"},
]

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
        "required": False,
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
            "por_que_mas_baratos", "por_que_no_hacerlo_solo", "por_que_tantas_preguntas",
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

# --- Pricing explanation (competitive messaging) — defined here so FAQ can reference it ---
PRICING_EXPLANATION = (
    "💰 *Nuestros Precios*\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📊 ¿POR QUÉ SOMOS MÁS BARATOS?\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Otros despachos cobran €389-450 por este proceso.\n"
    f"Nosotros cobramos *€{PRICING['total_phases']}* (o *€{PRICING['prepay_total']}* pagando de una vez).\n\n"
    "¿Cómo es posible?\n\n"
    "1️⃣ *Tecnología*\n"
    "Automatizamos la organización de documentos, verificación de datos, "
    "y seguimiento. Menos trabajo manual = menos coste.\n\n"
    "2️⃣ *Experiencia 2005*\n"
    "Ya hicimos esto hace 20 años. Sabemos exactamente qué funciona y qué no. "
    "Sin ensayo y error.\n\n"
    "3️⃣ *Volumen*\n"
    "Podemos atender más casos con el mismo equipo, gracias a la automatización.\n\n"
    "*El resultado:* Servicio premium a precio justo.\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "💳 OPCIONES DE PAGO\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "*Opción 1: Pago por fases*\n"
    f"• Fase 2 (evaluación): €{PRICING['phase2']}\n"
    f"• Fase 3 (expediente): €{PRICING['phase3']}\n"
    f"• Fase 4 (presentación): €{PRICING['phase4']}\n"
    f"• *Total: €{PRICING['total_phases']}*\n\n"
    "*Opción 2: Pago único* ⭐ RECOMENDADO\n"
    f"• Todo incluido: *€{PRICING['prepay_total']}*\n"
    f"• Ahorras €{PRICING['prepay_discount']} ({round(PRICING['prepay_discount']/PRICING['total_phases']*100)}%)\n\n"
    # NOTE: Servicios adicionales pricing hidden from user display (kept in PRICING dict)
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🏛️ TASAS DEL GOBIERNO (aparte)\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Estas tasas las cobra el gobierno, no nosotros:\n"
    "• Tasa 790-052: ~€16-20\n"
    "• Tasa TIE: ~€16-21\n"
    "• Total gobierno: ~€40-50\n\n"
    f"💡 ¿Quieres que las gestionemos? Por €{PRICING['govt_fees_service']} pagamos todo por ti."
)

# =============================================================================
# FAQ DATABASE — 44 entries, professional tone
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
        "text": PRICING_EXPLANATION,
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
            f"*Fase 2 (€{PRICING['phase2']}):* Revisión legal completa.\n"
            f"*Fase 3 (€{PRICING['phase3']}):* Preparación del expediente.\n"
            f"*Fase 4 (€{PRICING['phase4']}):* Presentación y seguimiento."
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

    # === NUESTRO SERVICIO ===
    "por_que_tantas_preguntas": {
        "title": "¿Por qué tantas preguntas?",
        "keywords": ["tantas preguntas", "muchas preguntas", "para qué preguntan", "por qué preguntan tanto"],
        "text": (
            "*¿Por qué tantas preguntas?*\n\n"
            "Cada pregunta tiene un propósito legal concreto:\n\n"
            "• Las de *Fase 2* nos permiten evaluar la solidez de tu caso "
            "y generar un informe de evaluación personalizado.\n"
            "• Las de *Fase 3* van directamente a los formularios oficiales "
            "que se presentan ante Extranjería.\n\n"
            "Un expediente incompleto o con errores se deniega. "
            "Nuestras preguntas evitan que eso pase."
        ),
    },
    "por_que_mas_baratos": {
        "title": "¿Por qué sois más baratos?",
        "keywords": ["más baratos", "tan baratos", "más barato", "precio bajo", "sois baratos"],
        "text": (
            "*¿Por qué nuestro precio es más bajo que la competencia?*\n\n"
            "La mayoría de despachos cobra €350-450 porque revisan cada caso "
            "manualmente, uno por uno. Nosotros usamos *tecnología*:\n\n"
            "• Bot de intake 24/7 (lo estás usando ahora)\n"
            "• Validación automática de documentos por IA\n"
            "• Generación asistida de expedientes\n\n"
            "Esto nos permite atender más casos con menos horas-hombre, "
            "y trasladamos ese ahorro al precio.\n\n"
            "La calidad legal es la misma — cada expediente lo revisa un abogado "
            "colegiado antes de presentarse."
        ),
    },
    "por_que_no_hacerlo_solo": {
        "title": "¿Por qué pagar si puedo hacerlo yo?",
        "keywords": ["hacerlo yo", "hacerlo solo", "por mi cuenta", "no necesito", "gratis el trámite"],
        "text": (
            "*¿Por qué pagar si el trámite es \"gratuito\"?*\n\n"
            "Técnicamente puedes presentar tú solo. Pero considera esto:\n\n"
            "• En 2005, el *10-20%* de solicitudes fueron denegadas, "
            "la mayoría por errores evitables.\n"
            "• Un solo día sin prueba de permanencia puede hacer que te denieguen.\n"
            "• Los formularios oficiales tienen campos técnicos que confunden.\n"
            "• Si te deniegan, no puedes volver a presentar — se acabó.\n\n"
            f"Nuestro servicio cuesta *€{PRICING['prepay_total']}*. "
            "Una denegación te cuesta *tu oportunidad de regularizarte*.\n\n"
            "Fase 1 es gratis — prueba sin compromiso."
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
            "en Fase 3 (expediente).\n\n"
            "*Para ti:*\n"
            "Cuando tu amigo pague Fase 3, ganas €25 de crédito "
            "que se aplica a tus siguientes pagos.\n\n"
            f"Máximo: €{PRICING['referral_max']} en créditos (10 amigos = servicio gratis).\n\n"
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
            phase2_answers TEXT,
            phase3_answers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Migration: add phase2_answers if missing
        try:
            c.execute("SAVEPOINT sp_phase2_answers")
            c.execute("ALTER TABLE users ADD COLUMN phase2_answers TEXT")
            c.execute("RELEASE SAVEPOINT sp_phase2_answers")
        except Exception:
            c.execute("ROLLBACK TO SAVEPOINT sp_phase2_answers")

        # Migration: add phase3_answers if missing
        try:
            c.execute("SAVEPOINT sp_phase3_answers")
            c.execute("ALTER TABLE users ADD COLUMN phase3_answers TEXT")
            c.execute("RELEASE SAVEPOINT sp_phase3_answers")
        except Exception:
            c.execute("ROLLBACK TO SAVEPOINT sp_phase3_answers")

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
            phase2_answers TEXT,
            phase3_answers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Migration: add phase2_answers if missing
        try:
            c.execute("ALTER TABLE users ADD COLUMN phase2_answers TEXT")
        except Exception:
            pass

        # Migration: add phase3_answers if missing
        try:
            c.execute("ALTER TABLE users ADD COLUMN phase3_answers TEXT")
        except Exception:
            pass

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

    # Create waitlist table
    if USE_POSTGRES:
        c.execute("""CREATE TABLE IF NOT EXISTS waitlist (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            name VARCHAR(100),
            country VARCHAR(50),
            docs_uploaded INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notified BOOLEAN DEFAULT FALSE,
            converted BOOLEAN DEFAULT FALSE
        )""")
    else:
        c.execute("""CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            name VARCHAR(100),
            country VARCHAR(50),
            docs_uploaded INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notified INTEGER DEFAULT 0,
            converted INTEGER DEFAULT 0
        )""")
    conn.commit()

    try:
        c.execute("CREATE INDEX IF NOT EXISTS idx_waitlist_telegram ON waitlist(telegram_id)")
        conn.commit()
    except Exception:
        conn.rollback()

    conn.commit()
    conn.close()


# =============================================================================
# CAPACITY & WAITLIST FUNCTIONS
# =============================================================================

def get_current_clients() -> int:
    """Count users who have paid Phase 2 or higher."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE phase2_paid = 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def get_available_slots() -> int:
    return max(0, TOTAL_CAPACITY - get_current_clients())


def is_capacity_full() -> bool:
    return get_available_slots() <= 0


def get_capacity_message() -> str:
    available = get_available_slots()
    if available > 0:
        return f"📊 Plazas disponibles: *{available} de {TOTAL_CAPACITY}*"
    else:
        return f"📊 *{TOTAL_CAPACITY} plazas ocupadas* — Lista de espera activa"


def add_to_waitlist(telegram_id: int, name: str, country: str, docs_uploaded: int) -> None:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    try:
        if USE_POSTGRES:
            c.execute(f"""INSERT INTO waitlist (telegram_id, name, country, docs_uploaded)
                VALUES ({p}, {p}, {p}, {p})
                ON CONFLICT (telegram_id) DO UPDATE SET docs_uploaded = {p}""",
                (telegram_id, name, country, docs_uploaded, docs_uploaded))
        else:
            c.execute(f"""INSERT OR REPLACE INTO waitlist (telegram_id, name, country, docs_uploaded)
                VALUES ({p}, {p}, {p}, {p})""",
                (telegram_id, name, country, docs_uploaded))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding to waitlist: {e}")
    finally:
        conn.close()


def get_waitlist_position(telegram_id: int) -> int:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT COUNT(*) FROM waitlist WHERE joined_at <= (SELECT joined_at FROM waitlist WHERE telegram_id = {p})", (telegram_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def get_waitlist_stats() -> dict:
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) FROM waitlist")
    stats['total'] = c.fetchone()[0]
    if USE_POSTGRES:
        c.execute("SELECT COUNT(*) FROM waitlist WHERE notified = TRUE")
    else:
        c.execute("SELECT COUNT(*) FROM waitlist WHERE notified = 1")
    stats['notified'] = c.fetchone()[0]
    if USE_POSTGRES:
        c.execute("SELECT COUNT(*) FROM waitlist WHERE converted = TRUE")
    else:
        c.execute("SELECT COUNT(*) FROM waitlist WHERE converted = 1")
    stats['converted'] = c.fetchone()[0]
    c.execute("SELECT country, COUNT(*) FROM waitlist GROUP BY country ORDER BY COUNT(*) DESC")
    stats['by_country'] = {row[0] or 'Unknown': row[1] for row in c.fetchall()}
    conn.close()
    return stats


def get_waitlist_users(limit: int = 10, notified: bool = False) -> list:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    if USE_POSTGRES:
        val = notified
    else:
        val = 1 if notified else 0
    c.execute(f"SELECT telegram_id, name FROM waitlist WHERE notified = {p} ORDER BY joined_at ASC LIMIT {limit}", (val,))
    rows = c.fetchall()
    conn.close()
    return [{'telegram_id': r[0], 'name': r[1]} for r in rows]


def mark_waitlist_notified(telegram_id: int) -> None:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    if USE_POSTGRES:
        c.execute(f"UPDATE waitlist SET notified = TRUE WHERE telegram_id = {p}", (telegram_id,))
    else:
        c.execute(f"UPDATE waitlist SET notified = 1 WHERE telegram_id = {p}", (telegram_id,))
    conn.commit()
    conn.close()


def is_on_waitlist(telegram_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    p = db_param()
    c.execute(f"SELECT 1 FROM waitlist WHERE telegram_id = {p}", (telegram_id,))
    row = c.fetchone()
    conn.close()
    return row is not None


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


def get_waitlist_count() -> int:
    """Deterministic fake waitlist counter. Grows 50-200/day + 2-8/hour from base 3127."""
    import hashlib
    from datetime import datetime, date, timedelta

    LAUNCH_DATE = date(2026, 2, 15)
    BASE_COUNT = 3127

    now = datetime.now()
    today = now.date()
    days = (today - LAUNCH_DATE).days

    if days < 0:
        return BASE_COUNT

    total = BASE_COUNT

    for day in range(days):
        seed = f"waitlist-{LAUNCH_DATE + timedelta(days=day)}"
        day_hash = int(hashlib.md5(seed.encode()).hexdigest(), 16)
        total += 50 + (day_hash % 151)

    current_hour = now.hour
    for hour in range(current_hour + 1):
        seed = f"waitlist-{today}-{hour}"
        hour_hash = int(hashlib.md5(seed.encode()).hexdigest(), 16)
        total += 2 + (hour_hash % 7)

    return total


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
        [InlineKeyboardButton("WhatsApp", url=wa_url),
         InlineKeyboardButton("Telegram", url=tg_url)],
        [InlineKeyboardButton("Facebook", url=fb_url),
         InlineKeyboardButton("Copiar", callback_data=f"copy_ref_{code}")],
        [InlineKeyboardButton("Volver", callback_data="back")],
    ])


def get_share_buttons(code: str) -> list:
    """Generate social media share button rows (without back button)."""
    wa_url = get_whatsapp_share_url(code)
    tg_url = get_telegram_share_url(code)
    fb_url = get_facebook_share_url(code)
    return [
        [InlineKeyboardButton("WhatsApp", url=wa_url),
         InlineKeyboardButton("Telegram", url=tg_url)],
        [InlineKeyboardButton("Facebook", url=fb_url),
         InlineKeyboardButton("Copiar", callback_data=f"copy_ref_{code}")],
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
        "¿CÓMO FUNCIONA?\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ *COMPARTE* tu código con amigos que necesiten regularizarse\n\n"
        "2️⃣ *ELLOS RECIBEN* €25 de descuento\n\n"
        "3️⃣ *TÚ GANAS* €25 de crédito cuando completen el proceso"
    )

    activation_block = (
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Comparte ahora. Los créditos se acumulan para cuando abra el proceso."
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
        "📌 OBLIGATORIOS\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ *Pasaporte vigente*\n"
        "   Todas las páginas, incluyendo vacías.\n\n"
        "2️⃣ *Antecedentes penales - España*\n"
        "   Del Ministerio de Justicia.\n\n"
        f"3️⃣ *Antecedentes penales - {name}*\n"
        "   Apostillado y traducido si necesario.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📍 PRUEBA DE PRESENCIA EN ESPAÑA\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Debes demostrar que estabas aquí antes del *{CUTOFF_DATE}*.\n\n"
        "*NO necesitas empadronamiento.* Sirve CUALQUIER documento:\n"
        "facturas, médico, banco, transporte, trabajo, móvil...\n\n"
        "👉 Usa el botón de abajo para ver la lista de 40+ documentos válidos.\n\n"
        "💡 _Cuantos más documentos de prueba, mejor._\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📎 RECOMENDADOS (refuerzan tu caso)\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "• Contrato de trabajo actual\n"
        "• Nóminas recientes\n"
        "• Certificados de estudios\n"
        "• Cartas de apoyo"
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
        buttons.append([InlineKeyboardButton(d['name'], callback_data=f"dt_{code}")])
    buttons.append([InlineKeyboardButton("Volver al menu", callback_data="back")])
    return InlineKeyboardMarkup(buttons)


def main_menu_kb(user: Dict) -> InlineKeyboardMarkup:
    dc = get_doc_count(user["telegram_id"])
    btns = [
        [InlineKeyboardButton("Continuar con mi proceso", callback_data="continue_process")],
        [InlineKeyboardButton("Mi checklist de documentos", callback_data="m_checklist")],
        [InlineKeyboardButton(f"Mis documentos ({dc})", callback_data="m_docs")],
        [InlineKeyboardButton("Subir documento", callback_data="m_upload")],
        [InlineKeyboardButton("Ver lista de espera", callback_data="waitlist")],
        [InlineKeyboardButton("Invitar amigos", callback_data="m_referidos")],
        [InlineKeyboardButton("Preguntas frecuentes", callback_data="m_faq")],
        [InlineKeyboardButton("Consultar con abogado", callback_data="m_contact")],
    ]
    return InlineKeyboardMarkup(btns)


def faq_menu_kb() -> InlineKeyboardMarkup:
    """Show FAQ category buttons (accordion top level)."""
    btns = []
    btns.append([InlineKeyboardButton("¿Que incluye cada fase?", callback_data="fq_fases")])
    for cat_key, cat in FAQ_CATEGORIES.items():
        btns.append([InlineKeyboardButton(cat["title"], callback_data=f"fcat_{cat_key}")])
    btns.append([InlineKeyboardButton("Volver al menu", callback_data="back")])
    return InlineKeyboardMarkup(btns)


def faq_category_kb(cat_key: str) -> InlineKeyboardMarkup:
    """Show question buttons within a FAQ category."""
    cat = FAQ_CATEGORIES.get(cat_key, {})
    btns = []
    for faq_key in cat.get("keys", []):
        faq = FAQ.get(faq_key)
        if faq:
            btns.append([InlineKeyboardButton(faq["title"], callback_data=f"fq_{faq_key}")])
    btns.append([InlineKeyboardButton("Todas las categorias", callback_data="m_faq")])
    btns.append([InlineKeyboardButton("Menu principal", callback_data="back")])
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
        btns.append([InlineKeyboardButton("Pagar con tarjeta", url=stripe_link)])
    btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
    btns.append([InlineKeyboardButton("Ya he realizado el pago", callback_data=paid_callback)])
    btns.append([InlineKeyboardButton("Tengo dudas", callback_data="m_contact")])
    btns.append([InlineKeyboardButton("Volver", callback_data="back")])
    return InlineKeyboardMarkup(btns)


def docs_ready_payment_kb(has_referral_discount: bool = False) -> InlineKeyboardMarkup:
    """Payment options shown AFTER documents are uploaded (not at eligibility)."""
    prepay_price = PRICING["prepay_total"] - PRICING["referral_discount"] if has_referral_discount else PRICING["prepay_total"]
    phase2_price = PRICING["phase2"] - PRICING["referral_discount"] if has_referral_discount else PRICING["phase2"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"Pagar TODO — €{prepay_price} (ahorra €{PRICING['prepay_discount']})",
            callback_data="pay_full")],
        [InlineKeyboardButton(
            f"Evaluacion personalizada — €{phase2_price}",
            callback_data="m_pay2")],
        [InlineKeyboardButton(
            "Subir mas documentos",
            callback_data="m_upload")],
        [InlineKeyboardButton("¿Por que estos precios?", callback_data="faq_pricing")],
        [InlineKeyboardButton("Menu", callback_data="back")],
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
    f"Por *€{PRICING['antecedentes_foreign']}* nos encargamos de todo:\n\n"
    "✅ Investigamos el proceso de tu país\n"
    "✅ Solicitamos el certificado\n"
    "✅ Gestionamos apostilla/legalización\n"
    "✅ Traducción jurada si necesario\n"
    "✅ Te lo entregamos listo\n\n"
    "⏱️ Tiempo: 2-4 semanas (varía por país)\n\n"
    "⚠️ _Nota: Algunos países tienen procesos muy complejos o lentos. "
    "Te informaremos antes de empezar si tu país presenta dificultades especiales._"
)

# --- Spain antecedentes upsell ---
UPSELL_ANTECEDENTES_SPAIN = (
    "📜 *Antecedentes Penales de España*\n\n"
    "Este documento es *obligatorio* para tu solicitud.\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "EL PROBLEMA\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Para conseguirlo tú mismo necesitas:\n"
    "• Cl@ve o certificado digital (difícil sin NIE)\n"
    "• O ir en persona con cita previa\n"
    "• O enviarlo por correo y esperar\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    f"NUESTRA SOLUCIÓN — €{PRICING['antecedentes_spain']}\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Lo tramitamos por ti:\n"
    "✅ Solicitud en tu nombre (con autorización)\n"
    "✅ Pago de la tasa (€3.86 incluido)\n"
    "✅ Descarga y verificación\n"
    "✅ Te lo enviamos en 24-48h\n\n"
    "Sin Cl@ve. Sin colas. Sin complicaciones."
)

ANTECEDENTES_SPAIN_DIY = (
    "👍 Perfecto, aquí tienes las instrucciones:\n\n"
    "*Online (si tienes Cl@ve):*\n"
    "1. Ve a sede.mjusticia.gob.es\n"
    "2. Busca \"Certificado Antecedentes Penales\"\n"
    "3. Identifícate con Cl@ve\n"
    "4. Paga €3.86 (tasa 006)\n"
    "5. Descarga el certificado\n\n"
    "*En persona:*\n"
    "1. Pide cita en tu Gerencia Territorial\n"
    "2. Lleva pasaporte + formulario 790\n"
    "3. Paga €3.86 en banco\n"
    "4. Recógelo en el momento\n\n"
    "*Por correo:*\n"
    "1. Descarga modelo 790 de mjusticia.gob.es\n"
    "2. Paga €3.86 en banco\n"
    "3. Envía a: Ministerio de Justicia, Calle Bolsa 8, 28012 Madrid\n"
    "4. Espera 10 días hábiles\n\n"
    f"💡 Si cambias de opinión, el servicio de €{PRICING['antecedentes_spain']} sigue disponible."
)

# --- Translation upsell ---
UPSELL_TRANSLATION = (
    "🔤 *Este documento necesita traducción jurada*\n\n"
    "Para el expediente de regularización, los documentos "
    "deben estar en español o tener traducción jurada.\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    f"SERVICIO DE TRADUCCIÓN — €{PRICING['translation_per_doc']}\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Por cada documento:\n"
    "✅ Traducción jurada oficial\n"
    "✅ Traductor certificado\n"
    "✅ Válida para extranjería\n"
    "✅ Entrega en 48-72 horas\n\n"
    "¿Quieres que traduzcamos este documento?"
)

# --- Priority processing upsell ---
UPSELL_PRIORITY = (
    "⚡ *Procesamiento Prioritario — €{price}*\n\n"
    "¿Quieres ser de los primeros en presentar?\n\n"
    "El plazo de solicitudes es abril-junio 2026.\n"
    "Los primeros en presentar, primeros en recibir respuesta.\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "QUÉ INCLUYE\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "✅ Tu expediente se prepara primero\n"
    "✅ Presentación en los primeros días de abril\n"
    "✅ Seguimiento reforzado\n"
    "✅ Respuesta a requerimientos en 24h\n\n"
    "💡 Ideal si tu situación es urgente o quieres tranquilidad."
).format(price=PRICING['urgent_processing'])

# --- Phase 2 pitch (shown after 3+ docs uploaded) ---
PHASE2_PITCH = (
    "📊 *Has subido {{doc_count}} documentos. Buen trabajo.*\n\n"
    "Ahora viene la parte importante: *entender TU caso*.\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    f"EVALUACIÓN PERSONALIZADA — €{PRICING['phase2']}\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "No vamos a darte un checklist genérico.\n"
    "Vamos a:\n\n"
    "✅ *Revisar cada documento* que subiste\n"
    "✅ *Hacerte preguntas específicas* sobre tu situación\n"
    "✅ *Identificar fortalezas y debilidades* de TU caso\n"
    "✅ *Crear una estrategia personalizada* solo para ti\n"
    "✅ *Detectar qué documentos te faltan*\n\n"
    "Esto no es un \"estudio de viabilidad\" de 5 minutos.\n"
    "Es tu *diagnóstico legal completo*.\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    f"💡 *¿Por qué €{PRICING['phase2']}?*\n"
    f"Otros cobran €{PRICING['phase2']} por un formulario genérico.\n"
    "Nosotros te damos una evaluación real porque ya tenemos tus documentos.\n\n"
    "⭐ *¿Prefieres pagar todo de una vez?*\n"
    f"Por €{PRICING['prepay_total']} tienes TODO el servicio hasta la resolución.\n"
    f"Ahorras €{PRICING['prepay_discount']} y te olvidas de pagos."
)

# --- Bundle offers ---
PHASE4_BUNDLE_OFFER = (
    "📦 *Oferta Fase Final*\n\n"
    "Estás a punto de completar tu proceso.\n"
    "Te ofrecemos un paquete con todo incluido:\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "PAQUETE COMPLETO\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    f"• Fase 4 (presentación + seguimiento): €{PRICING['phase4']}\n"
    f"• Gestión de tasas gubernamentales: €{PRICING['govt_fees_service']}\n"
    "• Total tasas gobierno (~€45): incluido *\n\n"
    f"*Precio del paquete: €{PRICING['phase4_bundle']}* (en vez de €{PRICING['phase4'] + PRICING['govt_fees_service']}+tasas)\n"
    "Ahorras y no te preocupas de nada.\n\n"
    "\\* Nos encargaremos de todo: pago de tasas, "
    "presentación, seguimiento, requerimientos."
)

VIP_BUNDLE_OFFER = (
    "⭐ *Servicio Completo Todo Incluido*\n\n"
    "¿Prefieres no preocuparte de nada?\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    f"PAQUETE VIP — €{PRICING['vip_bundle']}\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Todo incluido:\n"
    "Evaluación personalizada (Fase 2)\n"
    "Expediente a medida (Fase 3)\n"
    "Presentación y seguimiento (Fase 4)\n"
    "Antecedentes España tramitados\n"
    "Gestión de tasas gubernamentales\n\n"
    f"*Precio normal:* €{PRICING['phase2']} + €{PRICING['phase3']} + €{PRICING['phase4']} + "
    f"€{PRICING['antecedentes_spain']} + €{PRICING['govt_fees_service']} = "
    f"€{PRICING['phase2'] + PRICING['phase3'] + PRICING['phase4'] + PRICING['antecedentes_spain'] + PRICING['govt_fees_service']}\n"
    f"*Precio paquete:* €{PRICING['vip_bundle']}\n\n"
    f"Ahorras €{PRICING['phase2'] + PRICING['phase3'] + PRICING['phase4'] + PRICING['antecedentes_spain'] + PRICING['govt_fees_service'] - PRICING['vip_bundle']} y tienes TODO resuelto."
)


FAQ_PROOF_DOCUMENTS_FULL = (
    "📄 *Documentos que sirven como prueba de presencia*\n\n"
    "El decreto acepta CUALQUIER documento público o privado.\n"
    "*NO necesitas empadronamiento obligatoriamente.*\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🏠 VIVIENDA\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "• Empadronamiento (NO obligatorio)\n"
    "• Contrato de alquiler\n"
    "• Recibos de alquiler\n"
    "• Facturas de luz (Endesa, Iberdrola, Naturgy)\n"
    "• Facturas de agua\n"
    "• Facturas de gas\n"
    "• Facturas de internet/fibra\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🏥 MÉDICOS\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "• Tarjeta sanitaria (SIP, TSI)\n"
    "• Citas médicas\n"
    "• Recetas de farmacia\n"
    "• Informes médicos\n"
    "• Urgencias\n"
    "• Vacunaciones (COVID, gripe, etc.)\n"
    "• Visitas al dentista\n"
    "• Pruebas médicas\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🏦 BANCARIOS Y ENVÍOS DE DINERO\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "• Extractos bancarios\n"
    "• Tarjetas fintech: Revolut, N26, Wise, Bnext\n"
    "• Recibos de Western Union\n"
    "• Recibos de Ria Money Transfer\n"
    "• Recibos de MoneyGram\n"
    "• Recibos de Small World\n"
    "• Movimientos de Bizum\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🚌 TRANSPORTE\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "• Abono transporte (con recargas)\n"
    "• Billetes de Renfe / Cercanías\n"
    "• Billetes de autobús\n"
    "• Recibos de Cabify, Uber, Bolt\n"
    "• BiciMad, Bicing\n"
    "• Recibos de parking\n"
    "• Multas de tráfico (sí, también sirven)\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📚 EDUCACIÓN Y FAMILIA\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "• Matrícula escolar (tuya o de tus hijos)\n"
    "• Boletines de notas\n"
    "• Cursos de español\n"
    "• Cursos de formación profesional\n"
    "• Guardería\n"
    "• Actividades extraescolares\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "💼 TRABAJO\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "• Nóminas\n"
    "• Contratos de trabajo\n"
    "• Vida laboral\n"
    "• Registros de Glovo, Uber Eats, Deliveroo\n"
    "• Facturas como autónomo\n"
    "• Carta de empleador\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📱 VIDA DIARIA\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "• Facturas de móvil (Movistar, Vodafone, Orange, Digi)\n"
    "• Recargas de móvil prepago\n"
    "• Abono de gimnasio\n"
    "• Carnet de biblioteca\n"
    "• Paquetes o correo a tu nombre\n"
    "• Compras online con dirección española\n"
    "• Entradas a cine, conciertos, eventos\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "⛪ COMUNIDAD Y MASCOTAS\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "• Participación en iglesia/parroquia/mezquita\n"
    "• Voluntariado en ONGs\n"
    "• Cartas de Cruz Roja, Cáritas\n"
    "• Visitas al veterinario\n"
    "• Cartilla de vacunación de mascota\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "💡 CONSEJOS IMPORTANTES\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "✅ Combina 3-5 documentos de DIFERENTES categorías\n"
    f"✅ Documentos con fechas antes del {CUTOFF_DATE}\n"
    "✅ Mejor si cubren varios meses (demuestra continuidad)\n"
    "✅ Más documentos = más fuerte tu caso\n\n"
    "❌ NO necesitas empadronamiento obligatoriamente\n"
    "❌ NO necesitas contrato de trabajo\n"
    "❌ NO necesitas TODOS estos documentos"
)


def antecedentes_service_kb() -> InlineKeyboardMarkup:
    """Buttons for foreign antecedentes service offer."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Si, quiero ayuda — €{PRICING['antecedentes_foreign']}", callback_data="buy_antecedentes")],
        [InlineKeyboardButton("Lo hago yo mismo", callback_data="back")],
    ])


def antecedentes_help_kb() -> InlineKeyboardMarkup:
    """Buttons for antecedentes help — request support flow."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Antecedentes pais de origen — €{PRICING['antecedentes_foreign']}", callback_data="request_antecedentes_help")],
        [InlineKeyboardButton(f"Antecedentes España — €{PRICING['antecedentes_spain']}", callback_data="upsell_antec_spain")],
        [InlineKeyboardButton("Lo gestiono yo mismo", callback_data="m_checklist")],
        [InlineKeyboardButton("Menu", callback_data="back")],
    ])


def antecedentes_spain_kb() -> InlineKeyboardMarkup:
    """Buttons for Spain antecedentes upsell."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Si, tramitadlo — €{PRICING['antecedentes_spain']}", callback_data="buy_antec_spain")],
        [InlineKeyboardButton("Lo hago yo mismo", callback_data="diy_antec_spain")],
        [InlineKeyboardButton("Volver", callback_data="antecedentes_help")],
    ])


def govt_fees_service_kb() -> InlineKeyboardMarkup:
    """Buttons for government fees service offer."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Si, gestionadlo — €{PRICING['govt_fees_service']}", callback_data="buy_govt_fees")],
        [InlineKeyboardButton("Las pago yo mismo", callback_data="back")],
        [InlineKeyboardButton("¿Como se pagan?", callback_data="explain_govt_fees")],
    ])


def translation_service_kb() -> InlineKeyboardMarkup:
    """Buttons for translation service upsell."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Traducir documento — €{PRICING['translation_per_doc']}", callback_data="buy_translation")],
        [InlineKeyboardButton("Ya tengo traductor", callback_data="back")],
    ])


def phase4_bundle_kb() -> InlineKeyboardMarkup:
    """Buttons for Phase 4 bundle offer."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Paquete completo — €{PRICING['phase4_bundle']}", callback_data="buy_phase4_bundle")],
        [InlineKeyboardButton(f"Solo Fase 4 — €{PRICING['phase4']}", callback_data="m_pay4")],
    ])


def vip_bundle_kb(has_referral: bool = False) -> InlineKeyboardMarkup:
    """Buttons for VIP bundle offer."""
    price = PRICING['vip_bundle'] - PRICING['referral_discount'] if has_referral else PRICING['vip_bundle']
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Paquete VIP — €{price}", callback_data="buy_vip_bundle")],
        [InlineKeyboardButton(f"Solo evaluacion — €{PRICING['phase2']}", callback_data="m_pay2")],
        [InlineKeyboardButton("¿Que incluye?", callback_data="faq_pricing")],
    ])


def get_antecedentes_upsell_message(country_code: str) -> str:
    """Get country-specific antecedentes upsell message."""
    country = COUNTRIES.get(country_code, COUNTRIES["other"])
    info = COUNTRIES_ANTECEDENTES_INFO.get(country_code, {})
    difficulty_emoji = {"baja": "🟢", "media": "🟡", "alta": "🔴"}.get(info.get("difficulty", "media"), "🟡")

    if not info:
        return ANTECEDENTES_HELP_TEXT

    return (
        f"🌍 *Antecedentes Penales de {country['name']}* {country['flag']}\n\n"
        "Este documento es *obligatorio* para tu solicitud.\n"
        "Debe estar apostillado/legalizado y traducido.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"INFORMACIÓN DE {country['name'].upper()}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{difficulty_emoji} Dificultad: {info.get('difficulty', 'variable').capitalize()}\n"
        f"⏱️ Tiempo estimado: {info.get('time', '2-6 semanas')}\n"
        f"📋 Proceso: {info.get('process', 'Variable')}\n\n"
        f"💡 {info.get('notes', '')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "¿QUIERES QUE NOS ENCARGUEMOS?\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Por *€{PRICING['antecedentes_foreign']}* gestionamos TODO:\n"
        "✅ Solicitamos el certificado\n"
        "✅ Gestionamos apostilla/legalización\n"
        "✅ Traducción jurada incluida\n"
        "✅ Te lo entregamos listo para presentar\n\n"
        "⚠️ *Importante:* Muchos candidatos pierden el plazo por empezar tarde con este trámite."
    )


# --- Phase 2 Questionnaire helpers ---

def get_next_question_index(answers: Dict, current_idx: int) -> int:
    """Get the next question index, skipping conditional questions whose conditions aren't met."""
    for i in range(current_idx + 1, len(PHASE2_QUESTIONS)):
        q = PHASE2_QUESTIONS[i]
        cond_field = q.get("condition_field")
        if cond_field:
            cond_values = q.get("condition_values", [])
            if answers.get(cond_field) not in cond_values:
                continue
        return i
    return -1  # No more questions


def build_question_keyboard(question: Dict) -> InlineKeyboardMarkup:
    """Build keyboard for a Phase 2 question."""
    if question["type"] == "buttons":
        btns = []
        for label, value in question.get("options", []):
            btns.append([InlineKeyboardButton(label, callback_data=f"p2q_{question['id']}_{value}")])
        btns.append([InlineKeyboardButton("Saltar", callback_data=f"p2q_{question['id']}_skip")])
        return InlineKeyboardMarkup(btns)
    return None


def generate_phase2_report(user: Dict, answers: Dict) -> str:
    """Generate personalized strategy report based on questionnaire + documents."""
    country = COUNTRIES.get(user.get("country_code", "other"), COUNTRIES["other"])

    strengths = []
    weaknesses = []
    recommendations = []

    # Passport analysis
    ps = answers.get("passport_status", "")
    if ps == "passport_valid":
        strengths.append("✅ Pasaporte vigente")
    elif ps == "passport_expiring":
        weaknesses.append("⚠️ Pasaporte caduca pronto")
        recommendations.append("Renueva tu pasaporte en el consulado ANTES de abril")
    elif ps in ("passport_expired", "passport_lost"):
        weaknesses.append("🔴 Pasaporte no vigente — urgente renovar")
        recommendations.append("Contacta tu consulado INMEDIATAMENTE para renovar pasaporte")

    # Housing
    housing = answers.get("housing", "")
    if housing == "housing_own":
        strengths.append("✅ Vivienda a tu nombre — excelente prueba")
    elif housing in ("housing_other", "housing_room"):
        recommendations.append("Intenta conseguir un contrato de subarrendamiento o declaración del titular")

    # Employment
    emp = answers.get("employment", "")
    if emp == "work_contract":
        strengths.append("✅ Empleo con contrato — fortalece mucho tu caso")
    elif emp in ("work_informal", "work_apps"):
        strengths.append("✅ Actividad laboral (documentar recibos y registros)")

    # Bank account
    bank = answers.get("bank_account", "")
    if bank in ("bank_traditional", "bank_both"):
        strengths.append("✅ Cuenta bancaria en España")
    elif bank == "bank_fintech":
        strengths.append("✅ Cuenta fintech — extractos son válidos como prueba")

    # Children
    if answers.get("children") == "children_yes":
        strengths.append("✅ Hijos menores en España — fortalece significativamente")
        recommendations.append("Incluir documentación escolar/sanitaria de los hijos")

    # Partner
    partner = answers.get("partner", "")
    if partner == "partner_legal":
        strengths.append("✅ Pareja con residencia legal — vínculo fuerte")
    elif partner == "partner_irregular":
        recommendations.append("Tu pareja también podría acogerse a esta regularización")

    # Family ties
    if answers.get("other_family") == "family_yes":
        strengths.append("✅ Familiares con papeles en España — vínculo importante")

    # Empadronamiento
    empad = answers.get("empadronamiento_status", "")
    if empad in ("empad_current", "empad_old"):
        strengths.append("✅ Tiene empadronamiento")
    elif empad in ("empad_never", "empad_removed"):
        recommendations.append("No te preocupes por el empadronamiento — tienes otras pruebas válidas")

    # Foreign antecedentes
    antec = answers.get("antecedentes_foreign_status", "")
    if antec == "antec_ready":
        strengths.append("✅ Antecedentes penales del país listos")
    elif antec == "antec_partial":
        recommendations.append("Necesitas apostillar/traducir tus antecedentes — hazlo YA")
    elif antec in ("antec_none", "antec_difficult"):
        weaknesses.append("⚠️ Faltan antecedentes penales del país de origen")
        recommendations.append("Solicita antecedentes de tu país lo antes posible")

    # Police record
    police = answers.get("police_spain", "")
    if police == "police_never":
        strengths.append("✅ Sin problemas policiales en España")
    elif police == "police_minor":
        recommendations.append("Tu abogado revisará el detalle — probablemente no sea problema")
    elif police == "police_serious":
        weaknesses.append("⚠️ Antecedentes policiales serios — requiere análisis legal detallado")

    # Asylum
    asylum = answers.get("asylum", "")
    if asylum == "asylum_pending":
        recommendations.append("Puedes aplicar con solicitud de asilo pendiente — compatibles")

    # Travel outside Spain
    left = answers.get("left_spain", "")
    if left == "left_never":
        strengths.append("✅ No ha salido de España — continuidad perfecta")
    elif left in ("left_once", "left_multiple"):
        recommendations.append("Documentar bien las fechas de salida y entrada — viajes cortos no rompen continuidad")

    # Risk assessment
    if len(weaknesses) == 0:
        risk = "ALTA"
        risk_msg = "Tu caso tiene buenas perspectivas"
    elif len(weaknesses) <= 2:
        risk = "MEDIA-ALTA"
        risk_msg = "Tu caso es viable con algunos ajustes"
    else:
        risk = "MEDIA"
        risk_msg = "Tu caso requiere atención especial en algunos puntos"

    name = user.get("full_name") or user.get("first_name", "Usuario")
    doc_count = get_doc_count(user["telegram_id"])

    report = (
        "*INFORME DE EVALUACIÓN PERSONALIZADA*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 *{name}*\n"
        f"🌍 {country['flag']} {country['name']}\n"
        f"📄 {doc_count} documentos subidos\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 EVALUACIÓN DE TU CASO\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Probabilidad de aprobación: {risk}*\n"
        f"_{risk_msg}_\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ FORTALEZAS DE TU CASO\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    report += "\n".join(strengths) if strengths else "Analizando..."
    report += (
        "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ PUNTOS DE ATENCIÓN\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    report += "\n".join(weaknesses) if weaknesses else "Ninguno crítico detectado"
    report += (
        "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 RECOMENDACIONES\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    report += "\n".join(f"• {r}" for r in recommendations) if recommendations else "• Tu caso está bien encaminado"
    report += (
        "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*¿Siguiente paso?*\n"
        "Con esta información, podemos preparar tu expediente personalizado.\n"
        f"Fase 3 (expediente a medida): €{PRICING['phase3']}"
    )

    return report


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
                f"🎉 ¡Código aplicado! Tienes *€{PRICING['referral_discount']} de descuento* en tu primer pago.\n\n"
                "🇪🇸 *¡Bienvenido/a a tuspapeles2026!*\n\n"
                "Esta plataforma ha sido desarrollada por los abogados de "
                "*Pombo, Horowitz & Espinosa* para ayudarte con la "
                "regularización extraordinaria de 2026.\n\n"
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
        "*Pombo, Horowitz & Espinosa* para ayudarte con el proceso de regularización.\n\n"
        "✅ Comprobación de elegibilidad\n"
        "✅ Revisión de documentos\n"
        "✅ Evaluación personalizada de tu caso\n"
        "✅ Preparación del expediente completo\n"
        "✅ Redacción de memoria legal\n"
        "✅ Presentación telemática\n"
        "✅ Seguimiento hasta resolución\n"
        "✅ Recurso incluido si fuera necesario\n"
        "✅ Acompañamiento hasta que recibas tu permiso\n\n"
        "💡 *Empezar es gratis.* Sin compromiso.\n\n"
        "📅 El plazo cierra el *30 de junio de 2026*.\n\n"
        "Empecemos verificando si cumples los requisitos básicos...\n\n"
        f"¿Tienes un código de un amigo? Escríbelo para €{PRICING['referral_discount']} de descuento.\n\n"
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
        f"Código aplicado. Tienes €{PRICING['referral_discount']} de descuento en tu primer pago.\n\n"
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


# --- Phase 3 Questionnaire helpers ---

def get_next_p3_question_index(answers: Dict, current_idx: int) -> int:
    """Get the next Phase 3 question index, skipping conditional questions."""
    for i in range(current_idx + 1, len(PHASE3_QUESTIONS)):
        q = PHASE3_QUESTIONS[i]
        cond_field = q.get("condition_field")
        if cond_field:
            cond_values = q.get("condition_values", [])
            if answers.get(cond_field) not in cond_values:
                continue
        return i
    return -1


def build_p3_question_keyboard(question: Dict) -> InlineKeyboardMarkup:
    """Build keyboard for a Phase 3 question."""
    if question["type"] == "buttons":
        btns = []
        for label, value in question.get("options", []):
            btns.append([InlineKeyboardButton(label, callback_data=f"p3q_{question['id']}_{value}")])
        if not question.get("required"):
            btns.append([InlineKeyboardButton("Saltar", callback_data=f"p3q_{question['id']}_skip")])
        return InlineKeyboardMarkup(btns)
    return None


# --- Country selection ---

async def handle_country(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    code = q.data.replace("c_", "")
    country = COUNTRIES.get(code, COUNTRIES["other"])
    update_user(update.effective_user.id, country_code=code)

    # Info only — no upsell at this stage
    antec_info = COUNTRIES_ANTECEDENTES_INFO.get(code, {})
    antec_line = ""
    if antec_info and code != "other":
        antec_line = (
            f"\n📜 Necesitarás antecedentes penales de {country['name']}.\n"
            "_Te explicaremos cómo conseguirlos más adelante._\n"
        )

    await q.edit_message_text(
        f"✅ Registrado: {country['flag']} *{country['name']}*\n"
        f"{antec_line}\n"
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

    counter = get_waitlist_count()
    await q.edit_message_text(
        f"*{name}, cumples los requisitos.*\n\n"
        f"Expediente: *{case['case_number']}*\n"
        f"Plazo: 1 abril — 30 junio 2026 ({days_left()} días)\n\n"
        f"{counter:,} personas en lista de espera.\n\n"
        "*Siguiente paso:* sube tus documentos para tenerlos listos cuando abra el proceso.\n\n"
        "Subir documentos es gratuito.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Subir documentos", callback_data="m_upload")],
            [InlineKeyboardButton("Ver lista de espera", callback_data="waitlist")],
            [InlineKeyboardButton("Preguntas frecuentes", callback_data="m_faq")],
        ]),
    )
    return ST_ELIGIBLE


# --- Waitlist wall ---

async def handle_waitlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Waitlist wall - blocks progress until BOE publishes."""
    q = update.callback_query
    if q:
        await q.answer()

    tid = update.effective_user.id
    user = get_user(tid)
    doc_count = get_doc_count(tid)
    counter = get_waitlist_count()

    text = (
        "*LISTA DE ESPERA*\n\n"
        f"{counter:,} personas en lista de espera.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "¿QUÉ SIGNIFICA?\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "El proceso aún no es oficial. Cuando el Gobierno publique "
        "el Real Decreto en el BOE (previsto marzo/abril 2026), "
        "abriremos el pago.\n\n"
        "• Notificaremos a todos simultáneamente\n"
        "• Las primeras 1.000 en pagar aseguran plaza\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "¿QUÉ PUEDES HACER AHORA?\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• Subir documentos — tenlos listos ({doc_count} subidos)\n"
        f"• Invitar amigos — €{PRICING['referral_credit']} descuento por cada uno"
    )

    keyboard = [
        [InlineKeyboardButton("Continuar con mi proceso", callback_data="continue_process")],
        [InlineKeyboardButton("Subir documentos", callback_data="m_upload")],
        [InlineKeyboardButton("Ver mis documentos", callback_data="m_docs")],
        [InlineKeyboardButton("Invitar amigos", callback_data="m_referidos")],
        [InlineKeyboardButton("Preguntas frecuentes", callback_data="m_faq")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if q:
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else:
        await update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    return ST_WAITLIST


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

    # Waitlist state
    if d == "waitlist" or d == "m_waitlist":
        return await handle_waitlist(update, ctx)

    # Continue process — show next step info
    if d == "continue_process":
        tid = update.effective_user.id
        counter = get_waitlist_count()
        text = (
            "*SIGUIENTE PASO: PAGO*\n\n"
            "Tu siguiente paso es realizar el pago, pero el proceso "
            "aún no está abierto.\n\n"
            f"{counter:,} personas en lista de espera.\n\n"
            "Cuando el BOE publique el Real Decreto "
            "(previsto marzo/abril 2026):\n"
            "• Notificaremos a todos simultáneamente\n"
            "• Las primeras 1.000 en pagar aseguran plaza\n\n"
            "Mientras tanto, asegúrate de tener todos tus documentos listos."
        )
        keyboard = [
            [InlineKeyboardButton("Subir documentos", callback_data="m_upload")],
            [InlineKeyboardButton("Ver mis documentos", callback_data="m_docs")],
            [InlineKeyboardButton("Volver", callback_data="m_menu")],
        ]
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard))
        return ST_WAITLIST

    # Block all payment paths → redirect to waitlist wall
    if d in ("m_pay2", "m_pay3", "m_pay4", "pay_full", "pay_bypass",
             "paid2", "paid2_free", "paid3", "paid4", "request_phase2",
             "join_waitlist", "m_price"):
        text = (
            "*No disponible*\n\n"
            "El pago aún no está abierto. Cuando el Gobierno publique "
            "el Real Decreto en el BOE, abriremos el proceso de pago "
            "y te notificaremos.\n\n"
            "Mientras tanto, sigue subiendo documentos para tenerlo todo listo."
        )
        keyboard = [
            [InlineKeyboardButton("Ver lista de espera", callback_data="waitlist")],
            [InlineKeyboardButton("Subir documentos", callback_data="m_upload")],
        ]
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard))
        return ST_WAITLIST

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

    # Phase FAQ — custom entry not in FAQ dict
    if d == "fq_fases":
        text = (
            "*¿QUÉ INCLUYE CADA FASE?*\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "FASE 1 — GRATIS\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Comprobamos tu elegibilidad y subes tus documentos.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"FASE 2 — €{PRICING['phase2']}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Evaluación de tu caso. Informe con probabilidad de "
            "éxito y documentos pendientes.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"FASE 3 — €{PRICING['phase3']}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Expediente preparado: formularios cumplimentados, "
            "documentos organizados.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"FASE 4 — €{PRICING['phase4']}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Memoria legal personalizada, presentación, seguimiento "
            "hasta resolución. Recurso incluido.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"PAGO ÚNICO — €{PRICING['prepay_total']}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Todas las fases incluidas. Ahorras €{PRICING['prepay_discount']}."
        )
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Todas las categorias", callback_data="m_faq")],
                [InlineKeyboardButton("Menu principal", callback_data="back")],
            ]))
        return ST_FAQ_ITEM

    # FAQ callback routing (from eligibility screen and other places)
    if d.startswith("fq_"):
        key = d[3:]
        faq = FAQ.get(key)
        if faq:
            text = faq["text"].replace("{days}", str(days_left()))
            # Document-related FAQs get extra button to see full 40+ proof list
            proof_keys = {"documentos_necesarios", "prueba_llegada", "prueba_permanencia",
                          "sin_empadronamiento", "documentos_otro_nombre"}
            btns = []
            if key in proof_keys:
                btns.append([InlineKeyboardButton("Ver 40+ documentos validos", callback_data="proof_docs_full")])
            btns.append([InlineKeyboardButton("Todas las categorias", callback_data="m_faq")])
            btns.append([InlineKeyboardButton("Menu principal", callback_data="back")])
            await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(btns))
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
                [InlineKeyboardButton("Subir documentos", callback_data="m_upload")],
                [InlineKeyboardButton("Ver 40+ documentos validos", callback_data="proof_docs_full")],
                [InlineKeyboardButton("Ayuda con antecedentes", callback_data="antecedentes_help")],
                [InlineKeyboardButton("Volver al menu", callback_data="back")],
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
                [InlineKeyboardButton("Subir documento", callback_data="m_upload")],
                [InlineKeyboardButton("Volver", callback_data="back")],
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
                [InlineKeyboardButton("Cancelar", callback_data="m_upload")],
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
                [InlineKeyboardButton("Cancelar", callback_data="m_upload")],
            ]))
        return ST_UPLOAD_PHOTO

    if d == "m_price":
        await q.edit_message_text(PRICING_EXPLANATION, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Pagar TODO — €{PRICING['prepay_total']}", callback_data="pay_full")],
                [InlineKeyboardButton(f"Evaluacion — €{PRICING['phase2']}", callback_data="m_pay2")],
                [InlineKeyboardButton("Ver servicios adicionales", callback_data="extra_services")],
                [InlineKeyboardButton("Volver", callback_data="back")],
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
                    [InlineKeyboardButton("Volver", callback_data="back")],
                ]),
            )
            return ST_MAIN_MENU

        text = build_referidos_text(stats)
        buttons = get_share_buttons(stats['code'])
        buttons.append([InlineKeyboardButton("Volver", callback_data="back")])

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
        tid = update.effective_user.id
        u = get_user(tid)
        if not u or not u.get("phase2_paid"):
            await q.edit_message_text(
                "*Consulta con abogado*\n\n"
                "La consulta con abogado está disponible para clientes "
                "a partir de Fase 2.\n\n"
                "Cuando el proceso sea oficial y completes tu pago, "
                "tendrás acceso a consultas personalizadas con nuestro "
                "equipo legal.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Volver", callback_data="back")],
                ]))
            return ST_MAIN_MENU
        await q.edit_message_text(
            "*¿Tienes una consulta para nuestro equipo legal?*\n\n"
            "Escribe tu mensaje aquí y lo trasladaremos a un abogado:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver", callback_data="back")],
            ]))
        ctx.user_data["awaiting_human_msg"] = True
        return ST_HUMAN_MSG

    if d == "write_msg":
        await q.edit_message_text(
            "*¿Tienes una consulta para nuestro equipo legal?*\n\n"
            "Escribe tu mensaje aquí y lo trasladaremos a un abogado:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Volver", callback_data="back")],
            ]))
        ctx.user_data["awaiting_human_msg"] = True
        return ST_HUMAN_MSG

    if d == "m_pay2":
        tid = update.effective_user.id
        dc = get_doc_count(tid)
        base_price = PRICING['phase2']

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

            kb = _payment_buttons("paid2", STRIPE_LINKS["phase2"])

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

        # Notify admins (referrer credit moved to Phase 3)
        await notify_admins(ctx,
            f"Pago Fase 2: User {tid}\n"
            f"Descuento: €{discount} | Créditos: €{credits_used}")

        # Get user's referral code for activation message
        user = get_user(tid)
        code = user.get('referral_code', '')
        share_btns = get_share_buttons(code)

        await q.edit_message_text(
            "✅ *Pago recibido.*\n\n"
            "Ahora viene la parte más importante: *conocer tu caso en detalle*.\n\n"
            "Te vamos a hacer unas preguntas sobre tu situación personal. "
            "Con tus respuestas + tus documentos, generaremos un *informe de evaluación personalizado*.\n\n"
            f"💡 Tu código de referidos: `{code}`\n"
            f"Cuando un amigo pague Fase 3, ambos ganáis €{PRICING['referral_credit']}.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Comenzar cuestionario", callback_data="start_questionnaire")],
                [InlineKeyboardButton("Mas tarde", callback_data="back")],
            ]),
        )
        return ST_MAIN_MENU

    if d == "m_pay3":
        u = get_user(update.effective_user.id)
        code = u.get("referral_code", "") if u else ""
        text = (
            f"*Preparación del expediente — €{PRICING['phase3']}*\n\n"
            "Sus documentos han sido verificados. Con este pago, nuestro equipo realizará:\n\n"
            "• Expediente legal completo.\n"
            "• Todos los formularios completados y revisados.\n"
            "• Revisión final por abogado.\n"
            "• Puesto reservado en cola de presentación.\n\n"
        )
        if code:
            text += f"💡 _Recuerda: ganas €{PRICING['referral_credit']} por cada amigo que pague. Tu código: `{code}`_\n\n"
        if STRIPE_LINKS["phase3"]:
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
            reply_markup=_payment_buttons("paid3", STRIPE_LINKS["phase3"]))
        return ST_PAY_PHASE3

    if d == "paid3":
        tid = update.effective_user.id
        update_user(tid, state="phase3_pending", phase3_paid=1, current_phase=3)
        u = get_user(tid)
        code = u.get("referral_code", "") if u else ""

        # Credit the referrer on Phase 3 payment (anti-gaming)
        result = credit_referrer(tid, 150)
        if result.get('credited'):
            try:
                user_data = get_user(tid)
                await ctx.bot.send_message(
                    result['referrer_id'],
                    f"🎉 Tu amigo {user_data.get('first_name', 'alguien')} completó Fase 3. +€{result['amount']} crédito.",
                )
            except Exception as e:
                logger.error(f"Failed to notify referrer: {e}")

        await notify_admins(ctx,
            f"💳 *Pago Fase 3 pendiente*\n"
            f"Usuario: {user.get('first_name')}\n"
            f"TID: {tid}\n"
            f"Aprobar: `/approve3 {tid}`")
        referral_line = f"\n💡 Tu código de referidos: `{code}` — invita amigos y gana €{PRICING['referral_credit']} por cada uno." if code else ""
        await q.edit_message_text(
            "✅ *Pago recibido.*\n\n"
            "Ahora viene la preparación de tu expediente. Te haremos unas "
            "preguntas con datos exactos para los formularios oficiales.\n\n"
            "Lo verificaremos y te avisaremos cuando esté activado."
            f"{referral_line}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Comenzar cuestionario", callback_data="start_phase3_questionnaire")],
                [InlineKeyboardButton("Mas tarde", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if d == "m_pay4":
        dl = days_left()
        u = get_user(update.effective_user.id)
        code = u.get("referral_code", "") if u else ""
        text = (
            f"*Presentación de solicitud — €{PRICING['phase4']}*\n\n"
            f"Su expediente está listo. Quedan *{dl} días* hasta el cierre del plazo.\n\n"
            "Con este pago final, realizaremos:\n\n"
            "• Presentación telemática oficial ante Extranjería.\n"
            "• Seguimiento del estado de su solicitud.\n"
            "• Notificación inmediata de resolución.\n"
            "• Asistencia para recogida de TIE.\n\n"
            f"📦 *¿Quieres todo incluido?* Por €{PRICING['phase4_bundle']} te gestionamos "
            "también las tasas del gobierno.\n\n"
        )
        if code:
            text += f"💡 _Invita amigos con tu código `{code}` y gana €{PRICING['referral_credit']} por cada uno._\n\n"
        if STRIPE_LINKS["phase4"]:
            text += "Pulse *Pagar con tarjeta* para un pago seguro instantáneo."
        else:
            text += (
                "*Formas de pago:*\n"
                f"Bizum: {BIZUM_PHONE}\n"
                f"Transferencia: {BANK_IBAN}\n"
                "Concepto: su nombre + número de expediente."
            )
        kb_buttons = []
        if STRIPE_LINKS["phase4_bundle"]:
            kb_buttons.append([InlineKeyboardButton(f"Paquete completo — €{PRICING['phase4_bundle']}", callback_data="buy_phase4_bundle")])
        kb_buttons.extend(_payment_buttons("paid4", STRIPE_LINKS["phase4"]).inline_keyboard)
        await q.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(kb_buttons))
        return ST_PAY_PHASE4

    if d == "paid4":
        tid = update.effective_user.id
        update_user(tid, state="phase4_pending")
        u = get_user(tid)
        code = u.get("referral_code", "") if u else ""
        await notify_admins(ctx,
            f"💳 *Pago Fase 4 pendiente*\n"
            f"Usuario: {user.get('first_name')}\n"
            f"TID: {tid}\n"
            f"Aprobar: `/approve4 {tid}`")
        referral_line = f"\n\n💡 _Invita amigos con tu código `{code}` — ganan €{PRICING['referral_discount']} de descuento y tú ganas €{PRICING['referral_credit']}._" if code else ""
        await q.edit_message_text(
            "✅ *Pago recibido.*\n\n"
            "Lo verificaremos y procederemos a presentar su solicitud. "
            f"Recibirá una confirmación con el número de registro.{referral_line}",
            parse_mode=ParseMode.MARKDOWN)
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
                [InlineKeyboardButton("Volver", callback_data="back")],
            ]))
        return ST_PAY_PHASE2

    if d == "pay_full":
        tid = update.effective_user.id
        u = get_user(tid)
        has_referral = u.get("used_referral_code") is not None
        price = PRICING["prepay_total"] - PRICING["referral_discount"] if has_referral else PRICING["prepay_total"]
        referral_line = f"\n🎁 _Descuento de €{PRICING['referral_discount']} aplicado por usar código de amigo._\n" if has_referral else ""
        btns = []
        if STRIPE_LINKS["prepay"]:
            btns.append([InlineKeyboardButton(f"Pagar €{price}", url=STRIPE_LINKS["prepay"])])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Tengo dudas", callback_data="m_contact")])
        btns.append([InlineKeyboardButton("Volver", callback_data="back")])
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

    if d == "proof_docs_full":
        await q.edit_message_text(
            FAQ_PROOF_DOCUMENTS_FULL,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Subir documentos", callback_data="m_upload")],
                [InlineKeyboardButton("Volver a checklist", callback_data="m_checklist")],
                [InlineKeyboardButton("Menu", callback_data="back")],
            ]))
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
                [InlineKeyboardButton("Si, contactadme", callback_data="confirm_antecedentes_request")],
                [InlineKeyboardButton("Volver", callback_data="antecedentes_help")],
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
            f"Contactar para dar presupuesto de servicio antecedentes (€{PRICING['antecedentes_foreign']} estándar)."
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
                [InlineKeyboardButton("Subir documentos", callback_data="m_upload")],
                [InlineKeyboardButton("Menu", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    if d == "buy_antecedentes":
        tid = update.effective_user.id
        u = get_user(tid)
        country_code = u.get("country_code", "other") if u else "other"
        # Show country-specific upsell message
        upsell_msg = get_antecedentes_upsell_message(country_code)
        btns = []
        if STRIPE_LINKS["antecedentes_foreign"]:
            btns.append([InlineKeyboardButton(f"Pagar €{PRICING['antecedentes_foreign']}", url=STRIPE_LINKS["antecedentes_foreign"])])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Volver", callback_data="back")])
        await q.edit_message_text(
            upsell_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    if d == "buy_govt_fees":
        tid = update.effective_user.id
        btns = []
        if STRIPE_LINKS["govt_fees"]:
            btns.append([InlineKeyboardButton(f"Pagar €{PRICING['govt_fees_service']}", url=STRIPE_LINKS["govt_fees"])])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Volver", callback_data="back")])
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
            f"📜 *Antecedentes España — €{PRICING['antecedentes_spain']}*\n"
            "Lo tramitamos por ti (sin Cl@ve, sin colas).\n\n"
            f"🌍 *Antecedentes País de Origen — €{PRICING['antecedentes_foreign']}*\n"
            "Solicitud + apostilla + traducción jurada.\n\n"
            f"🏛️ *Gestión de Tasas — €{PRICING['govt_fees_service']}*\n"
            "Pagamos las tasas gubernamentales (790) por ti.\n\n"
            f"🔤 *Traducción Jurada — €{PRICING['translation_per_doc']}/doc*\n"
            "Traducción oficial válida para extranjería.\n\n"
            f"⚡ *Procesamiento Prioritario — €{PRICING['urgent_processing']}*\n"
            "Tu expediente se prepara y presenta primero.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "_Puedes añadir estos servicios en cualquier momento._",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Antecedentes España — €{PRICING['antecedentes_spain']}", callback_data="upsell_antec_spain")],
                [InlineKeyboardButton(f"Antecedentes pais — €{PRICING['antecedentes_foreign']}", callback_data="buy_antecedentes")],
                [InlineKeyboardButton(f"Tasas gobierno — €{PRICING['govt_fees_service']}", callback_data="buy_govt_fees")],
                [InlineKeyboardButton(f"Traduccion — €{PRICING['translation_per_doc']}/doc", callback_data="buy_translation")],
                [InlineKeyboardButton(f"Prioritario — €{PRICING['urgent_processing']}", callback_data="buy_priority")],
                [InlineKeyboardButton("Volver", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # --- Spain antecedentes upsell ---
    if d == "upsell_antec_spain":
        await q.edit_message_text(
            UPSELL_ANTECEDENTES_SPAIN,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=antecedentes_spain_kb())
        return ST_MAIN_MENU

    if d == "buy_antec_spain":
        btns = []
        if STRIPE_LINKS["antecedentes_spain"]:
            btns.append([InlineKeyboardButton(f"Pagar €{PRICING['antecedentes_spain']}", url=STRIPE_LINKS["antecedentes_spain"])])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Volver", callback_data="extra_services")])
        await q.edit_message_text(
            f"📜 *Antecedentes España — €{PRICING['antecedentes_spain']}*\n\n"
            "Para tramitar en tu nombre, necesitamos:\n\n"
            "1️⃣ *Autorización firmada* (te enviamos el documento)\n"
            "2️⃣ *Copia de tu pasaporte*\n"
            "3️⃣ *Pago de €{price}*\n\n"
            "Tras el pago, te contactaremos para los datos.".format(price=PRICING['antecedentes_spain']),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    if d == "diy_antec_spain":
        await q.edit_message_text(
            ANTECEDENTES_SPAIN_DIY,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"He cambiado de opinión — €{PRICING['antecedentes_spain']}", callback_data="buy_antec_spain")],
                [InlineKeyboardButton("Menu", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # --- Translation service ---
    if d == "buy_translation":
        btns = []
        if STRIPE_LINKS["translation"]:
            btns.append([InlineKeyboardButton(f"Pagar €{PRICING['translation_per_doc']}", url=STRIPE_LINKS["translation"])])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Volver", callback_data="extra_services")])
        await q.edit_message_text(
            UPSELL_TRANSLATION,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    # --- Priority processing ---
    if d == "buy_priority":
        btns = []
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Volver", callback_data="extra_services")])
        await q.edit_message_text(
            UPSELL_PRIORITY,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    # --- Bundle offers ---
    if d == "buy_vip_bundle":
        u = get_user(update.effective_user.id)
        has_referral = u.get("used_referral_code") is not None if u else False
        price = PRICING['vip_bundle'] - PRICING['referral_discount'] if has_referral else PRICING['vip_bundle']
        btns = []
        if STRIPE_LINKS["vip_bundle"]:
            btns.append([InlineKeyboardButton(f"Pagar €{price}", url=STRIPE_LINKS["vip_bundle"])])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Volver", callback_data="back")])
        await q.edit_message_text(
            VIP_BUNDLE_OFFER,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    if d == "buy_phase4_bundle":
        btns = []
        if STRIPE_LINKS["phase4_bundle"]:
            btns.append([InlineKeyboardButton(f"Pagar €{PRICING['phase4_bundle']}", url=STRIPE_LINKS["phase4_bundle"])])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Volver", callback_data="back")])
        await q.edit_message_text(
            PHASE4_BUNDLE_OFFER,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
        return ST_MAIN_MENU

    # --- FAQ pricing explanation ---
    if d == "faq_pricing":
        await q.edit_message_text(
            PRICING_EXPLANATION,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Pagar TODO — €{PRICING['prepay_total']}", callback_data="pay_full")],
                [InlineKeyboardButton(f"Evaluacion — €{PRICING['phase2']}", callback_data="m_pay2")],
                [InlineKeyboardButton("Servicios adicionales", callback_data="extra_services")],
                [InlineKeyboardButton("Menu", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # --- Government fees explanation ---
    if d == "explain_govt_fees":
        await q.edit_message_text(
            "🏛️ *Cómo se pagan las tasas del gobierno*\n\n"
            "Las tasas gubernamentales se pagan a través de modelos 790 "
            "en la web de la Agencia Tributaria.\n\n"
            "• Modelo 790-052 (autorización de residencia): ~€16-20\n"
            "• Modelo 790-012 (TIE - tarjeta física): ~€16-21\n\n"
            "Para pagarlas necesitas:\n"
            "• Acceder a sede.administracionespublicas.gob.es\n"
            "• Rellenar los formularios correctamente\n"
            "• Pagar con tarjeta o en banco\n\n"
            f"💡 Por €{PRICING['govt_fees_service']} nos encargamos de todo esto por ti.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Gestionadlo — €{PRICING['govt_fees_service']}", callback_data="buy_govt_fees")],
                [InlineKeyboardButton("Volver", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # --- Phase 2 questionnaire start ---
    if d == "start_questionnaire":
        ctx.user_data["phase2_answers"] = {}
        ctx.user_data["phase2_q_idx"] = 0
        q_data = PHASE2_QUESTIONS[0]
        section = q_data.get("section", "")
        text = f"📋 *{section}*\n\n{q_data['text']}"
        if q_data["type"] == "buttons":
            await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=build_question_keyboard(q_data))
            return ST_PHASE2_QUESTIONNAIRE
        else:
            await q.edit_message_text(
                text + "\n\n_Escribe tu respuesta:_",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Saltar", callback_data=f"p2q_{q_data['id']}_skip")],
                ]))
            return ST_PHASE2_TEXT_ANSWER

    # --- Phase 3 questionnaire start ---
    if d == "start_phase3_questionnaire":
        ctx.user_data["phase3_answers"] = {}
        ctx.user_data["phase3_q_idx"] = 0
        # Show intro first, then first question
        q_data = PHASE3_QUESTIONS[0]
        section = q_data.get("section", "")
        text = f"{PHASE3_INTRO}\n\n📋 *{section}*\n\n{q_data['text']}"
        if q_data["type"] == "buttons":
            await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=build_p3_question_keyboard(q_data))
            return ST_PHASE3_QUESTIONNAIRE
        else:
            skip_btn = []
            if not q_data.get("required"):
                skip_btn = [[InlineKeyboardButton("Saltar", callback_data=f"p3q_{q_data['id']}_skip")]]
            await q.edit_message_text(
                text + "\n\n_Escribe tu respuesta:_",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(skip_btn) if skip_btn else None)
            return ST_PHASE3_TEXT_ANSWER

    # --- Phase 2 pitch (after 3+ docs) — capacity check ---
    if d == "request_phase2":
        dc = get_doc_count(update.effective_user.id)
        u = get_user(update.effective_user.id)

        if is_capacity_full():
            # CAPACITY FULL — redirect to waitlist
            return await handle_waitlist(update, ctx)

        # SLOTS AVAILABLE — normal Phase 2 pitch
        available = get_available_slots()
        has_referral = u.get("used_referral_code") is not None if u else False
        phase2_price = PRICING["phase2"] - PRICING["referral_discount"] if has_referral else PRICING["phase2"]
        prepay_price = PRICING["prepay_total"] - PRICING["referral_discount"] if has_referral else PRICING["prepay_total"]

        await q.edit_message_text(
            f"📊 *Has subido {dc} documentos. Buen trabajo.*\n\n"
            f"📊 Plazas disponibles: *{available} de {TOTAL_CAPACITY}*\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "EVALUACIÓN PERSONALIZADA\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ Revisamos cada documento\n"
            "✅ 20+ preguntas sobre tu situación\n"
            "✅ Estrategia personalizada\n"
            "✅ Detectamos qué te falta\n\n"
            f"⭐ *¿Prefieres pagar todo de una vez?*\n"
            f"Por €{prepay_price} tienes TODO hasta la resolución. Ahorras €48.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Evaluacion — €{phase2_price}", callback_data="m_pay2")],
                [InlineKeyboardButton(f"Todo incluido — €{prepay_price}", callback_data="pay_full")],
                [InlineKeyboardButton("Subir mas documentos", callback_data="m_upload")],
                [InlineKeyboardButton("¿Por que estos precios?", callback_data="faq_pricing")],
            ]))
        return ST_MAIN_MENU

    # --- Waitlist ---
    if d == "join_waitlist":
        tid = update.effective_user.id
        u = get_user(tid)
        dc = get_doc_count(tid)
        name = u.get("full_name") or u.get("first_name", "") if u else ""
        country = u.get("country_code", "") if u else ""
        add_to_waitlist(tid, name, country, dc)
        position = get_waitlist_position(tid)
        await notify_admins(ctx, f"⏳ *Nuevo en lista de espera*\nUsuario: {name} ({tid})\nPosición: #{position}\nDocs: {dc}")
        await q.edit_message_text(
            f"*Estás en la lista de espera*\n\n"
            "Tus documentos están guardados.\n"
            "Te avisaremos por este chat cuando el proceso sea oficial.\n\n"
            "Mientras tanto, sigue subiendo documentos para tenerlo todo listo.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Subir mas documentos", callback_data="m_upload")],
                [InlineKeyboardButton("Ver mis documentos", callback_data="m_docs")],
                [InlineKeyboardButton("Menu", callback_data="back")],
            ]))
        return ST_MAIN_MENU

    # --- Bypass waitlist with prepay ---
    if d == "pay_bypass":
        btns = []
        if STRIPE_LINKS["prepay"]:
            btns.append([InlineKeyboardButton(f"Pagar €{PREPAY_BYPASS_PRICE}", url=STRIPE_LINKS["prepay"])])
        btns.append([InlineKeyboardButton(f"Bizum: {BIZUM_PHONE}", callback_data="show_bizum")])
        btns.append([InlineKeyboardButton("Volver", callback_data="request_phase2")])
        await q.edit_message_text(
            f"⭐ *RESERVA TU PLAZA*\n\n"
            f"Pago único: *€{PREPAY_BYPASS_PRICE}*\n\n"
            "Incluye TODO hasta la resolución:\n"
            "Evaluación personalizada (Fase 2)\n"
            "Expediente a medida (Fase 3)\n"
            "Presentación + seguimiento (Fase 4)\n"
            "Recurso si necesario\n\n"
            f"*Ahorras €{PRICING['prepay_discount']}* vs pago por fases.\n"
            "*Empiezas mañana* — sin esperar lista.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))
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


# --- Phase 2 Questionnaire ---

async def handle_phase2_questionnaire(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button answers to Phase 2 questionnaire."""
    q = update.callback_query
    await q.answer()
    d = q.data

    answers = ctx.user_data.get("phase2_answers", {})
    current_idx = ctx.user_data.get("phase2_q_idx", 0)

    # Parse callback: p2q_{question_id}_{value}
    if d.startswith("p2q_"):
        parts = d[4:].rsplit("_", 1)
        if len(parts) == 2:
            q_id, value = parts
            if value != "skip":
                answers[q_id] = value
            ctx.user_data["phase2_answers"] = answers

    # Get next question
    next_idx = get_next_question_index(answers, current_idx)

    if next_idx < 0:
        # Questionnaire complete — generate report
        user = get_user(update.effective_user.id)
        update_user(update.effective_user.id, phase2_answers=json.dumps(answers))
        report = generate_phase2_report(user, answers)

        # Check for upsell opportunities based on answers
        upsell_btns = []
        if answers.get("antecedentes_foreign_status") in ("antec_none", "antec_partial", "antec_difficult"):
            upsell_btns.append([InlineKeyboardButton(
                f"🌍 Antecedentes país — €{PRICING['antecedentes_foreign']}", callback_data="buy_antecedentes")])
        if answers.get("passport_status") not in ("passport_valid",):
            pass  # Just note in report, no upsell
        upsell_btns.append([InlineKeyboardButton(
            f"📜 Antecedentes España — €{PRICING['antecedentes_spain']}", callback_data="upsell_antec_spain")])

        btns = upsell_btns + [
            [InlineKeyboardButton(f"Siguiente: expediente — €{PRICING['phase3']}", callback_data="m_pay3")],
            [InlineKeyboardButton("Ver servicios adicionales", callback_data="extra_services")],
            [InlineKeyboardButton("Menu", callback_data="back")],
        ]

        await q.edit_message_text(
            report,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))

        # Notify admins
        name = user.get("full_name") or user.get("first_name", "?")
        await notify_admins(ctx,
            f"📊 *Cuestionario Fase 2 completado*\n"
            f"Usuario: {name} ({update.effective_user.id})\n"
            f"Respuestas: {len(answers)}")
        return ST_MAIN_MENU

    # Show next question
    ctx.user_data["phase2_q_idx"] = next_idx
    q_data = PHASE2_QUESTIONS[next_idx]
    section = q_data.get("section", "")
    progress = f"({next_idx + 1}/{len(PHASE2_QUESTIONS)})"
    text = f"📋 *{section}* {progress}\n\n{q_data['text']}"

    if q_data["type"] == "buttons":
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_question_keyboard(q_data))
        return ST_PHASE2_QUESTIONNAIRE
    else:
        await q.edit_message_text(
            text + "\n\n_Escribe tu respuesta:_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Saltar", callback_data=f"p2q_{q_data['id']}_skip")],
            ]))
        return ST_PHASE2_TEXT_ANSWER


async def handle_phase2_text_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle free-text answers to Phase 2 questionnaire."""
    text = update.message.text or ""
    answers = ctx.user_data.get("phase2_answers", {})
    current_idx = ctx.user_data.get("phase2_q_idx", 0)

    if current_idx < len(PHASE2_QUESTIONS):
        q_data = PHASE2_QUESTIONS[current_idx]
        answers[q_data["id"]] = text
        ctx.user_data["phase2_answers"] = answers

    # Get next question
    next_idx = get_next_question_index(answers, current_idx)

    if next_idx < 0:
        # Questionnaire complete
        user = get_user(update.effective_user.id)
        update_user(update.effective_user.id, phase2_answers=json.dumps(answers))
        report = generate_phase2_report(user, answers)

        upsell_btns = []
        if answers.get("antecedentes_foreign_status") in ("antec_none", "antec_partial", "antec_difficult"):
            upsell_btns.append([InlineKeyboardButton(
                f"🌍 Antecedentes país — €{PRICING['antecedentes_foreign']}", callback_data="buy_antecedentes")])
        upsell_btns.append([InlineKeyboardButton(
            f"📜 Antecedentes España — €{PRICING['antecedentes_spain']}", callback_data="upsell_antec_spain")])

        btns = upsell_btns + [
            [InlineKeyboardButton(f"Siguiente: expediente — €{PRICING['phase3']}", callback_data="m_pay3")],
            [InlineKeyboardButton("Ver servicios adicionales", callback_data="extra_services")],
            [InlineKeyboardButton("Menu", callback_data="back")],
        ]

        await update.message.reply_text(
            report,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(btns))

        name = user.get("full_name") or user.get("first_name", "?")
        await notify_admins(ctx,
            f"📊 *Cuestionario Fase 2 completado*\n"
            f"Usuario: {name} ({update.effective_user.id})\n"
            f"Respuestas: {len(answers)}")
        return ST_MAIN_MENU

    # Show next question
    ctx.user_data["phase2_q_idx"] = next_idx
    q_data = PHASE2_QUESTIONS[next_idx]
    section = q_data.get("section", "")
    progress = f"({next_idx + 1}/{len(PHASE2_QUESTIONS)})"
    text_msg = f"📋 *{section}* {progress}\n\n{q_data['text']}"

    if q_data["type"] == "buttons":
        await update.message.reply_text(text_msg, parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_question_keyboard(q_data))
        return ST_PHASE2_QUESTIONNAIRE
    else:
        await update.message.reply_text(
            text_msg + "\n\n_Escribe tu respuesta:_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Saltar", callback_data=f"p2q_{q_data['id']}_skip")],
            ]))
        return ST_PHASE2_TEXT_ANSWER


# --- Phase 3 Questionnaire ---

async def handle_phase3_questionnaire(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button answers to Phase 3 questionnaire."""
    q = update.callback_query
    await q.answer()
    d = q.data

    answers = ctx.user_data.get("phase3_answers", {})
    current_idx = ctx.user_data.get("phase3_q_idx", 0)

    # Parse callback: p3q_{question_id}_{value}
    if d.startswith("p3q_"):
        parts = d[4:].rsplit("_", 1)
        if len(parts) == 2:
            q_id, value = parts
            if value != "skip":
                answers[q_id] = value
            ctx.user_data["phase3_answers"] = answers

    # Get next question
    next_idx = get_next_p3_question_index(answers, current_idx)

    if next_idx < 0:
        # Questionnaire complete — save and notify
        tid = update.effective_user.id
        update_user(tid, phase3_answers=json.dumps(answers))

        await q.edit_message_text(
            PHASE3_COMPLETION,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Menu principal", callback_data="back")],
            ]))

        user = get_user(tid)
        name = user.get("full_name") or user.get("first_name", "?") if user else "?"
        await notify_admins(ctx,
            f"📝 *Cuestionario Fase 3 completado*\n"
            f"Usuario: {name} ({tid})\n"
            f"Respuestas: {len(answers)}\n"
            f"Expediente en preparación.")
        return ST_MAIN_MENU

    # Show next question
    ctx.user_data["phase3_q_idx"] = next_idx
    q_data = PHASE3_QUESTIONS[next_idx]
    section = q_data.get("section", "")
    progress = f"({next_idx + 1}/{len(PHASE3_QUESTIONS)})"
    text = f"📋 *{section}* {progress}\n\n{q_data['text']}"

    if q_data["type"] == "buttons":
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_p3_question_keyboard(q_data))
        return ST_PHASE3_QUESTIONNAIRE
    else:
        skip_btn = []
        if not q_data.get("required"):
            skip_btn = [[InlineKeyboardButton("Saltar", callback_data=f"p3q_{q_data['id']}_skip")]]
        await q.edit_message_text(
            text + "\n\n_Escribe tu respuesta:_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(skip_btn) if skip_btn else None)
        return ST_PHASE3_TEXT_ANSWER


async def handle_phase3_text_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle free-text answers to Phase 3 questionnaire."""
    text = update.message.text or ""
    answers = ctx.user_data.get("phase3_answers", {})
    current_idx = ctx.user_data.get("phase3_q_idx", 0)

    if current_idx < len(PHASE3_QUESTIONS):
        q_data = PHASE3_QUESTIONS[current_idx]
        answers[q_data["id"]] = text
        ctx.user_data["phase3_answers"] = answers

    # Get next question
    next_idx = get_next_p3_question_index(answers, current_idx)

    if next_idx < 0:
        # Questionnaire complete
        tid = update.effective_user.id
        update_user(tid, phase3_answers=json.dumps(answers))

        await update.message.reply_text(
            PHASE3_COMPLETION,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Menu principal", callback_data="back")],
            ]))

        user = get_user(tid)
        name = user.get("full_name") or user.get("first_name", "?") if user else "?"
        await notify_admins(ctx,
            f"📝 *Cuestionario Fase 3 completado*\n"
            f"Usuario: {name} ({tid})\n"
            f"Respuestas: {len(answers)}\n"
            f"Expediente en preparación.")
        return ST_MAIN_MENU

    # Show next question
    ctx.user_data["phase3_q_idx"] = next_idx
    q_data = PHASE3_QUESTIONS[next_idx]
    section = q_data.get("section", "")
    progress = f"({next_idx + 1}/{len(PHASE3_QUESTIONS)})"
    text_msg = f"📋 *{section}* {progress}\n\n{q_data['text']}"

    if q_data["type"] == "buttons":
        await update.message.reply_text(text_msg, parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_p3_question_keyboard(q_data))
        return ST_PHASE3_QUESTIONNAIRE
    else:
        skip_btn = []
        if not q_data.get("required"):
            skip_btn = [[InlineKeyboardButton("Saltar", callback_data=f"p3q_{q_data['id']}_skip")]]
        await update.message.reply_text(
            text_msg + "\n\n_Escribe tu respuesta:_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(skip_btn) if skip_btn else None)
        return ST_PHASE3_TEXT_ANSWER


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
            proof_keys = {"documentos_necesarios", "prueba_llegada", "prueba_permanencia",
                          "sin_empadronamiento", "documentos_otro_nombre"}
            btns = []
            if key in proof_keys:
                btns.append([InlineKeyboardButton("Ver 40+ documentos validos", callback_data="proof_docs_full")])
            cat_key = ctx.user_data.get("faq_cat")
            if cat_key and cat_key in FAQ_CATEGORIES:
                btns.append([InlineKeyboardButton(
                    f"← {FAQ_CATEGORIES[cat_key]['title']}",
                    callback_data=f"fcat_{cat_key}")])
            btns.append([InlineKeyboardButton("Todas las categorias", callback_data="m_faq")])
            btns.append([InlineKeyboardButton("Menu principal", callback_data="back")])
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

    # Post-upload response — direct to waitlist
    response_btns = [
        [InlineKeyboardButton("Subir otro documento", callback_data="m_upload")],
        [InlineKeyboardButton("Ver lista de espera", callback_data="waitlist")],
    ]

    await update.message.reply_text(
        f"*Documento guardado.*\n\n"
        f"Documentos aportados: {dc}\n\n"
        "Puedes seguir subiendo documentos o ver la lista de espera.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(response_btns),
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

    # Post-upload response — direct to waitlist
    response_btns2 = [
        [InlineKeyboardButton("Subir otro documento", callback_data="m_upload")],
        [InlineKeyboardButton("Ver lista de espera", callback_data="waitlist")],
    ]

    await update.message.reply_text(
        f"*Documento guardado.*\n\n"
        f"Documentos aportados: {dc}\n\n"
        "Puedes seguir subiendo documentos o ver la lista de espera.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(response_btns2),
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
                [InlineKeyboardButton("Volver al menu", callback_data="back")],
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
    rev = (p2 * PRICING['phase2']) + (p3 * PRICING['phase3']) + (p4 * PRICING['phase4'])
    db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
    available = get_available_slots()
    wl_stats = get_waitlist_stats()
    await update.message.reply_text(
        f"*Estadísticas*\n\n"
        f"Usuarios: {total}\n"
        f"Elegibles: {eligible}\n"
        f"Documentos: {docs}\n"
        f"Mensajes recibidos: {msgs}\n\n"
        f"Fase 2 pagados: {p2} (€{p2*PRICING['phase2']})\n"
        f"Fase 3 pagados: {p3} (€{p3*PRICING['phase3']})\n"
        f"Fase 4 pagados: {p4} (€{p4*PRICING['phase4']})\n"
        f"*Ingresos: €{rev}*\n\n"
        f"📊 *Capacidad:* {TOTAL_CAPACITY - available}/{TOTAL_CAPACITY} ({available} libres)\n"
        f"⏳ *Lista espera:* {wl_stats['total']}\n\n"
        f"DB: {db_type}\n"
        f"Días restantes: {days_left()}", parse_mode=ParseMode.MARKDOWN)


async def cmd_waitlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /waitlist — view capacity and waitlist stats."""
    if update.effective_user.id not in ADMIN_IDS:
        return
    available = get_available_slots()
    stats = get_waitlist_stats()
    text = (
        f"📊 *CAPACITY & WAITLIST*\n\n"
        f"*Capacidad:*\n"
        f"• Total: {TOTAL_CAPACITY}\n"
        f"• Ocupadas: {TOTAL_CAPACITY - available}\n"
        f"• Disponibles: {available}\n\n"
        f"*Lista de espera:*\n"
        f"• Total: {stats['total']}\n"
        f"• Notificados: {stats['notified']}\n"
        f"• Convertidos: {stats['converted']}\n\n"
    )
    if stats.get('by_country'):
        text += "*Por país:*\n"
        for country, count in stats['by_country'].items():
            text += f"• {country}: {count}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_release(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /release [N] — notify N waitlist users that slots are open."""
    if update.effective_user.id not in ADMIN_IDS:
        return
    try:
        count = int(ctx.args[0]) if ctx.args else 10
    except (ValueError, IndexError):
        count = 10

    users = get_waitlist_users(limit=count, notified=False)
    sent = 0
    for wl_user in users:
        try:
            await ctx.bot.send_message(
                chat_id=wl_user['telegram_id'],
                text=(
                    "🎉 *¡Hay plaza para ti!*\n\n"
                    "Se han abierto nuevas plazas y eres de los primeros.\n\n"
                    "Tienes *48 horas* para continuar tu proceso.\n"
                    "Tus documentos siguen guardados."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Continuar ahora", callback_data="request_phase2")]
                ]))
            mark_waitlist_notified(wl_user['telegram_id'])
            sent += 1
        except Exception as e:
            logger.warning(f"Failed to notify waitlist {wl_user['telegram_id']}: {e}")
    await update.message.reply_text(f"✅ Notificados: {sent}/{len(users)}")


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
            InlineKeyboardButton("Aprobar", callback_data=f"pdoc_approve_{doc_id}"),
            InlineKeyboardButton("Rechazar", callback_data=f"pdoc_reject_{doc_id}"),
        ],
        [
            InlineKeyboardButton("Pedir nueva foto", callback_data=f"pdoc_resubmit_{doc_id}"),
            InlineKeyboardButton("Siguiente", callback_data="pdoc_next"),
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
            [InlineKeyboardButton("Borroso/ilegible", callback_data=f"prej_blur_{doc_id}")],
            [InlineKeyboardButton("Incompleto/recortado", callback_data=f"prej_inc_{doc_id}")],
            [InlineKeyboardButton("Documento vencido", callback_data=f"prej_exp_{doc_id}")],
            [InlineKeyboardButton("Tipo incorrecto", callback_data=f"prej_wrong_{doc_id}")],
            [InlineKeyboardButton("No es documento valido", callback_data=f"prej_invalid_{doc_id}")],
            [InlineKeyboardButton("Otro motivo", callback_data=f"prej_other_{doc_id}")],
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
            [InlineKeyboardButton("Flash/reflejo", callback_data=f"pres_flash_{doc_id}")],
            [InlineKeyboardButton("Poca luz", callback_data=f"pres_dark_{doc_id}")],
            [InlineKeyboardButton("Borroso", callback_data=f"pres_blur_{doc_id}")],
            [InlineKeyboardButton("Cortado", callback_data=f"pres_cut_{doc_id}")],
            [InlineKeyboardButton("Angulo incorrecto", callback_data=f"pres_angle_{doc_id}")],
            [InlineKeyboardButton("Sube frente/reverso", callback_data=f"pres_flip_{doc_id}")],
            [InlineKeyboardButton("Escribir mensaje personalizado", callback_data=f"pres_custom_{doc_id}")],
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
    buttons.append([InlineKeyboardButton("Menu", callback_data="back")])

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
            [InlineKeyboardButton("Ver documentos", callback_data="m_docs")],
            [InlineKeyboardButton("Subir documento", callback_data="m_upload")],
            [InlineKeyboardButton("Compartir mi codigo", callback_data="m_referidos")],
            [InlineKeyboardButton("Menu", callback_data="back")],
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
                [InlineKeyboardButton("Subir documentos", callback_data="m_docs")],
                [InlineKeyboardButton("Menu", callback_data="m_menu")],
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
            [InlineKeyboardButton("Subir mas documentos", callback_data="m_docs")],
            [InlineKeyboardButton("Menu", callback_data="m_menu")],
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
            [InlineKeyboardButton("Menu", callback_data="m_menu")],
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
            ST_PHASE2_QUESTIONNAIRE: [
                CallbackQueryHandler(handle_phase2_questionnaire, pattern="^p2q_"),
                CallbackQueryHandler(handle_menu),
            ],
            ST_PHASE2_TEXT_ANSWER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phase2_text_answer),
                CallbackQueryHandler(handle_phase2_questionnaire, pattern="^p2q_"),
                CallbackQueryHandler(handle_menu),
            ],
            ST_PHASE3_QUESTIONNAIRE: [
                CallbackQueryHandler(handle_phase3_questionnaire, pattern="^p3q_"),
                CallbackQueryHandler(handle_menu),
            ],
            ST_PHASE3_TEXT_ANSWER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phase3_text_answer),
                CallbackQueryHandler(handle_phase3_questionnaire, pattern="^p3q_"),
                CallbackQueryHandler(handle_menu),
            ],
            ST_WAITLIST: [
                CallbackQueryHandler(handle_menu),
                MessageHandler(filters.PHOTO, handle_photo_upload),
                MessageHandler(filters.Document.ALL, handle_file_upload),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text),
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
    app.add_handler(CommandHandler("waitlist", cmd_waitlist), group=-1)
    app.add_handler(CommandHandler("release", cmd_release), group=-1)
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

    logger.info("PH-Bot v6.0.0 starting")
    logger.info(f"ADMIN_IDS: {ADMIN_IDS}")
    logger.info(f"Payment: FREE > €{PRICING['phase2']} > €{PRICING['phase3']} > €{PRICING['phase4']} | Days left: {days_left()} | BOE: {BOE_PUBLISHED}")
    logger.info(f"Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
