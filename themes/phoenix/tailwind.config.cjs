const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: [
    './templates/**/*.html',
    './templates/**/*.jinja',
    './src/**/*.{js,ts}',
    '../../templates/**/*.html'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f7ff',
          100: '#ebf0fe',
          200: '#dce4fd',
          300: '#bccbfb',
          400: '#97a9f7',
          500: '#7c8ef1',
          600: '#6366f1',
          700: '#5558e3',
          800: '#4547c8',
          900: '#3d3fa2',
          950: '#262763',
          DEFAULT: '#6366f1'
        },
        accent: {
          50: '#fdf3ec',
          100: '#fbe3d0',
          200: '#f6c2a0',
          300: '#f09b6c',
          400: '#ea6f36',
          500: '#de4a0f',
          600: '#c13909',
          700: '#99270b',
          800: '#7a2212',
          900: '#641f14',
          DEFAULT: '#ea6f36'
        }
      },
      fontFamily: {
        sans: ['"Inter"', '"Segoe UI"', ...defaultTheme.fontFamily.sans],
        heading: ['"Plus Jakarta Sans"', '"Inter"', ...defaultTheme.fontFamily.sans]
      },
      boxShadow: {
        soft: '0 20px 40px -24px rgba(15, 46, 80, 0.25)'
      },
      maxWidth: {
        '8xl': '88rem'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
};
