import path from "path"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import viteCompression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // Gzip 压缩
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240, // 10KB 以上的文件才压缩
      algorithm: 'gzip',
      ext: '.gz',
    }),
    // Brotli 压缩
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240, // 10KB 以上的文件才压缩
      algorithm: 'brotliCompress',
      ext: '.br',
      compressionOptions: {
        level: 11,
      },
      deleteOriginFile: false,
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:5085"
      },
    },
  },
  build: {
    assetsDir: 'static',
    // 生成 source map（开发阶段可以设为 true）
    sourcemap: false,
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 设置 chunk 大小警告限制
    chunkSizeWarningLimit: 1000, // 1MB
    // 静态资源内联阈值
    assetsInlineLimit: 4096, // 4KB
  },
  // 定义全局常量
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
})
