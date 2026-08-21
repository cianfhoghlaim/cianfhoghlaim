/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Crypto-themed colors
        crypto: {
          primary: '#6366f1', // Indigo
          secondary: '#8b5cf6', // Violet
          accent: '#22c55e', // Green for gains
          danger: '#ef4444', // Red for losses
          dark: '#0f172a',
          darker: '#020617',
        },
      },
    },
  },
  plugins: [],
};
