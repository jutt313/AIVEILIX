/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark theme
        dark: {
          primary: '#0B3C49',
          accent: '#2DFFB7',
          bg: '#050B0D',
          surface: '#0E1F24',
          text: '#E6F1F5',
        },
        // Light theme
        light: {
          primary: '#0B3C49',
          accent: '#1FE0A5',
          bg: '#E5F2ED',
          surface: '#D9EDE5',
          text: '#062A33',
        },
      },
    },
  },
  plugins: [],
}
