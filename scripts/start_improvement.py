#!/usr/bin/env python3
"""
Code Quality Improvement Starter Script
=======================================

Dieses Skript hilft bei der Implementierung des Code-Qualitäts-Verbesserungsplans.
Es automatisiert die ersten Schritte und erstellt die notwendigen Konfigurationsdateien.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any


class CodeQualityImprover:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        
    def run_command(self, command: List[str], cwd: str = None) -> subprocess.CompletedProcess:
        """Führt einen Befehl aus und gibt das Ergebnis zurück."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or str(self.project_root),
                capture_output=True,
                text=True,
                check=False
            )
            return result
        except Exception as e:
            print(f"❌ Fehler beim Ausführen von {' '.join(command)}: {e}")
            return subprocess.CompletedProcess(command, -1, "", str(e))

    def check_tools_installed(self) -> Dict[str, bool]:
        """Überprüft, ob die benötigten Tools installiert sind."""
        tools = {
            "ruff": False,
            "bandit": False,
            "mypy": False
        }
        
        for tool in tools.keys():
            result = self.run_command([tool, "--version"])
            tools[tool] = result.returncode == 0
            
        return tools

    def install_missing_tools(self) -> None:
        """Installiert fehlende Tools."""
        print("🔧 Installiere fehlende Tools...")
        
        tools_status = self.check_tools_installed()
        missing_tools = [tool for tool, installed in tools_status.items() if not installed]
        
        if missing_tools:
            print(f"📦 Installiere: {', '.join(missing_tools)}")
            result = self.run_command([
                "pip", "install", "--break-system-packages"
            ] + missing_tools)
            
            if result.returncode == 0:
                print("✅ Tools erfolgreich installiert")
            else:
                print(f"❌ Fehler beim Installieren der Tools: {result.stderr}")
        else:
            print("✅ Alle Tools sind bereits installiert")

    def install_type_stubs(self) -> None:
        """Installiert fehlende Type-Stubs."""
        print("📚 Installiere Type-Stubs...")
        
        type_stubs = [
            "types-requests",
            "types-PyYAML", 
            "types-psutil"
        ]
        
        result = self.run_command([
            "pip", "install", "--break-system-packages"
        ] + type_stubs)
        
        if result.returncode == 0:
            print("✅ Type-Stubs erfolgreich installiert")
        else:
            print(f"❌ Fehler beim Installieren der Type-Stubs: {result.stderr}")

    def create_ruff_config(self) -> None:
        """Erstellt die Ruff-Konfiguration."""
        print("⚙️ Erstelle Ruff-Konfiguration...")
        
        ruff_config = """[tool.ruff]
target-version = "py39"
line-length = 88
select = [
    "E", "F", "I", "N", "W", "B", "C4", "UP", "ARG", "SIM", 
    "TCH", "Q", "RSE", "RET", "SLF", "SLOT", "TID", "PIE", 
    "PYI", "PT", "LOG", "PTH", "ERA", "PD", "PGH", "PL", 
    "TRY", "NPY", "AIR", "PERF", "FURB", "BLE"
]
ignore = ["E501", "B101"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
"""
        
        config_file = self.project_root / "pyproject.toml"
        
        # Prüfe, ob pyproject.toml bereits existiert
        if config_file.exists():
            print("📝 pyproject.toml existiert bereits - füge Ruff-Konfiguration hinzu")
            # Hier könnte man die bestehende Datei parsen und erweitern
            # Für jetzt erstellen wir eine separate ruff.toml
            config_file = self.project_root / "ruff.toml"
        
        with open(config_file, "w") as f:
            f.write(ruff_config)
        
        print(f"✅ Ruff-Konfiguration erstellt: {config_file}")

    def create_bandit_config(self) -> None:
        """Erstellt die Bandit-Konfiguration."""
        print("🛡️ Erstelle Bandit-Konfiguration...")
        
        bandit_config = """[bandit]
exclude_dirs = tests
skips = B101
"""
        
        config_file = self.project_root / ".bandit"
        
        with open(config_file, "w") as f:
            f.write(bandit_config)
        
        print(f"✅ Bandit-Konfiguration erstellt: {config_file}")

    def create_mypy_config(self) -> None:
        """Erstellt die Mypy-Konfiguration."""
        print("🔍 Erstelle Mypy-Konfiguration...")
        
        mypy_config = """[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Start with False, enable later
disallow_incomplete_defs = False
check_untyped_defs = True
disallow_untyped_decorators = False
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy.plugins.sqlalchemy.ext.*]
init_subclass = True
"""
        
        config_file = self.project_root / "mypy.ini"
        
        with open(config_file, "w") as f:
            f.write(mypy_config)
        
        print(f"✅ Mypy-Konfiguration erstellt: {config_file}")

    def create_pre_commit_config(self) -> None:
        """Erstellt die Pre-commit-Konfiguration."""
        print("🔗 Erstelle Pre-commit-Konfiguration...")
        
        pre_commit_config = """repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.6
    hooks:
      - id: bandit
        args: [-r, backend/]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.17.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML, types-psutil]
"""
        
        config_file = self.project_root / ".pre-commit-config.yaml"
        
        with open(config_file, "w") as f:
            f.write(pre_commit_config)
        
        print(f"✅ Pre-commit-Konfiguration erstellt: {config_file}")

    def run_ruff_auto_fix(self) -> None:
        """Führt automatische Ruff-Fixes aus."""
        print("🔧 Führe automatische Ruff-Fixes aus...")
        
        # Setze PATH für lokale Installation
        env = os.environ.copy()
        env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"
        
        # Ruff check mit auto-fix
        result = subprocess.run(
            ["ruff", "check", "--fix", "backend/"],
            cwd=str(self.project_root),
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Ruff auto-fix erfolgreich")
            if result.stdout:
                print(f"📝 Gefixte Probleme:\n{result.stdout}")
        else:
            print(f"⚠️ Ruff auto-fix mit Warnungen: {result.stderr}")

    def run_ruff_format(self) -> None:
        """Formatiert Code mit Ruff."""
        print("🎨 Formatiere Code mit Ruff...")
        
        env = os.environ.copy()
        env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            ["ruff", "format", "backend/"],
            cwd=str(self.project_root),
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Code-Formatierung erfolgreich")
        else:
            print(f"⚠️ Code-Formatierung mit Warnungen: {result.stderr}")

    def generate_improvement_report(self) -> None:
        """Generiert einen aktuellen Verbesserungsbericht."""
        print("📊 Generiere Verbesserungsbericht...")
        
        env = os.environ.copy()
        env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"
        
        # Ruff Report
        ruff_result = subprocess.run(
            ["ruff", "check", "backend/", "--output-format=json"],
            cwd=str(self.project_root),
            env=env,
            capture_output=True,
            text=True
        )
        
        # Bandit Report
        bandit_result = subprocess.run(
            ["bandit", "-r", "backend/", "-f", "json"],
            cwd=str(self.project_root),
            env=env,
            capture_output=True,
            text=True
        )
        
        # Mypy Report (nur Stichprobe)
        mypy_result = subprocess.run(
            ["mypy", "backend/main.py"],
            cwd=str(self.project_root),
            env=env,
            capture_output=True,
            text=True
        )
        
        report = {
            "timestamp": subprocess.run(["date"], capture_output=True, text=True).stdout.strip(),
            "ruff_issues": len(json.loads(ruff_result.stdout)) if ruff_result.returncode == 1 else 0,
            "bandit_issues": len(json.loads(bandit_result.stdout)) if bandit_result.returncode == 1 else 0,
            "mypy_has_errors": mypy_result.returncode != 0,
            "tools_installed": self.check_tools_installed()
        }
        
        report_file = self.project_root / "improvement_progress.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Verbesserungsbericht erstellt: {report_file}")
        print(f"📈 Aktuelle Metriken:")
        print(f"   - Ruff Issues: {report['ruff_issues']}")
        print(f"   - Bandit Issues: {report['bandit_issues']}")
        print(f"   - Mypy Errors: {'Ja' if report['mypy_has_errors'] else 'Nein'}")

    def create_phase1_checklist(self) -> None:
        """Erstellt eine Checkliste für Phase 1."""
        print("📋 Erstelle Phase 1 Checkliste...")
        
        checklist = """# Phase 1 Checkliste - Kritische Fixes

## ✅ Automatisierte Fixes (bereits erledigt)
- [x] Tools installiert
- [x] Type-Stubs installiert
- [x] Konfigurationsdateien erstellt
- [x] Automatische Ruff-Fixes ausgeführt
- [x] Code-Formatierung durchgeführt

## 🔧 Manuelle Fixes (noch zu erledigen)

### 1. Undefinierte Variablen in main.py
- [ ] `db` Variable definieren oder importieren
- [ ] `get_db` Funktion implementieren oder importieren
- [ ] **Datei**: backend/main.py
- [ ] **Zeitaufwand**: 2-4 Stunden

### 2. Import-Fehler beheben
- [ ] Fehlende Imports in main.py ergänzen
- [ ] Zirkuläre Imports auflösen
- [ ] **Datei**: backend/main.py
- [ ] **Zeitaufwand**: 4-6 Stunden

### 3. Blind Exception Handling
- [ ] Spezifische Exception-Typen verwenden
- [ ] **Datei**: backend/main.py:254
- [ ] **Zeitaufwand**: 2-3 Stunden

### 4. Debug-Code entfernen
- [ ] Print-Statements in output.py entfernen
- [ ] **Datei**: backend/cli/utils/output.py
- [ ] **Zeitaufwand**: 1-2 Stunden

## 📊 Fortschritt
- **Gesamtaufwand**: 8-13 Stunden
- **Aktueller Status**: Automatisierte Fixes abgeschlossen
- **Verbleibend**: Manuelle Fixes

## 🎯 Nächste Schritte
1. Manuelle Fixes durchführen
2. Tests ausführen
3. Phase 2 beginnen
"""
        
        checklist_file = self.project_root / "PHASE1_CHECKLIST.md"
        with open(checklist_file, "w") as f:
            f.write(checklist)
        
        print(f"✅ Phase 1 Checkliste erstellt: {checklist_file}")

    def run_phase1_automation(self) -> None:
        """Führt alle automatisierten Schritte von Phase 1 aus."""
        print("🚀 Starte Phase 1 - Automatisierte Fixes")
        print("=" * 50)
        
        # 1. Tools installieren
        self.install_missing_tools()
        print()
        
        # 2. Type-Stubs installieren
        self.install_type_stubs()
        print()
        
        # 3. Konfigurationsdateien erstellen
        self.create_ruff_config()
        self.create_bandit_config()
        self.create_mypy_config()
        self.create_pre_commit_config()
        print()
        
        # 4. Automatische Fixes ausführen
        self.run_ruff_auto_fix()
        print()
        self.run_ruff_format()
        print()
        
        # 5. Berichte und Checklisten erstellen
        self.generate_improvement_report()
        self.create_phase1_checklist()
        print()
        
        print("🎉 Phase 1 - Automatisierte Fixes abgeschlossen!")
        print("📋 Überprüfe PHASE1_CHECKLIST.md für die nächsten Schritte")


def main():
    """Hauptfunktion."""
    print("🔧 Code Quality Improvement Starter")
    print("===================================")
    
    improver = CodeQualityImprover()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--phase1":
        improver.run_phase1_automation()
    else:
        print("Verwendung:")
        print("  python scripts/start_improvement.py --phase1")
        print()
        print("Verfügbare Optionen:")
        print("  --phase1    Führt alle automatisierten Fixes von Phase 1 aus")


if __name__ == "__main__":
    main()