import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      react({
        babel: {
          plugins: [['babel-plugin-react-compiler']],
        },
      }),
      tailwindcss()
    ],
    server: {
      proxy: {
        '/api/auth': {
          target: env.VITE_SPRINGBOOT_URL,
          changeOrigin: true,
          secure: false,
        },
        '/v3/api-docs': {
          target: env.VITE_SPRINGBOOT_URL,
          changeOrigin: true,
          secure: false,
        },
        '/swagger-ui': {
          target: env.VITE_SPRINGBOOT_URL,
          changeOrigin: true,
          secure: false,
        },
        '/actuator': {
          target: env.VITE_SPRINGBOOT_URL,
          changeOrigin: true,
          secure: false,
        },
        '/api/profile': {
          target: env.VITE_SPRINGBOOT_URL,
          changeOrigin: true,
          secure: false,
        },
        '/api/polls': {
          target: env.VITE_SPRINGBOOT_URL,
          changeOrigin: true,
          secure: false,
        },
        '/api/python': {
          target: env.VITE_PYTHON_URL,
          changeOrigin: true,
          secure: false,
        }
      }
    }
  }
})
