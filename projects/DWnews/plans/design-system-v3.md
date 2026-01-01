# The Daily Worker - Design System v3.0
**Traditional Newspaper Layout**
**Date:** 2025-12-31
**Version:** 3.0 (Newspaper Redesign)

---

## Design Philosophy v3.0

**"Traditional newspaper authority + modern visual storytelling = The Daily Worker"**

This redesign returns to traditional broadsheet newspaper design principles, inspired by the original Daily Worker (1924-1958), while incorporating modern web capabilities and rich imagery.

**Core Principles:**
1. **Newspaper Authority:** Multi-column layout, traditional typography, clear hierarchy
2. **Central Masthead:** "THE DAILY WORKER" prominently centered with date beneath
3. **Working-Class Accessibility:** Black/white/yellow color scheme, affordable pricing (50¢/day)
4. **Visual Storytelling:** Modern imagery and graphics throughout
5. **Monetization Ready:** Ad spaces for revenue generation
6. **Archive Access:** Search and browse older editions

---

## 1. Color Palette (Black/White/Yellow)

### Primary Colors

```css
/* Newspaper Black & White */
--color-black: #000000;           /* Pure black for text, borders, headlines */
--color-white: #FFFFFF;           /* Pure white for background */
--color-gray-dark: #333333;       /* Dark gray for secondary text */
--color-gray: #666666;            /* Medium gray for metadata */
--color-gray-light: #CCCCCC;      /* Light gray for borders, rules */
--color-gray-lighter: #F5F5F5;    /* Very light gray for subtle backgrounds */

/* Working-Class Yellow */
--color-yellow: #FDB913;          /* Bold yellow for accents, buttons, highlights */
--color-yellow-dark: #D89B0D;     /* Darker yellow for hover states */
--color-yellow-light: #FFF4D6;    /* Light yellow for backgrounds */

/* Socialist Red (subtle accent only) */
--color-red: #CC0000;             /* Deep red for subtle socialist nod */
--color-red-dark: #990000;        /* Darker red */
--color-red-light: #FFE5E5;       /* Very light red for backgrounds */
```

### Color Usage

| Element | Color | Variable |
|---------|-------|----------|
| **Body text** | Black | `--color-black` |
| **Headlines** | Black | `--color-black` |
| **Background** | White | `--color-white` |
| **Masthead** | Black | `--color-black` |
| **Date line** | Black on Yellow | `--color-black` on `--color-yellow` |
| **Subscribe button** | Yellow | `--color-yellow` |
| **Price** | Yellow highlight | `--color-yellow` |
| **Borders/Rules** | Black or Light Gray | `--color-black` / `--color-gray-light` |
| **Links** | Black underlined | `--color-black` with underline |
| **Hover links** | Yellow background | `--color-yellow-light` |
| **Socialist accent** | Red (sparingly) | `--color-red` (star, flag icon) |

---

## 2. Typography System

### Font Families

**Headlines & Masthead:**
```css
font-family: 'Playfair Display', 'Times New Roman', Georgia, serif;
```
- **Rationale:** Traditional newspaper serif with strong presence, free Google Font
- **Usage:** Masthead, major headlines, subheadlines
- **Weights:** 700 (bold), 900 (black for masthead)

**Body Text:**
```css
font-family: 'Merriweather', Georgia, 'Times New Roman', serif;
```
- **Rationale:** Highly readable web-optimized serif
- **Usage:** Article body, captions, metadata
- **Weights:** 400 (regular), 700 (bold)

**Labels & UI:**
```css
font-family: 'Franklin Gothic', 'Arial Narrow', Arial, sans-serif;
```
- **Rationale:** Condensed sans-serif for tight newspaper UI elements
- **Usage:** Category labels, edition info, metadata tags
- **Weights:** 400 (regular), 700 (bold)

### Type Scale (Newspaper Style)

| Element | Size | Line Height | Usage |
|---------|------|-------------|-------|
| **Masthead** | 72px | 0.9 | "THE DAILY WORKER" |
| **Major Headline** | 48px | 1.1 | Daily lead story |
| **H1 Subheadline** | 36px | 1.2 | Secondary major stories |
| **H2 Subheadline** | 28px | 1.2 | Column headlines |
| **H3 Subheadline** | 22px | 1.3 | Minor story headlines |
| **Body** | 16px | 1.6 | Article text |
| **Caption** | 14px | 1.4 | Image captions, metadata |
| **Label** | 12px | 1.2 | Category tags, edition info |

---

## 3. Layout System (Multi-Column Newspaper Grid)

### Grid Structure

**Desktop (1024px+):**
```
┌─────────────────────────────────────────────────────────────┐
│                         MASTHEAD                             │
│                    THE DAILY WORKER                          │
│                   Tuesday, December 31, 2025                 │
├─────────────────────────────────────────────────────────────┤
│  [Edition]  [Search]                    [Subscribe: 50¢/day]│
├────────────┬────────────┬────────────┬──────────────────────┤
│            │            │            │                      │
│   COLUMN   │   COLUMN   │   COLUMN   │   SIDEBAR           │
│     1      │     2      │     3      │   (Ongoing,         │
│            │            │            │    Ads, Archive)     │
│  (Major    │ (Stories)  │ (Stories)  │                      │
│   Story)   │            │            │                      │
│            │            │            │                      │
└────────────┴────────────┴────────────┴──────────────────────┘
```

**12-Column Grid:**
- Columns 1-3: Main story (3 columns = 9 grid units)
- Column 4: Sidebar (1 column = 3 grid units)

**Tablet (768px-1023px):**
- 2 columns + sidebar
- Major story spans 2 columns

**Mobile (< 768px):**
- Single column stack
- Sidebar moves below main content

### Column Widths

```css
--column-width: calc((100% - 90px) / 12); /* 12-column grid with 10px gutters */
--column-gutter: 10px;
--sidebar-width: 300px;
```

---

## 4. Masthead Design

### Structure

```html
<header class="newspaper-masthead">
  <!-- Top bar: Edition info, Search, Subscribe -->
  <div class="masthead-top">
    <span class="edition-info">Vol. 102, No. 365</span>
    <div class="masthead-search">
      <input type="search" placeholder="Search archives...">
    </div>
    <a href="/subscribe" class="subscribe-btn">
      <span class="price-display">50¢ PER DAY</span>
      <span class="subscribe-text">Subscribe Now</span>
    </a>
  </div>

  <!-- Main title: THE DAILY WORKER -->
  <div class="masthead-title">
    <h1>THE DAILY WORKER</h1>
    <p class="masthead-tagline">Working-Class News That Doesn't Pull Punches</p>
  </div>

  <!-- Date line -->
  <div class="masthead-date">
    <time datetime="2025-12-31">Tuesday, December 31, 2025</time>
  </div>

  <!-- Navigation -->
  <nav class="masthead-nav">
    <a href="/">Latest</a>
    <span class="nav-sep">|</span>
    <a href="/labor">Labor</a>
    <span class="nav-sep">|</span>
    <a href="/politics">Politics</a>
    <!-- More categories -->
  </nav>
</header>
```

### Styling

```css
.newspaper-masthead {
  background: var(--color-white);
  border-top: 3px solid var(--color-black);
  border-bottom: 3px solid var(--color-black);
  padding: 20px 0;
}

.masthead-title h1 {
  font-family: 'Playfair Display', serif;
  font-size: 72px;
  font-weight: 900;
  letter-spacing: 0.05em;
  text-align: center;
  margin: 20px 0 10px 0;
  color: var(--color-black);
  text-transform: uppercase;
}

.masthead-date {
  background: var(--color-yellow);
  text-align: center;
  padding: 8px 0;
  font-family: 'Franklin Gothic', Arial, sans-serif;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-top: 1px solid var(--color-black);
  border-bottom: 1px solid var(--color-black);
}

.subscribe-btn {
  background: var(--color-yellow);
  color: var(--color-black);
  padding: 10px 20px;
  border: 2px solid var(--color-black);
  font-family: 'Franklin Gothic', Arial, sans-serif;
  font-weight: 700;
  text-transform: uppercase;
}

.price-display {
  font-size: 18px;
  display: block;
}
```

---

## 5. Homepage Layout (Newspaper Front Page)

### Section Hierarchy

1. **Major Headline (Above the Fold)**
   - Full-width or 2/3 width
   - Large image
   - 48px headline
   - First 2-3 paragraphs visible

2. **Secondary Stories (3-column grid)**
   - Column 1: 2nd most important story
   - Column 2: 3rd most important story
   - Column 3: 4th story

3. **Sidebar (Right Column)**
   - **Ongoing Stories** (smaller, right rail)
   - **Advertisement Space** (300x250px)
   - **Archive Access** ("Older Editions")
   - **Category Navigation**

4. **Below the Fold**
   - More stories in 3-column grid
   - Pagination

### Major Headline Component

```html
<article class="major-headline">
  <div class="major-headline-image">
    <img src="..." alt="...">
    <p class="caption">Workers rally outside factory. Photo: AP</p>
  </div>
  <div class="major-headline-content">
    <span class="category-label">LABOR ORGANIZING</span>
    <h2 class="major-headline-title">
      Auto Workers Win Historic Contract After 6-Week Strike
    </h2>
    <p class="major-headline-deck">
      UAW secures 25% wage increases, pension restoration in landmark agreement affecting 150,000 workers nationwide
    </p>
    <div class="major-headline-body">
      <p>First two paragraphs of story visible on homepage...</p>
    </div>
    <a href="/article/123" class="read-more">Continue Reading →</a>
  </div>
</article>
```

---

## 6. Subscription Element

### Visual Design (50¢/Day Display)

```html
<div class="subscription-widget">
  <div class="subscription-price">
    <span class="price-large">50¢</span>
    <span class="price-period">PER DAY</span>
  </div>
  <p class="subscription-detail">Billed as $15.00/month</p>
  <button class="subscribe-btn-large">Subscribe Now</button>
  <p class="subscription-tagline">Support worker-centric journalism</p>
</div>
```

### Styling

```css
.subscription-widget {
  background: var(--color-yellow-light);
  border: 3px solid var(--color-black);
  padding: 20px;
  text-align: center;
}

.price-large {
  font-size: 48px;
  font-weight: 900;
  font-family: 'Playfair Display', serif;
}

.subscribe-btn-large {
  background: var(--color-yellow);
  color: var(--color-black);
  border: 2px solid var(--color-black);
  padding: 15px 30px;
  font-size: 18px;
  font-weight: 700;
  text-transform: uppercase;
  cursor: pointer;
}
```

---

## 7. Search Functionality

### Search Bar (Masthead)

```html
<form class="newspaper-search" action="/search" method="GET">
  <input
    type="search"
    name="q"
    placeholder="Search archives..."
    class="search-input"
  >
  <button type="submit" class="search-btn">
    <span>Search</span>
  </button>
</form>
```

### Search Results Page Layout

- Title: "Search Results: [query]"
- List of matching articles
- Filters: Date range, category, region
- Pagination

---

## 8. Archive Access ("Older Editions")

### Archive Widget (Sidebar)

```html
<div class="archive-widget">
  <h3 class="archive-title">Older Editions</h3>
  <ul class="archive-list">
    <li><a href="/edition/2025-12-30">Monday, Dec 30, 2025</a></li>
    <li><a href="/edition/2025-12-29">Sunday, Dec 29, 2025</a></li>
    <li><a href="/edition/2025-12-28">Saturday, Dec 28, 2025</a></li>
  </ul>
  <a href="/archives" class="archive-browse-all">Browse All Archives →</a>
</div>
```

### Archive Browse Page

- Calendar view or list view
- Filter by month/year
- Browse by category
- Full-text search within archives

---

## 9. Advertisement Spaces

### Ad Placement Guidelines

**Sidebar Ads:**
- **Top sidebar:** 300x250px (Medium Rectangle)
- **Mid sidebar:** 300x600px (Half Page)

**In-content Ads:**
- **Between stories:** 728x90px (Leaderboard) on desktop, 320x50px on mobile
- **Bottom of article:** 300x250px (Medium Rectangle)

**Ad Styling:**
```css
.advertisement {
  border: 1px solid var(--color-gray-light);
  background: var(--color-gray-lighter);
  padding: 10px;
  margin: 20px 0;
  text-align: center;
}

.ad-label {
  font-size: 10px;
  color: var(--color-gray);
  text-transform: uppercase;
  margin-bottom: 5px;
  letter-spacing: 0.1em;
}
```

---

## 10. Ongoing Stories (Right Column)

### Reduced Prominence

Ongoing stories move from hero section to right sidebar:

```html
<div class="ongoing-stories-sidebar">
  <h3 class="sidebar-title">Ongoing Coverage</h3>
  <ul class="ongoing-list">
    <li class="ongoing-item">
      <span class="ongoing-badge">ONGOING</span>
      <a href="/article/123" class="ongoing-link">
        Tech Workers Unite: Silicon Valley Unionization Drive
      </a>
      <span class="ongoing-updated">Updated 2 hours ago</span>
    </li>
    <!-- More ongoing stories -->
  </ul>
</div>
```

---

## 11. Article Card (Newspaper Style)

### Standard Story Card

```html
<article class="newspaper-story-card">
  <img src="..." alt="..." class="story-image">
  <div class="story-content">
    <span class="story-category">ECONOMICS</span>
    <h3 class="story-headline">
      Inflation Hits Working Families Hardest, New Data Shows
    </h3>
    <p class="story-deck">
      Latest CPI report reveals grocery prices up 12% year-over-year
    </p>
    <div class="story-meta">
      <span class="story-date">Dec 31</span>
      <span class="story-reading-time">5 min read</span>
    </div>
  </div>
</article>
```

### Styling (Newspaper Column Style)

```css
.newspaper-story-card {
  border-bottom: 1px solid var(--color-gray-light);
  padding-bottom: 20px;
  margin-bottom: 20px;
}

.story-headline {
  font-family: 'Playfair Display', serif;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-black);
  margin: 10px 0;
}

.story-category {
  font-family: 'Franklin Gothic', Arial, sans-serif;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-gray-dark);
  border-left: 3px solid var(--color-yellow);
  padding-left: 8px;
}
```

---

## 12. Responsive Breakpoints

```css
--breakpoint-mobile: 768px;
--breakpoint-tablet: 1024px;
--breakpoint-desktop: 1280px;
```

**Mobile (< 768px):**
- Single column stack
- Masthead simplified
- Sidebar content moves below main

**Tablet (768px-1023px):**
- 2-column grid + sidebar
- Masthead reduced size

**Desktop (1024px+):**
- 3-column grid + sidebar
- Full newspaper layout

---

## 13. Components Summary

### Masthead Components
- [ ] Edition info (Vol, No)
- [ ] Search bar (archives)
- [ ] Subscribe button (50¢/day display)
- [ ] Main title: "THE DAILY WORKER"
- [ ] Tagline
- [ ] Date line (yellow background)
- [ ] Navigation (categories)

### Homepage Components
- [ ] Major headline section (daily lead story)
- [ ] 3-column story grid
- [ ] Sidebar: Ongoing stories (reduced)
- [ ] Sidebar: Ad space (300x250px)
- [ ] Sidebar: Archive access
- [ ] Footer

### New Features
- [ ] Search functionality (archives)
- [ ] Archive browse page
- [ ] Subscription page/widget
- [ ] Ad placeholder spaces

---

## Next Steps: Implementation

1. **Update HTML structure** - New masthead, multi-column grid
2. **Create v3.0 CSS** - Black/white/yellow color scheme, newspaper typography
3. **Add Google Fonts** - Playfair Display (masthead), Merriweather (body)
4. **Build major headline component** - Daily lead story feature
5. **Implement search** - Archive search functionality
6. **Add archive access** - Older editions browse
7. **Design subscription widget** - 50¢/day display
8. **Create ad spaces** - 300x250px placeholders

---

**Design System Version:** 3.0
**Design Philosophy:** Traditional Newspaper Layout
**Last Updated:** 2025-12-31
**Ready for Implementation:** Yes
