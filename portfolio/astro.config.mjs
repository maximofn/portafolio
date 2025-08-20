import { defineConfig } from 'astro/config';

import sitemap from "@astrojs/sitemap";

// https://astro.build/config
export default defineConfig({
  site: 'https://www.maximofn.com',
  i18n: {
    defaultLocale: "es",
    locales: ["es", "en", "pt-br"]
  },
  integrations: [sitemap()],
  build: {
    // Optimize build for better performance
    inlineStylesheets: 'auto',
    assets: '_astro'
  },
  vite: {
    build: {
      // Optimize CSS and JS splitting
      cssCodeSplit: true,
      rollupOptions: {
        output: {
          // Better chunking strategy
          manualChunks: {
            'vendor': ['astro']
          }
        }
      }
    },
    ssr: {
      // External dependencies that shouldn't be bundled
      external: []
    }
  },
  compressHTML: true,
  experimental: {
    // Enable performance optimizations
    optimizeHoistedScript: true
  }
});