import { defineConfig } from 'astro/config';

import sitemap from "@astrojs/sitemap";
import partytown from "@astrojs/partytown";

// https://astro.build/config
export default defineConfig({
  site: 'https://www.maximofn.com',
  i18n: {
    defaultLocale: "es",
    locales: ["es", "en", "pt-br"]
  },
  integrations: [
    sitemap(),
    partytown({
      config: {
        forward: ["gtag"]
      }
    })
  ],
  // Enable built-in prefetch for better navigation
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport'
  },
  build: {
    // Optimize build for better performance
    inlineStylesheets: 'never',
    assets: '_astro',
  },
  vite: {
    build: {
      // Disable CSS code splitting to prevent cross-page CSS loading
      cssCodeSplit: false,
      // Enable minification for better performance
      minify: 'terser',
      // Optimize chunk size
      chunkSizeWarningLimit: 1600,
      rollupOptions: {
        output: {
          // Better chunking strategy
          manualChunks: {
            'vendor': ['astro']
          },
          // Optimize asset naming for better caching
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.');
            let extType = info[info.length - 1];
            if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
              extType = 'img';
            } else if (/woff|woff2|eot|ttf|otf/i.test(extType)) {
              extType = 'fonts';
            }
            return `assets/${extType}/[name]-[hash][extname]`;
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
        }
      }
    },
    ssr: {
      // External dependencies that shouldn't be bundled
      external: []
    },
    // Enable asset optimization
    assetsInclude: ['**/*.woff', '**/*.woff2']
  },
  compressHTML: true
});