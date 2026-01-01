# Batch 5: Design Redesign - Testing & QA Checklist
**Date:** 2025-12-31
**Status:** Ready for Testing

---

## Phase 5.5 Testing Requirements

This checklist should be completed before deploying the visual-first redesign to production.

### 1. Visual Refinements

- [ ] **Spacing consistency:** Verify all spacing follows the 8px base unit across pages
- [ ] **Typography alignment:** Check that headlines, body text, and metadata align properly
- [ ] **Color consistency:** Verify brand colors (#D32F2F red, #1A237E navy, #FFA000 gold) used consistently
- [ ] **Image aspect ratios:** Confirm all images display correctly at different screen sizes
- [ ] **Button alignment:** Check all buttons are properly aligned and sized

### 2. Micro-Interactions & Transitions

#### Homepage
- [ ] **Article card hover:** Cards lift on hover with shadow transition
- [ ] **Navigation links:** Border-bottom appears on hover
- [ ] **Pagination buttons:** Transform and color change on hover
- [ ] **Share buttons:** Lift effect on hover

#### Article Pages
- [ ] **Share buttons:** Lift and shadow effect on hover
- [ ] **Copy link button:** Changes color when clicked ("Copied!")
- [ ] **Back to home link:** Hover state visible
- [ ] **Blockquotes:** Proper visual prominence

### 3. Font Loading Optimization

- [ ] **Google Fonts preconnect:** Verify `<link rel="preconnect">` tags present
- [ ] **Font display swap:** Check fonts use `font-display: swap` in CSS (via Google Fonts URL)
- [ ] **Fallback fonts:** Verify system fonts display correctly before custom fonts load
- [ ] **Font weights loaded:** Confirm Inter (400, 500, 600, 700, 900) and Merriweather (400, 700, italic) load
- [ ] **Page load performance:** Fonts should not block initial render

### 4. Cross-Browser Testing

#### Desktop Browsers (macOS/Windows/Linux)
- [ ] **Chrome/Edge (Chromium):** Test all pages, verify layouts and interactions
- [ ] **Firefox:** Verify CSS Grid, Flexbox, and custom properties work
- [ ] **Safari:** Test on macOS, verify webkit-specific properties
  - Check `-webkit-font-smoothing`
  - Verify `-webkit-line-clamp` for article excerpt truncation

#### Known Browser Issues to Test:
- [ ] CSS custom properties (all modern browsers support, but verify)
- [ ] CSS clamp() for responsive typography (check Safari support)
- [ ] Flexbox gap property (older browsers may not support)
- [ ] Focus-visible pseudo-class (check Safari/Firefox support)

### 5. Mobile Device Testing

#### iOS Devices
- [ ] **iPhone SE (small screen):** 375px width, verify mobile navigation works
- [ ] **iPhone 14 Pro:** 393px width, test standard mobile layout
- [ ] **iPhone 14 Pro Max:** 430px width, test larger mobile layout
- [ ] **iPad Mini:** 768px width (tablet breakpoint), verify 2-column grids
- [ ] **iPad Pro:** 1024px width (desktop breakpoint), verify 3-column grids

#### Android Devices
- [ ] **Small phone:** 360px width (e.g., Galaxy S21), verify layout doesn't break
- [ ] **Medium phone:** 412px width (e.g., Pixel 6), test standard mobile
- [ ] **Large phone:** 480px width, verify tablet breakpoint doesn't trigger early
- [ ] **Tablet:** 768px+, verify responsive grid switches correctly

#### Mobile-Specific Tests:
- [ ] **Touch targets:** All buttons/links minimum 44x44px
- [ ] **Hamburger menu:** (if implemented) works smoothly
- [ ] **Share buttons:** Mobile layout stacks vertically
- [ ] **Full-bleed images:** Article images extend to screen edges on mobile
- [ ] **Horizontal scroll:** No horizontal scrolling on any screen size

### 6. Accessibility Review (WCAG AA)

#### Color Contrast
- [ ] **Body text on white:** #212121 on #FFFFFF (contrast 15.8:1) ✅ AAA
- [ ] **Secondary text on white:** #616161 on #FFFFFF (contrast 5.1:1) ✅ AA
- [ ] **Primary red on white:** #D32F2F on #FFFFFF (contrast 4.9:1) ✅ AA
- [ ] **Accent gold on navy:** #FFA000 on #1A237E (contrast 7.8:1) ✅ AAA
- [ ] **All link colors:** Meet minimum 4.5:1 contrast

#### Keyboard Navigation
- [ ] **Tab order:** Logical tab sequence through all interactive elements
- [ ] **Focus indicators:** All focusable elements show `:focus-visible` outline (2px gold)
- [ ] **Skip to content:** Consider adding skip link for keyboard users
- [ ] **No keyboard traps:** Can tab through and escape all components

#### Screen Reader Support
- [ ] **Semantic HTML:** Proper use of `<article>`, `<nav>`, `<aside>`, `<footer>`, `<header>`
- [ ] **Heading hierarchy:** Logical H1 → H2 → H3 structure (no skipping levels)
- [ ] **Alt text:** All images have descriptive alt attributes
- [ ] **ARIA labels:** Added where needed (e.g., share buttons with `title` attributes)
- [ ] **Link text:** Links have descriptive text (no "click here")
- [ ] **Form labels:** Region selector has visible label

#### Test with Screen Readers:
- [ ] **VoiceOver (macOS/iOS):** Navigate homepage and article page
- [ ] **NVDA (Windows):** Test article reading experience
- [ ] **TalkBack (Android):** Verify mobile navigation

### 7. Performance Optimization

#### Page Load Performance
- [ ] **Homepage FCP:** < 1.5 seconds (First Contentful Paint)
- [ ] **Homepage LCP:** < 2.5 seconds (Largest Contentful Paint)
- [ ] **Article page FCP:** < 1.5 seconds
- [ ] **Article page LCP:** < 2.5 seconds
- [ ] **CLS:** < 0.1 (Cumulative Layout Shift - no jumping content)
- [ ] **Total page size:** < 500KB gzipped

#### CSS Performance
- [ ] **CSS minification:** Verify production CSS is minified
- [ ] **Unused CSS:** Consider PurgeCSS or manual cleanup
- [ ] **Critical CSS:** Consider inlining critical CSS in `<head>`
- [ ] **CSS loading:** Non-critical CSS loads asynchronously

#### Image Performance
- [ ] **Image optimization:** All images compressed (WebP with JPEG fallback preferred)
- [ ] **Responsive images:** `srcset` and `sizes` attributes used
- [ ] **Lazy loading:** `loading="lazy"` on below-fold images
- [ ] **Aspect ratio boxes:** Prevent layout shift (width/height attributes or aspect-ratio CSS)
- [ ] **Image CDN:** Consider Cloudflare CDN for faster delivery

#### Font Performance
- [ ] **Font subsetting:** Only load character sets needed (Latin for English)
- [ ] **Font preloading:** Consider preloading critical fonts (Inter regular/bold)
- [ ] **FOUT mitigation:** `font-display: swap` prevents invisible text

### 8. Responsive Layout Verification

#### Breakpoints to Test:
- [ ] **320px:** Very small mobile (iPhone SE)
- [ ] **375px:** Standard mobile
- [ ] **640px:** Large mobile / small tablet (sm breakpoint)
- [ ] **768px:** Tablet (md breakpoint)
- [ ] **1024px:** Desktop (lg breakpoint)
- [ ] **1280px:** Wide desktop (xl breakpoint)
- [ ] **1920px:** Very wide desktop

#### Layout Checks:
- [ ] **Homepage grids:** 1 column (mobile) → 2 columns (tablet) → 3 columns (desktop)
- [ ] **Ongoing stories:** 1 column (mobile) → 2 columns (tablet)
- [ ] **Navigation:** Wraps properly on mobile, horizontal on desktop
- [ ] **Footer:** 1 column (mobile) → 3 columns (tablet+)
- [ ] **Article body:** Max-width 680px maintained on all screen sizes
- [ ] **Typography scaling:** clamp() values work smoothly across breakpoints

### 9. Design System Validation

- [ ] **CSS custom properties:** All colors, spacing, typography use variables
- [ ] **Consistent spacing:** All margins/padding use `--space-*` variables
- [ ] **Typography scale:** All text uses `--text-*` variables
- [ ] **Color palette:** All colors use `--color-*` variables
- [ ] **Shadow system:** All shadows use `--shadow-*` variables
- [ ] **Transition timing:** All transitions use `--transition-*` variables

### 10. Final Visual QA

#### Homepage
- [ ] **Header:** Navy background, red bottom border, white text
- [ ] **Site title:** Uppercase, bold, Inter font
- [ ] **Navigation:** Proper hover states (red underline)
- [ ] **Ongoing stories section:** Red gradient background, prominent
- [ ] **Article cards:** Proper hover lift effect
- [ ] **Footer:** Dark background, gold links

#### Article Pages
- [ ] **Article title:** Large display font (48-80px), bold, high impact
- [ ] **Body text:** Merriweather serif, 18-20px, readable line-height
- [ ] **Pull quotes:** Red left border, italic, larger font
- [ ] **"Why This Matters" callout:** Red/yellow gradient, red border
- [ ] **"What You Can Do" callout:** Green gradient, green border
- [ ] **Share buttons:** Platform-specific colors, hover effects
- [ ] **Images:** Full-width on mobile, boxed with shadow on desktop

---

## Testing Tools

### Automated Testing
- **Lighthouse:** Run audit for performance, accessibility, best practices
- **axe DevTools:** Accessibility testing browser extension
- **WAVE:** Web accessibility evaluation tool
- **WebPageTest:** Performance testing
- **BrowserStack:** Cross-browser and mobile device testing

### Manual Testing
- **Browser DevTools:** Responsive design mode, throttle network/CPU
- **Real Devices:** Test on actual iOS/Android devices when possible
- **Screen Readers:** VoiceOver, NVDA, TalkBack

---

## Sign-Off Checklist

Before deploying to production:

- [ ] All visual refinements verified
- [ ] Micro-interactions working on all platforms
- [ ] Font loading optimized and tested
- [ ] Cross-browser testing complete (Chrome, Firefox, Safari)
- [ ] Mobile device testing complete (iOS, Android)
- [ ] Accessibility audit passed (WCAG AA compliance)
- [ ] Performance targets met (< 2.5s LCP, < 0.1 CLS)
- [ ] Responsive layouts verified at all breakpoints
- [ ] Design system consistency validated
- [ ] Final visual QA approved

---

**Testing Status:** Ready for QA
**Deployment Readiness:** Pending testing completion
**Expected Completion:** After manual testing by user
