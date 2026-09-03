/**
 * TanStack Start configuration for Crypteolas
 */

import { defineConfig } from '@tanstack/react-start/config';
import viteTsConfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  vite: {
    plugins: [viteTsConfigPaths()],
  },
  server: {
    preset: 'node-server',
  },
});
