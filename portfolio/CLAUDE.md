# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multilingual portfolio website built with Astro 5, featuring a personal blog, projects showcase, and technical content in Spanish (default), English, and Portuguese (Brazil). The site focuses on AI, machine learning, and software development topics.

## Development Commands

```bash
# Install dependencies
npm install

# Start development server (localhost:4321)
npm run dev
npm run start  # Alternative

# Build for production (outputs to ./dist/)
npm run build

# Preview production build locally
npm run preview

# Run Astro CLI commands
npm run astro [command]
npm run astro -- --help  # Get CLI help
```

## Architecture & Structure

### Internationalization (i18n)
- **Default locale**: Spanish (`es`)
- **Supported locales**: `es`, `en`, `pt-br`
- **URL structure**: 
  - Spanish: `/` (root)
  - English: `/en/[page]`
  - Portuguese: `/pt-br/[page]`

### Configuration Files
- **consts.json**: Central configuration for social links, SVG paths, color palette, metadata, and layout constants
- **tsconfig.json**: TypeScript configuration with path aliases for components, layouts, pages, and assets
- **vercel.json**: Contains extensive URL redirects for maintaining SEO and handling legacy routes
- **astro.config.mjs**: Astro configuration with sitemap integration and i18n setup

### Directory Structure
```
src/
├── components/         # Reusable Astro components
│   ├── All*.astro     # Listing components (AllPosts, AllProjects, etc.)
│   ├── Last*.astro    # Recent content components
│   ├── *Card.astro    # Card components for different content types
│   └── Layout components (Header, Footer, etc.)
├── layouts/
│   ├── Layout.astro      # Main site layout
│   └── PostLayout.astro  # Blog post layout with progress tracking
└── pages/               # File-based routing
    ├── [content].astro  # Spanish content (root level)
    ├── en/             # English translations
    ├── pt-br/          # Portuguese (Brazil) translations
    └── tips/           # Technical tips in all languages
```

### Path Aliases
Use these TypeScript path aliases defined in tsconfig.json:
- `@portfolio/*` - Root directory
- `@fonts/*` - Font files
- `@icons/*` - Icon assets
- `@images/*` - Image assets
- `@videos/*` - Video assets
- `@components/*` - Astro components
- `@layouts/*` - Layout components
- `@pages/*` - Page components
- `@pages_en/*` - English pages
- `@pages_pt/*` - Portuguese pages

### Data Files
The root directory contains JSON files for dynamic content:
- `last_posts.json` - Recent blog posts
- `last_projects.json` - Recent projects
- `last_tips.json` - Recent tips
- `last_datasets.json` - Recent datasets
- `last_dockers.json` - Recent Docker containers
- `last_experience.json` - Work experience
- `hero_texts.json` - Hero section content

### Content Management
Each content type (posts, projects, tips, datasets, dockers) has:
1. Individual `.astro` files for detailed pages
2. Listing components (`All*.astro`) for overview pages
3. Recent components (`Last*.astro`) for homepage display
4. Card components for consistent presentation

### Styling & Design
- **Dark theme** with custom color palette defined in consts.json
- **Responsive design** with max-width constraints
- **Custom fonts**: Cascadia Code family for code elements
- **Colors**: Blue-based palette with transparency variants
- **Icons**: SVG icons with paths defined in consts.json

### URL Management
- Extensive redirect rules in vercel.json handle legacy URLs
- Automatic HTTPS redirect from non-www to www domain
- Language-specific redirects (e.g., `/pt/*` → `/pt-br/*`)

### Link Checking
- `link_checker.py` script for validating internal and external links
- Configuration in `ignore_urls.json` for URLs to skip during validation
- Generates JSON and HTML reports of broken links

## Development Guidelines

### Adding New Content
1. Create the Spanish version first in `src/pages/`
2. Add English version in `src/pages/en/`
3. Add Portuguese version in `src/pages/pt-br/`
4. Update relevant JSON data files if needed
5. Add to appropriate listing components

### Component Creation
- Follow existing naming conventions (PascalCase)
- Use TypeScript interfaces for props
- Import constants from `@portfolio/consts.json`
- Utilize path aliases for imports

### Internationalization
- Each page should have identical file structure across all three language directories
- Use conditional logic in components for language-specific content
- Reference `consts.json` for language-specific metadata

### Asset Management
- Place static assets in `public/` directory
- Use path aliases for consistent asset referencing
- Icons should be SVG format when possible
- Images should be optimized (WebP preferred)

### Performance Considerations
- The site generates static files for all languages
- Sitemap automatically generated for SEO
- View transitions enabled for smooth navigation
- Font loading optimized with local Cascadia Code fonts