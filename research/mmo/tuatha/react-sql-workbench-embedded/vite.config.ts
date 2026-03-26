import { resolve } from 'path';
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite';
import { minify as terserMinify } from 'terser';
import dts from 'vite-plugin-dts';
import pkg from './package.json';

const banner = `/**
 * React Component for SQL Workbench Embedded v${pkg.version}
 * ${pkg.description}
 * https://github.com/tobilg/react-sql-workbench-embedded
 * (c) ${new Date().getFullYear()} ${pkg.author} - ${pkg.license} License
 */
`;

// Custom plugin to minify ESM build and add banner
const minifyESM = (): Plugin => ({
  name: 'minify-esm',
  apply: 'build',
  async generateBundle(_options, bundle) {
    for (const fileName in bundle) {
      const chunk = bundle[fileName];
      if (chunk.type === 'chunk' && fileName.endsWith('.esm.js')) {
        const minified = await terserMinify(chunk.code, {
          compress: {
            drop_console: true,
          },
          format: {
            comments: false,
            preamble: banner,
          },
          sourceMap: false,
        });
        if (minified.code) {
          chunk.code = minified.code;
        }
      }
    }
  },
});

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    dts({
      insertTypesEntry: true,
      rollupTypes: true, // Bundle all .d.ts files into a single file
      exclude: ['**/*.test.ts', '**/*.spec.ts', '**/__tests__/**', 'examples/**', 'node_modules/**'],
    }),
    minifyESM(),
    react({
      // Use classic JSX runtime for better UMD compatibility
      // This avoids the need for jsx-runtime polyfills
      jsxRuntime: 'classic'
    })
  ],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'SQLWorkbenchEmbedded',
      formats: ['umd', 'es'],
      fileName: (format) => {
        if (format === 'umd') return 'react-sql-workbench-embedded.umd.js';
        if (format === 'es') return 'react-sql-workbench-embedded.esm.js';
        return `react-sql-workbench-embedded.${format}.js`;
      },
    },
    rollupOptions: {
      external: [
        'react',
        'react-dom',
        // Don't externalize sql-workbench-embedded - we want to bundle it
        // But keep @duckdb/duckdb-wasm external since it's loaded dynamically at runtime
        '@duckdb/duckdb-wasm'
      ],
      output: [
        {
          format: 'es',
          // Force everything into a single chunk (no code splitting)
          inlineDynamicImports: true,
        },
        {
          format: 'umd',
          name: 'SQLWorkbenchEmbedded',
          globals: {
            react: 'React',
            'react-dom': 'ReactDOM',
          },
          // UMD format automatically inlines everything
        }
      ],
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      },
      format: {
        comments: false,
        preamble: banner,
      },
    },
    sourcemap: false, // Disable sourcemaps for production builds
  },
})
