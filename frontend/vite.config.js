import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiProxyTarget = env.VITE_PROXY_TARGET || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      host: true,
      // Túneles (ngrok, etc.): Vite valida el Host; sin esto rechaza *.ngrok-free.app
      allowedHosts: true,
      // Bind-mounts en Docker (colima) no emiten eventos de FS fiables;
      // el polling asegura que HMR detecte cambios de archivos del host.
      watch: { usePolling: true, interval: 200 },
      proxy: {
        '/api': {
          target: apiProxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
