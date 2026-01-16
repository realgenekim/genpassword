#!/usr/bin/env python3
"""
genpassword - Safe password generator

Generates passwords that:
- Don't break shells, databases, or URLs
- Can be double-click selected (underscore separators)
- Are readable (4-char segments)
- Satisfy most website requirements (upper, lower, digit, special)
"""

import argparse
import secrets
import subprocess
import sys
from typing import Optional


# Character sets
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"

# Unambiguous: no 0, O, o, l, 1, I, i
LOWERCASE_UNAMBIGUOUS = "abcdefghjkmnpqrstuvwxyz"
DIGITS_UNAMBIGUOUS = "23456789"

# Safe special characters (don't break shells, SQL, URLs)
SAFE_SPECIALS = "-_.^:,=+"


def generate_segment(length: int, charset: str) -> str:
    """Generate a random segment from the given charset."""
    return ''.join(secrets.choice(charset) for _ in range(length))


def generate_default(segments: int = 4, segment_length: int = 4) -> str:
    """
    Generate readable strong password.
    Format: Kp4x_Tm9n_Bc2w_Qf7v

    - Mixed case + digits
    - Underscore separators (special char + word char = double-click friendly)
    - Each segment has at least one of each type
    """
    charset = LOWERCASE + UPPERCASE + DIGITS
    result_segments = []

    for i in range(segments):
        # Ensure each segment has variety
        segment = [
            secrets.choice(UPPERCASE),
            secrets.choice(LOWERCASE),
            secrets.choice(DIGITS),
        ]
        # Fill remaining with random from full charset
        while len(segment) < segment_length:
            segment.append(secrets.choice(charset))

        # Shuffle the segment
        secrets.SystemRandom().shuffle(segment)
        result_segments.append(''.join(segment))

    return '_'.join(result_segments)


def generate_simple(segments: int = 4, segment_length: int = 4) -> str:
    """
    Generate simple password for dictating/typing.
    Format: hn4k_xp2m_b7qf_9dtc

    - Lowercase + digits only
    - No ambiguous characters (0, O, l, 1, I)
    - Easy to dictate over phone
    - No shift key required
    """
    charset = LOWERCASE_UNAMBIGUOUS + DIGITS_UNAMBIGUOUS
    result_segments = []

    for _ in range(segments):
        segment = generate_segment(segment_length, charset)
        result_segments.append(segment)

    return '_'.join(result_segments)


def generate_paranoid(segments: int = 4, segment_length: int = 4) -> str:
    """
    Generate paranoid password with multiple special chars.
    Format: Kp4x.Tm9n-Bc2w!Qf7v

    - Mixed case + digits + rotating special separators
    - Maximum symbol variety
    - Note: breaks double-click selection (explicit tradeoff)
    """
    charset = LOWERCASE + UPPERCASE + DIGITS
    separators = "._-^"  # Rotate through safe specials
    result_segments = []

    for i in range(segments):
        segment = [
            secrets.choice(UPPERCASE),
            secrets.choice(LOWERCASE),
            secrets.choice(DIGITS),
        ]
        while len(segment) < segment_length:
            segment.append(secrets.choice(charset))

        secrets.SystemRandom().shuffle(segment)
        result_segments.append(''.join(segment))

    # Join with rotating separators
    result = result_segments[0]
    for i, seg in enumerate(result_segments[1:]):
        sep = separators[i % len(separators)]
        result += sep + seg

    return result


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True on success."""
    try:
        if sys.platform == "darwin":
            # macOS
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            return True
        elif sys.platform.startswith("linux"):
            # Linux with xclip or xsel
            try:
                subprocess.run(["xclip", "-selection", "clipboard"],
                             input=text.encode(), check=True)
                return True
            except FileNotFoundError:
                try:
                    subprocess.run(["xsel", "--clipboard", "--input"],
                                 input=text.encode(), check=True)
                    return True
                except FileNotFoundError:
                    return False
        elif sys.platform == "win32":
            # Windows
            subprocess.run(["clip"], input=text.encode(), check=True)
            return True
    except Exception:
        return False
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate safe, readable passwords",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  genpassword                 # Kp4x_Tm9n_Bc2w_Qf7v (default, ~93 bits)
  genpassword --simple        # hn4k_xp2m_b7qf_9dtc (easy to dictate)
  genpassword --paranoid      # Kp4x.Tm9n-Bc2w^Qf7v (max symbols)
  genpassword -n 5            # Generate 5 passwords
  genpassword --no-copy       # Don't copy to clipboard

Longer passwords:
  genpassword --segments 5         # 24 chars, ~116 bits (high-value accounts)
  genpassword --segments 6         # 29 chars, ~139 bits (maximum security)
  genpassword --segment-length 5   # 23 chars, ~126 bits (compliance)
  genpassword -l 30                # Exactly 30 chars total

Modes:
  default   Mixed case + digits + underscore separators (~93 bits)
            Double-click friendly, satisfies most site requirements

  simple    Lowercase + digits only, no ambiguous chars (0,O,l,1,I)
            Perfect for dictating or typing on mobile

  paranoid  Multiple special character types
            For sites that reject underscore as "not a symbol"
"""
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--simple", "-s", action="store_true",
                           help="Simple mode: lowercase + digits, easy to dictate")
    mode_group.add_argument("--paranoid", "-p", action="store_true",
                           help="Paranoid mode: multiple special chars")

    parser.add_argument("-n", "--count", type=int, default=1,
                       help="Number of passwords to generate (default: 1)")
    parser.add_argument("-l", "--length", type=int,
                       help="Total length (overrides segment count)")
    parser.add_argument("--segments", type=int, default=4,
                       help="Number of segments (default: 4)")
    parser.add_argument("--segment-length", type=int, default=4,
                       help="Characters per segment (default: 4)")
    parser.add_argument("--no-copy", action="store_true",
                       help="Don't copy to clipboard")
    parser.add_argument("--list", action="store_true",
                       help="Show available modes with examples")

    args = parser.parse_args()

    if args.list:
        print("Available modes:")
        print(f"  default   {generate_default()}  (readable + strong)")
        print(f"  simple    {generate_simple()}  (easy to dictate)")
        print(f"  paranoid  {generate_paranoid()}  (max symbols)")
        return

    # Calculate segments from length if specified
    segments = args.segments
    segment_length = args.segment_length
    if args.length:
        # Account for separators: total = segments * seg_len + (segments - 1)
        # So segments = (length + 1) / (seg_len + 1)
        segments = (args.length + 1) // (segment_length + 1)
        segments = max(1, segments)

    # Generate passwords
    passwords = []
    for _ in range(args.count):
        if args.simple:
            pw = generate_simple(segments, segment_length)
        elif args.paranoid:
            pw = generate_paranoid(segments, segment_length)
        else:
            pw = generate_default(segments, segment_length)
        passwords.append(pw)

    # Output
    for pw in passwords:
        print(pw)

    # Copy last password to clipboard (unless disabled or multiple)
    if not args.no_copy and args.count == 1:
        if copy_to_clipboard(passwords[-1]):
            print("✓ Copied to clipboard", file=sys.stderr)


if __name__ == "__main__":
    main()
