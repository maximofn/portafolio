import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
    i18n: {
      defaultLocale: "es",
      locales: ["es", "en", "pt-br"],
    },
    build: {
      assets: ['sitemap_index.xml', 'sitemap_*.xml']
    }
  })
