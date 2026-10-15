"""
Test that every theme defines ALL required keys used by the UI panels.
This test prevents KeyError crashes when switching themes.
"""
import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from theme import THEMES, _generate_tk_theme, _GATO_A_NOITE

# Every key that the UI code references via C["key"].
# Derived from: grep -oP 'C\["([^"]+)"\]' panels/**/*.py panels/*.py app.py | sort -u
REQUIRED_KEYS = [
    "bg_dark", "bg_darker", "bg_darkest", "bg_widget", "bg_toolbar",
    "bg_button", "bg_button_hover", "bg_subtle", "bg_subtle_hover",
    "fg_primary", "fg_secondary", "fg_muted", "fg_dim",
    "accent_blue", "accent_blue_h", "accent_blue_hover",
    "accent_orange", "accent_green", "accent_green_h",
    "accent_purple", "accent_red", "accent_red_h",
    "sidebar_bg", "sidebar_active",
    "select_bg", "select_fg",
    "border", "error_red", "error_red_h",
]


class TestThemeKeysCompleteness:
    """Verify every registered theme has all required keys."""

    @pytest.mark.parametrize("theme_name", list(THEMES.keys()))
    def test_theme_has_all_required_keys(self, theme_name):
        theme = THEMES[theme_name]
        missing = [k for k in REQUIRED_KEYS if k not in theme]
        assert not missing, (
            f"Theme '{theme_name}' is missing keys: {missing}"
        )

    @pytest.mark.parametrize("theme_name", list(THEMES.keys()))
    def test_theme_values_are_hex_colors(self, theme_name):
        theme = THEMES[theme_name]
        for key in REQUIRED_KEYS:
            if key in theme:
                val = theme[key]
                assert isinstance(val, str) and val.startswith("#"), (
                    f"Theme '{theme_name}' key '{key}' = {val!r} is not a hex color"
                )

    def test_gato_a_noite_is_default_template(self):
        """Gato a Noite must be the superset template."""
        missing = [k for k in REQUIRED_KEYS if k not in _GATO_A_NOITE]
        assert not missing, f"Default theme missing keys: {missing}"

    def test_generated_theme_has_all_keys(self):
        """Auto-generated themes from _generate_tk_theme must also have all keys."""
        sample = {"primaryColor": "#FF4B4B", "backgroundColor": "#FFFFFF",
                  "secondaryBackgroundColor": "#F0F2F6", "textColor": "#31333F"}
        generated = _generate_tk_theme(sample)
        missing = [k for k in REQUIRED_KEYS if k not in generated]
        assert not missing, f"Generated theme missing keys: {missing}"
