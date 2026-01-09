#!/usr/bin/env python3
"""
calc_entropy.py - Verify entropy calculations for genpassword

This program:
1. Calculates theoretical entropy for all configurations
2. Shows the math step-by-step
3. Compares configurations
4. Validates claims made in documentation
"""

import math
from typing import Tuple

# Character set sizes (matching genpassword.py)
UPPERCASE_SIZE = 26
LOWERCASE_SIZE = 26
DIGIT_SIZE = 10
FULL_CHARSET_SIZE = 62  # 26 + 26 + 10

# Unambiguous charset (simple mode)
LOWERCASE_UNAMBIGUOUS_SIZE = 23  # excludes l, o, i
DIGITS_UNAMBIGUOUS_SIZE = 8      # excludes 0, 1
SIMPLE_CHARSET_SIZE = 31         # 23 + 8


def factorial(n: int) -> int:
    """Calculate n!"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def calc_default_segment_combinations(segment_length: int) -> Tuple[int, float]:
    """
    Calculate combinations for a default mode segment.

    Structure: 1 uppercase + 1 lowercase + 1 digit + (segment_length-3) from full charset
    Then shuffled.

    Returns: (combinations, entropy_bits)
    """
    if segment_length < 3:
        raise ValueError("Default mode requires at least 3 chars per segment")

    # Fixed picks
    upper_choices = UPPERCASE_SIZE      # 26
    lower_choices = LOWERCASE_SIZE      # 26
    digit_choices = DIGIT_SIZE          # 10

    # Remaining positions from full charset
    remaining = segment_length - 3
    remaining_choices = FULL_CHARSET_SIZE ** remaining  # 62^remaining

    # Shuffle arrangements
    shuffle_arrangements = factorial(segment_length)

    # Total combinations
    combinations = (upper_choices * lower_choices * digit_choices *
                   remaining_choices * shuffle_arrangements)

    entropy_bits = math.log2(combinations)

    return combinations, entropy_bits


def calc_simple_segment_combinations(segment_length: int) -> Tuple[int, float]:
    """
    Calculate combinations for a simple mode segment.

    Structure: Pure random from unambiguous charset (31 chars)

    Returns: (combinations, entropy_bits)
    """
    combinations = SIMPLE_CHARSET_SIZE ** segment_length
    entropy_bits = math.log2(combinations)

    return combinations, entropy_bits


def calc_total_entropy(segment_combinations: int, num_segments: int) -> Tuple[int, float]:
    """
    Calculate total combinations and entropy for multiple segments.

    Returns: (total_combinations, total_entropy_bits)
    """
    total_combinations = segment_combinations ** num_segments
    total_entropy_bits = math.log2(total_combinations)

    return total_combinations, total_entropy_bits


def format_large_number(n: int) -> str:
    """Format large number in scientific notation."""
    if n < 1e6:
        return f"{n:,}"
    exp = math.floor(math.log10(n))
    mantissa = n / (10 ** exp)
    return f"{mantissa:.2f} × 10^{exp}"


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def analyze_default_mode(segments: int, segment_length: int):
    """Analyze default mode configuration."""
    seg_combos, seg_entropy = calc_default_segment_combinations(segment_length)
    total_combos, total_entropy = calc_total_entropy(seg_combos, segments)

    total_chars = segments * segment_length + (segments - 1)  # chars + underscores
    bits_per_char = total_entropy / total_chars

    print(f"\n  Configuration: {segments} segments × {segment_length} chars")
    print(f"  Total length:  {total_chars} characters (including separators)")
    print()
    print(f"  Per segment calculation:")
    print(f"    Uppercase choices:    {UPPERCASE_SIZE}")
    print(f"    Lowercase choices:    {LOWERCASE_SIZE}")
    print(f"    Digit choices:        {DIGIT_SIZE}")
    remaining = segment_length - 3
    if remaining > 0:
        print(f"    Remaining ({remaining} chars):     {FULL_CHARSET_SIZE}^{remaining} = {FULL_CHARSET_SIZE**remaining:,}")
    print(f"    Shuffle ({segment_length}!):          {factorial(segment_length):,}")
    print(f"    ─────────────────────────")
    print(f"    Segment combinations: {format_large_number(seg_combos)}")
    print(f"    Segment entropy:      {seg_entropy:.2f} bits")
    print()
    print(f"  Total ({segments} segments):")
    print(f"    Combinations: {format_large_number(total_combos)}")
    print(f"    Entropy:      {total_entropy:.2f} bits")
    print(f"    Bits/char:    {bits_per_char:.2f}")

    return total_entropy


def analyze_simple_mode(segments: int, segment_length: int):
    """Analyze simple mode configuration."""
    seg_combos, seg_entropy = calc_simple_segment_combinations(segment_length)
    total_combos, total_entropy = calc_total_entropy(seg_combos, segments)

    total_chars = segments * segment_length + (segments - 1)
    bits_per_char = total_entropy / total_chars

    print(f"\n  Configuration: {segments} segments × {segment_length} chars")
    print(f"  Total length:  {total_chars} characters (including separators)")
    print()
    print(f"  Charset: {SIMPLE_CHARSET_SIZE} chars (unambiguous lowercase + digits)")
    print(f"    Lowercase (no l,o,i): {LOWERCASE_UNAMBIGUOUS_SIZE}")
    print(f"    Digits (no 0,1):      {DIGITS_UNAMBIGUOUS_SIZE}")
    print()
    print(f"  Per segment: {SIMPLE_CHARSET_SIZE}^{segment_length} = {format_large_number(seg_combos)}")
    print(f"  Segment entropy: {seg_entropy:.2f} bits")
    print()
    print(f"  Total ({segments} segments):")
    print(f"    Combinations: {format_large_number(total_combos)}")
    print(f"    Entropy:      {total_entropy:.2f} bits")
    print(f"    Bits/char:    {bits_per_char:.2f}")

    return total_entropy


def analyze_pure_random(length: int, charset_size: int = FULL_CHARSET_SIZE):
    """Analyze pure random password (no structure)."""
    combinations = charset_size ** length
    entropy = math.log2(combinations)
    bits_per_char = entropy / length

    print(f"\n  Configuration: {length} chars, pure random")
    print(f"  Charset size:  {charset_size}")
    print()
    print(f"  Combinations: {charset_size}^{length} = {format_large_number(combinations)}")
    print(f"  Entropy:      {entropy:.2f} bits")
    print(f"  Bits/char:    {bits_per_char:.2f}")

    return entropy


def main():
    print("\n" + "="*60)
    print("       GENPASSWORD ENTROPY CALCULATOR")
    print("="*60)

    # =========================================================
    print_section("DEFAULT MODE - Current (4 segments × 4 chars)")
    default_4x4 = analyze_default_mode(segments=4, segment_length=4)

    # =========================================================
    print_section("SIMPLE MODE - Current (4 segments × 4 chars)")
    simple_4x4 = analyze_simple_mode(segments=4, segment_length=4)

    # =========================================================
    print_section("OPTION A: 5 segments × 4 chars")
    option_a = analyze_default_mode(segments=5, segment_length=4)

    # =========================================================
    print_section("OPTION B: 4 segments × 5 chars")
    option_b = analyze_default_mode(segments=4, segment_length=5)

    # =========================================================
    print_section("COMPARISON: Pure Random (no structure)")
    print("\n  For comparison - if we just picked random chars:")
    pure_16 = analyze_pure_random(16)
    pure_17 = analyze_pure_random(17)
    pure_20 = analyze_pure_random(20)

    # =========================================================
    print_section("SUMMARY")

    results = [
        ("Default (4×4)", 19, default_4x4),
        ("Simple (4×4)", 19, simple_4x4),
        ("Option A (5×4)", 24, option_a),
        ("Option B (4×5)", 23, option_b),
        ("Pure random 16", 16, pure_16),
        ("Pure random 17", 17, pure_17),
        ("Pure random 20", 20, pure_20),
    ]

    print(f"\n  {'Configuration':<20} {'Length':>8} {'Entropy':>12} {'Bits/char':>10}")
    print(f"  {'-'*20} {'-'*8} {'-'*12} {'-'*10}")
    for name, length, entropy in results:
        bits_per_char = entropy / length
        print(f"  {name:<20} {length:>8} {entropy:>10.1f}b {bits_per_char:>10.2f}")

    # =========================================================
    print_section("VERIFICATION OF CLAIMS")

    claims = [
        ("Default mode ~93 bits", default_4x4, 93, 2),
        ("Simple mode ~79 bits", simple_4x4, 79, 2),
        ("Option A ~116 bits", option_a, 116, 2),
        ("Option B ~126 bits", option_b, 126, 2),  # Corrected from earlier ~140 claim
    ]

    print()
    all_pass = True
    for claim, actual, expected, tolerance in claims:
        diff = abs(actual - expected)
        passed = diff <= tolerance
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}  {claim}")
        print(f"         Expected: ~{expected} bits")
        print(f"         Actual:   {actual:.2f} bits")
        print(f"         Diff:     {diff:.2f} bits")
        print()
        if not passed:
            all_pass = False

    # =========================================================
    print_section("SECURITY CONTEXT")

    print("""
  What does this entropy protect against?

  Bits    Time to crack (1B guesses/sec)    Threat level
  ────    ─────────────────────────────    ────────────
   64     ~585 years                        Online attacks
   80     ~38 million years                 Commodity hardware
   93     ~315 billion years                Current default ✓
  100     ~40 trillion years                Nation-state
  116     ~2.6 × 10^18 years                Option A ✓
  128     ~1 × 10^22 years                  Quantum-resistant
  140     ~4 × 10^25 years                  Option B ✓

  Note: Age of universe ≈ 1.4 × 10^10 years
    """)

    # =========================================================
    print_section("RECOMMENDATION")

    print(f"""
  Current default ({default_4x4:.0f} bits) is already excellent.

  For 100+ bits:
    • Option A (5×4): {option_a:.0f} bits in 24 chars - cleaner visual rhythm
    • Option B (4×5): {option_b:.0f} bits in 23 chars - more entropy-efficient

  Option B wins on efficiency ({option_b/23:.2f} bits/char vs {option_a/24:.2f}).
  Option A wins on readability (4-char chunks easier to scan).

  Both are overkill. Choose based on aesthetics.
    """)

    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
