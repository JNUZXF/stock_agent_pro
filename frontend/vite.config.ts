import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    // 优化依赖解析，解决嵌套依赖问题
    commonjsOptions: {
      include: [/node_modules/],
      transformMixedEsModules: true
    },
    rollupOptions: {
      output: {
        // 手动分割代码，将大型依赖库分离成独立的 chunk
        manualChunks(id) {
          // 将 node_modules 中的依赖分离
          if (id.includes('node_modules')) {
            // React 核心库单独打包
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor';
            }
            // Framer Motion 动画库单独打包（体积较大）
            if (id.includes('framer-motion')) {
              return 'framer-motion';
            }
            // Markdown 相关库单独打包
            if (
              id.includes('react-markdown') ||
              id.includes('remark-') ||
              id.includes('rehype-') ||
              id.includes('unified') ||
              id.includes('mdast-') ||
              id.includes('hast-') ||
              id.includes('unist-') ||
              id.includes('vfile') ||
              id.includes('highlight.js')
            ) {
              return 'markdown-vendor';
            }
            // React Router 单独打包
            if (id.includes('react-router')) {
              return 'router-vendor';
            }
            // Lucide React 图标库单独打包
            if (id.includes('lucide-react')) {
              return 'icons-vendor';
            }
            // Tailwind CSS 相关
            if (id.includes('tailwind')) {
              return 'tailwind-vendor';
            }
            // 其他第三方库
            return 'vendor';
          }
        },
        // 优化 chunk 文件命名
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    },
    // 设置 chunk 大小警告限制（可选，如果确实需要更大的 chunk）
    chunkSizeWarningLimit: 1000
  },
  optimizeDeps: {
    // 强制预构建某些可能有问题的依赖
    include: ['react-markdown', 'remark-gfm', 'rehype-highlight', 'rehype-raw']
  }
})

