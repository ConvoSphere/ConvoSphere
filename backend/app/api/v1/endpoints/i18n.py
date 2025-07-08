"""
Internationalization (i18n) API endpoints.

This module provides endpoints for language management, translation retrieval,
and internationalization features.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel

from app.core.i18n import i18n_manager, get_language, is_rtl, t
from app.core.security import get_current_user

router = APIRouter()


class LanguageInfo(BaseModel):
    """Language information model for API responses."""
    code: str
    name: str
    native_name: str
    direction: str


class TranslationResponse(BaseModel):
    """Translation response model."""
    language: str
    translations: Dict[str, Any]
    is_rtl: bool


@router.get("/languages", response_model=List[LanguageInfo])
async def get_supported_languages():
    """
    Get list of supported languages with metadata.
    
    Returns:
        List of supported languages with their display names and text direction.
    """
    return i18n_manager.get_supported_languages()


@router.get("/current", response_model=Dict[str, Any])
async def get_current_language_info(request: Request):
    """
    Get current language information for the request.
    
    Returns:
        Current language code and metadata.
    """
    language = get_language(request)
    lang_info = i18n_manager.get_language_info(language)
    
    if not lang_info:
        raise HTTPException(status_code=404, detail="Language not found")
    
    return {
        "language": language,
        "is_rtl": is_rtl(request),
        "info": lang_info.to_dict()
    }


@router.get("/translations", response_model=TranslationResponse)
async def get_translations(
    request: Request,
    keys: str = None,
    namespace: str = None
):
    """
    Get translations for the current language.
    
    Args:
        keys: Comma-separated list of translation keys to retrieve
        namespace: Specific namespace to retrieve (e.g., 'auth', 'user')
    
    Returns:
        Translations for the specified keys or namespace.
    """
    language = get_language(request)
    translations = i18n_manager.translations.get(language, {})
    
    if namespace:
        # Return specific namespace
        namespace_translations = translations.get(namespace, {})
        return TranslationResponse(
            language=language,
            translations={namespace: namespace_translations},
            is_rtl=is_rtl(request)
        )
    
    if keys:
        # Return specific keys
        key_list = [k.strip() for k in keys.split(",")]
        selected_translations = {}
        
        for key in key_list:
            translation = i18n_manager.translate(key, language)
            if translation != key:  # Only include if translation found
                selected_translations[key] = translation
        
        return TranslationResponse(
            language=language,
            translations=selected_translations,
            is_rtl=is_rtl(request)
        )
    
    # Return all translations
    return TranslationResponse(
        language=language,
        translations=translations,
        is_rtl=is_rtl(request)
    )


@router.post("/translate")
async def translate_text(
    request: Request,
    text: str,
    target_language: str = None
):
    """
    Translate a specific text to the target language.
    
    Args:
        text: Text to translate (should be a translation key)
        target_language: Target language code (optional, uses current if not provided)
    
    Returns:
        Translated text.
    """
    if not target_language:
        target_language = get_language(request)
    
    if target_language not in i18n_manager.supported_languages:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported language: {target_language}"
        )
    
    translated_text = i18n_manager.translate(text, target_language)
    
    return {
        "original": text,
        "translated": translated_text,
        "language": target_language,
        "is_rtl": i18n_manager.is_rtl(target_language)
    }


@router.post("/reload")
async def reload_translations(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Reload translation files (admin only).
    
    This endpoint allows administrators to reload translation files
    without restarting the application.
    """
    # TODO: Add proper admin role check
    # if not current_user or current_user.get("role") != "admin":
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        i18n_manager.reload_translations()
        return {
            "message": t("common.success", request),
            "detail": "Translations reloaded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload translations: {str(e)}"
        )


@router.get("/health")
async def i18n_health_check():
    """
    Check i18n system health.
    
    Returns:
        Health status of the internationalization system.
    """
    health_status = {
        "status": "healthy",
        "supported_languages": len(i18n_manager.supported_languages),
        "loaded_languages": len(i18n_manager.translations),
        "default_language": i18n_manager.default_language,
        "rtl_languages": [
            lang for lang in i18n_manager.supported_languages 
            if i18n_manager.is_rtl(lang)
        ]
    }
    
    # Check if all supported languages have translations loaded
    missing_translations = [
        lang for lang in i18n_manager.supported_languages
        if not i18n_manager.translations.get(lang)
    ]
    
    if missing_translations:
        health_status["status"] = "warning"
        health_status["missing_translations"] = missing_translations
    
    return health_status 