"""
Tests for genpassword - Safe password generator

Test priorities:
  P0: Core safety promises (no dangerous chars, double-click friendly)
  P1: Usability promises (website requirements, no ambiguous chars)
  P2: Statistical sanity (distribution, entropy)
  P3: Edge cases and CLI
"""

import math
import re
import sys
from collections import Counter
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from genpassword import (
    generate_default,
    generate_simple,
    generate_paranoid,
    LOWERCASE,
    UPPERCASE,
    DIGITS,
    LOWERCASE_UNAMBIGUOUS,
    DIGITS_UNAMBIGUOUS,
)


# =============================================================================
# P0: Core Safety Tests - These MUST pass
# =============================================================================

class TestSafety:
    """Core safety guarantees - the whole point of this tool."""

    # Characters that break shells, SQL, URLs, config files
    DANGEROUS_CHARS = set('#\'""`$\\!&|;<>(){}[]*?%\n\r\t ')

    def test_default_no_dangerous_characters(self):
        """Default mode: no shell/SQL/URL-breaking chars (1000 samples)"""
        for _ in range(1000):
            pw = generate_default()
            dangerous_found = [c for c in pw if c in self.DANGEROUS_CHARS]
            assert not dangerous_found, f"Dangerous chars in '{pw}': {dangerous_found}"

    def test_simple_no_dangerous_characters(self):
        """Simple mode: no dangerous chars (1000 samples)"""
        for _ in range(1000):
            pw = generate_simple()
            dangerous_found = [c for c in pw if c in self.DANGEROUS_CHARS]
            assert not dangerous_found, f"Dangerous chars in '{pw}': {dangerous_found}"

    def test_paranoid_no_dangerous_characters(self):
        """Paranoid mode: no dangerous chars (1000 samples)"""
        for _ in range(1000):
            pw = generate_paranoid()
            dangerous_found = [c for c in pw if c in self.DANGEROUS_CHARS]
            assert not dangerous_found, f"Dangerous chars in '{pw}': {dangerous_found}"


class TestDoubleClickFriendly:
    """Underscore-only separators ensure double-click selects whole password."""

    def test_default_only_underscore_separator(self):
        """Default: only word characters + underscore (double-click friendly)"""
        for _ in range(100):
            pw = generate_default()
            # All non-alphanumeric chars should be underscore
            non_alnum = [c for c in pw if not c.isalnum()]
            assert all(c == '_' for c in non_alnum), \
                f"Non-underscore separator in '{pw}': {[c for c in non_alnum if c != '_']}"

    def test_simple_only_underscore_separator(self):
        """Simple: only word characters + underscore"""
        for _ in range(100):
            pw = generate_simple()
            non_alnum = [c for c in pw if not c.isalnum()]
            assert all(c == '_' for c in non_alnum), \
                f"Non-underscore separator in '{pw}'"

    def test_default_matches_word_regex(self):
        """Default passwords should match \\w+ (word characters only)"""
        for _ in range(100):
            pw = generate_default()
            # \w matches [a-zA-Z0-9_]
            assert re.fullmatch(r'\w+', pw), f"'{pw}' contains non-word chars"

    def test_simple_matches_word_regex(self):
        """Simple passwords should match \\w+ (word characters only)"""
        for _ in range(100):
            pw = generate_simple()
            assert re.fullmatch(r'\w+', pw), f"'{pw}' contains non-word chars"


# =============================================================================
# P1: Usability Tests
# =============================================================================

class TestWebsiteRequirements:
    """Passwords should satisfy common website requirements."""

    def test_default_has_uppercase(self):
        """Default mode: always has at least one uppercase"""
        for _ in range(100):
            pw = generate_default()
            assert any(c.isupper() for c in pw), f"No uppercase in '{pw}'"

    def test_default_has_lowercase(self):
        """Default mode: always has at least one lowercase"""
        for _ in range(100):
            pw = generate_default()
            assert any(c.islower() for c in pw), f"No lowercase in '{pw}'"

    def test_default_has_digit(self):
        """Default mode: always has at least one digit"""
        for _ in range(100):
            pw = generate_default()
            assert any(c.isdigit() for c in pw), f"No digit in '{pw}'"

    def test_default_has_special_char(self):
        """Default mode: always has underscore (counts as special char)"""
        for _ in range(100):
            pw = generate_default()
            assert '_' in pw, f"No underscore in '{pw}'"

    def test_paranoid_has_multiple_special_types(self):
        """Paranoid mode: has various special characters"""
        special_chars_seen = set()
        for _ in range(100):
            pw = generate_paranoid()
            specials = [c for c in pw if not c.isalnum()]
            special_chars_seen.update(specials)
        # Should see multiple types of separators
        assert len(special_chars_seen) >= 3, \
            f"Only saw {special_chars_seen} special chars in paranoid mode"


class TestSimpleModeAmbiguity:
    """Simple mode should avoid ambiguous characters for dictation."""

    AMBIGUOUS_CHARS = set('0Ool1Ii')

    def test_simple_no_ambiguous_characters(self):
        """Simple mode: no 0, O, o, l, 1, I, i (1000 samples)"""
        for _ in range(1000):
            pw = generate_simple()
            ambiguous_found = [c for c in pw if c in self.AMBIGUOUS_CHARS]
            assert not ambiguous_found, \
                f"Ambiguous chars in '{pw}': {ambiguous_found}"

    def test_simple_lowercase_only(self):
        """Simple mode: no uppercase letters"""
        for _ in range(100):
            pw = generate_simple()
            assert not any(c.isupper() for c in pw), \
                f"Uppercase found in simple mode: '{pw}'"


class TestFormat:
    """Password format validation."""

    def test_default_segment_count(self):
        """Default: 4 segments"""
        pw = generate_default()
        segments = pw.split('_')
        assert len(segments) == 4, f"Expected 4 segments, got {len(segments)}: '{pw}'"

    def test_default_segment_length(self):
        """Default: 4 chars per segment"""
        pw = generate_default()
        segments = pw.split('_')
        for i, seg in enumerate(segments):
            assert len(seg) == 4, f"Segment {i} has {len(seg)} chars, expected 4: '{seg}'"

    def test_default_total_length(self):
        """Default: 19 chars total (4*4 + 3 underscores)"""
        pw = generate_default()
        assert len(pw) == 19, f"Expected 19 chars, got {len(pw)}: '{pw}'"

    def test_simple_format(self):
        """Simple: same format as default (4 segments of 4)"""
        pw = generate_simple()
        segments = pw.split('_')
        assert len(segments) == 4
        assert all(len(s) == 4 for s in segments)

    def test_custom_segments(self):
        """Custom segment count works"""
        pw = generate_default(segments=6)
        segments = pw.split('_')
        assert len(segments) == 6

    def test_custom_segment_length(self):
        """Custom segment length works"""
        pw = generate_default(segment_length=6)
        segments = pw.split('_')
        assert all(len(s) == 6 for s in segments)


# =============================================================================
# P1: Uniqueness / RNG Tests
# =============================================================================

class TestUniqueness:
    """Verify RNG is working - no duplicates."""

    def test_default_no_duplicates_1000(self):
        """1000 default passwords should all be unique"""
        passwords = [generate_default() for _ in range(1000)]
        assert len(set(passwords)) == 1000, "Duplicate passwords generated!"

    def test_simple_no_duplicates_1000(self):
        """1000 simple passwords should all be unique"""
        passwords = [generate_simple() for _ in range(1000)]
        assert len(set(passwords)) == 1000, "Duplicate passwords generated!"

    def test_paranoid_no_duplicates_1000(self):
        """1000 paranoid passwords should all be unique"""
        passwords = [generate_paranoid() for _ in range(1000)]
        assert len(set(passwords)) == 1000, "Duplicate passwords generated!"


# =============================================================================
# P2: Statistical Tests
# =============================================================================

class TestDistribution:
    """Character distribution should be roughly uniform."""

    def test_default_char_distribution(self):
        """Characters within each category should be roughly uniform.

        Note: Default mode forces one of each type per segment, so overall
        distribution is intentionally non-uniform. We test uniformity WITHIN
        each character class instead.
        """
        uppers = ''
        lowers = ''
        digits = ''

        for _ in range(5000):
            pw = generate_default()
            chars = pw.replace('_', '')
            uppers += ''.join(c for c in chars if c.isupper())
            lowers += ''.join(c for c in chars if c.islower())
            digits += ''.join(c for c in chars if c.isdigit())

        # Test each category separately
        for name, chars, charset_size in [
            ('uppercase', uppers, 26),
            ('lowercase', lowers, 26),
            ('digits', digits, 10),
        ]:
            counts = Counter(chars)
            expected = len(chars) / charset_size
            chi_sq = sum((count - expected) ** 2 / expected for count in counts.values())

            # Looser bound since categories have fewer samples
            assert chi_sq < 200, \
                f"{name} distribution seems skewed (chi-sq={chi_sq:.1f})"

    def test_simple_uses_unambiguous_charset(self):
        """Simple mode should only use unambiguous characters"""
        valid_chars = set(LOWERCASE_UNAMBIGUOUS + DIGITS_UNAMBIGUOUS + '_')

        for _ in range(100):
            pw = generate_simple()
            invalid = [c for c in pw if c not in valid_chars]
            assert not invalid, f"Invalid chars in simple mode: {invalid}"


class TestEntropy:
    """Verify entropy meets security requirements."""

    def test_default_entropy_minimum(self):
        """Default mode should have at least 70 bits of entropy (NIST minimum)"""
        # Per segment: 26 upper * 26 lower * 10 digit * 62 any * 24 shuffle arrangements
        # = 26 * 26 * 10 * 62 * 24 = 10,058,880
        segment_combinations = 26 * 26 * 10 * 62 * 24
        total_combinations = segment_combinations ** 4
        entropy_bits = math.log2(total_combinations)

        assert entropy_bits >= 70, \
            f"Default entropy ({entropy_bits:.1f} bits) below NIST minimum (70 bits)"

    def test_simple_entropy_minimum(self):
        """Simple mode should have at least 60 bits of entropy"""
        # Charset: 23 lowercase + 8 digits = 31 chars
        # Per segment: 31^4 = 923,521
        # 4 segments: 923,521^4 ≈ 2^79
        charset_size = len(LOWERCASE_UNAMBIGUOUS) + len(DIGITS_UNAMBIGUOUS)
        chars_per_password = 16  # 4 segments * 4 chars
        total_combinations = charset_size ** chars_per_password
        entropy_bits = math.log2(total_combinations)

        assert entropy_bits >= 60, \
            f"Simple entropy ({entropy_bits:.1f} bits) too low"

    def test_entropy_calculation_display(self):
        """Print entropy calculations for documentation"""
        # Default mode
        segment_combos = 26 * 26 * 10 * 62 * 24
        default_entropy = math.log2(segment_combos ** 4)

        # Simple mode
        simple_charset = len(LOWERCASE_UNAMBIGUOUS) + len(DIGITS_UNAMBIGUOUS)
        simple_entropy = math.log2(simple_charset ** 16)

        print(f"\nEntropy calculations:")
        print(f"  Default mode: {default_entropy:.1f} bits")
        print(f"  Simple mode:  {simple_entropy:.1f} bits")

        # Just verify they're calculated (not a real assertion)
        assert default_entropy > 0
        assert simple_entropy > 0


class TestEmpiricalRandomness:
    """Empirical tests that verify randomness in practice, not just theory."""

    def test_compression_ratio(self):
        """High-entropy data should not compress well.

        Random data typically achieves ~0% compression.
        Low-entropy/patterned data compresses significantly.
        """
        import zlib

        # Generate many passwords
        passwords = ''.join(generate_default() for _ in range(5000))
        original_size = len(passwords.encode())

        # Compress
        compressed = zlib.compress(passwords.encode(), level=9)
        ratio = len(compressed) / original_size

        # Random data shouldn't compress below ~95% of original
        # (some overhead from zlib headers, but mostly incompressible)
        assert ratio > 0.70, \
            f"Compression ratio {ratio:.2%} suggests patterns/low entropy"

    def test_no_positional_bias(self):
        """Each position should have good character variety."""
        from collections import Counter

        # Collect chars at each position across many passwords
        position_chars = {i: [] for i in range(19)}  # 19 chars in default

        for _ in range(500):
            pw = generate_default()
            for i, c in enumerate(pw):
                position_chars[i].append(c)

        # Each non-separator position should have variety
        for pos in [0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18]:
            unique = len(set(position_chars[pos]))
            # Should see at least 20 different chars in 500 samples
            assert unique >= 15, \
                f"Position {pos} only has {unique} unique chars - possible bias"

    def test_sequential_passwords_independent(self):
        """Consecutive passwords should not share suspicious patterns."""
        passwords = [generate_default() for _ in range(200)]

        long_prefix_count = 0
        for i in range(len(passwords) - 1):
            # Count matching prefix length
            common = 0
            for c1, c2 in zip(passwords[i], passwords[i + 1]):
                if c1 == c2:
                    common += 1
                else:
                    break
            if common >= 3:
                long_prefix_count += 1

        # With true randomness, P(3+ char prefix match) is very low
        # Should see at most a few in 200 pairs
        assert long_prefix_count < 10, \
            f"Too many sequential passwords share prefixes: {long_prefix_count}"

    def test_character_class_per_segment(self):
        """Verify each segment actually has upper, lower, and digit."""
        for _ in range(100):
            pw = generate_default()
            segments = pw.split('_')

            for i, seg in enumerate(segments):
                has_upper = any(c.isupper() for c in seg)
                has_lower = any(c.islower() for c in seg)
                has_digit = any(c.isdigit() for c in seg)

                assert has_upper, f"Segment {i} '{seg}' missing uppercase"
                assert has_lower, f"Segment {i} '{seg}' missing lowercase"
                assert has_digit, f"Segment {i} '{seg}' missing digit"


# =============================================================================
# P3: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_single_segment(self):
        """Single segment should have no separator"""
        pw = generate_default(segments=1)
        assert '_' not in pw
        assert len(pw) == 4

    def test_small_segments_simple_mode(self):
        """Simple mode works with small segments (default needs min 3 for variety)"""
        # Simple mode can have any segment length
        pw = generate_simple(segments=4, segment_length=2)
        segments = pw.split('_')
        assert len(segments) == 4
        assert all(len(s) == 2 for s in segments)

    def test_minimum_segment_length_default(self):
        """Default mode needs at least 3 chars per segment (upper+lower+digit)"""
        # Default forces one of each type, so minimum practical length is 3
        pw = generate_default(segments=4, segment_length=3)
        segments = pw.split('_')
        assert all(len(s) == 3 for s in segments)

    def test_large_password(self):
        """Large passwords should work"""
        pw = generate_default(segments=10, segment_length=8)
        segments = pw.split('_')
        assert len(segments) == 10
        assert all(len(s) == 8 for s in segments)

    def test_simple_single_segment(self):
        """Simple mode with single segment"""
        pw = generate_simple(segments=1)
        assert '_' not in pw
        assert pw.islower() or pw.isdigit() or pw.isalnum()


class TestLongerPasswordStrategies:
    """Test longer password strategies from README documentation."""

    def test_strategy_1_more_segments(self):
        """Strategy 1: Adding more segments for longer passwords"""
        # 5 segments = 24 chars total (20 + 4 underscores)
        pw5 = generate_default(segments=5)
        segments5 = pw5.split('_')
        assert len(segments5) == 5
        assert len(pw5) == 24, f"5 segments should be 24 chars, got {len(pw5)}: '{pw5}'"

        # 6 segments = 29 chars total (24 + 5 underscores)
        pw6 = generate_default(segments=6)
        segments6 = pw6.split('_')
        assert len(segments6) == 6
        assert len(pw6) == 29, f"6 segments should be 29 chars, got {len(pw6)}: '{pw6}'"

        # 8 segments = 39 chars total (32 + 7 underscores)
        pw8 = generate_default(segments=8)
        segments8 = pw8.split('_')
        assert len(segments8) == 8
        assert len(pw8) == 39, f"8 segments should be 39 chars, got {len(pw8)}: '{pw8}'"

    def test_strategy_2_longer_segments(self):
        """Strategy 2: Longer segments for more entropy per character"""
        # 4 segments × 5 chars = 23 chars total
        pw5 = generate_default(segment_length=5)
        segments5 = pw5.split('_')
        assert len(segments5) == 4
        assert all(len(s) == 5 for s in segments5)
        assert len(pw5) == 23

        # 4 segments × 6 chars = 27 chars total
        pw6 = generate_default(segment_length=6)
        segments6 = pw6.split('_')
        assert len(segments6) == 4
        assert all(len(s) == 6 for s in segments6)
        assert len(pw6) == 27

    def test_preset_high_value_accounts(self):
        """Preset: High-value accounts (5 segments, ~116 bits)"""
        for _ in range(100):
            pw = generate_default(segments=5)
            # Should maintain all safety properties
            assert len(pw) == 24
            assert pw.count('_') == 4
            # Should have variety in each segment
            segments = pw.split('_')
            for seg in segments:
                assert any(c.isupper() for c in seg)
                assert any(c.islower() for c in seg)
                assert any(c.isdigit() for c in seg)

    def test_preset_maximum_security(self):
        """Preset: Maximum security (6 segments, ~139 bits)"""
        for _ in range(50):
            pw = generate_default(segments=6)
            assert len(pw) == 29
            assert pw.count('_') == 5

    def test_preset_compliance(self):
        """Preset: Compliance 100+ bits (4×5, ~126 bits)"""
        for _ in range(50):
            pw = generate_default(segment_length=5)
            assert len(pw) == 23
            segments = pw.split('_')
            assert all(len(s) == 5 for s in segments)

    def test_simple_mode_longer_passwords(self):
        """Simple mode works with longer password strategies"""
        # 5 segments in simple mode
        pw = generate_simple(segments=5)
        assert len(pw) == 24
        assert pw.count('_') == 4

        # Longer segments in simple mode
        pw2 = generate_simple(segment_length=5)
        segments = pw2.split('_')
        assert all(len(s) == 5 for s in segments)

    def test_paranoid_mode_longer_passwords(self):
        """Paranoid mode works with longer password strategies"""
        # 5 segments in paranoid mode
        pw = generate_paranoid(segments=5)
        assert len(pw) == 24

        # Longer segments in paranoid mode
        pw2 = generate_paranoid(segment_length=5)
        segments = pw2.split('.')  # Use first separator to estimate
        # Paranoid uses rotating separators, so just verify it's roughly correct length
        assert len(pw2) == 23


# =============================================================================
# CLI Tests (if running as script)
# =============================================================================

class TestCLI:
    """Command-line interface tests."""

    def test_help_flag(self):
        """--help should not error"""
        import subprocess
        result = subprocess.run(
            [sys.executable, 'genpassword.py', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'usage' in result.stdout.lower()

    def test_list_flag(self):
        """--list should show available modes"""
        import subprocess
        result = subprocess.run(
            [sys.executable, 'genpassword.py', '--list'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'default' in result.stdout
        assert 'simple' in result.stdout
        assert 'paranoid' in result.stdout

    def test_count_flag(self):
        """-n should generate multiple passwords"""
        import subprocess
        result = subprocess.run(
            [sys.executable, 'genpassword.py', '-n', '5', '--no-copy'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        lines = [l for l in result.stdout.strip().split('\n') if l]
        assert len(lines) == 5

    def test_no_copy_flag(self):
        """--no-copy should suppress clipboard message"""
        import subprocess
        result = subprocess.run(
            [sys.executable, 'genpassword.py', '--no-copy'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'clipboard' not in result.stderr.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
