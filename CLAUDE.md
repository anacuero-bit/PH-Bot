 PH-Bot — Project Context

## WHAT THIS IS
Telegram bot for tuspapeles2026 — client intake and case management for Spain's 2026 extraordinary regularization process. Backed by Pombo & Horowitz law firm.

## CURRENT STATUS
- Pre-launch waitlist phase
- `BOE_PUBLISHED = False` — NO payments until BOE publishes (expected March 2026)
- All payment flows redirect to waitlist wall
- Solicitations open April 1 - June 30, 2026

## PRICING (FINAL — DO NOT CHANGE)
| Phase | Price | Deliverable |
|-------|-------|-------------|
| Phase 1 | FREE | Eligibility check + document upload |
| Phase 2 | €29 | Evaluación (case overview, probability assessment) |
| Phase 3 | €89 | Expediente (forms filled, docs organized — NO memoria) |
| Phase 4 | €129 | Memoria legal + presentación + seguimiento + recurso |
| **Total phased** | **€247** | |
| **Prepay** | **€199** | Same service, €48 savings |

## PHASE DELIVERABLES (IMPORTANT)
- **Phase 1:** Eligibility, doc upload (FREE)
- **Phase 2:** Evaluación — overview of case, probability assessment. **NO detailed how-to guide** (that would let them DIY)
- **Phase 3:** Expediente — forms completed, documents organized strategically. **NO memoria yet**
- **Phase 4:** Memoria legal personalizada (THE key deliverable that justifies the service) + submission + tracking + appeal if needed

## REFERRAL SYSTEM — Cónsul/Embajador Tiers

### OLD SYSTEM (REMOVED)
- ❌ €25 credits per referral
- ❌ Credit accumulation toward payments
- ❌ 10% cash after cap
- ❌ Credits applied to any phase

### NEW SYSTEM

**Constants:**
```python
CONSUL_THRESHOLD = 3           # Friends who paid Phase 2
EMBAJADOR_THRESHOLD = 10       # Friends who paid Phase 2
EMBAJADOR_FULL_PAY_THRESHOLD = 5  # OR 5 friends who paid full
FRIEND_DISCOUNT = 25           # €25 off Phase 4 for referred friend
```

**Cónsul Status:**
- Requirement: 3 friends pay Phase 2 (€29) + YOU paid in full
- OR: Pay €199 prepay (instant Cónsul)
- Benefits (service perks, not payment advantages):
  - Procesamiento prioritario
  - Respuesta urgente a requerimientos
  - Revisión extra de documentos
  - WhatsApp directo con el equipo

**Embajador Status:**
- Requirement: 10 friends pay Phase 2 + YOU paid in full
- OR: 5 friends pay full (€199 or €247) + YOU paid in full
- Benefits: All Cónsul benefits PLUS:
  - Gestor de caso dedicado
  - Aparición en nuestra web
  - Consulta gratuita para futuras gestiones
  - Certificado de Embajador
  - Descuento de por vida en servicios legales

**Friend Benefit:**
- €25 off **Phase 4 only** (€129 → €104)
- Applied automatically when friend reaches Phase 4
- Every referred friend gets this, regardless of referrer's tier status

**Key Rules:**
- Tier status is EARNED but LOCKED until referrer pays in full
- Progress is tracked during waitlist phase
- Benefits activate only after referrer completes payment
- €199 prepay = instant Cónsul (no referrals needed)
- One code per user, cannot use own code
- "Paid Phase 2" means completed the €29 payment (since Phase 1 is free)

### Database Schema
```sql
-- Tier tracking columns
referral_tier VARCHAR(20) DEFAULT NULL  -- 'consul', 'embajador', or NULL
referral_tier_locked INTEGER DEFAULT 1  -- 1=locked, 0=active
referrals_phase2_count INTEGER DEFAULT 0
referrals_full_count INTEGER DEFAULT 0
```

## WAITLIST COUNTER
- Base: 3,127 (as of Feb 15, 2026)
- Growth: 2-8 per hour (seeded random for consistency)
- Function: `get_waitlist_count()`
- Display: Exact number, not "más de"

## TONE
- Professional law firm voice
- Minimal emojis (only in section headers, not in prose)
- Trust through competence, not hype
- No "Auditoría" — use "Evaluación"
- No sales pressure, just clear information

## CRITICAL RULES

### Version Control
**NEVER rewrite bot from scratch.** Always:
1. Read deployed main.py from GitHub first
2. Patch changes on top
3. Maintain changelog in file header
4. Increment version number

### Payment Gates
Until `BOE_PUBLISHED = True`:
- All payment callbacks → waitlist wall
- Show "proceso aún no oficial"
- Encourage document upload + referrals

## FILES IN THIS REPO
| File | Purpose |
|------|---------|
| `main.py` | Bot code (single file) |
| `CLAUDE.md` | This context file |
| `requirements.txt` | Python dependencies |
| `Procfile` | Railway deployment |
| `nixpacks.toml` | Tesseract OCR config |
| `runtime.txt` | Python version |

## DO NOT MODIFY
- Pricing constants (already correct)
- Waitlist wall logic
- Document upload flow
- Phase questionnaires
- Admin commands
- OCR/Claude Vision integration
