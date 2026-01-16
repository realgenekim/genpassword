# genpassword

A safe password generator that creates passwords humans can actually use.

## The Problem

After 20+ years with MySQL, I started using Postgres again. After some fantastic successes, I spent 30 minutes struggling with an authentication error.

**It took me over 30 minutes to learn that Postgres passwords don't allow the `#` character.**

My password generator had not so helpfully included one.

This is a solved problem that shouldn't exist. In 2017, Branden Williams drafted an [IETF RFC for Open Password Automation Recipe (OPAR)](https://datatracker.ietf.org/doc/html/draft-bwilliams-kitten-opar-00) to create an open standard for password format requirements. Until that's universally adopted, we need passwords that don't break things.

## Design Goals

### 1. No Dangerous Characters

Characters that cause problems across systems:

| Character | Shell | URL | SQL | Config Files |
|-----------|-------|-----|-----|--------------|
| `#` | comment | fragment | - | comment |
| `'` | string delimiter | - | string delimiter | - |
| `"` | string delimiter | - | identifier | - |
| `` ` `` | command substitution | - | - | - |
| `$` | variable expansion | - | - | - |
| `\` | escape | encoding | escape | escape |
| `!` | history expansion | - | - | - |
| `&` | background process | param separator | - | - |
| `%` | - | escape char | - | - |
| `;` | command separator | - | statement end | - |
| `<` `>` | redirects | - | - | - |
| `(` `)` | subshells | - | - | - |
| `{` `}` | brace expansion | - | - | - |
| `[` `]` | glob patterns | - | - | - |
| `*` `?` | wildcards | - | - | - |

**Safe special characters:** `_` `-` `.` `^` `:` `,` `=` `+`

### 2. Double-Click to Copy

When you double-click text, the OS selects a "word" bounded by non-word characters.

**Word characters (stay selected):**
```
a-z  A-Z  0-9  _ (underscore!)
```

**Word boundaries (break selection):**
```
-  .  ,  :  ;  !  @  #  $  %  ^  &  *  (  )  space
```

Test it yourself:
```
Kp4x.Tm9n-Bc2w_Qf7v    ← double-click selects ONE segment (bad!)
Kp4x_Tm9n_Bc2w_Qf7v    ← double-click selects WHOLE thing (good!)
```

### 3. The Underscore

The underscore `_` is special. It's **both**:
- A "special character" (satisfies "must contain symbol" website requirements)
- A "word character" (doesn't break double-click selection)

Thus our default format.

### 4. Human-Readable Segments

Breaking passwords into 4-character segments makes them:
- Easier to read
- Easier to verify ("did I type that right?")
- Easier to dictate over the phone
- Easier to type on mobile keyboards

### 5. Satisfy Website Requirements

Most websites require passwords with:
- Uppercase letters ✓
- Lowercase letters ✓
- Numbers ✓
- Special characters ✓ (underscore counts!)

The default format satisfies all of these.

## Entropy & Security

### How much entropy do we have?

| Mode | Calculation | Entropy |
|------|-------------|---------|
| **Default** | (26 × 26 × 10 × 62 × 24)^4 segments | **~93 bits** |
| **Simple** | 31^16 chars (unambiguous charset) | **~79 bits** |
| **Paranoid** | Same as default | **~93 bits** |

### How much do you need?

| Bits | Time to crack (1B guesses/sec) | Protection Level |
|------|-------------------------------|------------------|
| 64 | ~585 years | Online attacks (with rate limiting) |
| 80 | ~38 million years | Offline attacks, commodity hardware |
| **93** | **~315 billion years** | **Our default** |
| 128 | ~1 × 10^22 years | Quantum-resistant |

*Note: Age of universe ≈ 1.4 × 10^10 years*

[NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) specifies 64 bits as the threshold below which rate-limiting is required for passwords. The 112-bit minimum you may have heard about is for *cryptographic keys* (AES, TLS sessions), not passwords—keys face offline attacks at hardware speed with no rate limiting. Passwords are protected by hashing and rate limiting, so 64+ bits is plenty. Our 93 bits is 22× the age of the universe.

### Comparison

| Generator | Default Entropy |
|-----------|-----------------|
| **genpassword** | **~93 bits** |
| Bitwarden (14 chars) | ~90 bits |
| 1Password (20 chars) | ~130 bits |
| Random 16 alphanumeric | ~95 bits |

Our ~93 bits is solid—22× the age of the universe to brute-force at 1 billion guesses/second.

## Modes

### Default: Readable Strong
```
Kp4x_Tm9n_Bc2w_Qf7v
```
- Mixed case + digits + underscore separators
- Double-click selects entire password
- Satisfies most website requirements
- ~95 bits of entropy

### Simple: Easy to Dictate
```
hn4k_xp2m_b7qf_9dtc
```
- Lowercase + digits only (no ambiguous characters: 0, O, l, 1, I)
- Perfect for dictating over the phone
- Easy to type on mobile or foreign keyboards
- No shift key required

### Paranoid: Maximum Symbols
```
Kp4x.Tm9n-Bc2w!Qf7v
```
- Multiple special character types
- For sites requiring "real" symbols
- Breaks double-click selection (explicit tradeoff)

## Usage

```bash
# Default (readable strong)
$ genpassword
Kp4x_Tm9n_Bc2w_Qf7v

# Generate multiple
$ genpassword -n 5
Hb7m_Qx4k_Tn2w_Fp9c
Wc3n_Rv8t_Km5x_Bq2j
Yd6p_Fn4h_Tw9m_Kc3b
Np8r_Bv2m_Qf6x_Ht4w
Jk9c_Dm3p_Xn7v_Ws5t

# Simple mode (easy to dictate)
$ genpassword --simple
hn4k_xp2m_b7qf_9dtc

# Paranoid mode (max symbols)
$ genpassword --paranoid
Kp4x.Tm9n-Bc2w!Qf7v

# Longer passwords - more segments
$ genpassword --segments 5
pF3M_im4B_HqY4_19Rk_0LaF

# Longer passwords - longer segments
$ genpassword --segment-length 5
Bu9Vo_75DDc_nGNx4_qcW4H

# Custom exact length
$ genpassword -l 30
y5tY_vO2c_56Wu_wUR9_Xw82_Nj3u

# Show all profiles
$ genpassword --list
```

## When to Use Each Mode

| Mode | Use Case |
|------|----------|
| **Default** | Most situations. Passwords you'll copy-paste. |
| **Simple** | Dictating over phone. Typing on mobile. Teaching non-tech users. |
| **Paranoid** | Sites that reject underscore as "not a symbol". Maximum entropy. |

## Longer Passwords: Strategies & Use Cases

The default 19-character password (~93 bits) is already excellent for most uses, but you might want longer passwords for:
- High-value accounts (banking, email, password managers)
- Compliance requirements (some industries mandate minimum entropy)
- Peace of mind ("future-proofing" against quantum computing)
- Systems with unusually long maximum password lengths

### Strategy 1: Add More Segments (Recommended)

**Best for: Maximum readability and visual rhythm**

```bash
# 5 segments = 24 chars, ~116 bits
$ genpassword --segments 5
pF3M_im4B_HqY4_19Rk_0LaF

# 6 segments = 29 chars, ~139 bits
$ genpassword --segments 6
Kp4x_Tm9n_Bc2w_Qf7v_Hn3m_Xt8y

# 8 segments = 39 chars, ~186 bits (overkill for most)
$ genpassword --segments 8
```

**Why this works:**
- Maintains 4-character chunks (easiest to read)
- Natural visual rhythm
- Easy to verify ("did I type that correctly?")
- Scales linearly: +5 chars = +23 bits entropy

**Use cases:**
- Password manager master password
- Root/administrator accounts
- Encryption passphrases
- Long-lived credentials

### Strategy 2: Longer Segments

**Best for: Maximum entropy per character**

```bash
# 4 segments × 5 chars = 23 chars, ~126 bits
$ genpassword --segment-length 5
Bu9Vo_75DDc_nGNx4_qcW4H

# 4 segments × 6 chars = 27 chars, ~160 bits
$ genpassword --segment-length 6
Kp4xYm_Tm9nBc_2wQf7v_Hn3mXt
```

**Why this works:**
- More entropy-efficient (5.48 bits/char vs 4.85)
- Slightly shorter overall for same security
- Still relatively readable

**Trade-off:**
- 5-6 character chunks harder to scan than 4-character
- Requires more concentration to verify

### Strategy 3: Use Length Flag for Specific Requirements

**Best for: Meeting exact character requirements**

```bash
# "I need exactly 30 characters"
$ genpassword -l 30
y5tY_vO2c_56Wu_wUR9_Xw82_Nj3u

# "I need at least 40 characters"
$ genpassword -l 40
```

**Note:** The `-l` flag calculates segments automatically, maintaining 4-char segments where possible.

### Recommended Presets by Use Case

| Use Case | Command | Length | Entropy | Notes |
|----------|---------|--------|---------|-------|
| **Standard** (default) | `genpassword` | 19 chars | ~93 bits | Excellent for 99% of cases |
| **High-value accounts** | `genpassword --segments 5` | 24 chars | ~116 bits | Email, banking, password manager |
| **Maximum security** | `genpassword --segments 6` | 29 chars | ~139 bits | Root access, encryption keys |
| **Compliance (100+ bits)** | `genpassword --segment-length 5` | 23 chars | ~126 bits | Meets SOC2/ISO27001 guidelines |
| **Future-proof** | `genpassword --segments 8` | 39 chars | ~186 bits | Quantum-resistant overkill |

### Password Manager Integration

**Master Password Strategy:**

For your password manager's master password, use a longer, memorable approach:

```bash
# Option 1: More segments for high entropy
$ genpassword --segments 6
Kp4x_Tm9n_Bc2w_Qf7v_Hn3m_Xt8y   # 139 bits

# Option 2: Simple mode for easier manual typing
$ genpassword --simple --segments 5
hn4k_xp2m_b7qf_9dtc_t7wr   # ~99 bits, no shift key

# Option 3: Custom length for specific requirement
$ genpassword -l 32
```

**Tips for password managers:**
1. **Master password:** Use 5-6 segments (116-139 bits). You'll type this frequently, so balance security with usability.
2. **Generated passwords:** Use default (93 bits) for most accounts. The password manager handles the complexity.
3. **High-value accounts:** Use 5 segments even within your password manager for critical accounts.
4. **Recovery codes:** Generate multiple with `-n 5` and store separately.

### Combining Strategies: Creative Approaches

**1. Passphrase + Structure**

Use genpassword segments as "word substitutes":
```bash
$ genpassword --segments 4 --no-copy
Kp4x_Tm9n_Bc2w_Qf7v

# Mentally map: "Kp4x is my cat, Tm9n likes Bc2w, remember Qf7v"
```

**2. Layered Security**

For different account tiers:
```bash
# Tier 1 (low value): Default
$ genpassword

# Tier 2 (important): 5 segments
$ genpassword --segments 5

# Tier 3 (critical): 6 segments
$ genpassword --segments 6
```

**3. Simple Mode for Shared Access**

When dictating to others or sharing temporarily:
```bash
$ genpassword --simple --segments 5
hn4k_xp2m_b7qf_9dtc_x6wq   # No ambiguous chars, easier to communicate
```

### Security vs Usability Trade-offs

| Factor | Default (4×4) | 5 Segments | 6 Segments | Longer Segments |
|--------|---------------|------------|------------|-----------------|
| **Entropy** | 93 bits ✓ | 116 bits ✓✓ | 139 bits ✓✓✓ | 126+ bits ✓✓ |
| **Readability** | Excellent | Very Good | Good | Fair |
| **Typing speed** | Fast | Medium | Slower | Medium |
| **Copy-paste** | Easy | Easy | Easy | Easy |
| **Mobile typing** | Good | Fair | Challenging | Fair |
| **Memorability** | Low | Lower | Lowest | Low |

**General guidance:**
- **Below 64 bits:** Vulnerable to offline attacks (don't go here)
- **64-80 bits:** Acceptable for low-value accounts with rate limiting
- **80-100 bits:** Good for most accounts
- **93 bits (our default):** Excellent for general use
- **100-128 bits:** High-value accounts, compliance requirements
- **128+ bits:** Future-proofing, quantum resistance, overkill

### When NOT to Use Longer Passwords

❌ **Don't use longer passwords when:**
- The system has a low maximum length (some old systems cap at 16-20 chars)
- You need to type it frequently on mobile devices
- It's for a low-value account (newsletter signups, forums)
- The system has aggressive rate limiting (length won't help against 3-tries-then-lockout)

✅ **Do use longer passwords when:**
- It's a password manager master password
- It's for root/admin access
- It's for encryption keys or certificates
- Compliance requires 100+ bits of entropy
- The account has high value (financial, email, identity)
- It will be stored in a password manager (never typed)

## Installation

```bash
# Clone the repo
git clone https://github.com/realgenekim/genpassword.git
cd genpassword

# Install to ~/bin
make install

# Or run directly
python genpassword.py
```

**Note:** Auto-copy to clipboard tested on macOS. Linux/Windows support included but untested.

## Why Not Just Use...

**1Password / LastPass / Bitwarden / etc.?**

They're great! But they generate passwords like `x#7$Kp@9!mQ` that:
- Break when pasted into shell commands
- Break in database connection strings
- Break in URLs
- Are hard to read and verify

**This tool?**

Generates passwords that are safe by default, readable, and work everywhere.

Wrote with Claude Code, which took about as long as it took to write [this tweet](https://x.com/RealGeneKim/status/2009399795996348576) where I complained about the Postgres password problem.

## References

- [IETF OPAR Draft](https://datatracker.ietf.org/doc/html/draft-bwilliams-kitten-opar-00) - Open Password Automation Recipe
- [OWASP Password Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## License

MIT
