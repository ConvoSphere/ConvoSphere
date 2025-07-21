"""
Internationalization (i18n) manager for the frontend.

This module provides language detection, translation management, and
internationalization support for the NiceGUI frontend.
"""

import json
from pathlib import Path

from nicegui import app, ui
from utils.constants import SUPPORTED_LANGUAGES
from utils.logger import get_logger


class I18nManager:
    """Frontend internationalization manager."""

    def __init__(self):
        """Initialize the i18n manager."""
        self.current_language = "de"  # Default to German
        self.translations: dict[str, dict[str, str]] = {}
        self.supported_languages = SUPPORTED_LANGUAGES
        self.translations_path = Path(__file__).parent.parent / "i18n"
        self.logger = get_logger(__name__)

        # Load translations
        self._load_translations()

        # Load language preference from storage
        self._load_language_preference()

    def _load_translations(self):
        """Load translation files for all supported languages."""
        try:
            for language_code in self.supported_languages.keys():
                translation_file = self.translations_path / f"{language_code}.json"
                if translation_file.exists():
                    with open(translation_file, encoding="utf-8") as f:
                        self.translations[language_code] = json.load(f)
                    self.logger.info(f"Loaded translations for language: {language_code}")
                else:
                    self.logger.warning(f"Translation file not found: {translation_file}")
                    self.translations[language_code] = {}
        except Exception as e:
            self.logger.error(f"Error loading translations: {e}")
            # Fallback to empty translations
            for language_code in self.supported_languages.keys():
                self.translations[language_code] = {}

    def _load_language_preference(self):
        """Load language preference from browser storage."""
        try:
            # Try to get from NiceGUI storage
            stored_language = app.storage.user.get("language")
            if stored_language and stored_language in self.supported_languages:
                self.current_language = stored_language
        except Exception as e:
            self.logger.error(f"Error loading language preference: {e}")

    def _save_language_preference(self):
        """Save language preference to browser storage."""
        try:
            app.storage.user["language"] = self.current_language
        except Exception as e:
            self.logger.error(f"Error saving language preference: {e}")

    def set_language(self, language: str):
        """
        Change application language.

        Args:
            language: Language code (e.g., 'de', 'en')
        """
        if language not in self.supported_languages:
            self.logger.warning(f"Language {language} not supported")
            return

        if language != self.current_language:
            self.current_language = language
            self._save_language_preference()

            # Trigger UI update
            self._update_ui_language()

    def get_current_language(self) -> str:
        """Get current language code."""
        return self.current_language

    def get_current_language_name(self) -> str:
        """Get current language display name."""
        return self.supported_languages.get(self.current_language, "Unknown")

    def t(self, key: str, **kwargs) -> str:
        """
        Translate key in current language with parameter substitution.

        Args:
            key: Translation key (e.g., 'auth.login_success')
            **kwargs: Parameters for string formatting

        Returns:
            Translated string or key if translation not found
        """
        # Get translations for current language
        translations = self.translations.get(self.current_language, {})

        # Try to get translation
        translation = self._get_nested_value(translations, key, key)

        # If translation is the same as key, try English as fallback
        if translation == key and self.current_language != "en":
            en_translations = self.translations.get("en", {})
            translation = self._get_nested_value(en_translations, key, key)

        # Apply parameter substitution
        try:
            if kwargs:
                translation = translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            self.logger.error(f"Error formatting translation for key '{key}': {e}")

        return translation

    def _get_nested_value(self, data: dict, key: str, default: str) -> str:
        """
        Get nested value from dictionary using dot notation.

        Args:
            data: Dictionary to search in
            key: Key with dot notation (e.g., 'auth.login_success')
            default: Default value if key not found

        Returns:
            Value or default
        """
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return str(current) if current is not None else default

    def get_supported_languages(self) -> dict[str, str]:
        """Get list of supported languages with their display names."""
        return self.supported_languages.copy()

    def _update_ui_language(self):
        """Update UI elements with new language."""
        # This would trigger a UI refresh in a real application
        # For now, we'll just log the change
        self.logger.info(f"Language changed to: {self.current_language}")

    async def create_language_selector(self) -> ui.select:
        """
        Create a language selector component.

        Returns:
            NiceGUI select component for language switching
        """
        languages = self.get_supported_languages()

        language_selector = ui.select(
            options=languages,
            value=self.current_language,
            label=self.t("common.language"),
            on_change=self._on_language_change,
        ).classes("w-32")

        return language_selector

    def _on_language_change(self, event):
        """Handle language change event."""
        new_language = event.value
        if new_language:
            self.set_language(new_language)

    def get_translation_keys(self) -> dict[str, str]:
        """Get all translation keys for current language."""
        return self.translations.get(self.current_language, {})

    def has_translation(self, key: str) -> bool:
        """Check if translation key exists."""
        return (
            self._get_nested_value(
                self.translations.get(self.current_language, {}), key, "",
            )
            != ""
        )

    def get_missing_translations(self) -> dict[str, str]:
        """Get missing translations by comparing with English."""
        en_translations = self.translations.get("en", {})
        current_translations = self.translations.get(self.current_language, {})

        missing = {}

        def find_missing(en_dict: dict, current_dict: dict, prefix: str = ""):
            for key, value in en_dict.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, dict):
                    if key not in current_dict:
                        missing[full_key] = "Missing section"
                    else:
                        find_missing(value, current_dict[key], full_key)
                elif key not in current_dict:
                    missing[full_key] = value

        find_missing(en_translations, current_translations)
        return missing


# Global i18n manager instance
i18n_manager = I18nManager()


def t(key: str, **kwargs) -> str:
    """
    Translate key using global i18n manager.

    Args:
        key: Translation key
        **kwargs: Parameters for string formatting

    Returns:
        Translated string
    """
    return i18n_manager.t(key, **kwargs)


def get_language() -> str:
    """Get current language."""
    return i18n_manager.get_current_language()


def set_language(language: str):
    """Set current language."""
    i18n_manager.set_language(language)


def get_supported_languages() -> dict[str, str]:
    """Get supported languages."""
    return i18n_manager.get_supported_languages()
