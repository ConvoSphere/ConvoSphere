#!/usr/bin/env python3
"""
Comprehensive i18n validation script for ConvoSphere.

This script validates:
1. Translation file completeness
2. Key consistency across languages
3. Parameter consistency
4. JSON syntax
5. Missing translations
6. Unused translations
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class I18nValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.frontend_i18n_dir = project_root / "frontend-react" / "src" / "i18n"
        self.backend_i18n_dir = project_root / "backend" / "app" / "translations"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Expected languages
        self.expected_languages = {"en", "de", "fr", "es"}
        
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting i18n validation...")
        
        success = True
        success &= self.validate_file_existence()
        success &= self.validate_json_syntax()
        success &= self.validate_key_consistency()
        success &= self.validate_parameter_consistency()
        success &= self.check_missing_translations()
        success &= self.validate_translation_usage()
        
        self.print_summary()
        return success
    
    def validate_file_existence(self) -> bool:
        """Check if all required translation files exist."""
        print("\n📁 Checking file existence...")
        success = True
        
        # Check frontend files
        for lang in self.expected_languages:
            file_path = self.frontend_i18n_dir / f"{lang}.json"
            if not file_path.exists():
                self.errors.append(f"Missing frontend translation file: {file_path}")
                success = False
            else:
                print(f"✅ Frontend {lang}.json exists")
        
        # Check backend files
        for lang in self.expected_languages:
            file_path = self.backend_i18n_dir / f"{lang}.json"
            if not file_path.exists():
                self.errors.append(f"Missing backend translation file: {file_path}")
                success = False
            else:
                print(f"✅ Backend {lang}.json exists")
        
        return success
    
    def validate_json_syntax(self) -> bool:
        """Validate JSON syntax in all translation files."""
        print("\n🔧 Validating JSON syntax...")
        success = True
        
        for directory in [self.frontend_i18n_dir, self.backend_i18n_dir]:
            for lang in self.expected_languages:
                file_path = directory / f"{lang}.json"
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                        print(f"✅ {file_path.relative_to(self.project_root)} - Valid JSON")
                    except json.JSONDecodeError as e:
                        self.errors.append(f"Invalid JSON in {file_path}: {e}")
                        success = False
        
        return success
    
    def validate_key_consistency(self) -> bool:
        """Check if all languages have the same keys."""
        print("\n🔑 Validating key consistency...")
        success = True
        
        for directory_name, directory in [("Frontend", self.frontend_i18n_dir), ("Backend", self.backend_i18n_dir)]:
            translations = self.load_translations(directory)
            if not translations:
                continue
                
            # Get all keys from English (reference)
            reference_keys = set()
            if "en" in translations:
                reference_keys = self.get_all_keys(translations["en"])
            
            # Check each language against reference
            for lang, data in translations.items():
                if lang == "en":
                    continue
                    
                lang_keys = self.get_all_keys(data)
                
                # Missing keys
                missing = reference_keys - lang_keys
                if missing:
                    self.errors.append(f"{directory_name} {lang}: Missing keys: {sorted(missing)}")
                    success = False
                
                # Extra keys
                extra = lang_keys - reference_keys
                if extra:
                    self.warnings.append(f"{directory_name} {lang}: Extra keys: {sorted(extra)}")
                
                if not missing and not extra:
                    print(f"✅ {directory_name} {lang}: Key consistency OK")
        
        return success
    
    def validate_parameter_consistency(self) -> bool:
        """Check if translation parameters are consistent."""
        print("\n🔧 Validating parameter consistency...")
        success = True
        
        for directory_name, directory in [("Frontend", self.frontend_i18n_dir), ("Backend", self.backend_i18n_dir)]:
            translations = self.load_translations(directory)
            if not translations or "en" not in translations:
                continue
            
            # Extract parameters from English translations
            en_params = self.extract_parameters(translations["en"])
            
            # Check each language
            for lang, data in translations.items():
                if lang == "en":
                    continue
                    
                lang_params = self.extract_parameters(data)
                
                for key, en_param_set in en_params.items():
                    if key in lang_params:
                        lang_param_set = lang_params[key]
                        if en_param_set != lang_param_set:
                            self.errors.append(
                                f"{directory_name} {lang}: Parameter mismatch in '{key}'. "
                                f"EN: {en_param_set}, {lang.upper()}: {lang_param_set}"
                            )
                            success = False
                
                if success:
                    print(f"✅ {directory_name} {lang}: Parameter consistency OK")
        
        return success
    
    def check_missing_translations(self) -> bool:
        """Check for empty or missing translations."""
        print("\n❓ Checking for missing translations...")
        success = True
        
        for directory_name, directory in [("Frontend", self.frontend_i18n_dir), ("Backend", self.backend_i18n_dir)]:
            translations = self.load_translations(directory)
            
            for lang, data in translations.items():
                missing = self.find_missing_values(data)
                if missing:
                    self.warnings.append(f"{directory_name} {lang}: Empty translations: {sorted(missing)}")
                else:
                    print(f"✅ {directory_name} {lang}: No missing translations")
        
        return success
    
    def validate_translation_usage(self) -> bool:
        """Check if translations are actually used in the code."""
        print("\n🔍 Checking translation usage...")
        success = True
        
        # Find all translation keys used in frontend
        frontend_used_keys = self.find_used_translation_keys()
        
        # Load frontend translations
        frontend_translations = self.load_translations(self.frontend_i18n_dir)
        if "en" in frontend_translations:
            available_keys = self.get_all_keys(frontend_translations["en"])
            
            # Find unused keys
            unused = available_keys - frontend_used_keys
            if unused:
                self.warnings.append(f"Frontend: Unused translation keys: {sorted(unused)}")
            
            # Find missing keys
            missing = frontend_used_keys - available_keys
            if missing:
                self.errors.append(f"Frontend: Used but not defined keys: {sorted(missing)}")
                success = False
            
            print(f"✅ Frontend: {len(frontend_used_keys)} keys used, {len(unused)} unused")
        
        return success
    
    def load_translations(self, directory: Path) -> Dict[str, dict]:
        """Load all translation files from a directory."""
        translations = {}
        for lang in self.expected_languages:
            file_path = directory / f"{lang}.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        translations[lang] = json.load(f)
                except json.JSONDecodeError:
                    continue
        return translations
    
    def get_all_keys(self, obj: dict, prefix: str = "") -> Set[str]:
        """Recursively get all keys from nested dictionary."""
        keys = set()
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            if isinstance(value, dict):
                keys.update(self.get_all_keys(value, full_key))
        return keys
    
    def extract_parameters(self, obj: dict, prefix: str = "") -> Dict[str, Set[str]]:
        """Extract parameter names from translation strings."""
        params = {}
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, str):
                # Find {param} style parameters
                param_matches = re.findall(r'\{(\w+)\}', value)
                if param_matches:
                    params[full_key] = set(param_matches)
            elif isinstance(value, dict):
                params.update(self.extract_parameters(value, full_key))
        return params
    
    def find_missing_values(self, obj: dict, prefix: str = "") -> Set[str]:
        """Find keys with empty or missing values."""
        missing = set()
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, str):
                if not value.strip():
                    missing.add(full_key)
            elif isinstance(value, dict):
                missing.update(self.find_missing_values(value, full_key))
        return missing
    
    def find_used_translation_keys(self) -> Set[str]:
        """Find all translation keys used in frontend components."""
        used_keys = set()
        
        # Search in React components
        frontend_src = self.project_root / "frontend-react" / "src"
        if frontend_src.exists():
            for file_path in frontend_src.rglob("*.tsx"):
                content = file_path.read_text(encoding='utf-8')
                
                # Find t('key') patterns
                matches = re.findall(r"t\(['\"]([^'\"]+)['\"]", content)
                used_keys.update(matches)
                
                # Find t("key") patterns
                matches = re.findall(r't\(["\']([^"\']+)["\']\)', content)
                used_keys.update(matches)
        
        return used_keys
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("🎉 All validations passed! i18n implementation is perfect.")
        else:
            if self.errors:
                print(f"❌ {len(self.errors)} ERRORS found:")
                for i, error in enumerate(self.errors, 1):
                    print(f"  {i}. {error}")
            
            if self.warnings:
                print(f"\n⚠️  {len(self.warnings)} WARNINGS found:")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
        
        print("\n" + "="*60)


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    validator = I18nValidator(project_root)
    
    success = validator.validate_all()
    
    if success:
        print("\n✅ Validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()