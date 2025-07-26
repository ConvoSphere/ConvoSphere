# ConvoSphere Logo Collection

## Übersicht

Die ConvoSphere Logo-Sammlung besteht aus verschiedenen SVG-Varianten, die für unterschiedliche Anwendungsfälle optimiert wurden. Alle Logos sind vollständig skalierbar und enthalten sanfte Animationen.

## Logo-Varianten

### 1. `logo-convosphere.svg` (200x200)

**Hauptlogo für große Anwendungen**

- Vollständige Animation mit allen Elementen
- Optimiert für Header, Landing Pages und Marketing-Material
- Enthält: Hauptsphäre, KI-Schaltkreise, Konversationslinien, AI-Nodes, Datenpartikel

### 2. `logo-convosphere-text.svg` (400x120)

**Textlogo mit integriertem Icon**

- Kombiniert das Sphere-Icon mit dem "ConvoSphere" Schriftzug
- Ideal für Navigation, Header und Branding
- Enthält Tagline "AI-Powered Conversations"

### 3. `logo-convosphere-icon.svg` (64x64)

**Icon-Version für mittlere Anwendungen**

- Reduzierte Komplexität bei Beibehaltung der Animation
- Perfekt für App-Icons, Buttons und kleinere UI-Elemente
- Optimiert für 64x64 Pixel Anzeige

### 4. `logo-convosphere-dark.svg` (200x200)

**Dark Theme Version**

- Erhöhte Sichtbarkeit auf dunklen Hintergründen
- Stärkere Glow-Effekte und Kontraste
- Zusätzliche Partikel für bessere Wirkung

### 5. `logo-convosphere-minimal.svg` (32x32)

**Minimal-Version für Favicon**

- Stark vereinfacht für sehr kleine Darstellungen
- Behält die Kernanimation bei
- Ideal für Favicon, Tab-Icons und 16x16/32x32 Anwendungen

## Design-Elemente

### Farbpalette (basierend auf Design-System)

- **Primär**: Deep Indigo (#23224A)
- **Sekundär**: Soft Azure (#5BC6E8)
- **Akzent**: Accent Lime (#B6E74B)
- **Hintergrund**: White Smoke (#F7F9FB) / Deep Indigo (#23224A)

### Animationen

- **Pulsierende Sphäre**: Sanfte Atmung der Hauptform (3s Zyklus)
- **Fließende Linien**: Wellenförmige Bewegung der Konversationslinien (3.5-4.5s)
- **Glühende Nodes**: Pulsierende AI-Verbindungspunkte (1.8-2.5s)
- **Datenpartikel**: Bewegende Punkte entlang der Konversationslinien

### KI-Elemente

- **Schaltkreise**: Organische Pfade mit Verbindungspunkten
- **AI-Nodes**: Glühende Verbindungspunkte
- **Datenfluss**: Animierte Partikel, die Informationen symbolisieren

## Verwendung

### Web-Anwendungen

```html
<!-- Hauptlogo -->
<img src="/logo-convosphere.svg" alt="ConvoSphere" />

<!-- Textlogo für Header -->
<img src="/logo-convosphere-text.svg" alt="ConvoSphere" />

<!-- Icon für Navigation -->
<img src="/logo-convosphere-icon.svg" alt="ConvoSphere" />
```

### React-Komponenten

```tsx
import { useThemeStore } from "../store/themeStore";

const Logo = () => {
  const { mode } = useThemeStore();

  return (
    <img
      src={
        mode === "dark" ? "/logo-convosphere-dark.svg" : "/logo-convosphere.svg"
      }
      alt="ConvoSphere"
    />
  );
};
```

### CSS-Integration

```css
.logo {
  width: 200px;
  height: 200px;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

/* Responsive Anpassungen */
@media (max-width: 768px) {
  .logo {
    width: 120px;
    height: 120px;
  }
}
```

## Technische Spezifikationen

### SVG-Features

- **Vollständig skalierbar**: Alle Größen ohne Qualitätsverlust
- **Animationen**: Native SVG-Animationen für bessere Performance
- **Gradienten**: Radial- und Linear-Gradienten für Tiefe
- **Filter**: Glow-Effekte für moderne Optik
- **Responsive**: ViewBox-basiert für flexible Größenanpassung

### Browser-Kompatibilität

- **Moderne Browser**: Vollständige Unterstützung (Chrome, Firefox, Safari, Edge)
- **Animationen**: SMIL-Animationen (SVG-native)
- **Gradienten**: CSS-Gradienten für Fallback

### Performance

- **Laufzeit**: ~3-5KB pro Logo-Variante
- **Animationen**: GPU-beschleunigt
- **Skalierung**: CPU-freundlich durch Vektor-Grafik

## Anpassungen

### Farben ändern

Die Farben können über CSS-Variablen angepasst werden:

```css
:root {
  --colorPrimary: #23224a;
  --colorSecondary: #5bc6e8;
  --colorAccent: #b6e74b;
}
```

### Animationen deaktivieren

```css
.logo * {
  animation: none !important;
}
```

### Größe anpassen

```css
.logo {
  width: 150px;
  height: 150px;
}
```

## Branding-Richtlinien

### Mindestgrößen

- **Hauptlogo**: 100x100px
- **Textlogo**: 200x60px
- **Icon**: 32x32px
- **Minimal**: 16x16px

### Abstände

- Mindestens 20px Abstand zu anderen Elementen
- Bei Textlogo: 30px Abstand zu Text-Elementen

### Hintergrund

- Hell: Standard-Version verwenden
- Dunkel: Dark-Version verwenden
- Kontrast: Mindestens 4.5:1 für WCAG-Konformität
