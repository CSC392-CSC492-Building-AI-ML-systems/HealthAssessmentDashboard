import './globals.css'; 

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./app/**/*.{js,ts,jsx,tsx}",     // if you're using the app directory
      "./pages/**/*.{js,ts,jsx,tsx}",   
      "./components/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          background: "var(--background)",
          foreground: "var(--foreground)",
          brandDark: "var(--brand-dark)",
          brandLight: "var(--brand-light)",
          buttonRed: "var(--button-red)",
          textLight: "var(--text-light)",
          featureBg: "var(--feature-bg)",
        },
        fontFamily: {
          sans: "var(--font-sans)",
          mono: "var(--font-mono)",
          inter: "var(--font-inter)",
          outfit: "var(--font-outfit)"
        },
      },
    },
    plugins: [],
  }
  