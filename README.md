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

# Custom length
$ genpassword -l 24
Kp4x_Tm9n_Bc2w_Qf7v_Hn3m

# Show all profiles
$ genpassword --list
```

## When to Use Each Mode

| Mode | Use Case |
|------|----------|
| **Default** | Most situations. Passwords you'll copy-paste. |
| **Simple** | Dictating over phone. Typing on mobile. Teaching non-tech users. |
| **Paranoid** | Sites that reject underscore as "not a symbol". Maximum entropy. |

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

**Random bash one-liners?**

```bash
< /dev/urandom tr -dc 'A-Za-z0-9' | head -c 16
```

No control over format, no segments, easy to get wrong.

**This tool?**

Generates passwords that are safe by default, readable, and work everywhere.

Wrote with Claude Code, which took about as long as it took to write [this tweet](https://x.com/RealGeneKim/status/2009399795996348576) where I complained about the Postgres password problem.

## References

- [IETF OPAR Draft](https://datatracker.ietf.org/doc/html/draft-bwilliams-kitten-opar-00) - Open Password Automation Recipe
- [OWASP Password Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## License

MIT
