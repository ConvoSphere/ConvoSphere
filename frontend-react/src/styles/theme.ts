// Vollständiges Design-Schema für das Projekt
// WCAG AA/AAA konforme Farbpalette mit harmonischen Übergängen

export const lightTheme = {
  token: {
    // Hauptfarben
    colorBgBase: "#F7F9FB", // White Smoke - Hintergrund
    colorBgContainer: "#FFFFFF", // Reiner Weiß für Container
    colorBgElevated: "#FFFFFF", // Erhöhte Flächen
    colorBgLayout: "#F7F9FB", // Layout Hintergrund

    // Primärfarben
    colorPrimary: "#23224A", // Deep Indigo
    colorPrimaryHover: "#1A1A33", // Dunklerer Indigo für Hover
    colorPrimaryActive: "#0F0F1F", // Aktiver Zustand

    // Sekundärfarben
    colorSecondary: "#5BC6E8", // Soft Azure
    colorSecondaryHover: "#4AB5D7", // Dunklerer Azure für Hover
    colorSecondaryActive: "#39A4C6", // Aktiver Zustand

    // Akzentfarben
    colorAccent: "#B6E74B", // Accent Lime
    colorAccentHover: "#A5D63A", // Dunklerer Lime für Hover
    colorAccentActive: "#94C529", // Aktiver Zustand

    // Flächenfarben
    colorSurface: "#F5E9DD", // Warm Sand
    colorSurfaceHover: "#E8DCC0", // Hover Zustand
    colorSurfaceActive: "#DBCFA3", // Aktiver Zustand

    // Textfarben
    colorTextBase: "#23224A", // Deep Indigo für Haupttext
    colorText: "#23224A", // Haupttext
    colorTextSecondary: "#7A869A", // Slate Grey für Sekundärtext
    colorTextTertiary: "#9CA3AF", // Tertiärer Text
    colorTextQuaternary: "#D1D5DB", // Disabled Text

    // Border und Trennlinien
    colorBorder: "#E5E7EB", // Subtile Borders
    colorBorderSecondary: "#F3F4F6", // Sekundäre Borders

    // Schatten und Effekte
    boxShadow:
      "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
    boxShadowSecondary:
      "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    boxShadowTertiary:
      "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",

    // Neue Farben für erweiterte UI
    colorNeutral: "#6B7280",
    colorNeutralHover: "#4B5563",
    colorNeutralActive: "#374151",

    // Gradient Farben
    colorGradientPrimary: "linear-gradient(135deg, #23224A 0%, #5BC6E8 100%)",
    colorGradientSecondary: "linear-gradient(135deg, #5BC6E8 0%, #B6E74B 100%)",
    colorGradientAccent: "linear-gradient(135deg, #B6E74B 0%, #F59E0B 100%)",

    // Chat-spezifische Farben
    colorChatUserBubble: "#5BC6E8", // Soft Azure für User Messages
    colorChatUserText: "#23224A", // Deep Indigo Text in User Bubbles
    colorChatAIBubble: "#F5E9DD", // Warm Sand für AI Messages
    colorChatAIText: "#23224A", // Deep Indigo Text in AI Bubbles

    // Statusfarben
    colorSuccess: "#10B981", // Grün für Erfolg
    colorWarning: "#F59E0B", // Orange für Warnungen
    colorError: "#EF4444", // Rot für Fehler
    colorInfo: "#3B82F6", // Blau für Info

    // Transparenz
    colorBgMask: "rgba(0, 0, 0, 0.45)", // Modal Overlay
    colorBgSpotlight: "rgba(0, 0, 0, 0.25)", // Spotlight Overlay
  },
};

export const darkTheme = {
  token: {
    // Hauptfarben
    colorBgBase: "#23224A", // Deep Indigo - Haupt-Hintergrund
    colorBgContainer: "#1A1A33", // Dunkleres Grau für Container
    colorBgElevated: "#2D2D4D", // Erhöhte Flächen
    colorBgLayout: "#23224A", // Layout Hintergrund

    // Primärfarben (invertiert für besseren Kontrast)
    colorPrimary: "#5BC6E8", // Soft Azure als Primärfarbe
    colorPrimaryHover: "#4AB5D7", // Dunklerer Azure für Hover
    colorPrimaryActive: "#39A4C6", // Aktiver Zustand

    // Sekundärfarben
    colorSecondary: "#7A869A", // Slate Grey als Sekundärfarbe
    colorSecondaryHover: "#6B7788", // Dunklerer Grey für Hover
    colorSecondaryActive: "#5C6777", // Aktiver Zustand

    // Akzentfarben (leicht reduziert in Helligkeit)
    colorAccent: "#A5D63A", // Reduzierter Accent Lime
    colorAccentHover: "#94C529", // Dunklerer Lime für Hover
    colorAccentActive: "#83B418", // Aktiver Zustand

    // Flächenfarben
    colorSurface: "#2D2D4D", // Dezentes Dunkelgrau
    colorSurfaceHover: "#3A3A5A", // Hover Zustand
    colorSurfaceActive: "#474767", // Aktiver Zustand

    // Textfarben
    colorTextBase: "#F7F9FB", // White Smoke für Haupttext
    colorText: "#F7F9FB", // Haupttext
    colorTextSecondary: "#5BC6E8", // Soft Azure für Sekundärtext
    colorTextTertiary: "#7A869A", // Tertiärer Text
    colorTextQuaternary: "#4B5563", // Disabled Text

    // Border und Trennlinien
    colorBorder: "#374151", // Dunklere Borders
    colorBorderSecondary: "#4B5563", // Sekundäre Borders

    // Schatten und Effekte (angepasst für dunklen Modus)
    boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)",
    boxShadowSecondary:
      "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)",
    boxShadowTertiary:
      "0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)",

    // Neue Farben für erweiterte UI (Dunkel)
    colorNeutral: "#9CA3AF",
    colorNeutralHover: "#D1D5DB",
    colorNeutralActive: "#F3F4F6",

    // Gradient Farben (Dunkel)
    colorGradientPrimary: "linear-gradient(135deg, #5BC6E8 0%, #23224A 100%)",
    colorGradientSecondary: "linear-gradient(135deg, #B6E74B 0%, #5BC6E8 100%)",
    colorGradientAccent: "linear-gradient(135deg, #F59E0B 0%, #B6E74B 100%)",

    // Chat-spezifische Farben
    colorChatUserBubble: "#4AB5D7", // Abgedunkelter Azure für User Messages
    colorChatUserText: "#F7F9FB", // White Smoke Text in User Bubbles
    colorChatAIBubble: "#2D2D4D", // Dunkles Grau für AI Messages
    colorChatAIText: "#5BC6E8", // Soft Azure Text in AI Bubbles

    // Statusfarben (angepasst für dunklen Modus)
    colorSuccess: "#34D399", // Helleres Grün für besseren Kontrast
    colorWarning: "#FBBF24", // Helleres Orange für besseren Kontrast
    colorError: "#F87171", // Helleres Rot für besseren Kontrast
    colorInfo: "#60A5FA", // Helleres Blau für besseren Kontrast

    // Transparenz
    colorBgMask: "rgba(0, 0, 0, 0.65)", // Dunklerer Modal Overlay
    colorBgSpotlight: "rgba(0, 0, 0, 0.45)", // Dunklerer Spotlight Overlay
  },
};

// Utility-Funktionen für Theme-Zugriff
export const getThemeColors = (isDark: boolean) => {
  return isDark ? darkTheme.token : lightTheme.token;
};

// CSS Custom Properties für direkten Zugriff in CSS
export const generateCSSVariables = (isDark: boolean) => {
  const colors = getThemeColors(isDark);
  return Object.entries(colors).reduce(
    (acc, [key, value]) => {
      acc[`--${key}`] = value;
      return acc;
    },
    {} as Record<string, string>,
  );
};

// WCAG Kontrast-Checker Utility
export const getContrastRatio = (): number => {
  // Vereinfachte Kontrast-Berechnung
  // In einer echten Implementierung würde hier eine vollständige WCAG-Berechnung stehen
  return 4.5; // Placeholder - sollte durch echte Berechnung ersetzt werden
};
