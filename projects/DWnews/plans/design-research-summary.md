# Design Research Summary
**Project:** DWnews - The Daily Worker
**Date:** 2025-12-31
**Purpose:** Research findings to inform visual-first redesign (Batch 5)

---

## Executive Summary

This document synthesizes design research from award-winning news sites (ProPublica, The Markup), modern web design best practices for 2025, and historical Daily Worker newspaper aesthetics. The goal is to transform The Daily Worker's functional design into a visual-first storytelling experience that honors its historical roots while employing modern design excellence.

**Key Insight:** The best news design combines bold visual hierarchy, strategic typography, and ample whitespace to create engaging, credible storytelling that guides readers naturally through content.

---

## 1. ProPublica: Investigative Journalism Visual Strategy

### Visual Storytelling Approach
- **Featured story cards** with high-quality photography establish emotional connection before text engagement
- Photography creates **visual gravity** that signals serious journalistic work
- Homepage showcases investigations (e.g., "Sick in a Hospital Town") with compelling imagery
- **Full-width image layouts** with careful caption positioning

### Typography Hierarchy
- **Dual-typeface system:**
  - **Serif fonts** for body content (authority, traditional journalism credibility)
  - **Sans-serif fonts** for headings and navigation (modern, structured)
- **Dramatic header scaling** across breakpoints:
  - Mobile: `--scale3`
  - Desktop: `--scale5`
- Bylines and dates: smaller sans-serif fonts
- Metadata uses specialized color classes (`--color-text-meta`)

### Layout & Content Structure
- **Constrained content widths** (`--wp--style--global--content-size`) for optimal readability
- **Carousel treatment** for featured investigations with visual rotation
- **Sidebars highlight reporter contact** information (personalizes journalism, encourages sources)

### Color Palette & Identity
- **Neutral backgrounds** with **teal accent links** (`--color-accent-70`)
- **Dark text** for legibility
- **Call-to-action buttons:** dark gray backgrounds
- **Outline buttons:** subtle borders
- **Conservative choices** reinforce institutional credibility over flash

### Interactive Elements
- Prominent **promo bar** for announcements (matching donations)
- **Interactive tools** receive dedicated prominence (e.g., "Rx Inspector," "Nonprofit Explorer")

**Key Takeaway:** ProPublica balances serious investigative credibility with visual impact through strategic photography, dual typography, and restrained color palette.

---

## 2. The Markup: Data Journalism Presentation

### Typography & Readability
- **Clean, minimal typography** focused on content hierarchy
- **Bold sans-serif headlines** draw attention to investigative findings
- **Straightforward navigation** supports comprehension of complex tech topics
- **No visual clutter**

### Data & Investigation Visualization
- **Layered storytelling structure:**
  1. Headline (attention-grabbing finding)
  2. Imagery (symbolic visual)
  3. "Related links" sections (deeper exploration)
- State-level breakdowns for investigations (e.g., license plate data)

### Article Layout & Structure
- **Modular card-based design system**
- Consistent spacing across all cards
- **Homepage grouped into clear categories:**
  - Investigations
  - Blueprints
  - Tools
  - Impact

### Imagery & Graphics
- **Illustrations dominate over photography**
- **Symbolic visuals** represent abstract tech concepts
  - Digital illustration of Earth with connection points → global data extraction
  - Pixelated imagery → privacy intrusion
- Makes **complex systems visually digestible**

### Color Scheme & Identity
- **High-contrast elements**
- **Prominent red accent** (#ef3961) paired with **navy backgrounds**
- Creates **urgency** around accountability journalism while maintaining **professional credibility**

### Design Philosophy
- **Clarity over decoration**
- Visual hierarchy **consistently elevates evidence-based findings**
- Communicates that technology's impacts are **serious, actionable subjects** deserving rigorous investigation

**Key Takeaway:** The Markup prioritizes clarity and evidence through bold color contrasts, symbolic illustrations, and modular card-based layouts that make complex topics accessible.

---

## 3. Historical Daily Worker Newspaper Aesthetic (1924-1958)

### Publication Format
- **Traditional broadsheet format** (43-55 cm)
- Published from **1924-1958** (Chicago → New York in 1927)
- Two editions: "National" and "New York/Final City" (1925-1934)

### Historical Context
- Era of **New Typography** influence (1930s)
- **Jan Tschichold principles:**
  - Asymmetric composition
  - Sans-serif type
  - Photography integration
- **Soviet/Communist design influences:**
  - Bold, geometric typography
  - Strong visual hierarchy
  - Revolutionary aesthetics
  - Workers' struggle visual themes

### Typography Trends of the Era
- **Futura-style geometric sans-serifs** (Zhurnalnaya Roublennaya)
- **Bold, utilitarian type** for worker-focused messaging
- **Large, attention-grabbing headlines**
- **Dense text layouts** (maximizing information per page)

### Archive Access
- [The Marxists Internet Archive](https://www.marxists.org/history/usa/pubs/dailyworker/) (issues through 1936)
- [Library of Congress Chronicling America](https://chroniclingamerica.loc.gov/lccn/sn84020097/) (1924-1935)
- [Communist Historical Newspaper Collection - NYPL](https://www.nypl.org/node/449956)

**Key Takeaway:** The original Daily Worker used bold, utilitarian typography with strong visual hierarchy to convey urgency and worker-focused messaging—principles that can be modernized for digital storytelling.

---

## 4. Modern News Design Best Practices (2025)

### Visual Hierarchy Principles
- **Leverage white space** to create breathing room and focus
- **Strategic typography choices** guide reader attention
- **Clear visual hierarchy** using:
  - Image sizing
  - Font size variations
  - Font case (uppercase vs. lowercase)
  - Subtle dividers
  - Ample white space

### Typography Best Practices
- **Proportional text sizing:** Each size increase should be consistent value
- **Font hierarchy:**
  - Different sizes, weights (bold, regular), and styles (italics)
  - Distinguish headings, subheadings, and body text
- **Limit font styles:** Maximum of **2 different font families** for cohesion
- **Bold, gigantic fonts** as visual anchors (trend for 2025)
- **Variable fonts** offer flexible styling while improving load times

### Effective Visual Hierarchy
- **Guides user attention strategically**
- **Organizes elements** so users prioritize most crucial information first
- Uses **size, color, and spacing** to create intuitive content flow
- **Enhances UX** and improves content comprehension

### Modern News Site Examples
- **Bloomberg:** Minimalist design with white space and clear visual hierarchy
- **Al Jazeera:** Beautiful, readable typography hierarchy
- **The Guardian:** Clean typography with strong visual structure

**Sources:**
- [18 Best News Website Design Examples 2025 - Colorlib](https://colorlib.com/wp/best-news-website-design/)
- [8 stylish examples of news web design | Webflow Blog](https://webflow.com/blog/news-web-design)
- [Typography Trends in 2025: Elevate Your Website Design](https://learn.slicemypage.com/typography-trends-in-2025-elevate-your-website-design/)
- [Web Design Best Practices For Your Next Website Project in 2025](https://elementor.com/blog/web-design-best-practices/)

---

## 5. Key Design Patterns Identified

### Typography Hierarchy
1. **Dual-typeface system** (serif body + sans-serif headings) creates authority + modernity
2. **Dramatic scaling** across breakpoints for emphasis
3. **Bold headlines** serve as visual anchors
4. **Proportional sizing** maintains clear hierarchy
5. **Limited font families** (max 2) for cohesion

### Visual Hierarchy
1. **High-quality imagery** creates emotional connection and credibility
2. **Strategic use of whitespace** prevents clutter, improves focus
3. **Consistent spacing** across modular card-based layouts
4. **Size, color, and spacing** guide attention to priority content
5. **Full-width hero images** for featured/ongoing stories

### Color & Identity
1. **Neutral backgrounds** with **bold accent colors** for urgency
2. **High contrast** for readability and impact
3. **Conservative palettes** reinforce credibility
4. **Red/navy combinations** convey seriousness and action
5. **Accent colors** (teal, red) for links and CTAs

### Layout Structures
1. **Modular card-based design** for article presentation
2. **Constrained content widths** for optimal readability (600-800px)
3. **Clear category grouping** (Investigations, Tools, etc.)
4. **Featured story carousels** with visual rotation
5. **Asymmetric layouts** for visual interest (inspired by New Typography)

### Storytelling Elements
1. **Layered information architecture:** Headline → Image → Context → Exploration
2. **Pull quotes and callouts** break up long text
3. **Symbolic illustrations** make abstract concepts digestible
4. **Reporter bylines with photos** personalize journalism
5. **Interactive tools and data visualizations** for deep dives

---

## 6. Design Recommendations for The Daily Worker

### Honoring Historical Roots
1. **Bold, utilitarian typography** echoing 1920s-1950s worker publications
2. **Strong visual hierarchy** for urgent, worker-focused messaging
3. **Red accent color** (#ef3961 or similar) as homage to revolutionary aesthetics
4. **Geometric sans-serif headlines** (Futura-inspired) for impact
5. **"Daily Worker" masthead** with vintage newspaper inspiration

### Modern Adaptation
1. **Visual-first storytelling** with high-quality imagery for each article
2. **Ample whitespace** (modern web design vs. dense print layouts)
3. **Modular card-based layouts** for homepage and category pages
4. **Responsive breakpoints** with dramatic scaling for mobile-first design
5. **Dual typography:** Serif body (authority) + bold sans-serif headings (impact)

### Visual Impact
1. **Ongoing stories** get full-width hero treatment with large imagery
2. **Article cards** feature prominent images, bold headlines, minimal metadata
3. **Pull quotes** styled with red accent borders or backgrounds
4. **"What This Means For Workers"** callout sections with visual emphasis
5. **Data visualizations** when covering economic/labor statistics

### Color Palette
- **Primary:** Red (#ef3961 or similar communist/worker red)
- **Secondary:** Navy or dark gray backgrounds for contrast
- **Neutral:** White/light gray backgrounds for readability
- **Text:** Dark gray/black for body, white for dark backgrounds
- **Accent:** Teal or gold for links and secondary CTAs

### Typography System
- **Headlines:** Bold geometric sans-serif (e.g., Inter, Work Sans, or Montserrat)
- **Body:** Readable serif (e.g., Merriweather, Georgia, or PT Serif)
- **Metadata:** Smaller sans-serif, reduced opacity
- **Scale:** Mobile scale3 → Desktop scale5 for dramatic hierarchy

---

## 7. Next Steps: Design System Development (Phase 5.2)

Based on this research, Phase 5.2 will define:

1. **Typography System:**
   - Font families, sizes, weights, line heights
   - Responsive scaling rules
   - Header, body, quote, caption styles

2. **Color Palette:**
   - Primary, secondary, neutral, accent colors
   - Text colors with WCAG AA compliance
   - Background color pairings

3. **Spacing & Grid System:**
   - 8px or 4px base unit
   - Margin, padding scale (0.5x, 1x, 2x, 4x, 8x)
   - Grid columns and breakpoints

4. **Component Library:**
   - Article cards (standard, featured, ongoing)
   - Buttons (primary, secondary, outline)
   - Navigation (header, footer, breadcrumbs)
   - Article elements (pull quotes, callouts, captions)
   - Share buttons

5. **Responsive Breakpoints:**
   - Mobile: 320px-639px
   - Tablet: 640px-1023px
   - Desktop: 1024px+
   - Wide: 1280px+

---

## Conclusion

This research reveals that award-winning news design balances **visual impact** with **credibility** through strategic typography, ample whitespace, and powerful imagery. The Daily Worker can honor its historical roots (bold, worker-focused, urgent) while adopting modern design excellence (visual-first storytelling, responsive layouts, accessibility).

**Design Philosophy:**
**"Bold typography + visual storytelling + worker-centric urgency = Modern Daily Worker"**

The next phase will translate these findings into a concrete design system ready for implementation.

---

**Research Sources:**
- [ProPublica](https://www.propublica.org) - Investigative journalism visual strategy
- [The Markup](https://themarkup.org) - Data journalism presentation
- [Daily Worker - Wikipedia](https://en.wikipedia.org/wiki/Daily_Worker)
- [The Daily Workers - Marxists Archive](https://www.marxists.org/history/usa/pubs/dailyworker/)
- [Library of Congress Daily Worker Collection](https://chroniclingamerica.loc.gov/lccn/sn84020097/)
- [18 Best News Website Design Examples 2025 - Colorlib](https://colorlib.com/wp/best-news-website-design/)
- [Typography Trends in 2025](https://learn.slicemypage.com/typography-trends-in-2025-elevate-your-website-design/)
- [Web Design Best Practices 2025](https://elementor.com/blog/web-design-best-practices/)
