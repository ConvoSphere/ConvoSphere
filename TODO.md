# TODO – Frontend/Backend Arbeiten zur Fortführung

## Kurzüberblick (bereits umgesetzt)
- Flexible Dashboard-Architektur mit Widget-Registry (`components/widgets/registry.ts`).
- `SystemMetrics` als Dashboard-Widget integriert.
- Grid-Layout umgesetzt: positionsbasierte Anordnung via `gridLayout` (24 Spalten, 50px-Zellen).
- Dashboard-Persistenz: Frontend-Service + Backend-API (`GET/PUT /api/v1/dashboard/me/dashboard`).
- Backend: Modell `UserDashboard` (UUID FK `user_id`, JSON `widgets`, `layout`), Router eingebunden.
- Reporting-Store: `systemSummary` + `systemMetrics`; Admin-Stats nutzen diese Daten.
- i18n: Basis-Keys für `widgets.*` und `monitoring.*` ergänzt.

---

## Offene Arbeitspakete

### 1) Einstellungen/Config modularisieren
- `pages/Settings.tsx` aufteilen in kleine Komponenten unter `components/settings/*`:
  - `GeneralSettings`, `NotificationsSettings`, `PrivacySettings`, `ThemeSettings`, `AIModelSettings`.
- Schema-getriebener Form-Renderer:
  - Feldschema (Typ, Label-Key, Hilfetext, Validierung, Transform z. B. MB ↔ Bytes).
  - Wiederverwendung im Admin `SystemConfig` für konsistente UIs.
- Zentraler `settingsStore` (Zustand):
  - Laden/Speichern (Server bevorzugt, LocalStorage als Fallback), Migrationspfad vom lokalen Component-State.

### 2) Analytics-Bausteine und -Nutzung
- Komponenten unter `components/analytics/`:
  - `StatCard` (vorhanden) konsequent nutzen.
  - `KPIGrid`, `TrendBadge`, `TimeSeriesChart` (Wrapper), `BreakdownList`.
- `SystemStats.tsx` und Widgets (`StatsWidget`, `ChartWidget`) auf diese Bausteine umstellen.
- Einheitliche Toolbar (Zeitbereich, Auto-Refresh, Export CSV/JSON) als wiederverwendbarer Header.

### 3) Routing & Informationsarchitektur
- Admin-Deep-Links: Tabs mit Route synchronisieren (`/admin/:tab`, z. B. `/admin/stats`, `/admin/config`, `/admin/audit`).
- Breadcrumbs/Seitentitel vereinheitlichen.

### 4) UX-Standards (Loading/Error/Refresh)
- `useAsyncData`-Hook einführen: Loading/Error/Retry/StaleTime konsistent.
- Konsistente Refresh-Logik: globale „Refresh all“ Aktion, `lastRefresh` anzeigen (WidgetBase unterstützt dies bereits).

### 5) Dashboard-Funktionen abrunden
- Widget-Settings-Trigger: `openWidgetSettings` an Widgets anbinden (Kontext/Prop), sodass Settings direkt aus dem Widget-Menü geöffnet werden.
- Größen-Synchronisierung: `ResizableBox`-Pixelgrößen mit `gridLayout.width/height` harmonisieren oder eine Quelle als führend definieren.
- Default-Layout-Generator verbessern (aktuell simple Rasterlogik; Kollisionen vermeiden, Spannen sinnvoll wählen).
- `saveDashboard()`-Optimierung: Debounce/Throttle bei Move/Resize.

### 6) Backend-Persistenz finalisieren
- Alembic-Migration für `user_dashboards` erstellen (Tabelle, Indizes, FK `user_id`).
- Backend-Tests für `GET/PUT /api/v1/dashboard/me/dashboard` (Auth, Validierung, Limits).
- Optional: Payload-Validierung (Max. Widgets, Max. Layoutgröße), Schema via Pydantic verfeinern.

### 7) Internationalisierung (i18n)
- Keys-Audit und Ergänzungen in `de.json`, `en.json`, `fr.json`, `es.json` (insbesondere `dashboard.*`, `admin.*`, `settings.*`).
- Fehlende Übersetzungen nachziehen; konsistente Namensräume sicherstellen.

### 8) Build/Tests
- Frontend Build/Test lauffähig machen (Vite/Vitest in CI/Dev-Umgebung sicherstellen).
- Tests aktualisieren/ergänzen:
  - Widget-Registry-Rendering und Fallback.
  - `SystemMetricsWidget` Lade-/Errorfälle.
  - Admin-Stats über `reportingStore` (Disk/Uptime integriert).
  - Grid-Layout-Persistenz (Move/Resize/Reload) und Backend-Roundtrip.
  - E2E: `/admin/:tab` Deep-Linking, Dashboard-Persistenz über Reload.

### 9) Offline/Synchronisation
- Offline-Queue für Dashboard-Persistenz (PUTs zwischenpuffern, Retry bei Reconnect).
- Konfliktstrategie bei paralleler Änderung (Client vs. Server – „last write wins“ oder Versionszähler).

### 10) Sicherheit & Validierung
- Autorisierung prüfen (nur eigener Dashboard-State zugreifbar).
- Rate-Limits für `PUT /me/dashboard` (Move/Resize-Spam eindämmen).
- Payload-Validierung (z. B. gültige Widget-Typen nur aus Registry).

### 11) Performance
- Network: Batching/Throttling bei häufiger Interaktion (Resize/Move).
- Rendering: Memoization des Registry-Lookups, Virtualisierung bei vielen Widgets.

### 12) Dokumentation
- README für Widget-Registry-API (Typen, DefaultSettings, Capabilities).
- Reporting-API/Store-Dokumentation.
- Config-Form-Renderer: Schema-Beispiele und Best Practices.

---

## Nächste empfohlene Schritte
1) Settings modularisieren + Form-Renderer implementieren; `settingsStore` einführen.
2) Analytics-Bausteine erweitern und `SystemStats.tsx`/Widgets darauf umstellen.
3) Admin-Deep-Links + `useAsyncData` integrieren.
4) Alembic-Migration für `user_dashboards` und Backend-Tests.
5) Build/Tests stabilisieren (Vite/Vitest in der Umgebung lauffähig machen).

## Hinweise
- Grid-Layout: aktuell 24 Spalten, 50px-Zellen – bei Bedarf zentral konfigurierbar machen.
- `dashboardService`: bei Fehlern Fallback auf LocalStorage vorhanden; Offline-Strategie (Queue) offen.