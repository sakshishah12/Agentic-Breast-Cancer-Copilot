/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 12px 30px rgba(20, 20, 20, 0.08)",
        lift: "0 18px 46px rgba(20, 20, 20, 0.14)",
      },
    },
  },
  plugins: [],
};
