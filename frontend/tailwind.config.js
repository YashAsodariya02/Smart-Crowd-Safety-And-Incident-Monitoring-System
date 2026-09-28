/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brutal-bg': '#181A1E',
        'brutal-surface': '#22252A',
        'brutal-card': '#1C1F24',
        'accent-critical': '#FF005B',
        'accent-warning': '#FFE53B',
        'accent-safe': '#00FF5B',
        'accent-info': '#2D27FF',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'],
        heading: ['"Space Grotesk"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
