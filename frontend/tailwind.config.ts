import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0A2342',
          light: '#0F3460',
          dark: '#061825',
        },
        accent: {
          blue: '#1D4ED8',
          light: '#3B82F6',
          cyan: '#06B6D4',
        },
        success: '#10B981',
        danger: '#EF4444',
        warning: '#F59E0B',
        surface: {
          DEFAULT: '#0D1117',
          card: '#161B22',
          elevated: '#1C2128',
          border: '#30363D',
        },
        text: {
          primary: '#E6EDF3',
          secondary: '#8B949E',
          muted: '#6E7681',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 20px rgba(29, 78, 216, 0.3)',
        'glow-lg': '0 0 40px rgba(29, 78, 216, 0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-right': 'slideRight 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideRight: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;