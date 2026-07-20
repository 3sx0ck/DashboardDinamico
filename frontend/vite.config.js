import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    // Bind-mounts en Docker (colima) no emiten eventos de FS fiables;
    // el polling asegura que HMR detecte cambios de archivos del host.
    watch: { usePolling: true, interval: 200 },
  },
})
