import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import prerenderPlugin from 'vite-plugin-prerender'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    prerenderPlugin({
      // Routes to pre-render for AI crawlers and SEO
      staticDir: path.join(__dirname, 'dist'),
      routes: [
        '/',
        '/pricing',
        '/doc',
        '/terms',
        '/privacy',
        '/login',
        '/signup',
      ],
      renderer: '@prerenderer/renderer-puppeteer',
      rendererOptions: {
        maxConcurrentRoutes: 4,
        renderAfterTime: 500, // Wait for React to render
      },
    }),
  ],
  build: {
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 6677,
    proxy: {
      '/api': {
        target: 'http://localhost:7223',
        changeOrigin: true,
      },
    },
  },
})
