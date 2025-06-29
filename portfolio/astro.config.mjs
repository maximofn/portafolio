import { defineConfig } from 'astro/config';

import sitemap from "@astrojs/sitemap";

// https://astro.build/config
export default defineConfig({
  site: 'https://www.maximofn.com',
  i18n: {
    defaultLocale: "es",
    locales: ["es", "en", "pt-br"]
  },
  integrations: [sitemap()]
});