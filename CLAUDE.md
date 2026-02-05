# tuspapeles2026 — Full Project Context

## THE BUSINESS

**Pombo & Horowitz Abogados** is a Spanish law firm launching a mass-market service to help undocumented immigrants regularize their status under Spain's 2026 regularization decree (Royal Decree, approved Jan 27, 2026).

**The opportunity:** ~840,000 undocumented immigrants in Spain. Application window: April 1 – June 30, 2026 (3 months, no extension confirmed). 90% are Latin American (~760k), with Colombians at 35%. The decree presumes vulnerability for anyone in irregular status — NO job offer needed (biggest difference from the 2005 process). 80-90% approval rate expected based on 2005 precedent. Applications are 100% online (telematic).

**Our edge:** AI-automated document intake, OCR validation, and 24/7 Telegram bot — no competitor has this. We're a "factory" vs their "one-by-one" manual review. Lower price (€297 vs avg €370).

**Brand:** tuspapeles2026.es ("your papers 2026") — warm, professional, trustworthy. Target audience is scared immigrants who've often been scammed. Professional lawyer tone in Spanish — no slang, no "quiubo parce."

---

## ARCHITECTURE — 4 Components

### 1. PH-Site (Law Firm Website)
- **URL:** pombohorowitz.es
- **Repo:** github.com/anacuero-bit/PH-Site
- **Hosting:** GitHub Pages
- **Tech:** Static HTML/CSS/JS
- **Features:** Law firm homepage, news ticker (managed by Content Bot), regularization info
- **Status:** ✅ Live

### 2. tus-papeles-2026 (Campaign Microsite)
- **URL:** tuspapeles2026.es
- **Repo:** github.com/anacuero-bit/tus-papeles-2026
- **Hosting:** GitHub Pages
- **Tech:** Static HTML/CSS/JS
- **Features:** Dedicated regularization landing page, eligibility CTA, countdown to deadline, FAQ, pricing, trust badges
- **Status:** ✅ Live

### 3. PH-Bot (Client Intake Bot) ← MAIN CODEBASE
- **Platform:** Telegram
- **Repo:** github.com/anacuero-bit/PH-Bot
- **Hosting:** Railway (auto-deploys from main branch)
- **Tech:** Python 3.11+, python-telegram-bot v20+ (async)
- **Current version:** v5.1.0 (`main.py`, ~2200 lines)
- **Status:** ✅ Live (but v5.0.1 deployed — v5.1.0 ready to deploy)

#### Bot Flow
```
/start → Country selection (9 countries) → 3 eligibility questions →
  IF eligible: Main Menu hub
  IF not eligible: Notify option + contact lawyer

Main Menu →
  📄 Upload docs (13 categories + OCR auto-classification)
  ❓ FAQ (17 entries + NLU free-text routing)
  💰 Pricing breakdown
  📞 Contact (human handoff queue)
  💳 Payments (Phase 2/3 when eligible)
```

#### Payment Model (FREE → €47 → €150 → €100 = €297 total)
| Phase | Price | Trigger | Psychology |
|-------|-------|---------|------------|
| Phase 1 — FREE | €0 | Start → eligibility + upload 3 docs | Zero friction, endowment effect |
| Phase 2 — Commitment | €47 | After 3+ docs uploaded | Sunk cost, "foot in the door" |
| Phase 3 — Processing | €150 | All docs verified | Loss aversion, invested too much to quit |
| Phase 4 — Filing | €100 | Submission to government | Finish line effect |
| Gov fees (external) | ~€55 | Paid by client directly | |

#### Key Technical Details
- **States:** ST_COUNTRY, ST_Q1_DATE, ST_Q2_TIME, ST_Q3_RECORD, ST_ELIGIBLE, ST_NOT_ELIGIBLE, ST_MAIN_MENU, ST_UPLOAD_SELECT, ST_UPLOAD_PHOTO, ST_FAQ_MENU, ST_PAY_PHASE2, ST_PAY_PHASE3, ST_CONTACT, ST_HUMAN_MSG, ST_SERVICE_INFO, ST_FULL_NAME
- **Callback prefixes:** `c_` country, `d_` date, `t_` time, `r_` record, `m_` menu, `dt_` doc type, `fq_` FAQ, `paid` payment confirm
- **OCR:** Pillow-based keyword matching (ENDESA, IBERDROLA, REVOLUT, N26, VODAFONE, RENFE, GLOVO, etc.)
- **NLU:** Regex + keyword intent detection for free-text → routes to FAQ or canned responses
- **Database:** In-memory dicts (users, cases, messages) — NO persistent DB yet
- **Admin commands:** /approve2, /approve3, /reply TID msg, /stats, /broadcast msg

#### ENV VARS (PH-Bot)
```
TELEGRAM_BOT_TOKEN    (required)
ADMIN_CHAT_IDS        comma-separated Telegram user IDs
SUPPORT_PHONE         WhatsApp number
BIZUM_PHONE           Bizum number
BANK_IBAN             Bank transfer IBAN
STRIPE_LINK_P2        Stripe checkout URL for Phase 2 (€47)
STRIPE_LINK_P3        Stripe checkout URL for Phase 3 (€150)
ANTHROPIC_API_KEY     (optional, for AI escalation)
```

#### Deploy
```bash
git add -A && git commit -m "description" && git push origin main
# Railway auto-deploys from main
```

### 4. Content Bot (News Ticker Manager)
- **Repo:** TBD (needs new repo)
- **Hosting:** Not yet deployed (ready for Railway)
- **Tech:** Python, uses Claude API + GitHub API
- **Purpose:** Admin Telegram bot that manages the news ticker on PH-Site. Admin sends content → bot uses Claude to format → pushes to content.json in PH-Site repo via GitHub API
- **Status:** 📦 Ready, not deployed

#### ENV VARS (Content Bot)
```
TELEGRAM_TOKEN        From @BotFather
CLAUDE_API_KEY        From console.anthropic.com
GITHUB_TOKEN          Personal access token with 'repo' scope
GITHUB_REPO           anacuero-bit/PH-Site
ADMIN_CHAT_IDS        Telegram user ID
```

---

## COMPETITOR LANDSCAPE

**Main competitor:** regularizacionmasiva.es (Inmaculada Moncho)
- Price: €389 (€39 viability + €350)
- Stripe live, professional Next.js site, active blog/SEO, TikTok content
- BUT: manual review, doesn't scale, no AI automation

**Market average:** ~€370 for full service. Top 10 competitors all manual, 300-450€ range.
**Our advantages:** Automation, lower price (€297), 24/7 bot, OCR validation, scalable to 5000+ users.
**Their advantages:** Polished websites, live payments, active content/SEO.

---

## CONTENT PIPELINE (Ready but not published/filmed)

| Asset | Status | Notes |
|-------|--------|-------|
| 8 TikTok scripts | Written, not filmed | In project knowledge |
| 10 Instagram carousel concepts | Written, not designed | In project knowledge |
| 3 SEO blog articles | Written, not published | In project knowledge |
| 27 WhatsApp broadcast templates | Written, not sent | In project knowledge |
| Ad copy (FB/IG/TikTok/Google) | ⚠️ Has old pricing | AD-COPY.md needs €99+€199 → FREE+€47+€150+€100 |
| Email sequences | ⚠️ Has old pricing | EMAIL-SEQUENCES.md needs same fix |
| Website copy | ⚠️ Has old €336.28 | WEBSITE-COPY.md needs → €297 |
| Bot conversation flows | ✅ Updated | 01-BOT-FLOWS-UPDATED.md |
| Brand voice guide | ✅ Current | BRAND-VOICE-CONVERSATION-GUIDE.md |

---

## MARKETING STRATEGY (Not yet executed)

**"Cadena de Papeles" referral system:** Unique code per user. 3 friends sign up = €50 off for all. Physical stickers + digital sharing. NOT BUILT YET.

**Digital channels:**
- TikTok/Reels: Demo videos ("upload docs in 2 min"), testimonials, myth-busting
- FB/IG ads: Targeted at Latinos in Spain
- WhatsApp blasts: 27 templates ready
- Blog/SEO: 3 articles ready to publish

**Physical channels:**
- QR flyers in areperas, cevicherías, salons, butchers
- Pop-ups in plazas (coffee, music)
- Delivery crew kickbacks (€20 cash per referral)

**Community targeting by nationality:**
- Colombians (35%): Areperas, salsa nights, FB groups ("Colombianos en Madrid")
- Peruvians: Cevicherías, bakeries in Usera
- Hondurans: Tortillerías, soccer fields in Vallecas, WhatsApp family chains

---

## WHAT'S DONE vs TODO

### ✅ Completed
- Both websites live (PH-Site + tuspapeles2026.es)
- Client Bot v5.1.0 coded with all audit fixes (fq_ bug, dynamic progress bar, PDF uploads, 13 doc categories, expanded OCR, 5 new FAQs, Stripe env var support, improved Phase 2 trigger, name collection, social proof counter)
- Vulnerability clause in bot FAQ
- 40+ document types in residency FAQ
- Bot flowchart (bot-flowchart.mermaid)
- Full audit + conversion strategy (AUDIT-AND-CONVERSION-STRATEGY.md)
- All marketing content written (not published)

### 🔴 Code TODO (priority order — for Claude Code)
1. Deploy v5.1.0 → rename main_v5_1_0.py to main.py, push
2. Stripe integration — set up account, get checkout links (CRITICAL — 2-3x conversion lift)
3. Persistent database — PostgreSQL or SQLite (data lost on every restart)
4. Scheduled re-engagement reminders — 24h/72h/1wk after dropoff
5. Country-specific document checklists after registration
6. Antecedentes penales upsell flow — purchase button after Phase 2 review
7. Phase 4 payment flow — m_pay4 button + handler (needed by April)
8. Referral system backend — unique codes, tracking, discount application

### 🟡 Content/Strategy TODO (for Claude.ai)
1. Fix pricing in AD-COPY.md, WEBSITE-COPY.md, EMAIL-SEQUENCES.md
2. Publish blog articles to live sites
3. Design referral system details
4. Plan TikTok filming
5. SEO optimization
6. Deploy Content Bot

### 💰 Revenue Projections (conservative)
- 10,000 eligible → 6,000 upload → 2,400 pay P2 → 1,920 pay P3 → 1,728 pay P4
- Service: €573,600 + Antecedentes add-on: €75,000 = **~€650,000**

---

## CODE CONVENTIONS
- All user-facing text in **Spanish**
- Professional lawyer tone — formal but warm
- ParseMode.MARKDOWN for Telegram messages
- InlineKeyboardButton for all interactions (no ReplyKeyboard)
- FAQ entries in FAQ dict, accessed by key
- NLU intents in INTENT_PATTERNS dict
- No test suite yet — test manually via Telegram
