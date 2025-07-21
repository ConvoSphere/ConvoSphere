#!/usr/bin/env python3
"""
Translation validation script.

This script validates that all translation files have the same structure
and keys, and reports any missing or extra translations.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set


def load_translation_file(file_path: Path) -> Dict:
    """Load a translation file and return its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}


def get_all_keys(data: Dict, prefix: str = "") -> Set[str]:
    """Recursively get all keys from a nested dictionary."""
    keys = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))
        else:
            keys.add(full_key)
    return keys


def get_nested_value(data: Dict, key: str) -> str:
    """Get a nested value from a dictionary using dot notation."""
    keys = key.split(".")
    current = data
    
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return ""
    
    return str(current) if current is not None else ""


def validate_translation_files(translation_dir: Path, languages: List[str]) -> bool:
    """Validate that all translation files have the same structure."""
    print(f"Validating translation files in {translation_dir}")
    print("=" * 50)
    
    # Load all translation files
    translations = {}
    for lang in languages:
        file_path = translation_dir / f"{lang}.json"
        if file_path.exists():
            translations[lang] = load_translation_file(file_path)
        else:
            print(f"Warning: Translation file not found: {file_path}")
            translations[lang] = {}
    
    if not translations:
        print("No translation files found!")
        return False
    
    # Get all keys from each language
    all_keys = {}
    for lang, data in translations.items():
        all_keys[lang] = get_all_keys(data)
    
    # Use English as the reference
    reference_lang = "en"
    if reference_lang not in all_keys:
        print(f"Error: Reference language '{reference_lang}' not found!")
        return False
    
    reference_keys = all_keys[reference_lang]
    print(f"Reference language: {reference_lang} ({len(reference_keys)} keys)")
    
    # Check each language against the reference
    all_valid = True
    for lang, keys in all_keys.items():
        if lang == reference_lang:
            continue
            
        print(f"\nChecking {lang} ({len(keys)} keys):")
        
        # Find missing keys
        missing_keys = reference_keys - keys
        if missing_keys:
            print(f"  ❌ Missing keys ({len(missing_keys)}):")
            for key in sorted(missing_keys):
                print(f"    - {key}")
            all_valid = False
        else:
            print("  ✅ No missing keys")
        
        # Find extra keys
        extra_keys = keys - reference_keys
        if extra_keys:
            print(f"  ⚠️  Extra keys ({len(extra_keys)}):")
            for key in sorted(extra_keys):
                print(f"    - {key}")
        else:
            print("  ✅ No extra keys")
    
    return all_valid


def validate_parameter_consistency(translation_dir: Path, languages: List[str]) -> bool:
    """Validate that translation keys with parameters are consistent."""
    print(f"\nValidating parameter consistency in {translation_dir}")
    print("=" * 50)
    
    translations = {}
    for lang in languages:
        file_path = translation_dir / f"{lang}.json"
        if file_path.exists():
            translations[lang] = load_translation_file(file_path)
    
    # Find all keys with parameters
    param_keys = {}
    for lang, data in translations.items():
        param_keys[lang] = {}
        keys = get_all_keys(data)
        for key in keys:
            # Get the actual value from the nested structure
            value = get_nested_value(data, key)
            if isinstance(value, str) and "{" in value and "}" in value:
                # Extract parameter names
                import re
                params = re.findall(r'\{(\w+)\}', value)
                if params:
                    param_keys[lang][key] = set(params)
    
    # Check consistency
    reference_lang = "en"
    if reference_lang not in param_keys:
        return False
    
    reference_params = param_keys[reference_lang]
    all_consistent = True
    
    for lang, params in param_keys.items():
        if lang == reference_lang:
            continue
            
        print(f"\nChecking parameter consistency for {lang}:")
        
        for key, ref_params in reference_params.items():
            if key in params:
                lang_params = params[key]
                if ref_params != lang_params:
                    print(f"  ❌ Parameter mismatch in '{key}':")
                    print(f"    Reference ({reference_lang}): {sorted(ref_params)}")
                    print(f"    {lang}: {sorted(lang_params)}")
                    all_consistent = False
                else:
                    print(f"  ✅ Parameters match for '{key}'")
            else:
                print(f"  ❌ Missing key with parameters: '{key}'")
                all_consistent = False
    
    return all_consistent


def main():
    """Main validation function."""
    # Define paths and languages
    frontend_dir = Path("frontend/i18n")
    backend_dir = Path("backend/app/translations")
    languages = ["en", "de", "fr", "es"]
    
    print("Translation Validation Script")
    print("=" * 50)
    
    # Validate frontend translations
    frontend_valid = validate_translation_files(frontend_dir, languages)
    
    # Validate backend translations
    backend_valid = validate_translation_files(backend_dir, languages)
    
    # Validate parameter consistency
    frontend_params_valid = validate_parameter_consistency(frontend_dir, languages)
    backend_params_valid = validate_parameter_consistency(backend_dir, languages)
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Frontend structure: {'✅ PASS' if frontend_valid else '❌ FAIL'}")
    print(f"Backend structure:  {'✅ PASS' if backend_valid else '❌ FAIL'}")
    print(f"Frontend params:    {'✅ PASS' if frontend_params_valid else '❌ FAIL'}")
    print(f"Backend params:     {'✅ PASS' if backend_params_valid else '❌ FAIL'}")
    
    overall_success = frontend_valid and backend_valid and frontend_params_valid and backend_params_valid
    
    if overall_success:
        print("\n🎉 All validations passed!")
        return 0
    else:
        print("\n❌ Some validations failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())