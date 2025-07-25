# Design System Dokumentation

## Übersicht

Das Design-System implementiert ein konsistentes, WCAG-konformes Farbschema mit harmonischen Übergängen zwischen hellen und dunklen Modi. Es basiert auf dem Ant Design Framework und erweitert es um spezifische Farben und Komponenten.

## Farbpalette

### Heller Modus
- **Hintergrund**: White Smoke (#F7F9FB)
- **Primär**: Deep Indigo (#23224A)
- **Sekundär**: Soft Azure (#5BC6E8)
- **Akzent**: Accent Lime (#B6E74B)
- **Flächen**: Warm Sand (#F5E9DD)
- **Text**: Deep Indigo (#23224A) / Slate Grey (#7A869A)

### Dunkler Modus
- **Hintergrund**: Deep Indigo (#23224A)
- **Sekundär-Hintergrund**: Dunkleres Grau (#1A1A33)
- **Primär**: Soft Azure (#5BC6E8)
- **Akzent**: Accent Lime (#B6E74B) - reduziert in Helligkeit
- **Flächen**: Dezentes Dunkelgrau (#2D2D4D)
- **Text**: White Smoke (#F7F9FB) / Soft Azure (#5BC6E8)

## Design-Prinzipien

### 1. Harmonische Übergänge
- Farben werden nicht stumpf invertiert
- Jede Farbe hat eine harmonische Entsprechung im anderen Modus
- Warm Sand wird im dunklen Modus durch dezentes Dunkelgrau ersetzt

### 2. Konsistente Akzente
- Accent Lime bleibt in beiden Modi erhalten
- Im dunklen Modus wird die Sättigung reduziert um Überstrahlung zu vermeiden

### 3. WCAG-Konformität
- Mindestens AA-Standard (Kontrast 4.5:1)
- Idealerweise AAA-Standard (Kontrast 7:1)
- Automatische Kontrast-Optimierung

### 4. Tiefe und Hierarchie
- Verschiedene Schatten-Ebenen für Tiefe
- Staffelung von Flächenfarben im dunklen Modus
- Klare visuelle Hierarchie

## Komponenten

### Theme Store
```typescript
import { useThemeStore } from '../store/themeStore';

const { mode, toggleMode, getCurrentColors } = useThemeStore();
const colors = getCurrentColors();
```

### CSS-Variablen
Alle Farben sind als CSS-Variablen verfügbar:
```css
background-color: var(--colorBgBase);
color: var(--colorPrimary);
border: 1px solid var(--colorBorder);
```

### Utility-Klassen
```css
.text-primary { color: var(--colorPrimary); }
.bg-surface { background-color: var(--colorSurface); }
.btn-accent { /* Accent Button Styles */ }
```

## Chat-spezifische Farben

### User Messages
- **Hell**: Soft Azure Hintergrund mit Deep Indigo Text
- **Dunkel**: Abgedunkelter Azure mit White Smoke Text

### AI Messages
- **Hell**: Warm Sand Hintergrund mit Deep Indigo Text
- **Dunkel**: Dunkles Grau mit Soft Azure Text

## Implementierung

### 1. Theme-Integration
```typescript
// In App.tsx
const { mode, getCurrentTheme } = useThemeStore();
const currentTheme = getCurrentTheme();

<ConfigProvider
  theme={{
    algorithm: mode === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
    token: currentTheme.token,
  }}
>
```

### 2. Dynamische CSS-Variablen
```typescript
// In main.tsx
const cssVariables = generateCSSVariables(mode === 'dark');
Object.entries(cssVariables).forEach(([key, value]) => {
  root.style.setProperty(key, value);
});
```

### 3. Komponenten-Styling
```typescript
const colors = getCurrentColors();

const style = {
  backgroundColor: colors.colorBgContainer,
  color: colors.colorTextBase,
  border: `1px solid ${colors.colorBorder}`,
};
```

## Responsive Design

### Breakpoints
- **Mobile**: < 480px
- **Tablet**: 480px - 768px
- **Desktop**: > 768px

### Anpassungen
- Reduzierte Padding auf kleinen Bildschirmen
- Kleinere Schriftgrößen
- Optimierte Touch-Targets

## Accessibility

### Focus Management
- Sichtbare Focus-Indikatoren
- Keyboard-Navigation
- Screen Reader Support

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}
```

### High Contrast
```css
@media (prefers-contrast: high) {
  :root {
    --colorBorder: #000000;
    --colorTextSecondary: #000000;
  }
}
```

## Best Practices

### 1. Farbverwendung
- Verwende immer die Theme-Farben, nie Hardcoded-Werte
- Nutze die vordefinierten Hover- und Active-States
- Teste Kontrast in beiden Modi

### 2. Komponenten-Entwicklung
- Verwende CSS-Variablen für dynamische Anpassungen
- Implementiere Theme-Aware Styling
- Teste in beiden Modi

### 3. Performance
- CSS-Variablen für smooth Theme-Wechsel
- Vermeide JavaScript-basierte Style-Berechnungen
- Nutze CSS-Transitions für Animationen

## Troubleshooting

### Theme-Wechsel funktioniert nicht
1. Prüfe Theme Store Integration
2. Verifiziere CSS-Variablen Setzung
3. Kontrolliere Ant Design ConfigProvider

### Farben werden nicht angewendet
1. Prüfe CSS-Variablen Namen
2. Verifiziere Theme Store State
3. Kontrolliere CSS-Spezifität

### Kontrast-Probleme
1. Verwende WCAG-Kontrast-Checker
2. Teste in beiden Modi
3. Prüfe Farbkombinationen

## Neue Features (Implementiert)

### ✅ Erweiterte Typography-Skala
- Vollständige Font-Size-Skala (xs bis 6xl)
- Font-Weight-System (light bis extrabold)
- Line-Height-Varianten (tight bis loose)
- Letter-Spacing-Optionen (tighter bis widest)

### ✅ Umfassendes Spacing-System
- Konsistente Spacing-Skala (0 bis 24)
- Margin- und Padding-Utilities
- Gap-System für Flexbox/Grid
- Komponenten-spezifisches Spacing

### ✅ Moderne Komponenten
- **ModernButton**: Erweiterte Button-Varianten mit Micro-Interactions
- **ModernCard**: Flexible Card-System mit Hover-Effekten
- Erweiterte Animation-System mit Staggered-Effekten

### ✅ Enhanced Micro-Interactions
- Hover-Lift-Effekte
- Ripple-Animationen
- Smooth Transitions
- Loading-States mit Shimmer-Effekt

### ✅ Erweiterte Farbpalette
- Gradient-Farben für moderne UI
- Neutral-Farben für bessere Balance
- Verbesserte Kontrast-Verhältnisse

## Phase 2: Component Enhancement (Implementiert)

### ✅ Moderne Form-Elemente
- **ModernInput**: Erweiterte Input-Varianten mit Focus-States
- **ModernSelect**: Verbesserte Dropdown-Styles mit Animationen
- **ModernForm**: Flexibles Form-System mit Validation-States
- Password-Toggle und Clear-Funktionalität

### ✅ Enhanced Loading-States
- **SkeletonCard**: Moderne Skeleton-Loading für Cards
- **LoadingSpinner**: Verschiedene Spinner-Varianten
- **ProgressIndicator**: Gradient-Progress-Bars
- **LoadingOverlay**: Overlay-Loading mit Blur-Effekt
- **PulseLoading & WaveLoading**: Alternative Loading-Animationen

### ✅ Form-Validation & Feedback
- Real-time Validation-States
- Error/Warning/Success-Indikatoren
- Smooth Validation-Animationen
- Helper-Text mit Status-Farben

### ✅ Responsive Form-Layouts
- Grid-Layout-System für Forms
- Inline-Form-Varianten
- Mobile-optimierte Form-Elemente
- Flexible Form-Sections

## Zukünftige Erweiterungen

### Geplante Features
- Automatische Kontrast-Optimierung
- Icon-System mit SVG-Sprites
- Advanced Animation-Orchestrator
- Component Library Documentation

### Customization
- User-definierte Farben
- Theme-Export/Import
- Branding-Integration
- Custom Component Builder