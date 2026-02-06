# Master Reference: Pricing, Branding & Alignment

## Firm Branding

| Element | Value |
|---------|-------|
| **Firm Name** | Pombo, Horowitz & Espinosa |
| **Abbreviation** | PHE |
| **Firm Site** | pombohorowitz.com |
| **Product Site** | tuspapeles2026.es |
| **Product Name** | tuspapeles2026 |
| **Relationship** | "tuspapeles2026 es un servicio de Pombo, Horowitz & Espinosa" |

---

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Navy | `#1E3A5F` | Primary backgrounds, headers, CTAs |
| Navy Light | `#2C4A6E` | Hover states, secondary elements |
| Gold | `#E8D4A8` | Accent, CTAs, highlights |
| Gold Dark | `#D4C494` | Hover states for gold elements |
| Charcoal | `#4D4D4D` | Body text |
| Gray Light | `#E8E8E8` | Backgrounds, borders |
| White | `#FFFFFF` | Backgrounds |
| Black | `#1A1A1A` | Headings |

---

## Pricing Structure (FINAL)

| Phase | Name | Price | Cumulative |
|-------|------|-------|------------|
| 1 | Verificación | **FREE** | €0 |
| 2 | Preparación | **€39** | €39 |
| 3 | Revisión Legal | **€150** | €189 |
| 4 | Presentación | **€110** | €299 |

**Total: €299**

**Anchor copy:** "Todo por menos de 300 euros"

### Add-on Services
| Service | Price |
|---------|-------|
| Antecedentes penales (gestión + apostilla) | €75 |

---

## BOT UPDATE REQUIRED

The bot (`main_v5_1_0.py`) currently has **wrong pricing**:
- Phase 2: €47 → should be **€39**
- Phase 4: €100 → should be **€110**
- Total: €297 → should be **€299**

### Lines to update in bot:

```python
# Search for these values and replace:

# Phase 2 price
"€47" → "€39"
"47€" → "39€"

# Phase 4 price  
"€100" → "€110"
"100€" → "110€"

# Total
"€297" → "€299"
"297€" → "299€"
"menos de 300" → keep as is (still works)
```

### Stripe Price IDs
When creating Stripe products, use these exact amounts:
- `price_phase_2`: €39.00 EUR
- `price_phase_3`: €150.00 EUR
- `price_phase_4`: €110.00 EUR
- `price_antecedentes`: €75.00 EUR

---

## Typography

| Type | Font | Weight |
|------|------|--------|
| Headings | Playfair Display | 600-700 |
| Body | Inter | 400 |
| UI/Labels | Inter | 500-600 |
| Legal/Citations | JetBrains Mono | 400 |

---

## Trust Copy

### 25 Years Badge
- "25 años de experiencia en inmigración"
- "Desde 2001"

### Case Count
- "+10,000 casos resueltos"
- "Miles de familias regularizadas"

### 2005 Reference
- "Participamos en la regularización de 2005"
- "Nuestro equipo incluye abogados que trabajaron en el proceso de 2005"

### Credentials
- "Abogados colegiados"
- "Colegio de Abogados de Madrid"

---

## Urgency Copy

### Slot Counter
- "X de 1,000 plazas disponibles"
- Warning (<100): "¡Últimas plazas!"

### Countdown
- "Faltan X días para la fecha límite"

### Personal Reservation
- "Tu plaza #X está reservada por 7 días"
- "Quedan X días, X horas para asegurar tu plaza"

### Social Proof
- "X personas se inscribieron esta semana"
- "X personas completaron este paso esta semana"

---

## Platform Alignment

| Feature | Website | Telegram Bot |
|---------|---------|--------------|
| Eligibility check | ✓ | ✓ |
| Account creation | ✓ (Supabase Auth) | ✓ (in-memory DB) |
| Document upload | ✓ (Supabase Storage) | ✓ (Telegram files) |
| Payment | ✓ (Stripe Checkout) | ✓ (Stripe link) |
| Dashboard | ✓ (full UI) | ✓ (text-based) |
| Push notifications | ✗ | ✓ (Telegram native) |
| Slot counter | ✓ (real-time) | ✓ (on-demand) |

**User choice:** At eligibility result, user picks their preferred platform. They can switch later but would need to re-enter some info (Phase 1 only - shared DB comes in Phase 2 scaling).

---

## File Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Bot versions | `main_v{major}_{minor}_{patch}.py` | `main_v5_2_0.py` |
| Specs | `CLAUDE-CODE-SPEC-{project}.md` | `CLAUDE-CODE-SPEC-tuspapeles2026.md` |
| Knowledge base | `{TOPIC}-{TYPE}.md` | `BOT-GROK-UPDATES.md` |

---

## Deployment Targets

| Project | Platform | Repo |
|---------|----------|------|
| Telegram Bot | Railway | PH-Bot |
| pombohorowitz.com | Vercel | (create: phe-site) |
| tuspapeles2026.es | Vercel | (create: tuspapeles-app) |

---

## Immediate Claude Code Tasks

### Priority 1: Bot Pricing Fix
1. Update pricing in `main_v5_1_0.py`
2. Deploy to Railway
3. Test payment flow

### Priority 2: tuspapeles2026.es MVP
1. Landing page
2. Eligibility flow
3. Account creation
4. Basic dashboard

### Priority 3: pombohorowitz.com
1. Homepage
2. Regularization page (with tuspapeles CTA)
3. Blog (3 articles)
