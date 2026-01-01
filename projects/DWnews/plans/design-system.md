# The Daily Worker - Design System
**Version:** 1.0
**Date:** 2025-12-31
**Purpose:** Complete design system for visual-first redesign

---

## Design Philosophy

**"Bold typography + visual storytelling + worker-centric urgency = Modern Daily Worker"**

This design system honors the historical Daily Worker newspaper (1924-1958) while embracing modern visual-first storytelling. It balances **credibility** (serious journalism) with **impact** (bold visual hierarchy) to serve working-class readers who deserve news that doesn't pull punches.

**Core Principles:**
1. **Visual-First:** Images and typography create immediate impact
2. **Worker-Centric:** Bold, accessible design for $45k-$350k income bracket
3. **Credible:** Clean layouts and readable typography establish trust
4. **Urgent:** Red accents and strong hierarchy convey importance
5. **Accessible:** WCAG AA compliance, mobile-first, readable at all sizes

---

## 1. Typography System

### Font Families

**Headlines & Navigation:**
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
```
- **Rationale:** Inter is a geometric sans-serif with excellent readability at all sizes, echoing Futura-inspired worker publication aesthetics
- **Fallback:** System fonts ensure fast loading
- **Usage:** Headlines, subheads, navigation, buttons, metadata

**Body Text:**
```css
font-family: 'Merriweather', Georgia, 'Times New Roman', serif;
```
- **Rationale:** Merriweather is optimized for web readability with authority and warmth
- **Fallback:** Georgia provides excellent screen readability
- **Usage:** Article body text, long-form content, descriptions

### Type Scale

Mobile-first responsive scaling using **Major Third (1.250) ratio**:

| Element | Mobile (px) | Tablet (px) | Desktop (px) | CSS Variable |
|---------|-------------|-------------|--------------|--------------|
| **Display** | 48 | 64 | 80 | `--text-display` |
| **H1** | 32 | 40 | 48 | `--text-h1` |
| **H2** | 26 | 32 | 36 | `--text-h2` |
| **H3** | 21 | 26 | 28 | `--text-h3` |
| **H4** | 18 | 21 | 24 | `--text-h4` |
| **Body Large** | 18 | 19 | 20 | `--text-body-lg` |
| **Body** | 16 | 17 | 18 | `--text-body` |
| **Body Small** | 14 | 15 | 16 | `--text-body-sm` |
| **Caption** | 12 | 13 | 14 | `--text-caption` |

### Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| **Regular** | 400 | Body text, descriptions |
| **Medium** | 500 | Subheads, emphasized text |
| **Semibold** | 600 | H3, H4, buttons |
| **Bold** | 700 | H1, H2, CTAs |
| **Black** | 900 | Display (optional, for extra impact) |

### Line Heights

| Context | Line Height | Usage |
|---------|-------------|-------|
| **Tight** | 1.1 | Display headlines, large H1 |
| **Snug** | 1.25 | H2, H3, H4, pull quotes |
| **Normal** | 1.5 | Body text (optimal readability) |
| **Relaxed** | 1.75 | Captions, metadata |

### Typography Examples

```css
/* Display: Hero headlines for ongoing stories */
.text-display {
  font-family: var(--font-sans);
  font-size: var(--text-display);
  font-weight: 900;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

/* H1: Article headlines */
.text-h1 {
  font-family: var(--font-sans);
  font-size: var(--text-h1);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.01em;
}

/* Body: Article content */
.text-body {
  font-family: var(--font-serif);
  font-size: var(--text-body);
  font-weight: 400;
  line-height: 1.5;
  letter-spacing: 0;
}

/* Caption: Image captions, metadata */
.text-caption {
  font-family: var(--font-sans);
  font-size: var(--text-caption);
  font-weight: 400;
  line-height: 1.75;
  letter-spacing: 0.01em;
  opacity: 0.8;
}
```

---

## 2. Color Palette

### Brand Colors

```css
/* Primary Red: Revolutionary worker aesthetic */
--color-primary: #D32F2F;          /* Main red */
--color-primary-light: #EF5350;    /* Hover state */
--color-primary-dark: #B71C1C;     /* Active state */
--color-primary-subtle: #FFEBEE;   /* Background tint */

/* Secondary Navy: Credibility and contrast */
--color-secondary: #1A237E;        /* Navy blue */
--color-secondary-light: #283593;  /* Lighter navy */
--color-secondary-dark: #0D1446;   /* Dark navy */

/* Accent Gold: Links, highlights */
--color-accent: #FFA000;           /* Amber gold */
--color-accent-light: #FFB333;     /* Lighter gold */
--color-accent-dark: #FF8F00;      /* Darker gold */
```

### Neutral Colors

```css
/* Backgrounds */
--color-bg-primary: #FFFFFF;       /* White */
--color-bg-secondary: #F5F5F5;     /* Light gray */
--color-bg-tertiary: #EEEEEE;      /* Medium gray */
--color-bg-dark: #212121;          /* Dark gray/black */

/* Text */
--color-text-primary: #212121;     /* Primary text (almost black) */
--color-text-secondary: #616161;   /* Secondary text (medium gray) */
--color-text-tertiary: #9E9E9E;    /* Tertiary text (light gray) */
--color-text-inverse: #FFFFFF;     /* Text on dark backgrounds */

/* Borders */
--color-border-light: #E0E0E0;     /* Light borders */
--color-border: #BDBDBD;           /* Standard borders */
--color-border-dark: #757575;      /* Dark borders */
```

### Semantic Colors

```css
/* Success (unused in MVP) */
--color-success: #388E3C;
--color-success-bg: #E8F5E9;

/* Warning */
--color-warning: #F57C00;
--color-warning-bg: #FFF3E0;

/* Error */
--color-error: #D32F2F;
--color-error-bg: #FFEBEE;

/* Info */
--color-info: #1976D2;
--color-info-bg: #E3F2FD;
```

### Color Usage Guidelines

| Element | Color | Variable |
|---------|-------|----------|
| **Primary CTAs** | Red | `--color-primary` |
| **Links** | Gold | `--color-accent` |
| **Navigation** | Navy | `--color-secondary` |
| **Headlines** | Almost Black | `--color-text-primary` |
| **Body Text** | Almost Black | `--color-text-primary` |
| **Metadata** | Medium Gray | `--color-text-secondary` |
| **Borders** | Light Gray | `--color-border-light` |
| **Backgrounds** | White/Light Gray | `--color-bg-primary/secondary` |

### Accessibility

All color combinations meet **WCAG AA** standards:

| Foreground | Background | Contrast Ratio | Pass |
|------------|------------|----------------|------|
| Text Primary | BG Primary | 15.8:1 | ✅ AAA |
| Text Secondary | BG Primary | 5.1:1 | ✅ AA |
| Primary Red | White | 4.9:1 | ✅ AA |
| Accent Gold | Navy | 7.8:1 | ✅ AAA |

---

## 3. Spacing & Grid System

### Base Unit

**8px base unit** for consistent spacing across all devices.

### Spacing Scale

```css
--space-0: 0;
--space-1: 4px;    /* 0.5x */
--space-2: 8px;    /* 1x - base unit */
--space-3: 12px;   /* 1.5x */
--space-4: 16px;   /* 2x */
--space-6: 24px;   /* 3x */
--space-8: 32px;   /* 4x */
--space-12: 48px;  /* 6x */
--space-16: 64px;  /* 8x */
--space-24: 96px;  /* 12x */
--space-32: 128px; /* 16x */
```

### Usage Guidelines

| Element | Spacing | Usage |
|---------|---------|-------|
| **Component padding** | `--space-4` to `--space-8` | Card padding, button padding |
| **Section gaps** | `--space-12` to `--space-16` | Between homepage sections |
| **Paragraph spacing** | `--space-4` | Between paragraphs in articles |
| **List item spacing** | `--space-3` | Between navigation items |
| **Margin bottom** | `--space-6` to `--space-8` | Headlines, subheads |

### Grid System

**12-column responsive grid** with gutters:

```css
/* Container max-widths */
--container-sm: 640px;   /* Tablet */
--container-md: 768px;   /* Small desktop */
--container-lg: 1024px;  /* Desktop */
--container-xl: 1280px;  /* Wide desktop */

/* Content max-widths */
--content-width: 680px;   /* Article body (optimal readability) */
--content-width-wide: 900px; /* Wide content */
--content-width-narrow: 540px; /* Narrow content */

/* Gutters */
--gutter: 16px;  /* Mobile */
--gutter-md: 24px;  /* Tablet */
--gutter-lg: 32px;  /* Desktop */
```

### Responsive Breakpoints

```css
/* Mobile-first approach */
--breakpoint-sm: 640px;   /* Tablet */
--breakpoint-md: 768px;   /* Small desktop */
--breakpoint-lg: 1024px;  /* Desktop */
--breakpoint-xl: 1280px;  /* Wide desktop */
```

---

## 4. Visual Hierarchy Rules

### Hierarchy Levels

**Level 1: Hero/Featured**
- Ongoing stories, featured investigations
- Full-width image (16:9 aspect ratio)
- Display or H1 headline
- Large body text (18-20px)
- Primary red accent elements

**Level 2: Primary Content**
- Standard article cards on homepage
- Medium image (4:3 or 16:9 aspect ratio)
- H2 headline
- Body text (16-18px)
- Standard spacing

**Level 3: Secondary Content**
- Related articles, category listings
- Small image (square or 4:3 aspect ratio)
- H3 or H4 headline
- Body small text (14-16px)
- Compact spacing

**Level 4: Metadata**
- Bylines, dates, categories, reading level
- Caption text (12-14px)
- Secondary or tertiary text color
- Minimal spacing

### Z-Index Scale

```css
--z-base: 0;
--z-content: 10;
--z-card: 20;
--z-dropdown: 100;
--z-sticky: 200;
--z-modal: 500;
--z-toast: 1000;
```

---

## 5. Component Library

### 5.1 Article Cards

**Featured Card (Ongoing Stories):**
```html
<article class="card card--featured">
  <div class="card__image-wrapper">
    <img src="..." alt="..." class="card__image">
    <span class="card__badge">ONGOING</span>
  </div>
  <div class="card__content">
    <span class="card__category">Labor Organizing</span>
    <h2 class="card__title text-display">Headline Goes Here</h2>
    <p class="card__excerpt text-body-lg">Excerpt text...</p>
    <div class="card__meta">
      <span class="card__date">Dec 31, 2025</span>
      <span class="card__reading-level">Grade 8</span>
    </div>
  </div>
</article>
```

**Specifications:**
- Image: Full-width, 16:9 aspect ratio, min-height 400px
- Badge: Red background, white text, top-right corner
- Title: Display or H1 (48-80px), bold, tight line-height
- Excerpt: Body large (18-20px), 2-3 lines max
- Padding: `--space-8` (32px)
- Background: White with subtle shadow on hover

**Standard Card:**
```html
<article class="card card--standard">
  <img src="..." alt="..." class="card__image">
  <div class="card__content">
    <span class="card__category">Economic Justice</span>
    <h3 class="card__title text-h3">Article Headline</h3>
    <p class="card__excerpt text-body">Short excerpt...</p>
    <div class="card__meta">
      <span class="card__date">Dec 31</span>
      <span class="card__region">National</span>
    </div>
  </div>
</article>
```

**Specifications:**
- Image: 4:3 or 16:9 aspect ratio, min-height 200px
- Title: H3 (21-28px), semibold
- Excerpt: Body (16-18px), 2 lines max
- Padding: `--space-6` (24px)
- Border: 1px light gray, subtle shadow on hover

**Compact Card:**
```html
<article class="card card--compact">
  <img src="..." alt="..." class="card__image-small">
  <div class="card__content">
    <h4 class="card__title text-h4">Short Headline</h4>
    <span class="card__meta text-caption">Dec 31 · National</span>
  </div>
</article>
```

**Specifications:**
- Image: Square or 3:2 aspect ratio, max 120px
- Title: H4 (18-24px), semibold, 2 lines max
- Layout: Horizontal flex (image left, content right)
- Padding: `--space-4` (16px)

### 5.2 Buttons

**Primary Button (CTAs):**
```html
<button class="btn btn--primary">
  Read Full Story
</button>
```

**Specifications:**
```css
.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-family: var(--font-sans);
  font-size: 16px;
  font-weight: 600;
  padding: var(--space-3) var(--space-6); /* 12px 24px */
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn--primary:hover {
  background: var(--color-primary-light);
}

.btn--primary:active {
  background: var(--color-primary-dark);
}
```

**Secondary Button:**
```css
.btn--secondary {
  background: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  /* Same padding, font as primary */
}

.btn--secondary:hover {
  background: var(--color-primary-subtle);
}
```

**Text Button (Links):**
```css
.btn--text {
  background: none;
  color: var(--color-accent);
  border: none;
  padding: var(--space-2) var(--space-4);
  text-decoration: underline;
  text-decoration-thickness: 2px;
  text-underline-offset: 4px;
}

.btn--text:hover {
  color: var(--color-accent-dark);
}
```

### 5.3 Navigation

**Header Navigation:**
```html
<header class="site-header">
  <div class="site-header__container">
    <div class="site-header__logo">
      <h1 class="site-title">THE DAILY WORKER</h1>
      <p class="site-tagline">News for the Working Class</p>
    </div>
    <nav class="site-nav">
      <a href="#" class="site-nav__link">National</a>
      <a href="#" class="site-nav__link">Local</a>
      <a href="#" class="site-nav__link">Labor Organizing</a>
      <!-- More links -->
    </nav>
  </div>
</header>
```

**Specifications:**
```css
.site-header {
  background: var(--color-secondary); /* Navy */
  color: var(--color-text-inverse);
  padding: var(--space-4) var(--space-6);
  border-bottom: 4px solid var(--color-primary); /* Red accent */
}

.site-title {
  font-family: var(--font-sans);
  font-size: var(--text-h2);
  font-weight: 900;
  letter-spacing: 0.05em;
  margin: 0;
}

.site-tagline {
  font-size: var(--text-body-sm);
  opacity: 0.9;
  margin: var(--space-1) 0 0 0;
}

.site-nav__link {
  color: var(--color-text-inverse);
  text-decoration: none;
  font-weight: 500;
  padding: var(--space-2) var(--space-4);
  border-bottom: 2px solid transparent;
  transition: border-color 0.2s ease;
}

.site-nav__link:hover,
.site-nav__link--active {
  border-bottom-color: var(--color-primary);
}
```

**Footer:**
```html
<footer class="site-footer">
  <div class="site-footer__content">
    <div class="site-footer__section">
      <h3>About The Daily Worker</h3>
      <p>News for the working class that doesn't pull punches.</p>
    </div>
    <div class="site-footer__section">
      <h3>Categories</h3>
      <ul class="site-footer__links">
        <li><a href="#">Labor Organizing</a></li>
        <!-- More links -->
      </ul>
    </div>
  </div>
  <div class="site-footer__bottom">
    <p>&copy; 2025 The Daily Worker. All rights reserved.</p>
  </div>
</footer>
```

**Specifications:**
```css
.site-footer {
  background: var(--color-bg-dark);
  color: var(--color-text-inverse);
  padding: var(--space-16) var(--space-6) var(--space-8);
}

.site-footer__links a {
  color: var(--color-accent-light);
  text-decoration: none;
}

.site-footer__links a:hover {
  text-decoration: underline;
}
```

### 5.4 Article Elements

**Pull Quote:**
```html
<blockquote class="pull-quote">
  <p class="pull-quote__text">"This is a powerful quote from the article."</p>
  <cite class="pull-quote__cite">— Union Organizer</cite>
</blockquote>
```

**Specifications:**
```css
.pull-quote {
  border-left: 4px solid var(--color-primary);
  padding: var(--space-6) var(--space-8);
  margin: var(--space-8) 0;
  background: var(--color-bg-secondary);
}

.pull-quote__text {
  font-family: var(--font-serif);
  font-size: var(--text-h3);
  font-weight: 400;
  line-height: 1.25;
  font-style: italic;
  color: var(--color-text-primary);
}

.pull-quote__cite {
  font-family: var(--font-sans);
  font-size: var(--text-body-sm);
  color: var(--color-text-secondary);
  font-style: normal;
  margin-top: var(--space-4);
  display: block;
}
```

**Callout Section ("What This Means For Workers"):**
```html
<aside class="callout callout--workers">
  <h3 class="callout__title">What This Means For Workers</h3>
  <p class="callout__content">
    Explanation of how this news impacts working-class people...
  </p>
</aside>
```

**Specifications:**
```css
.callout--workers {
  background: var(--color-primary-subtle); /* Light red */
  border: 2px solid var(--color-primary);
  border-radius: 8px;
  padding: var(--space-6);
  margin: var(--space-8) 0;
}

.callout__title {
  font-family: var(--font-sans);
  font-size: var(--text-h4);
  font-weight: 700;
  color: var(--color-primary-dark);
  margin: 0 0 var(--space-4) 0;
}

.callout__content {
  font-family: var(--font-serif);
  font-size: var(--text-body);
  line-height: 1.5;
  color: var(--color-text-primary);
}
```

**Image with Caption:**
```html
<figure class="article-image">
  <img src="..." alt="..." class="article-image__img">
  <figcaption class="article-image__caption">
    <span class="article-image__description">Description of image.</span>
    <span class="article-image__credit">Photo: Reuters</span>
  </figcaption>
</figure>
```

**Specifications:**
```css
.article-image {
  margin: var(--space-8) 0;
}

.article-image__img {
  width: 100%;
  height: auto;
  border-radius: 4px;
}

.article-image__caption {
  font-family: var(--font-sans);
  font-size: var(--text-caption);
  color: var(--color-text-secondary);
  padding: var(--space-3) var(--space-2);
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}

.article-image__credit {
  opacity: 0.7;
  font-style: italic;
}
```

### 5.5 Badges & Tags

**"ONGOING" Badge:**
```html
<span class="badge badge--ongoing">ONGOING</span>
```

```css
.badge {
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: var(--space-1) var(--space-3);
  border-radius: 4px;
  display: inline-block;
}

.badge--ongoing {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}
```

**Category Tag:**
```html
<span class="tag tag--category">Labor Organizing</span>
```

```css
.tag {
  font-family: var(--font-sans);
  font-size: var(--text-caption);
  font-weight: 500;
  color: var(--color-text-secondary);
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--color-border-light);
  border-radius: 4px;
  display: inline-block;
}

.tag:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-border);
}
```

### 5.6 Share Buttons

```html
<div class="share-buttons">
  <button class="share-btn share-btn--twitter">
    <svg><!-- Twitter icon --></svg>
    <span>Twitter</span>
  </button>
  <button class="share-btn share-btn--facebook">
    <svg><!-- Facebook icon --></svg>
    <span>Facebook</span>
  </button>
  <button class="share-btn share-btn--reddit">
    <svg><!-- Reddit icon --></svg>
    <span>Reddit</span>
  </button>
  <button class="share-btn share-btn--copy">
    <svg><!-- Link icon --></svg>
    <span>Copy Link</span>
  </button>
</div>
```

```css
.share-buttons {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
  margin: var(--space-8) 0;
}

.share-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 4px;
  font-family: var(--font-sans);
  font-size: var(--text-body-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.share-btn:hover {
  background: var(--color-bg-tertiary);
  border-color: var(--color-border);
  transform: translateY(-2px);
}

.share-btn svg {
  width: 18px;
  height: 18px;
}
```

---

## 6. Mobile-First Responsive Design

### Breakpoint Strategy

**Mobile (< 640px):**
- Single column layouts
- Stacked navigation (hamburger menu)
- Full-width images
- Smaller typography scale
- Generous touch targets (min 44x44px)

**Tablet (640px - 1023px):**
- 2-column grids for article cards
- Horizontal navigation
- Medium typography scale
- Balanced spacing

**Desktop (1024px+):**
- 3-4 column grids
- Full navigation with dropdowns
- Largest typography scale
- Maximum spacing for readability

### Responsive Typography Example

```css
/* Mobile-first */
.text-h1 {
  font-size: 32px; /* Mobile */
  line-height: 1.1;
}

/* Tablet */
@media (min-width: 640px) {
  .text-h1 {
    font-size: 40px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .text-h1 {
    font-size: 48px;
  }
}
```

### Responsive Grid Example

```css
/* Mobile: Single column */
.article-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-6);
}

/* Tablet: 2 columns */
@media (min-width: 640px) {
  .article-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-8);
  }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) {
  .article-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-12);
  }
}
```

---

## 7. Accessibility Guidelines

### WCAG AA Compliance

**Color Contrast:**
- All text meets minimum 4.5:1 contrast ratio
- Large text (18px+ or 14px+ bold) meets 3:1 ratio
- Interactive elements have 3:1 contrast with surroundings

**Focus States:**
```css
*:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
  border-radius: 4px;
}
```

**Touch Targets:**
- Minimum size: 44x44px
- Adequate spacing between interactive elements
- Mobile-optimized button sizes

**Semantic HTML:**
- Proper heading hierarchy (H1 → H2 → H3)
- `<article>`, `<nav>`, `<aside>`, `<footer>` landmarks
- Alt text for all images
- ARIA labels where needed

**Keyboard Navigation:**
- All interactive elements focusable
- Logical tab order
- Skip to content link
- Escape key closes modals

**Screen Reader Support:**
```html
<!-- Example: Article card -->
<article aria-labelledby="article-123-title">
  <h3 id="article-123-title">Article Headline</h3>
  <img src="..." alt="Detailed description of image">
  <span class="sr-only">Published on</span>
  <time datetime="2025-12-31">Dec 31, 2025</time>
</article>

<!-- Screen reader only class -->
<style>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
```

---

## 8. Performance Guidelines

### Font Loading

```css
/* Preload critical fonts */
<link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/merriweather-regular.woff2" as="font" type="font/woff2" crossorigin>

/* Font display strategy */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-display: swap; /* Show fallback immediately, swap when loaded */
  font-weight: 400 900;
}
```

### Image Optimization

- **Use responsive images:**
  ```html
  <img
    src="image-800.jpg"
    srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
    alt="Description"
    loading="lazy"
  >
  ```
- **Aspect ratio boxes** to prevent layout shift
- **Lazy loading** for below-fold images
- **WebP format** with JPEG fallback

### CSS Optimization

- **Critical CSS** inlined in `<head>`
- **Minification** for production
- **Purge unused CSS** (PurgeCSS, Tailwind)
- **Logical property grouping** for better compression

### Performance Budget

- **First Contentful Paint (FCP):** < 1.5s
- **Largest Contentful Paint (LCP):** < 2.5s
- **Cumulative Layout Shift (CLS):** < 0.1
- **Total page size:** < 500KB (gzipped)

---

## 9. Implementation Checklist

### Phase 5.3: Homepage Redesign
- [ ] Implement CSS custom properties for design system
- [ ] Create featured card component for ongoing stories
- [ ] Create standard article card component
- [ ] Redesign hero section with visual-first approach
- [ ] Implement category/region filtering UI
- [ ] Add responsive navigation with mobile menu
- [ ] Test mobile, tablet, desktop layouts
- [ ] Verify WCAG AA compliance

### Phase 5.4: Article Detail Page Redesign
- [ ] Implement article header with large imagery
- [ ] Apply typography system to body content
- [ ] Create pull quote component
- [ ] Create "What This Means For Workers" callout
- [ ] Redesign metadata display
- [ ] Implement share buttons
- [ ] Add image caption styling
- [ ] Test readability across devices

### Phase 5.5: Design Polish & Refinements
- [ ] Refine spacing and alignment
- [ ] Add micro-interactions (hover, focus, active states)
- [ ] Optimize font loading
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile device testing (iOS, Android)
- [ ] Accessibility audit
- [ ] Performance optimization
- [ ] Final design QA

---

## 10. Design System Governance

### Version Control
- This design system is versioned (current: v1.0)
- Changes require documentation and communication
- Breaking changes increment major version

### Component Updates
- New components must follow existing patterns
- Variants added to existing components when possible
- Document component usage and examples

### Maintenance
- Regular accessibility audits
- Performance monitoring
- Browser compatibility testing
- User feedback integration

---

## Appendix: CSS Custom Properties (Complete List)

```css
:root {
  /* Fonts */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-serif: 'Merriweather', Georgia, 'Times New Roman', serif;

  /* Type Scale */
  --text-display: clamp(48px, 5vw, 80px);
  --text-h1: clamp(32px, 4vw, 48px);
  --text-h2: clamp(26px, 3vw, 36px);
  --text-h3: clamp(21px, 2.5vw, 28px);
  --text-h4: clamp(18px, 2vw, 24px);
  --text-body-lg: clamp(18px, 1.8vw, 20px);
  --text-body: clamp(16px, 1.6vw, 18px);
  --text-body-sm: clamp(14px, 1.4vw, 16px);
  --text-caption: clamp(12px, 1.2vw, 14px);

  /* Colors */
  --color-primary: #D32F2F;
  --color-primary-light: #EF5350;
  --color-primary-dark: #B71C1C;
  --color-primary-subtle: #FFEBEE;
  --color-secondary: #1A237E;
  --color-secondary-light: #283593;
  --color-secondary-dark: #0D1446;
  --color-accent: #FFA000;
  --color-accent-light: #FFB333;
  --color-accent-dark: #FF8F00;

  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F5F5F5;
  --color-bg-tertiary: #EEEEEE;
  --color-bg-dark: #212121;

  --color-text-primary: #212121;
  --color-text-secondary: #616161;
  --color-text-tertiary: #9E9E9E;
  --color-text-inverse: #FFFFFF;

  --color-border-light: #E0E0E0;
  --color-border: #BDBDBD;
  --color-border-dark: #757575;

  /* Spacing */
  --space-0: 0;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
  --space-24: 96px;
  --space-32: 128px;

  /* Layout */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --content-width: 680px;
  --content-width-wide: 900px;
  --content-width-narrow: 540px;
  --gutter: 16px;
  --gutter-md: 24px;
  --gutter-lg: 32px;

  /* Breakpoints */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;

  /* Z-index */
  --z-base: 0;
  --z-content: 10;
  --z-card: 20;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal: 500;
  --z-toast: 1000;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 250ms ease;
  --transition-slow: 350ms ease;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);

  /* Border radius */
  --radius-sm: 4px;
  --radius-base: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
}
```

---

**Design System Version:** 1.0
**Last Updated:** 2025-12-31
**Next Review:** After Phase 5.5 completion
