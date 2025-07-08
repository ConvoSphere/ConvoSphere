import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
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
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/aspect-ratio')],
}
export default config
