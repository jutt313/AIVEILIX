import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, '..');

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, repoRoot, '');
  const port = Number(env.VITE_DEV_PORT || 5173);

  return {
    envDir: repoRoot,
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port,
    },
    preview: {
      host: '0.0.0.0',
      port,
    },
  };
});
