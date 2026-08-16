import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          main: '#499A13',
          accent: '#BBDC12',
          light: '#8ECA3C',
          dark: '#276F27',
        },
        gray: {
          50: '#effaf0',
          100: '#def4e1',
          200: '#bfe7c4',
          300: '#8ed196',
          400: '#63b46c',
          500: '#3f8e48',
          600: '#2e6e35',
          700: '#225328',
          800: '#193e1e',
          900: '#102913',
          950: '#0a1c0d',
        },
        background: '#0f1115',
        surface: '#181b21',
        border: '#272b36',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}

export default config
