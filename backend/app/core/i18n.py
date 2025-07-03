"""
Internationalization (i18n) module for the AI Assistant Platform.

This module provides language detection, translation management, and
internationalization support for the backend API.
"""

import json
import os
from typing import Dict, Optional, Any
from pathlib import Path
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.core.config import settings


class I18nManager:
    """Internationalization manager for handling translations and language detection."""
    
    def __init__(self):
        """Initialize the i18n manager."""
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_language = "en"
        self.supported_languages = ["en", "de"]
        self.translations_path = Path(__file__).parent.parent / "translations"
        
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
        Detect language from request headers and query parameters.
        
        Priority order:
        1. Query parameter: ?lang=de
        2. Accept-Language header
        3. Default language
        """
        # Check query parameter first
        lang_param = request.query_params.get("lang")
        if lang_param and lang_param in self.supported_languages:
            return lang_param
        
        # Check Accept-Language header
        accept_language = request.headers.get("accept-language", "")
        if accept_language:
            # Parse Accept-Language header (e.g., "de-DE,de;q=0.9,en;q=0.8")
            languages = accept_language.split(",")
            for lang in languages:
                # Extract language code (e.g., "de-DE" -> "de")
                lang_code = lang.split(";")[0].split("-")[0].strip()
                if lang_code in self.supported_languages:
                    return lang_code
        
        return self.default_language
    
    def translate(self, key: str, language: str, **kwargs) -> str:
        """
        Translate a key to the specified language with parameter substitution.
        
        Args:
            key: Translation key
            language: Target language
            **kwargs: Parameters for string formatting
            
        Returns:
            Translated string or key if translation not found
        """
        # Get translations for language
        translations = self.translations.get(language, {})
        
        # Try to get translation
        translation = translations.get(key, key)
        
        # If translation is the same as key, try default language
        if translation == key and language != self.default_language:
            default_translations = self.translations.get(self.default_language, {})
            translation = default_translations.get(key, key)
        
        # Apply parameter substitution
        try:
            if kwargs:
                translation = translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(f"Error formatting translation for key '{key}': {e}")
        
        return translation
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages with their display names."""
        return {
            "en": "English",
            "de": "Deutsch"
        }


class I18nMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic language detection and translation."""
    
    def __init__(self, app, i18n_manager: I18nManager):
        """Initialize the middleware."""
        super().__init__(app)
        self.i18n_manager = i18n_manager
    
    async def dispatch(self, request: Request, call_next):
        """Process request and add language context."""
        # Detect language
        language = self.i18n_manager.detect_language(request)
        
        # Add language to request state
        request.state.language = language
        
        # Process request
        response = await call_next(request)
        
        # Add language header to response
        response.headers["Content-Language"] = language
        
        return response


# Global i18n manager instance
i18n_manager = I18nManager()


def get_language(request: Request) -> str:
    """Get current language from request state."""
    return getattr(request.state, 'language', i18n_manager.default_language)


def t(key: str, request: Request, **kwargs) -> str:
    """Translate key using request language context."""
    language = get_language(request)
    return i18n_manager.translate(key, language, **kwargs)


def translate_response(data: Any, request: Request) -> Any:
    """
    Translate response data recursively.
    
    This function can be used to translate API response messages
    based on the detected language.
    """
    if isinstance(data, dict):
        translated_data = {}
        for key, value in data.items():
            if key in ["message", "detail", "error"] and isinstance(value, str):
                # Translate common response fields
                translated_data[key] = t(value, request)
            else:
                translated_data[key] = translate_response(value, request)
        return translated_data
    elif isinstance(data, list):
        return [translate_response(item, request) for item in data]
    else:
        return data 