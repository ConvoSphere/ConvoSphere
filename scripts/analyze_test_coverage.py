#!/usr/bin/env python3
"""
Test Coverage Analysis Script

This script analyzes the current test coverage of the AI Assistant Platform
and generates a detailed report with recommendations for improvement.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class CoverageItem:
    """Represents a coverage item with its details."""

    name: str
    path: str
    lines: int
    has_tests: bool
    test_files: list[str]
    priority: str
    estimated_coverage: float


@dataclass
class CoverageReport:
    """Represents a complete coverage report."""

    backend_apis: list[CoverageItem]
    backend_services: list[CoverageItem]
    backend_models: list[CoverageItem]
    backend_utils: list[CoverageItem]
    frontend_components: list[CoverageItem]
    frontend_services: list[CoverageItem]
    frontend_pages: list[CoverageItem]
    frontend_store: list[CoverageItem]
    total_coverage: float
    recommendations: list[str]


class TestCoverageAnalyzer:
    """Analyzes test coverage for the AI Assistant Platform."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend-react"
        self.tests_path = self.project_root / "tests"
        self.backend_tests_path = self.backend_path / "tests"

    def analyze_backend_apis(self) -> list[CoverageItem]:
        """Analyze backend API endpoints coverage."""
        api_path = self.backend_path / "app" / "api" / "v1" / "endpoints"
        if not api_path.exists():
            return []

        items = []
        for file_path in api_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            name = file_path.stem
            lines = self._count_lines(file_path)
            has_tests, test_files = self._find_test_files(name, ["integration", "unit"])
            priority = self._determine_priority(name, lines, has_tests)
            estimated_coverage = 100.0 if has_tests else 0.0

            items.append(
                CoverageItem(
                    name=name,
                    path=str(file_path.relative_to(self.project_root)),
                    lines=lines,
                    has_tests=has_tests,
                    test_files=test_files,
                    priority=priority,
                    estimated_coverage=estimated_coverage,
                )
            )

        return sorted(items, key=lambda x: (x.priority == "HOCH", -x.lines))

    def analyze_backend_services(self) -> list[CoverageItem]:
        """Analyze backend services coverage."""
        services_path = self.backend_path / "app" / "services"
        if not services_path.exists():
            return []

        items = []
        for file_path in services_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            name = file_path.stem
            lines = self._count_lines(file_path)
            has_tests, test_files = self._find_test_files(name, ["integration", "unit"])
            priority = self._determine_priority(name, lines, has_tests)
            estimated_coverage = 100.0 if has_tests else 0.0

            items.append(
                CoverageItem(
                    name=name,
                    path=str(file_path.relative_to(self.project_root)),
                    lines=lines,
                    has_tests=has_tests,
                    test_files=test_files,
                    priority=priority,
                    estimated_coverage=estimated_coverage,
                )
            )

        return sorted(items, key=lambda x: (x.priority == "HOCH", -x.lines))

    def analyze_backend_models(self) -> list[CoverageItem]:
        """Analyze backend models coverage."""
        models_path = self.backend_path / "app" / "models"
        if not models_path.exists():
            return []

        items = []
        for file_path in models_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            name = file_path.stem
            lines = self._count_lines(file_path)
            has_tests, test_files = self._find_test_files(name, ["unit"])
            priority = "MITTEL" if has_tests else "NIEDRIG"
            estimated_coverage = 100.0 if has_tests else 0.0

            items.append(
                CoverageItem(
                    name=name,
                    path=str(file_path.relative_to(self.project_root)),
                    lines=lines,
                    has_tests=has_tests,
                    test_files=test_files,
                    priority=priority,
                    estimated_coverage=estimated_coverage,
                )
            )

        return items

    def analyze_backend_utils(self) -> list[CoverageItem]:
        """Analyze backend utilities coverage."""
        utils_path = self.backend_path / "app" / "utils"
        if not utils_path.exists():
            return []

        items = []
        for file_path in utils_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            name = file_path.stem
            lines = self._count_lines(file_path)
            has_tests, test_files = self._find_test_files(name, ["unit"])
            priority = "MITTEL" if has_tests else "NIEDRIG"
            estimated_coverage = 100.0 if has_tests else 0.0

            items.append(
                CoverageItem(
                    name=name,
                    path=str(file_path.relative_to(self.project_root)),
                    lines=lines,
                    has_tests=has_tests,
                    test_files=test_files,
                    priority=priority,
                    estimated_coverage=estimated_coverage,
                )
            )

        return items

    def analyze_frontend_components(self) -> list[CoverageItem]:
        """Analyze frontend components coverage."""
        components_path = self.frontend_path / "src" / "components"
        if not components_path.exists():
            return []

        items = []
        for file_path in components_path.glob("*.tsx"):
            if file_path.name.endswith(".test.tsx") or file_path.name.endswith(".bak"):
                continue

            name = file_path.stem
            lines = self._count_lines(file_path)
            has_tests, test_files = self._find_frontend_test_files(name, "components")
            priority = "MITTEL" if has_tests else "HOCH"
            estimated_coverage = 100.0 if has_tests else 0.0

            items.append(
                CoverageItem(
                    name=name,
                    path=str(file_path.relative_to(self.project_root)),
                    lines=lines,
                    has_tests=has_tests,
                    test_files=test_files,
                    priority=priority,
                    estimated_coverage=estimated_coverage,
                )
            )

        return sorted(items, key=lambda x: (x.priority == "HOCH", -x.lines))

    def analyze_frontend_services(self) -> list[CoverageItem]:
        """Analyze frontend services coverage."""
        services_path = self.frontend_path / "src" / "services"
        if not services_path.exists():
            return []

        items = []
        for file_path in services_path.glob("*.ts"):
            name = file_path.stem
            lines = self._count_lines(file_path)
            has_tests, test_files = self._find_frontend_test_files(name, "services")
            priority = "MITTEL" if has_tests else "HOCH"
            estimated_coverage = 100.0 if has_tests else 0.0

            items.append(
                CoverageItem(
                    name=name,
                    path=str(file_path.relative_to(self.project_root)),
                    lines=lines,
                    has_tests=has_tests,
                    test_files=test_files,
                    priority=priority,
                    estimated_coverage=estimated_coverage,
                )
            )

        return sorted(items, key=lambda x: (x.priority == "HOCH", -x.lines))

    def analyze_frontend_pages(self) -> list[CoverageItem]:
        """Analyze frontend pages coverage."""
        pages_path = self.frontend_path / "src" / "pages"
        if not pages_path.exists():
            return []

        items = []
        for file_path in pages_path.glob("*.tsx"):
            name = file_path.stem
            lines = self._count_lines(file_path)
            has_tests, test_files = self._find_frontend_test_files(name, "pages")
            priority = "NIEDRIG" if has_tests else "MITTEL"
            estimated_coverage = 100.0 if has_tests else 0.0

            items.append(
                CoverageItem(
                    name=name,
                    path=str(file_path.relative_to(self.project_root)),
                    lines=lines,
                    has_tests=has_tests,
                    test_files=test_files,
                    priority=priority,
                    estimated_coverage=estimated_coverage,
                )
            )

        return items

    def analyze_frontend_store(self) -> list[CoverageItem]:
        """Analyze frontend store coverage."""
        store_path = self.frontend_path / "src" / "store"
        if not store_path.exists():
            return []

        items = []
        for file_path in store_path.glob("*.ts"):
            name = file_path.stem
            lines = self._count_lines(file_path)
            has_tests, test_files = self._find_frontend_test_files(name, "store")
            priority = "MITTEL" if has_tests else "HOCH"
            estimated_coverage = 100.0 if has_tests else 0.0

            items.append(
                CoverageItem(
                    name=name,
                    path=str(file_path.relative_to(self.project_root)),
                    lines=lines,
                    has_tests=has_tests,
                    test_files=test_files,
                    priority=priority,
                    estimated_coverage=estimated_coverage,
                )
            )

        return sorted(items, key=lambda x: (x.priority == "HOCH", -x.lines))

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return len(f.readlines())
        except Exception:
            return 0

    def _find_test_files(
        self, name: str, test_types: list[str]
    ) -> tuple[bool, list[str]]:
        """Find test files for a given component name."""
        test_files = []
        has_tests = False

        # Check main tests directory
        for test_type in test_types:
            test_dir = self.tests_path / test_type / "backend"
            if test_dir.exists():
                for test_file in test_dir.glob(f"test_{name}.py"):
                    test_files.append(str(test_file.relative_to(self.project_root)))
                    has_tests = True

        # Check backend tests directory
        for test_type in test_types:
            test_dir = self.backend_tests_path / test_type
            if test_dir.exists():
                for test_file in test_dir.glob(f"test_{name}.py"):
                    test_files.append(str(test_file.relative_to(self.project_root)))
                    has_tests = True

        return has_tests, test_files

    def _find_frontend_test_files(
        self, name: str, component_type: str
    ) -> tuple[bool, list[str]]:
        """Find frontend test files for a given component name."""
        test_files = []
        has_tests = False

        # Check main tests directory
        test_dir = self.tests_path / "unit" / "frontend" / component_type
        if test_dir.exists():
            for test_file in test_dir.glob(f"test_{name}.ts"):
                test_files.append(str(test_file.relative_to(self.project_root)))
                has_tests = True

        return has_tests, test_files

    def _determine_priority(self, name: str, lines: int, has_tests: bool) -> str:
        """Determine priority for testing based on name and characteristics."""
        if has_tests:
            return "NIEDRIG"

        # High priority items
        high_priority_keywords = [
            "audit",
            "auth",
            "security",
            "rbac",
            "sso",
            "saml",
            "ai",
            "chat",
            "conversation",
            "assistant",
            "rag",
            "document",
            "embedding",
            "knowledge",
            "tool",
        ]

        if any(keyword in name.lower() for keyword in high_priority_keywords):
            return "HOCH"

        # Medium priority for large files
        if lines > 500:
            return "MITTEL"

        return "NIEDRIG"

    def calculate_total_coverage(self, items: list[CoverageItem]) -> float:
        """Calculate total coverage percentage."""
        if not items:
            return 0.0

        total_lines = sum(item.lines for item in items)
        covered_lines = sum(
            item.lines * (item.estimated_coverage / 100.0) for item in items
        )

        return (covered_lines / total_lines * 100.0) if total_lines > 0 else 0.0

    def generate_recommendations(self, report: CoverageReport) -> list[str]:
        """Generate recommendations based on coverage analysis."""
        recommendations = []

        # Backend API recommendations
        untested_apis = [item for item in report.backend_apis if not item.has_tests]
        if untested_apis:
            high_priority_apis = [
                item for item in untested_apis if item.priority == "HOCH"
            ]
            if high_priority_apis:
                recommendations.append(
                    f"🔴 KRITISCH: {len(high_priority_apis)} hochprioritäre API-Endpoints haben keine Tests: "
                    f"{', '.join(item.name for item in high_priority_apis[:5])}"
                )

        # Backend Services recommendations
        untested_services = [
            item for item in report.backend_services if not item.has_tests
        ]
        if untested_services:
            high_priority_services = [
                item for item in untested_services if item.priority == "HOCH"
            ]
            if high_priority_services:
                recommendations.append(
                    f"🔴 KRITISCH: {len(high_priority_services)} hochprioritäre Services haben keine Tests: "
                    f"{', '.join(item.name for item in high_priority_services[:5])}"
                )

        # Frontend recommendations
        untested_components = [
            item for item in report.frontend_components if not item.has_tests
        ]
        if untested_components:
            recommendations.append(
                f"🟡 WARNUNG: {len(untested_components)} Frontend-Komponenten haben keine Tests"
            )

        # Coverage targets
        if report.total_coverage < 50:
            recommendations.append("🔴 KRITISCH: Gesamt-Testabdeckung unter 50%")
        elif report.total_coverage < 70:
            recommendations.append("🟡 WARNUNG: Gesamt-Testabdeckung unter 70%")

        return recommendations

    def generate_report(self) -> CoverageReport:
        """Generate a complete coverage report."""
        print("🔍 Analysiere Testabdeckung...")

        backend_apis = self.analyze_backend_apis()
        backend_services = self.analyze_backend_services()
        backend_models = self.analyze_backend_models()
        backend_utils = self.analyze_backend_utils()
        frontend_components = self.analyze_frontend_components()
        frontend_services = self.analyze_frontend_services()
        frontend_pages = self.analyze_frontend_pages()
        frontend_store = self.analyze_frontend_store()

        # Calculate total coverage
        all_items = (
            backend_apis
            + backend_services
            + backend_models
            + backend_utils
            + frontend_components
            + frontend_services
            + frontend_pages
            + frontend_store
        )
        total_coverage = self.calculate_total_coverage(all_items)

        report = CoverageReport(
            backend_apis=backend_apis,
            backend_services=backend_services,
            backend_models=backend_models,
            backend_utils=backend_utils,
            frontend_components=frontend_components,
            frontend_services=frontend_services,
            frontend_pages=frontend_pages,
            frontend_store=frontend_store,
            total_coverage=total_coverage,
            recommendations=[],
        )

        report.recommendations = self.generate_recommendations(report)
        return report

    def print_report(self, report: CoverageReport):
        """Print a formatted coverage report."""
        print("\n" + "=" * 80)
        print("📊 TEST COVERAGE ANALYSE BERICHT")
        print("=" * 80)
        print(f"📅 Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Gesamt-Testabdeckung: {report.total_coverage:.1f}%")
        print()

        # Backend APIs
        print("🔧 BACKEND APIs")
        print("-" * 40)
        self._print_coverage_section(report.backend_apis)
        print()

        # Backend Services
        print("⚙️  BACKEND SERVICES")
        print("-" * 40)
        self._print_coverage_section(report.backend_services)
        print()

        # Frontend Components
        print("🎨 FRONTEND COMPONENTS")
        print("-" * 40)
        self._print_coverage_section(report.frontend_components)
        print()

        # Frontend Services
        print("🔌 FRONTEND SERVICES")
        print("-" * 40)
        self._print_coverage_section(report.frontend_services)
        print()

        # Recommendations
        if report.recommendations:
            print("💡 EMPFEHLUNGEN")
            print("-" * 40)
            for rec in report.recommendations:
                print(f"  {rec}")
            print()

        # Summary
        print("📈 ZUSAMMENFASSUNG")
        print("-" * 40)
        print(
            f"  Backend APIs: {len([i for i in report.backend_apis if i.has_tests])}/{len(report.backend_apis)} getestet"
        )
        print(
            f"  Backend Services: {len([i for i in report.backend_services if i.has_tests])}/{len(report.backend_services)} getestet"
        )
        print(
            f"  Frontend Components: {len([i for i in report.frontend_components if i.has_tests])}/{len(report.frontend_components)} getestet"
        )
        print(
            f"  Frontend Services: {len([i for i in report.frontend_services if i.has_tests])}/{len(report.frontend_services)} getestet"
        )

    def _print_coverage_section(self, items: list[CoverageItem]):
        """Print a coverage section."""
        for item in items:
            status = "✅" if item.has_tests else "❌"
            priority_emoji = {"HOCH": "🔴", "MITTEL": "🟡", "NIEDRIG": "🟢"}[
                item.priority
            ]
            print(
                f"  {status} {priority_emoji} {item.name:<30} ({item.lines:>4} Zeilen)"
            )

    def save_report_json(
        self, report: CoverageReport, output_path: str = "test_coverage_report.json"
    ):
        """Save the report as JSON."""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_coverage": report.total_coverage,
            "backend_apis": [self._item_to_dict(item) for item in report.backend_apis],
            "backend_services": [
                self._item_to_dict(item) for item in report.backend_services
            ],
            "backend_models": [
                self._item_to_dict(item) for item in report.backend_models
            ],
            "backend_utils": [
                self._item_to_dict(item) for item in report.backend_utils
            ],
            "frontend_components": [
                self._item_to_dict(item) for item in report.frontend_components
            ],
            "frontend_services": [
                self._item_to_dict(item) for item in report.frontend_services
            ],
            "frontend_pages": [
                self._item_to_dict(item) for item in report.frontend_pages
            ],
            "frontend_store": [
                self._item_to_dict(item) for item in report.frontend_store
            ],
            "recommendations": report.recommendations,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"📄 Bericht gespeichert: {output_path}")

    def _item_to_dict(self, item: CoverageItem) -> dict:
        """Convert CoverageItem to dictionary."""
        return {
            "name": item.name,
            "path": item.path,
            "lines": item.lines,
            "has_tests": item.has_tests,
            "test_files": item.test_files,
            "priority": item.priority,
            "estimated_coverage": item.estimated_coverage,
        }


def main():
    """Main function."""
    analyzer = TestCoverageAnalyzer()
    report = analyzer.generate_report()
    analyzer.print_report(report)
    analyzer.save_report_json(report)


if __name__ == "__main__":
    main()
