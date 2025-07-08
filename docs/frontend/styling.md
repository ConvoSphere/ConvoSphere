# Styling & Theming

Tailwind CSS powers all visual aspects while fully reflecting the ConvoSphere Brandbook.

---

## 1. Tailwind Setup

```bash
pnpm add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

`tailwind.config.ts` is extended with brand colors (see below) and design tokens (spacing, radius, shadows).

## 2. Color Palette

```ts title="tailwind.config.ts"{5-16}
export default {
  theme: {
    extend: {
      colors: {
        indigo: {
          DEFAULT: '#23224A',
          50: '#e4e4eb',
          900: '#16152c',
        },
        azure: '#5BC6E8',
        sand: '#F5E9DD',
        lime: '#B6E74B',
        slate: '#7A869A',
        smoke: '#F7F9FB',
      },
    },
  },
  darkMode: 'class',
};
```

### Light / Dark Variables

Global CSS variables ensure easy swapping:

```css title="src/styles/theme.css"
:root {
  --bg: theme('colors.smoke');
  --text: theme('colors.indigo');
  --primary: theme('colors.azure');
  --accent: theme('colors.lime');
}

.dark {
  --bg: theme('colors.indigo');
  --text: theme('colors.smoke');
  --primary: theme('colors.azure');
  --accent: theme('colors.lime');
}
```

Components use Tailwind utilities driven by these vars:

```tsx
<button className="px-4 py-2 font-semibold rounded bg-[var(--primary)] text-[var(--bg)] hover:opacity-90">
  Senden
</button>
```

## 3. Typography

* **Inter** (400/600/700) for UI copy. Imported via Google Fonts in `index.html`.
* **Roboto Mono** for code blocks.

```css
a {
  @apply text-azure hover:underline;
}
```

## 4. Animations

Minimal, subtle transitions using Tailwind’s `transition` utilities and `@keyframes` for chat bubble fade-in.

## 5. Accessibility

* Color contrast meets WCAG AA+ (checked via `@tailwindcss/aspect-ratio` & `@tailwindcss/forms`).
* Focus indicators `outline-azure` on interactive elements.

## 6. Iconography

`react-icons` with a custom wrapper enforcing size + color; icons adapt to theme automatically.

## 7. Example Component – Message Bubble

```tsx
export const MessageBubble = ({ role, text }: Props) => (
  <div
    className={`max-w-xl px-4 py-3 my-2 rounded-lg shadow
      ${role === 'user' ? 'bg-azure text-indigo ml-auto' : 'bg-sand text-indigo'}
      dark:${role === 'user' ? 'bg-azure/80 text-smoke' : 'bg-[#2D2D4D] text-smoke'}
    `}
  >
    {text}
  </div>
);
```

---
By codifying design tokens in Tailwind, we ensure consistency and ease of future brand iterations.
