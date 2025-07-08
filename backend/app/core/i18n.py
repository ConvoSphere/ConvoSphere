"""
Internationalization (i18n) module for the AI Assistant Platform.

This module provides language detection, translation management, and
internationalization support for the backend API with support for
non-Latin scripts and RTL languages.
"""

import json
import os
from typing import Dict, Optional, Any, List
from pathlib import Path
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.core.config import settings


class LanguageInfo:
    """Language information including metadata for UI display."""
    
    def __init__(self, code: str, name: str, native_name: str, direction: str = "ltr"):
        self.code = code
        self.name = name  # English name
        self.native_name = native_name  # Name in the language itself
        self.direction = direction  # ltr or rtl
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API responses."""
        return {
            "code": self.code,
            "name": self.name,
            "native_name": self.native_name,
            "direction": self.direction
        }


class I18nManager:
    """Enhanced internationalization manager for handling translations and language detection."""
    
    def __init__(self):
        """Initialize the i18n manager with extended language support."""
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_language = "en"
        self.supported_languages = ["en", "de", "fr", "es", "ar", "ja"]
        self.translations_path = Path(__file__).parent.parent / "translations"
        
        # Language metadata for UI display
        self.language_info = {
            "en": LanguageInfo("en", "English", "English", "ltr"),
            "de": LanguageInfo("de", "German", "Deutsch", "ltr"),
            "fr": LanguageInfo("fr", "French", "Français", "ltr"),
            "es": LanguageInfo("es", "Spanish", "Español", "ltr"),
            "ar": LanguageInfo("ar", "Arabic", "العربية", "rtl"),
            "ja": LanguageInfo("ja", "Japanese", "日本語", "ltr"),
        }
        
        # Load translations
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files for all supported languages."""
        try:
            for language in self.supported_languages:
                translation_file = self.translations_path / f"{language}.json"
                if translation_file.exists():
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[language] = json.load(f)
                    logger.info(f"Loaded translations for language: {language}")
                else:
                    logger.warning(f"Translation file not found: {translation_file}")
                    self.translations[language] = {}
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
            # Fallback to empty translations
            for language in self.supported_languages:
                self.translations[language] = {}
    
    def detect_language(self, request: Request) -> str:
        """
        Enhanced language detection from request headers and query parameters.
        
        Priority order:
        1. Query parameter: ?lang=ar
        2. Accept-Language header
        3. User preference (if authenticated)
        4. Default language
        """
        # Check query parameter first
        lang_param = request.query_params.get("lang")
        if lang_param and lang_param in self.supported_languages:
            return lang_param
        
        # Check Accept-Language header with better parsing
        accept_language = request.headers.get("accept-language", "")
        if accept_language:
            # Parse Accept-Language header (e.g., "ar-SA,ar;q=0.9,en;q=0.8")
            languages = accept_language.split(",")
            for lang in languages:
                # Extract language code (e.g., "ar-SA" -> "ar")
                lang_code = lang.split(";")[0].split("-")[0].strip().lower()
                if lang_code in self.supported_languages:
                    return lang_code
        
        # TODO: Check user preference from database if authenticated
        # user_lang = get_user_language_preference(request.user.id)
        # if user_lang and user_lang in self.supported_languages:
        #     return user_lang
        
        return self.default_language
    
    def translate(self, key: str, language: str, **kwargs) -> str:
        """
        Enhanced translation with better fallback handling.
        
        Args:
            key: Translation key (can be nested like "auth.login_success")
            language: Target language
            **kwargs: Parameters for string formatting
            
        Returns:
            Translated string or key if translation not found
        """
        # Get translations for language
        translations = self.translations.get(language, {})
        
        # Handle nested keys (e.g., "auth.login_success")
        translation = self._get_nested_value(translations, key, key)
        
        # If translation is the same as key, try default language
        if translation == key and language != self.default_language:
            default_translations = self.translations.get(self.default_language, {})
            translation = self._get_nested_value(default_translations, key, key)
        
        # Apply parameter substitution
        try:
            if kwargs:
                translation = translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(f"Error formatting translation for key '{key}': {e}")
        
        return translation
    
    def _get_nested_value(self, data: Dict, key: str, default: str) -> str:
        """Get nested value from dictionary using dot notation."""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return str(current) if current is not None else default
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages with metadata for API responses."""
        return [
            self.language_info[lang].to_dict() 
            for lang in self.supported_languages 
            if lang in self.language_info
        ]
    
    def get_language_info(self, language: str) -> Optional[LanguageInfo]:
        """Get language information for a specific language."""
        return self.language_info.get(language)
    
    def is_rtl(self, language: str) -> bool:
        """Check if a language is right-to-left."""
        lang_info = self.get_language_info(language)
        return lang_info.direction == "rtl" if lang_info else False
    
    def reload_translations(self) -> None:
        """Reload all translation files (useful for development)."""
        self.translations.clear()
        self._load_translations()
        logger.info("Translations reloaded successfully")


class I18nMiddleware(BaseHTTPMiddleware):
    """Enhanced FastAPI middleware for automatic language detection and translation."""
    
    def __init__(self, app, i18n_manager: I18nManager):
        """Initialize the middleware."""
        super().__init__(app)
        self.i18n_manager = i18n_manager
    
    async def dispatch(self, request: Request, call_next):
        """Process request and add language context."""
        # Detect language
        language = self.i18n_manager.detect_language(request)
        
        # Add language and direction to request state
        request.state.language = language
        request.state.is_rtl = self.i18n_manager.is_rtl(language)
        
        # Process request
        response = await call_next(request)
        
        # Add language headers to response
        response.headers["Content-Language"] = language
        response.headers["X-Text-Direction"] = "rtl" if request.state.is_rtl else "ltr"
        
        return response


# Global i18n manager instance
i18n_manager = I18nManager()


def get_language(request: Request) -> str:
    """Get current language from request state."""
    return getattr(request.state, 'language', i18n_manager.default_language)


def is_rtl(request: Request) -> bool:
    """Check if current language is RTL."""
    return getattr(request.state, 'is_rtl', False)


def t(key: str, request: Request, **kwargs) -> str:
    """Translate key using request language context."""
    language = get_language(request)
    return i18n_manager.translate(key, language, **kwargs)


def translate_response(data: Any, request: Request) -> Any:
    """
    Enhanced response translation with better field detection.
    
    This function can be used to translate API response messages
    based on the detected language.
    """
    if isinstance(data, dict):
        translated_data = {}
        for key, value in data.items():
            # Translate common response fields
            if key in ["message", "detail", "error", "title", "description"] and isinstance(value, str):
                translated_data[key] = t(value, request)
            elif key == "errors" and isinstance(value, list):
                # Handle error arrays
                translated_data[key] = [
                    translate_response(error, request) if isinstance(error, dict) else error
                    for error in value
                ]
            else:
                translated_data[key] = translate_response(value, request)
        return translated_data
    elif isinstance(data, list):
        return [translate_response(item, request) for item in data]
    else:
        return data 