"""
=============================================================
 Language Manager
 Loads and serves strings for the user's preferred language.
=============================================================
"""

from languages import so, en, ar
from config.config import DEFAULT_LANGUAGE

# Map language codes to their string modules
LANGUAGE_MODULES = {
    "so": so.STRINGS,
    "en": en.STRINGS,
    "ar": ar.STRINGS,
}

# Human-readable names for UI
LANGUAGE_NAMES = {
    "so": "🇸🇴 Soomaali",
    "en": "🇬🇧 English",
    "ar": "🇸🇦 العربية",
}


def get_text(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Retrieve a localized string by key.
    Falls back to Somali, then English if key is missing.

    Usage:
        get_text("welcome", lang="en", user="Ahmed", bot_name="MyBot")
    """
    strings = LANGUAGE_MODULES.get(lang) or LANGUAGE_MODULES.get(DEFAULT_LANGUAGE) or LANGUAGE_MODULES["en"]
    text = strings.get(key) or LANGUAGE_MODULES["en"].get(key, f"[{key}]")
    try:
        return text.format(**kwargs) if kwargs else text
    except KeyError:
        return text  # Return unformatted if variables are missing


def get_all_languages() -> dict:
    """Return dict of {code: name} for all supported languages."""
    return LANGUAGE_NAMES.copy()
