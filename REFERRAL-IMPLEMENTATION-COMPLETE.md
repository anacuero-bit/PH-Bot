# REFERRAL SYSTEM — COMPLETE IMPLEMENTATION SPEC

**Version:** 1.0
**Status:** Ready for implementation
**Created:** February 2026

---

## TABLE OF CONTENTS

1. [System Overview](#1-system-overview)
2. [Database Schema](#2-database-schema)
3. [Bot Implementation](#3-bot-implementation)
4. [Website Implementation](#4-website-implementation)
5. [Data Flow](#5-data-flow)
6. [Testing Checklist](#6-testing-checklist)
7. [Implementation Order](#7-implementation-order)

---

## 1. SYSTEM OVERVIEW

### 1.1 Business Rules

| Rule | Detail |
|------|--------|
| Code format | `FIRSTNAME-XXXX` (4 random alphanumeric) |
| Friend discount | €25 off first payment |
| Referrer credit | €25 per friend who pays |
| Credit eligibility | Referrer must have paid Phase 2 (€39) |
| Credit cap | €299 total |
| Cash eligibility | Referrer must have paid full €299 |
| Cash amount | 10% of each friend's payment |
| Cash timing | 30 days after friend's payment |
| Cash minimum | €30 accumulated |
| Cash cap | €1,000/year |

### 1.2 User States

```
                    ┌─────────────────────┐
                    │   NEW USER          │
                    │   - No code yet     │
                    │   - Can be referred │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   ELIGIBLE          │
                    │   - Has code        │
                    │   - Can share       │
                    │   - Cannot earn yet │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PHASE 2 PAID      │
                    │   - Earns credits   │
                    │   - Max €299        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   FULLY PAID (€299) │
                    │   - Earns 10% cash  │
                    │   - No credit cap   │
                    └─────────────────────┘
```

---

## 2. DATABASE SCHEMA

### 2.1 Modify `users` Table

```sql
-- Add these columns to existing users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code VARCHAR(20) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by_code VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by_user_id BIGINT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_credits_earned DECIMAL(10,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_credits_used DECIMAL(10,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_cash_earned DECIMAL(10,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_cash_paid DECIMAL(10,2) DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS friend_discount_applied BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS friend_discount_amount DECIMAL(10,2) DEFAULT 0;

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);
CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users(referred_by_code);
```

### 2.2 Create `referrals` Table

```sql
CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    
    -- Relationship
    referrer_user_id BIGINT NOT NULL,
    referrer_code VARCHAR(20) NOT NULL,
    referred_user_id BIGINT NOT NULL,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'registered',
    -- Values: 'registered', 'paid_phase2', 'paid_full', 'completed'
    
    -- Credit tracking (for referrer)
    credit_amount DECIMAL(10,2) DEFAULT 0,
    credit_awarded_at TIMESTAMP,
    
    -- Cash tracking (for referrer, after they're fully paid)
    cash_amount DECIMAL(10,2) DEFAULT 0,
    cash_available_at TIMESTAMP,
    cash_paid_at TIMESTAMP,
    
    -- Friend's payments (to calculate 10%)
    friend_total_paid DECIMAL(10,2) DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_payment_at TIMESTAMP,
    
    -- Fraud prevention
    referred_ip VARCHAR(45),
    referred_device_fingerprint VARCHAR(64),
    
    -- Constraints
    UNIQUE(referrer_user_id, referred_user_id)
);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referrer_code);
```

### 2.3 Create `referral_events` Table (Audit Log)

```sql
CREATE TABLE IF NOT EXISTS referral_events (
    id SERIAL PRIMARY KEY,
    referral_id INTEGER REFERENCES referrals(id),
    user_id BIGINT NOT NULL,
    
    -- Event details
    event_type VARCHAR(30) NOT NULL,
    -- Values: 'code_generated', 'code_used', 'credit_earned', 'credit_applied',
    --         'cash_earned', 'cash_paid', 'credit_clawed_back'
    
    amount DECIMAL(10,2),
    description TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_referral_events_user ON referral_events(user_id);
```

### 2.4 Database Helper Functions (Python)

```python
# Add to main.py

def generate_referral_code(first_name: str) -> str:
    """Generate unique referral code: NAME-XXXX"""
    import random
    import string
    
    # Clean name: uppercase, remove accents, max 10 chars
    clean_name = first_name.upper()[:10]
    clean_name = ''.join(c for c in clean_name if c.isalpha())
    
    if not clean_name:
        clean_name = "USER"
    
    # Generate random suffix
    for _ in range(10):  # Try up to 10 times for unique code
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code = f"{clean_name}-{suffix}"
        
        # Check uniqueness
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE referral_code = %s", (code,))
        if not cur.fetchone():
            conn.close()
            return code
        conn.close()
    
    # Fallback: add timestamp
    import time
    return f"{clean_name}-{int(time.time()) % 10000}"


def validate_referral_code(code: str) -> dict:
    """
    Validate referral code exists and return referrer info.
    Returns: {'valid': bool, 'referrer_id': int, 'referrer_name': str} or {'valid': False, 'error': str}
    """
    if not code or len(code) < 3:
        return {'valid': False, 'error': 'invalid_format'}
    
    code = code.upper().strip()
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT telegram_id, first_name FROM users WHERE referral_code = %s",
        (code,)
    )
    row = cur.fetchone()
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
    """Store referral relationship when new user enters a code."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Update user record
        cur.execute("""
            UPDATE users 
            SET referred_by_code = %s, 
                referred_by_user_id = %s,
                friend_discount_amount = 25.00
            WHERE telegram_id = %s AND referred_by_code IS NULL
        """, (code, referrer_id, user_id))
        
        # Create referral record
        cur.execute("""
            INSERT INTO referrals (referrer_user_id, referrer_code, referred_user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (referrer_user_id, referred_user_id) DO NOTHING
        """, (referrer_id, code, user_id))
        
        # Log event
        cur.execute("""
            INSERT INTO referral_events (user_id, event_type, description)
            VALUES (%s, 'code_used', %s)
        """, (user_id, f"Used code {code} from user {referrer_id}"))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logging.error(f"Error applying referral code: {e}")
        return False
    finally:
        conn.close()


def get_user_referral_stats(user_id: int) -> dict:
    """Get referral statistics for a user."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get user's referral info
    cur.execute("""
        SELECT referral_code, referral_count, 
               referral_credits_earned, referral_credits_used,
               referral_cash_earned, referral_cash_paid,
               phase2_paid, total_paid
        FROM users WHERE telegram_id = %s
    """, (user_id,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return None
    
    # Get referral details
    cur.execute("""
        SELECT r.referred_user_id, u.first_name, r.status, r.credit_amount, r.created_at
        FROM referrals r
        JOIN users u ON r.referred_user_id = u.telegram_id
        WHERE r.referrer_user_id = %s
        ORDER BY r.created_at DESC
        LIMIT 10
    """, (user_id,))
    referrals = cur.fetchall()
    
    conn.close()
    
    credits_available = (user[2] or 0) - (user[3] or 0)
    
    return {
        'code': user[0],
        'count': user[1] or 0,
        'credits_earned': user[2] or 0,
        'credits_used': user[3] or 0,
        'credits_available': max(0, credits_available),
        'cash_earned': user[4] or 0,
        'cash_paid': user[5] or 0,
        'cash_available': (user[4] or 0) - (user[5] or 0),
        'can_earn_credits': user[6] == 1,  # phase2_paid
        'can_earn_cash': (user[7] or 0) >= 299,  # total_paid
        'referrals': [
            {
                'user_id': r[0],
                'name': r[1],
                'status': r[2],
                'credit': r[3],
                'date': r[4]
            }
            for r in referrals
        ]
    }


def credit_referrer_for_payment(referred_user_id: int, payment_amount: float) -> dict:
    """
    Called when a referred user makes a payment.
    Credits the referrer appropriately.
    Returns: {'credited': bool, 'amount': float, 'type': 'credit'|'cash'}
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get referral relationship
        cur.execute("""
            SELECT r.referrer_user_id, r.referrer_code, r.credit_amount,
                   u.phase2_paid, u.total_paid, u.referral_credits_earned
            FROM referrals r
            JOIN users u ON r.referrer_user_id = u.telegram_id
            WHERE r.referred_user_id = %s
        """, (referred_user_id,))
        
        row = cur.fetchone()
        if not row:
            conn.close()
            return {'credited': False, 'reason': 'no_referrer'}
        
        referrer_id = row[0]
        referrer_code = row[1]
        existing_credit = row[2] or 0
        referrer_phase2_paid = row[3] == 1
        referrer_total_paid = row[4] or 0
        referrer_credits_earned = row[5] or 0
        
        # Referrer hasn't paid Phase 2 yet - no rewards
        if not referrer_phase2_paid:
            conn.close()
            return {'credited': False, 'reason': 'referrer_not_eligible'}
        
        # Determine reward type
        if referrer_total_paid >= 299:
            # Cash mode: 10% of payment
            cash_amount = round(payment_amount * 0.10, 2)
            available_at = datetime.now() + timedelta(days=30)
            
            cur.execute("""
                UPDATE referrals 
                SET cash_amount = cash_amount + %s,
                    cash_available_at = %s,
                    friend_total_paid = friend_total_paid + %s
                WHERE referred_user_id = %s
            """, (cash_amount, available_at, payment_amount, referred_user_id))
            
            cur.execute("""
                UPDATE users 
                SET referral_cash_earned = referral_cash_earned + %s
                WHERE telegram_id = %s
            """, (cash_amount, referrer_id))
            
            cur.execute("""
                INSERT INTO referral_events (referral_id, user_id, event_type, amount, description)
                SELECT id, %s, 'cash_earned', %s, %s
                FROM referrals WHERE referred_user_id = %s
            """, (referrer_id, cash_amount, f"10% of €{payment_amount} payment", referred_user_id))
            
            conn.commit()
            conn.close()
            return {'credited': True, 'amount': cash_amount, 'type': 'cash', 'referrer_id': referrer_id}
        
        else:
            # Credit mode: €25 per first payment (one-time)
            if existing_credit > 0:
                # Already credited for this referral
                conn.close()
                return {'credited': False, 'reason': 'already_credited'}
            
            # Check credit cap
            if referrer_credits_earned >= 299:
                conn.close()
                return {'credited': False, 'reason': 'credit_cap_reached'}
            
            credit_amount = min(25, 299 - referrer_credits_earned)
            
            cur.execute("""
                UPDATE referrals 
                SET credit_amount = %s,
                    credit_awarded_at = CURRENT_TIMESTAMP,
                    status = 'paid_phase2',
                    first_payment_at = CURRENT_TIMESTAMP,
                    friend_total_paid = %s
                WHERE referred_user_id = %s
            """, (credit_amount, payment_amount, referred_user_id))
            
            cur.execute("""
                UPDATE users 
                SET referral_credits_earned = referral_credits_earned + %s,
                    referral_count = referral_count + 1
                WHERE telegram_id = %s
            """, (credit_amount, referrer_id))
            
            cur.execute("""
                INSERT INTO referral_events (referral_id, user_id, event_type, amount, description)
                SELECT id, %s, 'credit_earned', %s, %s
                FROM referrals WHERE referred_user_id = %s
            """, (referrer_id, credit_amount, f"Friend made first payment", referred_user_id))
            
            conn.commit()
            conn.close()
            return {'credited': True, 'amount': credit_amount, 'type': 'credit', 'referrer_id': referrer_id}
            
    except Exception as e:
        conn.rollback()
        logging.error(f"Error crediting referrer: {e}")
        return {'credited': False, 'reason': 'error'}
    finally:
        if conn:
            conn.close()


def apply_credits_to_payment(user_id: int, original_price: float) -> dict:
    """
    Calculate price after applying referral credits.
    Returns: {'original': float, 'credits_applied': float, 'final_price': float, 'credits_remaining': float}
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT referral_credits_earned, referral_credits_used
        FROM users WHERE telegram_id = %s
    """, (user_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return {
            'original': original_price,
            'credits_applied': 0,
            'final_price': original_price,
            'credits_remaining': 0
        }
    
    credits_earned = row[0] or 0
    credits_used = row[1] or 0
    credits_available = credits_earned - credits_used
    
    if credits_available <= 0:
        return {
            'original': original_price,
            'credits_applied': 0,
            'final_price': original_price,
            'credits_remaining': 0
        }
    
    credits_to_apply = min(credits_available, original_price)
    final_price = original_price - credits_to_apply
    
    return {
        'original': original_price,
        'credits_applied': credits_to_apply,
        'final_price': final_price,
        'credits_remaining': credits_available - credits_to_apply
    }


def mark_credits_used(user_id: int, amount: float) -> bool:
    """Mark credits as used after successful payment."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE users 
            SET referral_credits_used = referral_credits_used + %s
            WHERE telegram_id = %s
        """, (amount, user_id))
        
        cur.execute("""
            INSERT INTO referral_events (user_id, event_type, amount, description)
            VALUES (%s, 'credit_applied', %s, 'Applied to payment')
        """, (user_id, amount))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logging.error(f"Error marking credits used: {e}")
        return False
    finally:
        conn.close()


def get_friend_discount(user_id: int) -> dict:
    """Check if user has a friend discount to apply."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT referred_by_code, referred_by_user_id, 
               friend_discount_applied, friend_discount_amount,
               u2.first_name as referrer_name
        FROM users u1
        LEFT JOIN users u2 ON u1.referred_by_user_id = u2.telegram_id
        WHERE u1.telegram_id = %s
    """, (user_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if not row or not row[0] or row[2]:  # No referrer or already applied
        return {'has_discount': False}
    
    return {
        'has_discount': True,
        'amount': row[3] or 25,
        'referrer_name': row[4] or 'un amigo'
    }


def mark_friend_discount_used(user_id: int) -> bool:
    """Mark friend discount as applied."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE users 
            SET friend_discount_applied = TRUE
            WHERE telegram_id = %s
        """, (user_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()
```

---

## 3. BOT IMPLEMENTATION

### 3.1 New Constants

```python
# Add to constants section of main.py

# Referral messages
REFERRAL_CODE_PROMPT = """
¿Alguien te recomendó tuspapeles2026?

Si un amigo te compartió su código, escríbelo ahora y recibirás *€25 de descuento*.

Ejemplo: `MARIA-7K2P`
"""

REFERRAL_CODE_SUCCESS = """
✅ *¡Código aplicado!*

{referrer_name} te ha regalado *€25 de descuento* que se aplicará a tu primer pago.
"""

REFERRAL_CODE_INVALID = """
❌ Código no encontrado.

Verifica que esté bien escrito (ejemplo: `MARIA-7K2P`) o continúa sin código.
"""

REFERRAL_CODE_GENERATED = """
🎉 *Tu código personal:* `{code}`

━━━━━━━━━━━━━━━━━━

📣 *COMPARTE Y GANA*

Cuando pagues tu primera fase (€39):
• Ganarás *€25* por cada amigo que pague
• Máximo *€299* = ¡tu servicio GRATIS!

Tu amigo recibe *€25 de descuento*.
"""

REFERRAL_SHARE_TEXT = """¡Hola! Acabo de verificar que califico para la regularización 2026 en España.

Si llevas tiempo aquí sin papeles, verifica gratis si calificas:
👉 tuspapeles2026.es/r/{code}

Usa mi código {code} y te descuentan €25.

Es el nuevo decreto — no necesitas contrato de trabajo. ¡Aprovecha!"""

REFERRAL_DASHBOARD = """
👥 *TUS REFERIDOS*

Tu código: `{code}`
🔗 `tuspapeles2026.es/r/{code}`

━━━━━━━━━━━━━━━━━━
📊 *ESTADO*

Referidos que han pagado: {count}
💰 Crédito ganado: €{earned}
💰 Crédito usado: €{used}
💰 *Crédito disponible: €{available}*

{status_message}

━━━━━━━━━━━━━━━━━━
{referral_list}
"""

REFERRAL_NOTIFY_CREDIT = """
🎉 *¡Tu amigo {friend_name} acaba de pagar!*

Has ganado: *+€{amount} crédito*

Tu crédito total: *€{total}*
Referidos que han pagado: {count}

💡 {tip}
"""

REFERRAL_NOTIFY_CASH = """
💸 *¡Ganancia en efectivo!*

Tu amigo {friend_name} pagó €{payment}.
Has ganado: *€{amount}* (10%)

Disponible para retiro en 30 días.
Saldo pendiente: *€{total}*
"""
```

### 3.2 New Conversation State

```python
# Add to states
ST_ENTER_REFERRAL_CODE = 25
```

### 3.3 Modified Registration Flow

```python
# In cmd_start, after country selection, before eligibility questions:

async def ask_referral_code(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask user if they have a referral code."""
    
    # Check if coming from website with code
    start_param = ctx.args[0] if ctx.args else None
    
    if start_param and len(start_param) > 3:
        # Validate the code
        result = validate_referral_code(start_param)
        if result['valid']:
            # Auto-apply the code
            user = get_user(update.effective_user.id)
            if user and not user.get('referred_by_code'):
                apply_referral_code_to_user(
                    update.effective_user.id,
                    result['code'],
                    result['referrer_id']
                )
                await update.message.reply_text(
                    REFERRAL_CODE_SUCCESS.format(referrer_name=result['referrer_name']),
                    parse_mode="Markdown"
                )
            # Continue to eligibility
            return await start_eligibility(update, ctx)
    
    # No auto-code, ask user
    keyboard = [[InlineKeyboardButton("No tengo código", callback_data="ref_none")]]
    
    await update.message.reply_text(
        REFERRAL_CODE_PROMPT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
    return ST_ENTER_REFERRAL_CODE


async def handle_referral_code_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Process user-entered referral code."""
    
    code = update.message.text.upper().strip()
    user_id = update.effective_user.id
    
    # Can't use own code
    user = get_user(user_id)
    if user and user.get('referral_code') == code:
        await update.message.reply_text(
            "❌ No puedes usar tu propio código.",
            parse_mode="Markdown"
        )
        return ST_ENTER_REFERRAL_CODE
    
    result = validate_referral_code(code)
    
    if result['valid']:
        # Can't refer yourself
        if result['referrer_id'] == user_id:
            await update.message.reply_text(
                "❌ No puedes usar tu propio código.",
                parse_mode="Markdown"
            )
            return ST_ENTER_REFERRAL_CODE
        
        apply_referral_code_to_user(user_id, result['code'], result['referrer_id'])
        
        await update.message.reply_text(
            REFERRAL_CODE_SUCCESS.format(referrer_name=result['referrer_name']),
            parse_mode="Markdown"
        )
        return await start_eligibility(update, ctx)
    
    else:
        keyboard = [
            [InlineKeyboardButton("🔄 Intentar de nuevo", callback_data="ref_retry")],
            [InlineKeyboardButton("➡️ Continuar sin código", callback_data="ref_none")]
        ]
        await update.message.reply_text(
            REFERRAL_CODE_INVALID,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return ST_ENTER_REFERRAL_CODE


async def handle_referral_callbacks(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle referral-related button presses."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "ref_none":
        # Continue without code
        return await start_eligibility(update, ctx)
    
    elif data == "ref_retry":
        await query.edit_message_text(
            REFERRAL_CODE_PROMPT,
            parse_mode="Markdown"
        )
        return ST_ENTER_REFERRAL_CODE
    
    elif data == "ref_share_wa":
        # Generate WhatsApp share link
        user = get_user(update.effective_user.id)
        code = user.get('referral_code', '')
        share_text = REFERRAL_SHARE_TEXT.format(code=code)
        wa_url = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
        
        await query.answer(url=wa_url)
        return ctx.user_data.get('state', ST_MAIN_MENU)
    
    elif data == "ref_copy":
        user = get_user(update.effective_user.id)
        code = user.get('referral_code', '')
        await query.answer(f"Código: {code}", show_alert=True)
        return ctx.user_data.get('state', ST_MAIN_MENU)
```

### 3.4 Modified Eligibility Result (Show Code)

```python
async def show_eligibility_result_positive(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show positive eligibility result with referral code."""
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    # Generate referral code if not exists
    if not user.get('referral_code'):
        code = generate_referral_code(user.get('first_name', 'USER'))
        update_user(user_id, referral_code=code)
        
        # Log event
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO referral_events (user_id, event_type, description)
            VALUES (%s, 'code_generated', %s)
        """, (user_id, f"Generated code: {code}"))
        conn.commit()
        conn.close()
    else:
        code = user['referral_code']
    
    # Build share URL
    import urllib.parse
    share_text = REFERRAL_SHARE_TEXT.format(code=code)
    wa_url = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
    
    keyboard = [
        [InlineKeyboardButton("📲 Compartir por WhatsApp", url=wa_url)],
        [InlineKeyboardButton("📋 Copiar enlace", callback_data="ref_copy")],
        [InlineKeyboardButton("➡️ Continuar", callback_data="m_menu")]
    ]
    
    text = (
        "✅ *¡Cumples los requisitos básicos!*\n\n"
        f"Tu plaza ha sido reservada.\n\n"
        + REFERRAL_CODE_GENERATED.format(code=code)
    )
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
    return ST_MAIN_MENU
```

### 3.5 Modified Payment Flow

```python
async def show_payment_screen(update: Update, ctx: ContextTypes.DEFAULT_TYPE, phase: int) -> int:
    """Show payment screen with discounts applied."""
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    # Base prices
    prices = {2: 39, 3: 150, 4: 110}
    base_price = prices.get(phase, 0)
    
    discounts = []
    final_price = base_price
    
    # Check friend discount (€25 off first payment)
    if phase == 2:  # Only applies to first payment
        friend_discount = get_friend_discount(user_id)
        if friend_discount['has_discount']:
            discount_amount = min(friend_discount['amount'], final_price)
            final_price -= discount_amount
            discounts.append(f"Descuento de {friend_discount['referrer_name']}: -€{discount_amount}")
    
    # Check referral credits
    credit_calc = apply_credits_to_payment(user_id, final_price)
    if credit_calc['credits_applied'] > 0:
        final_price = credit_calc['final_price']
        discounts.append(f"Tu crédito de referidos: -€{credit_calc['credits_applied']}")
    
    # Store for payment confirmation
    ctx.user_data['payment_phase'] = phase
    ctx.user_data['payment_original'] = base_price
    ctx.user_data['payment_final'] = final_price
    ctx.user_data['payment_credits_used'] = credit_calc['credits_applied']
    ctx.user_data['payment_friend_discount'] = friend_discount['has_discount'] if phase == 2 else False
    
    # Build message
    phase_names = {2: "Preparación", 3: "Revisión Legal", 4: "Presentación"}
    
    text = f"💳 *FASE {phase} — {phase_names[phase]}*\n\n"
    text += f"Precio: €{base_price}\n"
    
    for d in discounts:
        text += f"{d}\n"
    
    text += f"━━━━━━━━━━\n"
    
    if final_price == 0:
        text += f"*A pagar: €0* ✨\n\n"
        text += "¡Esta fase es GRATIS gracias a tus referidos!"
        if credit_calc['credits_remaining'] > 0:
            text += f"\nCrédito restante: €{credit_calc['credits_remaining']}"
        
        keyboard = [[InlineKeyboardButton("✅ Continuar gratis", callback_data=f"free_phase_{phase}")]]
    else:
        text += f"*A pagar: €{final_price}*\n"
        
        # Payment buttons
        keyboard = [
            [InlineKeyboardButton(f"💳 Pagar €{final_price}", url=get_stripe_link(phase, final_price))],
            [InlineKeyboardButton("📱 Pagar con Bizum", callback_data=f"bizum_{phase}")],
            [InlineKeyboardButton("🔙 Volver", callback_data="m_menu")]
        ]
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
    return ST_PAYMENT


async def confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Called when payment is confirmed. Credits referrer."""
    
    user_id = update.effective_user.id
    phase = ctx.user_data.get('payment_phase')
    credits_used = ctx.user_data.get('payment_credits_used', 0)
    friend_discount = ctx.user_data.get('payment_friend_discount', False)
    payment_amount = ctx.user_data.get('payment_final', 0)
    
    # Mark credits as used
    if credits_used > 0:
        mark_credits_used(user_id, credits_used)
    
    # Mark friend discount as used
    if friend_discount:
        mark_friend_discount_used(user_id)
    
    # Credit the referrer
    if payment_amount > 0 or phase == 2:  # Always credit on phase 2, even if free
        result = credit_referrer_for_payment(user_id, payment_amount or 39)
        
        if result.get('credited'):
            # Notify referrer
            await notify_referrer(
                referrer_id=result['referrer_id'],
                friend_name=get_user(user_id).get('first_name', 'Alguien'),
                amount=result['amount'],
                reward_type=result['type'],
                payment_amount=payment_amount or 39
            )
    
    # Continue with normal payment confirmation flow...


async def notify_referrer(referrer_id: int, friend_name: str, amount: float, reward_type: str, payment_amount: float):
    """Send notification to referrer about their reward."""
    
    stats = get_user_referral_stats(referrer_id)
    
    if reward_type == 'credit':
        # Calculate tip
        credits_available = stats['credits_available']
        if credits_available >= 299:
            tip = "¡Has alcanzado el máximo! Tu próximo pago será con créditos."
        elif credits_available >= 200:
            tip = f"¡Casi llegas! Te faltan €{299 - credits_available} para servicio gratis."
        else:
            needed = (299 - credits_available) // 25
            tip = f"Con {needed} amigos más, tu servicio es gratis."
        
        text = REFERRAL_NOTIFY_CREDIT.format(
            friend_name=friend_name,
            amount=amount,
            total=credits_available,
            count=stats['count'],
            tip=tip
        )
    else:
        text = REFERRAL_NOTIFY_CASH.format(
            friend_name=friend_name,
            payment=payment_amount,
            amount=amount,
            total=stats['cash_available']
        )
    
    try:
        from telegram import Bot
        bot = Bot(token=os.environ.get('TELEGRAM_BOT_TOKEN'))
        await bot.send_message(chat_id=referrer_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Failed to notify referrer {referrer_id}: {e}")
```

### 3.6 New Command: /referidos

```python
async def cmd_referidos(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show referral dashboard."""
    
    user_id = update.effective_user.id
    stats = get_user_referral_stats(user_id)
    
    if not stats or not stats['code']:
        await update.message.reply_text(
            "Aún no tienes código de referidos.\n"
            "Completa la verificación de elegibilidad para obtener tu código.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    
    # Build status message
    if not stats['can_earn_credits']:
        status_message = "⏳ Paga €39 para activar tus ganancias por referidos."
    elif stats['credits_available'] >= 299:
        status_message = "🎉 ¡Máximo alcanzado! Ahora ganas 10% en efectivo."
    else:
        remaining = 299 - stats['credits_earned']
        friends_needed = remaining // 25
        status_message = f"💡 Te faltan €{remaining} ({friends_needed} amigos) para servicio gratis."
    
    # Build referral list
    if stats['referrals']:
        referral_list = "📋 *ÚLTIMOS REFERIDOS*\n\n"
        for r in stats['referrals'][:5]:
            status_icon = "✅" if r['status'] != 'registered' else "⏳"
            credit_text = f" → +€{r['credit']}" if r['credit'] else ""
            referral_list += f"{status_icon} {r['name']}{credit_text}\n"
    else:
        referral_list = "_Aún no has referido a nadie._"
    
    text = REFERRAL_DASHBOARD.format(
        code=stats['code'],
        count=stats['count'],
        earned=stats['credits_earned'],
        used=stats['credits_used'],
        available=stats['credits_available'],
        status_message=status_message,
        referral_list=referral_list
    )
    
    # Share buttons
    import urllib.parse
    share_text = REFERRAL_SHARE_TEXT.format(code=stats['code'])
    wa_url = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
    
    keyboard = [
        [InlineKeyboardButton("📲 Compartir por WhatsApp", url=wa_url)],
        [InlineKeyboardButton("📋 Copiar enlace", callback_data="ref_copy")],
        [InlineKeyboardButton("🔙 Menú principal", callback_data="m_menu")]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
    return ST_MAIN_MENU
```

### 3.7 Handler Registration

```python
# Add to ConversationHandler

# Entry points - add referral code handling
entry_points=[
    CommandHandler("start", cmd_start),
    CommandHandler("referidos", cmd_referidos),
    # ... existing
]

# States - add new state
states={
    # ... existing states
    ST_ENTER_REFERRAL_CODE: [
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_referral_code_input),
        CallbackQueryHandler(handle_referral_callbacks, pattern=r'^ref_'),
    ],
}

# Callbacks - add referral callbacks
CallbackQueryHandler(handle_referral_callbacks, pattern=r'^ref_'),
```

---

## 4. WEBSITE IMPLEMENTATION

### 4.1 File Structure

```
tus-papeles-2026/
├── index.html          # MODIFY: Add referral section
├── verificar.html      # MODIFY: Add share CTA after result
├── r.html              # NEW: Referral landing page
├── referidos-terminos.html  # NEW: Terms page
├── js/
│   └── referral.js     # NEW: Referral handling
└── css/
    └── styles.css      # MODIFY: Add referral styles
```

### 4.2 NEW FILE: r.html

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>€25 de Descuento | tuspapeles2026</title>
    
    <!-- Same head content as index.html -->
    <link rel="stylesheet" href="css/styles.css">
    
    <script>
        // Parse referral code from URL
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            let code = urlParams.get('code');
            
            // Also check path: /r/CODE format
            const pathMatch = window.location.pathname.match(/\/r\/([A-Z0-9-]+)/i);
            if (pathMatch) {
                code = pathMatch[1].toUpperCase();
            }
            
            if (code && code.length >= 3) {
                // Store in localStorage
                localStorage.setItem('referral_code', code);
                localStorage.setItem('referral_timestamp', Date.now());
                
                // Extract name from code (before the dash)
                const name = code.split('-')[0];
                const displayName = name.charAt(0) + name.slice(1).toLowerCase();
                
                // Update UI
                document.getElementById('referrer-name').textContent = displayName;
                document.getElementById('referral-banner').style.display = 'block';
                
                // Update Telegram links to include code
                document.querySelectorAll('a[href*="t.me/TusPapeles2026Bot"]').forEach(link => {
                    link.href = `https://t.me/TusPapeles2026Bot?start=${code}`;
                });
            } else {
                // No valid code, redirect to homepage
                window.location.href = '/';
            }
        });
    </script>
</head>
<body>
    <!-- Referral Banner -->
    <div id="referral-banner" class="referral-banner" style="display: none;">
        <div class="referral-banner-content">
            <span class="referral-icon">🎁</span>
            <span class="referral-text">
                <strong><span id="referrer-name">Tu amigo</span></strong> te regala 
                <strong>€25 de descuento</strong>
            </span>
        </div>
    </div>
    
    <!-- Rest of page: Same as index.html hero and content -->
    <!-- Include all sections from index.html -->
    
    <script src="js/referral.js"></script>
</body>
</html>
```

### 4.3 NEW FILE: js/referral.js

```javascript
/**
 * Referral System JavaScript
 * Handles localStorage, URL params, and link modification
 */

(function() {
    'use strict';
    
    const STORAGE_KEY = 'referral_code';
    const TIMESTAMP_KEY = 'referral_timestamp';
    const EXPIRY_DAYS = 30;
    
    /**
     * Get stored referral code if not expired
     */
    function getStoredCode() {
        const code = localStorage.getItem(STORAGE_KEY);
        const timestamp = localStorage.getItem(TIMESTAMP_KEY);
        
        if (!code || !timestamp) return null;
        
        // Check if expired (30 days)
        const age = Date.now() - parseInt(timestamp);
        const maxAge = EXPIRY_DAYS * 24 * 60 * 60 * 1000;
        
        if (age > maxAge) {
            localStorage.removeItem(STORAGE_KEY);
            localStorage.removeItem(TIMESTAMP_KEY);
            return null;
        }
        
        return code;
    }
    
    /**
     * Store referral code
     */
    function storeCode(code) {
        if (!code || code.length < 3) return;
        
        localStorage.setItem(STORAGE_KEY, code.toUpperCase());
        localStorage.setItem(TIMESTAMP_KEY, Date.now().toString());
    }
    
    /**
     * Parse code from URL
     */
    function getCodeFromURL() {
        // Check query param: ?code=XXXX
        const urlParams = new URLSearchParams(window.location.search);
        let code = urlParams.get('code') || urlParams.get('ref');
        
        if (code) return code.toUpperCase();
        
        // Check path: /r/XXXX
        const pathMatch = window.location.pathname.match(/\/r\/([A-Z0-9-]+)/i);
        if (pathMatch) return pathMatch[1].toUpperCase();
        
        return null;
    }
    
    /**
     * Update all Telegram links to include referral code
     */
    function updateTelegramLinks(code) {
        if (!code) return;
        
        document.querySelectorAll('a[href*="t.me/TusPapeles2026Bot"]').forEach(link => {
            const baseUrl = 'https://t.me/TusPapeles2026Bot';
            link.href = `${baseUrl}?start=${code}`;
        });
    }
    
    /**
     * Show referral banner if code present
     */
    function showReferralBanner(code) {
        const banner = document.getElementById('referral-banner');
        if (!banner || !code) return;
        
        // Extract name from code
        const name = code.split('-')[0];
        const displayName = name.charAt(0) + name.slice(1).toLowerCase();
        
        const nameEl = document.getElementById('referrer-name');
        if (nameEl) nameEl.textContent = displayName;
        
        banner.style.display = 'block';
    }
    
    /**
     * Generate WhatsApp share link
     */
    function generateWhatsAppLink(code) {
        const text = `¡Hola! Acabo de verificar que califico para la regularización 2026 en España.

Si llevas tiempo aquí sin papeles, verifica gratis si calificas:
👉 tuspapeles2026.es/r.html?code=${code}

Usa mi código ${code} y te descuentan €25.

Es el nuevo decreto — no necesitas contrato de trabajo. ¡Aprovecha!`;
        
        return `https://wa.me/?text=${encodeURIComponent(text)}`;
    }
    
    /**
     * Copy text to clipboard
     */
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }
    
    /**
     * Initialize referral system
     */
    function init() {
        // Check URL for code
        const urlCode = getCodeFromURL();
        if (urlCode) {
            storeCode(urlCode);
        }
        
        // Get active code (from URL or storage)
        const code = urlCode || getStoredCode();
        
        if (code) {
            updateTelegramLinks(code);
            showReferralBanner(code);
        }
        
        // Set up share buttons
        document.querySelectorAll('[data-share="whatsapp"]').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const shareCode = this.dataset.code || code;
                if (shareCode) {
                    window.open(generateWhatsAppLink(shareCode), '_blank');
                }
            });
        });
        
        document.querySelectorAll('[data-share="copy"]').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const shareCode = this.dataset.code || code;
                if (shareCode) {
                    copyToClipboard(`tuspapeles2026.es/r.html?code=${shareCode}`);
                    
                    // Show feedback
                    const originalText = this.textContent;
                    this.textContent = '✓ Copiado';
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                }
            });
        });
    }
    
    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Expose functions for external use
    window.ReferralSystem = {
        getCode: getStoredCode,
        storeCode: storeCode,
        generateWhatsAppLink: generateWhatsAppLink,
        copyToClipboard: copyToClipboard
    };
    
})();
```

### 4.4 NEW FILE: referidos-terminos.html

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programa de Referidos — Términos | tuspapeles2026</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header>
        <!-- Same header as other pages -->
    </header>
    
    <main class="legal-page">
        <div class="container">
            <h1>Programa de Referidos — Términos</h1>
            
            <section>
                <h2>Cómo Funciona</h2>
                <ol>
                    <li>Al completar la verificación de elegibilidad, recibes un código personal único.</li>
                    <li>Cuando pagas tu primera fase (€39), tu código se activa para ganar recompensas.</li>
                    <li>Por cada amigo que pague usando tu código:
                        <ul>
                            <li>Tú recibes <strong>€25 de crédito</strong></li>
                            <li>Tu amigo recibe <strong>€25 de descuento</strong> en su primer pago</li>
                        </ul>
                    </li>
                    <li>Puedes acumular hasta <strong>€299 en créditos</strong> (el costo total del servicio).</li>
                    <li>Si ya pagaste los €299 completos, ganas <strong>10% en efectivo</strong> por cada pago de tus referidos. Pagamos mensualmente por Bizum (mínimo €30 acumulados).</li>
                </ol>
            </section>
            
            <section>
                <h2>Reglas</h2>
                <ul>
                    <li>Solo ganas por referidos <strong>directos</strong>. No es multinivel — no ganas por los amigos de tus amigos.</li>
                    <li>El crédito se aplica automáticamente a tus pagos pendientes.</li>
                    <li>Si tu amigo solicita reembolso en los primeros 14 días, el crédito se revierte.</li>
                    <li>Los pagos en efectivo se procesan 30 días después del pago del referido.</li>
                    <li>Máximo €1,000 en efectivo por año calendario.</li>
                    <li>Una cuenta bancaria/Bizum por código de referido.</li>
                    <li>Nos reservamos el derecho de revisar cuentas con actividad inusual.</li>
                </ul>
            </section>
            
            <section>
                <h2>Importante</h2>
                <p>Este programa recompensa a quienes ayudan a su comunidad a conocer nuestros servicios. El dinero viene de nuestros ingresos por servicios prestados, no de otros usuarios. <strong>No es un esquema multinivel.</strong></p>
            </section>
            
            <section>
                <h2>Ejemplos</h2>
                
                <div class="example-box">
                    <h3>Ejemplo 1: María refiere 12 amigos</h3>
                    <ul>
                        <li>Amigos 1-12 pagan → María gana €25 × 12 = €300 en créditos</li>
                        <li>María tiene €299 en créditos (el máximo)</li>
                        <li>María paga €39 → usa €39 de crédito → paga €0</li>
                        <li>María paga €150 → usa €150 de crédito → paga €0</li>
                        <li>María paga €110 → usa €110 de crédito → paga €0</li>
                        <li><strong>Resultado: María obtuvo el servicio completo GRATIS</strong></li>
                    </ul>
                </div>
                
                <div class="example-box">
                    <h3>Ejemplo 2: Carlos refiere 20 amigos</h3>
                    <ul>
                        <li>Amigos 1-12 → €299 en créditos (servicio gratis)</li>
                        <li>Carlos paga sus €299 con créditos</li>
                        <li>Amigos 13-20 pagan €299 cada uno:</li>
                        <li>Carlos gana 10% × €299 × 8 = €239.20 en efectivo</li>
                        <li><strong>Resultado: Servicio gratis + €239 en efectivo</strong></li>
                    </ul>
                </div>
            </section>
            
            <p class="last-updated">Última actualización: Febrero 2026</p>
        </div>
    </main>
    
    <footer>
        <!-- Same footer as other pages -->
    </footer>
</body>
</html>
```

### 4.5 MODIFY: index.html — Add Referral Section

Add this section after the hero:

```html
<!-- REFERRAL SECTION -->
<section id="referidos" class="section referral-section">
    <div class="container">
        <h2>📣 Comparte y Gana</h2>
        <p class="section-subtitle">Ayuda a tu comunidad — y gana tú también</p>
        
        <div class="referral-steps">
            <div class="referral-step">
                <div class="step-number">1</div>
                <div class="step-icon">✅</div>
                <h3>Verifica gratis</h3>
                <p>Comprueba si calificas y recibe tu código personal</p>
            </div>
            
            <div class="referral-step">
                <div class="step-number">2</div>
                <div class="step-icon">💳</div>
                <h3>Paga €39</h3>
                <p>Activa tu código y empieza a ganar</p>
            </div>
            
            <div class="referral-step">
                <div class="step-number">3</div>
                <div class="step-icon">🎁</div>
                <h3>Gana €25/amigo</h3>
                <p>Por cada amigo que pague</p>
            </div>
        </div>
        
        <div class="referral-summary">
            <div class="summary-item">
                <span class="summary-icon">👤</span>
                <span class="summary-text">Tu amigo recibe <strong>€25 de descuento</strong></span>
            </div>
            <div class="summary-item">
                <span class="summary-icon">💰</span>
                <span class="summary-text">Tú recibes <strong>€25 de crédito</strong></span>
            </div>
            <div class="summary-item">
                <span class="summary-icon">🎉</span>
                <span class="summary-text"><strong>12 amigos = servicio GRATIS</strong></span>
            </div>
        </div>
        
        <a href="https://t.me/TusPapeles2026Bot" class="btn btn-primary">
            Obtener mi código →
        </a>
        
        <p class="referral-note">
            <a href="/referidos-terminos.html">Ver términos del programa</a>
        </p>
    </div>
</section>
```

### 4.6 MODIFY: verificar.html — Add Share CTA

After the "¡Calificas!" result, add:

```html
<!-- Show this when user qualifies -->
<div id="result-qualified" class="result-box result-success" style="display: none;">
    <h2>✅ ¡Calificas!</h2>
    <p>Cumples los requisitos básicos para la regularización 2026.</p>
    
    <div class="share-cta">
        <h3>📣 Comparte y gana hasta €299</h3>
        <p>Tu código aparecerá cuando inicies el proceso en Telegram.</p>
        
        <p>Por cada amigo que refieras:</p>
        <ul>
            <li>Tu amigo recibe €25 de descuento</li>
            <li>Tú recibes €25 de crédito</li>
            <li>12 amigos = servicio GRATIS</li>
        </ul>
    </div>
    
    <a href="https://t.me/TusPapeles2026Bot" class="btn btn-primary btn-large">
        Consigue tus papeles →
    </a>
    
    <p class="terms-link">
        <a href="/referidos-terminos.html">Términos del programa de referidos</a>
    </p>
</div>
```

### 4.7 MODIFY: Footer — Add Terms Link

```html
<footer>
    <div class="container">
        <div class="footer-links">
            <!-- Existing links -->
            <a href="/aviso-legal.html">Aviso Legal</a>
            <a href="/privacidad.html">Privacidad</a>
            <a href="/referidos-terminos.html">Programa de Referidos</a>
        </div>
        <!-- Rest of footer -->
    </div>
</footer>
```

### 4.8 CSS Additions

```css
/* Referral Banner */
.referral-banner {
    background: linear-gradient(135deg, #E8D4A8, #D4C094);
    color: #1E3A5F;
    padding: 12px 20px;
    text-align: center;
    font-weight: 500;
}

.referral-banner-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}

.referral-icon {
    font-size: 1.5rem;
}

/* Referral Section */
.referral-section {
    background: #f8f9fa;
    padding: 60px 0;
    text-align: center;
}

.referral-steps {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin: 40px 0;
    flex-wrap: wrap;
}

.referral-step {
    max-width: 200px;
    position: relative;
}

.step-number {
    position: absolute;
    top: -10px;
    left: -10px;
    width: 30px;
    height: 30px;
    background: #1E3A5F;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.step-icon {
    font-size: 3rem;
    margin-bottom: 15px;
}

.referral-summary {
    background: white;
    border-radius: 12px;
    padding: 30px;
    max-width: 500px;
    margin: 30px auto;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.summary-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

.summary-item:last-child {
    border-bottom: none;
}

.summary-icon {
    font-size: 1.5rem;
}

.referral-note {
    margin-top: 20px;
    font-size: 0.9rem;
    color: #666;
}

/* Share CTA in verificar.html */
.share-cta {
    background: #f0f7ff;
    border-radius: 12px;
    padding: 25px;
    margin: 25px 0;
    text-align: left;
}

.share-cta h3 {
    margin-top: 0;
}

.share-cta ul {
    margin-bottom: 0;
}

/* Mobile */
@media (max-width: 768px) {
    .referral-steps {
        flex-direction: column;
        align-items: center;
        gap: 30px;
    }
    
    .referral-banner-content {
        flex-direction: column;
        gap: 5px;
    }
}
```

---

## 5. DATA FLOW

### 5.1 User Gets Referred via Website

```
User clicks: tuspapeles2026.es/r.html?code=MARIA-7K2P
                    │
                    ▼
            JavaScript parses code
                    │
                    ▼
            Stores in localStorage
                    │
                    ▼
            Updates Telegram links to include ?start=MARIA-7K2P
                    │
                    ▼
            User clicks "Consigue tus papeles"
                    │
                    ▼
            Opens: t.me/TusPapeles2026Bot?start=MARIA-7K2P
                    │
                    ▼
            Bot receives /start MARIA-7K2P
                    │
                    ▼
            Bot validates code, stores referred_by_code
                    │
                    ▼
            User completes eligibility, gets OWN code
                    │
                    ▼
            User pays Phase 2
                    │
                    ├─ €25 discount applied (friend discount)
                    │
                    └─ María gets notified, earns €25 credit
```

### 5.2 Referrer Earns and Uses Credits

```
María has referred 5 friends who paid
                    │
                    ▼
            María has €125 credit
                    │
                    ▼
            María goes to pay Phase 2 (€39)
                    │
                    ▼
            System calculates: €39 - €39 credit = €0
                    │
                    ▼
            María pays €0 (free!)
                    │
                    ▼
            €39 deducted from her credits
                    │
                    ▼
            María now has €86 credit remaining
```

---

## 6. TESTING CHECKLIST

### 6.1 Database Tests
- [ ] Users table has new columns
- [ ] Referrals table created
- [ ] Referral_events table created
- [ ] Indexes exist

### 6.2 Code Generation Tests
- [ ] Code generated on eligibility completion
- [ ] Code format is NAME-XXXX
- [ ] Code is unique (no collisions)
- [ ] Code stored in database

### 6.3 Code Application Tests
- [ ] Valid code accepted
- [ ] Invalid code rejected with message
- [ ] Can't use own code
- [ ] Can't use non-existent code
- [ ] Code stored in referred_by_code
- [ ] Referral record created

### 6.4 Friend Discount Tests
- [ ] €25 discount shown at first payment
- [ ] Discount only applies once
- [ ] Discount applied correctly to price

### 6.5 Credit Earning Tests
- [ ] No credits before paying Phase 2
- [ ] €25 credit when friend pays (after Phase 2)
- [ ] Credit capped at €299
- [ ] Referrer notified on earn

### 6.6 Credit Application Tests
- [ ] Credits shown at payment screen
- [ ] Credits deducted from price
- [ ] Free payment works when credits cover full amount
- [ ] Remaining credits tracked

### 6.7 Cash Earning Tests (After €299 paid)
- [ ] 10% calculated correctly
- [ ] Cash marked as available after 30 days
- [ ] Cash balance tracked

### 6.8 Website Tests
- [ ] /r.html?code=XXX loads
- [ ] Code stored in localStorage
- [ ] Telegram links updated with code
- [ ] Referral banner shows
- [ ] Referral section on homepage works
- [ ] Terms page loads

### 6.9 Edge Cases
- [ ] User with no referrer pays normally
- [ ] User tries code after already being referred
- [ ] Referrer reaches €299 cap
- [ ] Very long names handled
- [ ] Special characters in names handled

---

## 7. IMPLEMENTATION ORDER

### Phase 1: Database (Do First)
1. Add columns to users table
2. Create referrals table
3. Create referral_events table
4. Test migrations

### Phase 2: Bot Core (Do Second)
1. Add helper functions
2. Add code generation to eligibility result
3. Add /referidos command
4. Test code generation and display

### Phase 3: Bot Referral Flow (Do Third)
1. Add referral code prompt to registration
2. Add code validation
3. Add friend discount to payments
4. Test full referral flow

### Phase 4: Bot Credit System (Do Fourth)
1. Add credit earning on friend payment
2. Add credit application to payments
3. Add referrer notifications
4. Test credit flow end-to-end

### Phase 5: Website (Do Fifth)
1. Create r.html
2. Create referral.js
3. Create referidos-terminos.html
4. Modify index.html
5. Modify verificar.html
6. Add CSS
7. Test website flow

### Phase 6: Integration Testing (Do Last)
1. Full flow: website → bot → payment → credit
2. Edge cases
3. Mobile testing

---

## APPENDIX: Quick Reference

### Bot Commands
- `/referidos` — Show referral dashboard
- `/start CODE` — Start with referral code

### Database Queries
```sql
-- Get user's referral stats
SELECT referral_code, referral_count, referral_credits_earned, 
       referral_credits_used, (referral_credits_earned - referral_credits_used) as available
FROM users WHERE telegram_id = ?;

-- Get referrer's referrals
SELECT u.first_name, r.status, r.credit_amount, r.created_at
FROM referrals r
JOIN users u ON r.referred_user_id = u.telegram_id
WHERE r.referrer_user_id = ?
ORDER BY r.created_at DESC;

-- Count paid referrals
SELECT COUNT(*) FROM referrals 
WHERE referrer_user_id = ? AND status != 'registered';
```

### URLs
- Referral landing: `tuspapeles2026.es/r.html?code=XXXX`
- Telegram with code: `t.me/TusPapeles2026Bot?start=XXXX`
- Terms: `tuspapeles2026.es/referidos-terminos.html`

---

**END OF SPECIFICATION**
