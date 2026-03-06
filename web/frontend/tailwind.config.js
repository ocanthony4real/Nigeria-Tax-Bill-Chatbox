/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'nigeria-green': '#008751',
        'nigeria-green-dark': '#006b40',
      },
    },
  },
  plugins: [],
}
