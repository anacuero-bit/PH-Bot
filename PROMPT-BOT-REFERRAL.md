# CLAUDE CODE PROMPT — BOT REFERRAL SYSTEM

**Repository:** PH-Bot
**Branch:** Create new branch `feature/referral-system`

---

## OVERVIEW

Implement a referral system where:
1. Users get a unique code (MARIA-7K2P) after passing eligibility
2. Friends can use the code for €25 off
3. Referrers earn €25 credit per friend who pays (after referrer pays €39)
4. Credits cap at €299 (full service)
5. After €299 paid, referrers earn 10% cash

---

## STEP 1: DATABASE SCHEMA

**In `init_db()` function, add these table modifications:**

```python
# Add columns to users table
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code VARCHAR(20) UNIQUE")
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by_code VARCHAR(20)")
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by_user_id BIGINT")
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0")
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_credits_earned DECIMAL(10,2) DEFAULT 0")
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_credits_used DECIMAL(10,2) DEFAULT 0")
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_cash_earned DECIMAL(10,2) DEFAULT 0")
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS friend_discount_applied BOOLEAN DEFAULT FALSE")

# Create referrals table
c.execute("""CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_user_id BIGINT NOT NULL,
    referrer_code VARCHAR(20) NOT NULL,
    referred_user_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'registered',
    credit_amount DECIMAL(10,2) DEFAULT 0,
    credit_awarded_at TIMESTAMP,
    cash_amount DECIMAL(10,2) DEFAULT 0,
    friend_total_paid DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(referrer_user_id, referred_user_id)
)""")

# Create referral_events table for audit
c.execute("""CREATE TABLE IF NOT EXISTS referral_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(30) NOT NULL,
    amount DECIMAL(10,2),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

# Create indexes
c.execute("CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code)")
c.execute("CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referrer_code)")
```

---

## STEP 2: ADD CONSTANTS

**Add these constants near the top of main.py:**

```python
# =============================================================================
# REFERRAL SYSTEM
# =============================================================================

REFERRAL_CREDIT_AMOUNT = 25      # €25 per referral
REFERRAL_CREDIT_CAP = 299        # Max credits
REFERRAL_CASH_PERCENT = 0.10     # 10% cash after cap
REFERRAL_FRIEND_DISCOUNT = 25    # €25 off for friend

# Share message template
REFERRAL_SHARE_TEXT = """¡Hola! Acabo de verificar que califico para la regularización 2026 en España.

Si llevas tiempo aquí sin papeles, verifica gratis si calificas:
👉 tuspapeles2026.es/r.html?code={code}

Usa mi código {code} y te descuentan €25.

Es el nuevo decreto — no necesitas contrato de trabajo. ¡Aprovecha!"""
```

---

## STEP 3: ADD NEW STATE

**Add to states enum:**

```python
ST_ENTER_REFERRAL_CODE = 25  # Add after existing states
```

---

## STEP 4: ADD HELPER FUNCTIONS

**Add these functions after existing database functions:**

```python
# =============================================================================
# REFERRAL FUNCTIONS
# =============================================================================

import random
import string
import urllib.parse

def generate_referral_code(first_name: str) -> str:
    """Generate unique referral code: NAME-XXXX"""
    # Clean name
    clean_name = ''.join(c for c in first_name.upper() if c.isalpha())[:10]
    if not clean_name:
        clean_name = "USER"
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for _ in range(10):
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code = f"{clean_name}-{suffix}"
        c.execute("SELECT 1 FROM users WHERE referral_code = ?", (code,))
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
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT telegram_id, first_name FROM users WHERE referral_code = ?", (code,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {'valid': False, 'error': 'not_found'}
    
    return {
        'valid': True,
        'referrer_id': row['telegram_id'],
        'referrer_name': row['first_name'],
        'code': code
    }


def apply_referral_code_to_user(user_id: int, code: str, referrer_id: int) -> bool:
    """Store referral relationship."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute("""
            UPDATE users 
            SET referred_by_code = ?, referred_by_user_id = ?
            WHERE telegram_id = ? AND referred_by_code IS NULL
        """, (code, referrer_id, user_id))
        
        c.execute("""
            INSERT OR IGNORE INTO referrals (referrer_user_id, referrer_code, referred_user_id)
            VALUES (?, ?, ?)
        """, (referrer_id, code, user_id))
        
        c.execute("""
            INSERT INTO referral_events (user_id, event_type, description)
            VALUES (?, 'code_used', ?)
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    user = dict(c.fetchone()) if c.fetchone() else None
    
    if not user:
        conn.close()
        return None
    
    # Re-query since fetchone consumed it
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    user = dict(c.fetchone())
    
    c.execute("""
        SELECT r.*, u.first_name as referred_name
        FROM referrals r
        JOIN users u ON r.referred_user_id = u.telegram_id
        WHERE r.referrer_user_id = ?
        ORDER BY r.created_at DESC LIMIT 10
    """, (user_id,))
    referrals = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    earned = user.get('referral_credits_earned') or 0
    used = user.get('referral_credits_used') or 0
    
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        # Get referral info
        c.execute("""
            SELECT r.referrer_user_id, r.credit_amount,
                   u.phase2_paid, u.referral_credits_earned
            FROM referrals r
            JOIN users u ON r.referrer_user_id = u.telegram_id
            WHERE r.referred_user_id = ?
        """, (referred_user_id,))
        
        row = c.fetchone()
        if not row:
            conn.close()
            return {'credited': False, 'reason': 'no_referrer'}
        
        referrer_id = row['referrer_user_id']
        existing_credit = row['credit_amount'] or 0
        phase2_paid = row['phase2_paid'] == 1
        credits_earned = row['referral_credits_earned'] or 0
        
        # Must have paid Phase 2 to earn
        if not phase2_paid:
            conn.close()
            return {'credited': False, 'reason': 'referrer_not_eligible'}
        
        # Already credited this referral
        if existing_credit > 0:
            conn.close()
            return {'credited': False, 'reason': 'already_credited'}
        
        # Check credit cap
        if credits_earned >= REFERRAL_CREDIT_CAP:
            conn.close()
            return {'credited': False, 'reason': 'cap_reached'}
        
        credit_amount = min(REFERRAL_CREDIT_AMOUNT, REFERRAL_CREDIT_CAP - credits_earned)
        
        # Update referral record
        c.execute("""
            UPDATE referrals 
            SET credit_amount = ?, status = 'paid_phase2', 
                credit_awarded_at = CURRENT_TIMESTAMP,
                friend_total_paid = ?
            WHERE referred_user_id = ?
        """, (credit_amount, payment_amount, referred_user_id))
        
        # Update referrer's credits
        c.execute("""
            UPDATE users 
            SET referral_credits_earned = referral_credits_earned + ?,
                referral_count = referral_count + 1
            WHERE telegram_id = ?
        """, (credit_amount, referrer_id))
        
        # Log event
        c.execute("""
            INSERT INTO referral_events (user_id, event_type, amount, description)
            VALUES (?, 'credit_earned', ?, 'Friend paid')
        """, (referrer_id, credit_amount))
        
        conn.commit()
        conn.close()
        return {'credited': True, 'amount': credit_amount, 'referrer_id': referrer_id}
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error crediting referrer: {e}")
        return {'credited': False, 'reason': 'error'}
    finally:
        if conn:
            conn.close()


def get_friend_discount(user_id: int) -> dict:
    """Check if user has friend discount available."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT u1.referred_by_code, u1.friend_discount_applied,
               u2.first_name as referrer_name
        FROM users u1
        LEFT JOIN users u2 ON u1.referred_by_user_id = u2.telegram_id
        WHERE u1.telegram_id = ?
    """, (user_id,))
    
    row = c.fetchone()
    conn.close()
    
    if not row or not row['referred_by_code'] or row['friend_discount_applied']:
        return {'has_discount': False}
    
    return {
        'has_discount': True,
        'amount': REFERRAL_FRIEND_DISCOUNT,
        'referrer_name': row['referrer_name'] or 'un amigo'
    }


def apply_friend_discount(user_id: int) -> bool:
    """Mark friend discount as used."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET friend_discount_applied = 1 WHERE telegram_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


def apply_credits_to_payment(user_id: int, price: float) -> dict:
    """Calculate price after applying credits."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT referral_credits_earned, referral_credits_used FROM users WHERE telegram_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {'original': price, 'credits_applied': 0, 'final_price': price, 'credits_remaining': 0}
    
    earned = row['referral_credits_earned'] or 0
    used = row['referral_credits_used'] or 0
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET referral_credits_used = referral_credits_used + ? WHERE telegram_id = ?", (amount, user_id))
    c.execute("INSERT INTO referral_events (user_id, event_type, amount, description) VALUES (?, 'credit_applied', ?, 'Payment')", (user_id, amount))
    conn.commit()
    conn.close()


def get_whatsapp_share_url(code: str) -> str:
    """Generate WhatsApp share URL."""
    text = REFERRAL_SHARE_TEXT.format(code=code)
    return f"https://wa.me/?text={urllib.parse.quote(text)}"
```

---

## STEP 5: MODIFY cmd_start

**Replace cmd_start to handle referral deep links:**

```python
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
    
    # Check for referral code in start param
    if ctx.args and len(ctx.args) > 0:
        code = ctx.args[0].upper().strip()
        result = validate_referral_code(code)
        
        if result['valid'] and result['referrer_id'] != tid:
            apply_referral_code_to_user(tid, result['code'], result['referrer_id'])
            
            await update.message.reply_text(
                f"🎁 *¡Código aplicado!*\n\n"
                f"{result['referrer_name']} te ha regalado *€{REFERRAL_FRIEND_DISCOUNT} de descuento* "
                f"que se aplicará a tu primer pago.\n\n"
                f"Para empezar, indíquenos su país de origen:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=country_kb(),
            )
            return ST_COUNTRY
    
    # Normal start - ask if they have a code
    await update.message.reply_text(
        "Bienvenido/a al servicio de regularización de *Pombo & Horowitz Abogados*.\n\n"
        "¿Alguien te recomendó tuspapeles2026?\n\n"
        "Si un amigo te compartió su código, escríbelo ahora y recibirás *€25 de descuento*.\n\n"
        "Ejemplo: `MARIA-7K2P`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("No tengo código", callback_data="ref_skip")]
        ]),
    )
    return ST_ENTER_REFERRAL_CODE
```

---

## STEP 6: ADD REFERRAL CODE INPUT HANDLERS

```python
async def handle_referral_code_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user typing a referral code."""
    tid = update.effective_user.id
    code = update.message.text.upper().strip()
    
    # Validate
    result = validate_referral_code(code)
    
    if not result['valid']:
        await update.message.reply_text(
            "❌ Código no encontrado.\n\n"
            "Verifica que esté bien escrito (ejemplo: `MARIA-7K2P`) o continúa sin código.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Intentar de nuevo", callback_data="ref_retry")],
                [InlineKeyboardButton("➡️ Continuar sin código", callback_data="ref_skip")]
            ]),
        )
        return ST_ENTER_REFERRAL_CODE
    
    # Can't use own code
    if result['referrer_id'] == tid:
        await update.message.reply_text(
            "❌ No puedes usar tu propio código.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➡️ Continuar sin código", callback_data="ref_skip")]
            ]),
        )
        return ST_ENTER_REFERRAL_CODE
    
    # Apply code
    apply_referral_code_to_user(tid, result['code'], result['referrer_id'])
    
    await update.message.reply_text(
        f"✅ *¡Código aplicado!*\n\n"
        f"{result['referrer_name']} te ha regalado *€{REFERRAL_FRIEND_DISCOUNT} de descuento* "
        f"que se aplicará a tu primer pago.\n\n"
        f"Para empezar, indíquenos su país de origen:",
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
            "Bienvenido/a al servicio de regularización de *Pombo & Horowitz Abogados*.\n\n"
            "Para empezar, indíquenos su país de origen:",
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
        await q.answer(f"Tu código: {code}\nEnlace: tuspapeles2026.es/r.html?code={code}", show_alert=True)
        return ST_MAIN_MENU
    
    return ST_ENTER_REFERRAL_CODE
```

---

## STEP 7: MODIFY ELIGIBILITY RESULT (handle_q3)

**In the `r_clean` block where user is eligible, ADD referral code generation:**

Find this section in handle_q3 and modify:

```python
    # r_clean → ELIGIBLE
    update_user(update.effective_user.id, eligible=1, has_criminal_record=0)
    case = get_or_create_case(update.effective_user.id)
    
    # GENERATE REFERRAL CODE
    user = get_user(update.effective_user.id)
    if not user.get('referral_code'):
        code = generate_referral_code(user.get('first_name', 'USER'))
        update_user(update.effective_user.id, referral_code=code)
    else:
        code = user['referral_code']
    
    # Notify referrer if this user was referred
    if user.get('referred_by_user_id'):
        try:
            await ctx.bot.send_message(
                user['referred_by_user_id'],
                f"🎉 ¡{user.get('first_name', 'Alguien')} se registró con tu código!\n\n"
                "Cuando pagues tu Fase 2 y ellos paguen, ganarás €25.",
            )
        except:
            pass
    
    wa_url = get_whatsapp_share_url(code)
    
    await q.edit_message_text(
        f"*{name}, cumple los requisitos básicos para la regularización.*\n\n"
        f"Le hemos asignado el expediente *{case['case_number']}*.\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📣 *TU CÓDIGO PERSONAL*\n\n"
        f"`{code}`\n\n"
        f"• Tu amigo recibe €25 de descuento\n"
        f"• Tú ganas €25 por cada amigo (cuando pagues €39)\n"
        f"• 12 amigos = ¡servicio GRATIS!\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📅 Plazo: 1 abril – 30 junio 2026 ({days_left()} días).",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 Compartir por WhatsApp", url=wa_url)],
            [InlineKeyboardButton("📋 Copiar código", callback_data="ref_copy")],
            [InlineKeyboardButton("➡️ Continuar", callback_data="m_menu")],
        ]),
    )
    return ST_ELIGIBLE
```

---

## STEP 8: ADD /referidos COMMAND

```python
async def cmd_referidos(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Show referral dashboard."""
    tid = update.effective_user.id
    stats = get_referral_stats(tid)
    
    if not stats or not stats['code']:
        await update.message.reply_text(
            "Aún no tienes código de referidos.\n"
            "Completa la verificación de elegibilidad primero.",
        )
        return ConversationHandler.END
    
    # Status message
    if not stats['can_earn']:
        status = "⏳ _Paga €39 para activar tus ganancias_"
    elif stats['credits_available'] >= 299:
        status = "🎉 _¡Máximo alcanzado! Ahora ganas 10% en efectivo_"
    else:
        needed = (299 - stats['credits_earned']) // 25
        status = f"💡 _Te faltan {needed} amigos para servicio gratis_"
    
    # Referral list
    ref_list = ""
    if stats['referrals']:
        ref_list = "\n📋 *ÚLTIMOS REFERIDOS*\n\n"
        for r in stats['referrals'][:5]:
            icon = "✅" if r['status'] != 'registered' else "⏳"
            credit = f" → +€{r['credit_amount']}" if r['credit_amount'] else ""
            ref_list += f"{icon} {r['referred_name']}{credit}\n"
    
    wa_url = get_whatsapp_share_url(stats['code'])
    
    await update.message.reply_text(
        f"👥 *TUS REFERIDOS*\n\n"
        f"Tu código: `{stats['code']}`\n"
        f"🔗 `tuspapeles2026.es/r.html?code={stats['code']}`\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 *ESTADO*\n\n"
        f"{status}\n\n"
        f"Referidos que han pagado: {stats['count']}\n"
        f"💰 Crédito ganado: €{stats['credits_earned']}\n"
        f"💰 Crédito usado: €{stats['credits_used']}\n"
        f"💰 *Disponible: €{stats['credits_available']}*\n"
        f"{ref_list}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 Compartir por WhatsApp", url=wa_url)],
            [InlineKeyboardButton("📋 Copiar código", callback_data="ref_copy")],
            [InlineKeyboardButton("🔙 Menú", callback_data="m_menu")],
        ]),
    )
    return ST_MAIN_MENU
```

---

## STEP 9: MODIFY PAYMENT FLOW (m_pay2 handler)

**In handle_menu, modify the m_pay2 block:**

```python
    if d == "m_pay2":
        user = get_user(update.effective_user.id)
        base_price = PRICING['phase2']  # €39
        
        # Check friend discount
        friend_disc = get_friend_discount(update.effective_user.id)
        discount = friend_disc['amount'] if friend_disc['has_discount'] else 0
        
        # Check referral credits
        price_after_discount = base_price - discount
        credit_calc = apply_credits_to_payment(update.effective_user.id, price_after_discount)
        
        final_price = credit_calc['final_price']
        
        # Store for payment confirmation
        ctx.user_data['payment_discount'] = discount
        ctx.user_data['payment_credits'] = credit_calc['credits_applied']
        ctx.user_data['payment_final'] = final_price
        
        # Build message
        lines = [f"💳 *FASE 2 — Revisión legal*\n"]
        lines.append(f"Precio: €{base_price}")
        
        if discount > 0:
            lines.append(f"Descuento de {friend_disc['referrer_name']}: -€{discount}")
        
        if credit_calc['credits_applied'] > 0:
            lines.append(f"Tu crédito: -€{credit_calc['credits_applied']}")
        
        lines.append("━━━━━━━━━━")
        
        if final_price <= 0:
            lines.append(f"*A pagar: €0* ✨\n")
            lines.append("¡Esta fase es GRATIS gracias a tus referidos!")
            if credit_calc['credits_remaining'] > 0:
                lines.append(f"Crédito restante: €{credit_calc['credits_remaining']}")
            
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Continuar gratis", callback_data="paid2_free")],
                [InlineKeyboardButton("🔙 Volver", callback_data="m_menu")],
            ])
        else:
            lines.append(f"*A pagar: €{final_price}*\n")
            lines.append("Un abogado colegiado revisará toda su documentación...")
            
            kb = _payment_buttons("paid2", STRIPE_PHASE2_LINK)
        
        await q.edit_message_text(
            "\n".join(lines),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb,
        )
        return ST_PAY_PHASE2
```

---

## STEP 10: MODIFY PAYMENT CONFIRMATION (paid2 handler)

**Modify the paid2 callback handler to credit referrer:**

```python
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
        result = credit_referrer(tid, PRICING['phase2'])
        
        if result.get('credited'):
            # Notify referrer
            try:
                user = get_user(tid)
                referrer_stats = get_referral_stats(result['referrer_id'])
                
                await ctx.bot.send_message(
                    result['referrer_id'],
                    f"🎉 *¡Tu amigo {user.get('first_name', 'alguien')} acaba de pagar!*\n\n"
                    f"Has ganado: *+€{result['amount']} crédito*\n\n"
                    f"Tu crédito total: *€{referrer_stats['credits_available']}*\n"
                    f"Referidos que han pagado: {referrer_stats['count']}\n\n"
                    f"💡 Sigue compartiendo para conseguir tu servicio gratis.",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception as e:
                logger.error(f"Failed to notify referrer: {e}")
        
        # Continue with normal flow...
        # Notify admins
        for aid in ADMIN_IDS:
            try:
                await ctx.bot.send_message(aid, f"💳 Pago Fase 2: User {tid}")
            except:
                pass
        
        await q.edit_message_text(
            "✅ *¡Pago recibido!*\n\n"
            "Nuestro equipo revisará su documentación en las próximas 24-48 horas.\n\n"
            "Le notificaremos cuando esté listo para la siguiente fase.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Ver mi progreso", callback_data="m_menu")]
            ]),
        )
        return ST_MAIN_MENU
```

---

## STEP 11: UPDATE CONVERSATION HANDLER

**Add new handlers to the ConversationHandler:**

```python
# In entry_points, add:
CommandHandler("referidos", cmd_referidos),

# In states dict, add:
ST_ENTER_REFERRAL_CODE: [
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_referral_code_text),
    CallbackQueryHandler(handle_referral_callbacks, pattern=r'^ref_'),
],

# Add ref_ callback handler to all states that might need it:
# In fallbacks or as a general handler:
CallbackQueryHandler(handle_referral_callbacks, pattern=r'^ref_'),
```

---

## TESTING

After implementing, test:

1. `/start` shows referral code prompt
2. Valid code accepted, user gets discount stored
3. Invalid code rejected gracefully
4. Skip works, continues to country selection
5. Eligibility completion generates code
6. `/referidos` shows dashboard
7. Share buttons work (WhatsApp opens)
8. Payment shows discount breakdown
9. Free payment works when credits sufficient
10. Referrer gets notification on friend's payment

---

## DEPLOYMENT

1. Create branch: `git checkout -b feature/referral-system`
2. Make changes
3. Test locally
4. Push and create PR
5. Merge to main
6. Railway auto-deploys

---

**END OF PROMPT**
