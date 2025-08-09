#!/bin/bash

# ConvoSphere Report Cleanup Script
# Organisiert alte Report- und Planungsdateien

echo "🧹 ConvoSphere Report Cleanup gestartet..."

# Archiv-Verzeichnis erstellen
ARCHIVE_DIR="archive/reports_$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"

echo "📁 Archiv-Verzeichnis erstellt: $ARCHIVE_DIR"

# Abgeschlossene Berichte archivieren
echo "📋 Archiviere abgeschlossene Berichte..."

# Phase Completion Summaries
mv PHASE_1_COMPLETION_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null
mv PHASE_2_COMPLETION_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null
mv PHASE_3_COMPLETION_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null
mv PHASE_4_COMPLETION_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null
mv PHASE1_COMPLETION_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null
mv PHASE_5_TASKS_COMPLETION_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null

# Alte Analysen archivieren
echo "📊 Archiviere alte Analysen..."
mv PHASE_1_ANALYSIS.md "$ARCHIVE_DIR/" 2>/dev/null
mv PHASE_2_ANALYSIS.md "$ARCHIVE_DIR/" 2>/dev/null
mv CODE_QUALITY_ANALYSIS.md "$ARCHIVE_DIR/" 2>/dev/null
mv CODE_QUALITY_ANALYSIS_REPORT.md "$ARCHIVE_DIR/" 2>/dev/null

# Alte Implementierungsberichte archivieren
echo "🔧 Archiviere alte Implementierungsberichte..."
mv REFACTORING_IMPLEMENTATION_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null
mv REFACTORING_STATUS_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null
mv CODE_CLEANUP_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null
mv DOCUMENTATION_CLEANUP_COMPLETE.md "$ARCHIVE_DIR/" 2>/dev/null

# Alte Pläne archivieren (behalte aktuelle)
echo "📋 Archiviere alte Pläne..."
mv REFACTORING_PLAN.md "$ARCHIVE_DIR/" 2>/dev/null
mv CODE_QUALITY_IMPROVEMENT_PLAN.md "$ARCHIVE_DIR/" 2>/dev/null

# Erstelle Index der archivierten Dateien
echo "📝 Erstelle Archiv-Index..."
cat > "$ARCHIVE_DIR/ARCHIVE_INDEX.md" << EOF
# Archivierte Reports - $(date +%Y-%m-%d)

## Abgeschlossene Phase-Berichte
- PHASE_1_COMPLETION_SUMMARY.md - Phase 1 Code-Qualitätsverbesserung
- PHASE_2_COMPLETION_SUMMARY.md - Phase 2 Code-Style und Formatierung
- PHASE_3_COMPLETION_SUMMARY.md - Phase 3 Sicherheit und Best Practices
- PHASE_4_COMPLETION_SUMMARY.md - Phase 4 Typannotationen
- PHASE1_COMPLETION_SUMMARY.md - Duplikat von Phase 1
- PHASE_5_TASKS_COMPLETION_SUMMARY.md - Phase 5 Tasks

## Alte Analysen
- PHASE_1_ANALYSIS.md - Ursprüngliche Phase 1 Analyse
- PHASE_2_ANALYSIS.md - Ursprüngliche Phase 2 Analyse
- CODE_QUALITY_ANALYSIS.md - Ursprüngliche Code-Qualitätsanalyse
- CODE_QUALITY_ANALYSIS_REPORT.md - Code-Qualitätsbericht

## Alte Implementierungsberichte
- REFACTORING_IMPLEMENTATION_SUMMARY.md - Alte Refactoring-Implementierung
- REFACTORING_STATUS_SUMMARY.md - Alter Refactoring-Status
- CODE_CLEANUP_SUMMARY.md - Code-Cleanup-Zusammenfassung
- DOCUMENTATION_CLEANUP_COMPLETE.md - Dokumentation-Cleanup

## Alte Pläne
- REFACTORING_PLAN.md - Ursprünglicher Refactoring-Plan
- CODE_QUALITY_IMPROVEMENT_PLAN.md - Code-Qualitätsverbesserungsplan

## Hinweis
Diese Dateien wurden archiviert, da sie durch neuere, konsolidierte Berichte ersetzt wurden.
Für aktuelle Informationen siehe: CONSOLIDATED_PROJECT_STATUS.md
EOF

echo "✅ Archivierung abgeschlossen!"
echo "📁 Archiviert in: $ARCHIVE_DIR"
echo "📋 Index erstellt: $ARCHIVE_DIR/ARCHIVE_INDEX.md"

# Zeige verbleibende aktuelle Dateien
echo ""
echo "📋 Verbleibende aktuelle Dateien:"
echo "✅ CONSOLIDATED_PROJECT_STATUS.md - Konsolidierter Projektstatus"
echo "✅ FINAL_COMPLETION_SUMMARY.md - Finale Zusammenfassung"
echo "✅ NEXT_STEPS.md - Nächste Schritte"
echo "✅ PHASE_5_COMPLETION_SUMMARY.md - Aktuelle Phase 5 Zusammenfassung"
echo "✅ REFACTORING_ROADMAP.md - Aktuelle Roadmap"
echo "✅ UPDATED_REFACTORING_ANALYSIS.md - Aktualisierte Analyse"
echo "✅ improvement_progress.json - Aktuelle Metriken"
echo "✅ ruff-report.json - Aktuelle Ruff-Analyse"
echo "✅ bandit_report.json - Aktuelle Sicherheitsanalyse"

echo ""
echo "🎉 Cleanup erfolgreich abgeschlossen!"