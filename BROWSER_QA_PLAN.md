# Browser QA Plan

## Phase 1: Smoke Test
- [ ] Navigate to target URL
- [ ] Check console errors (filter analytics/third-party)
- [ ] Verify no 4xx/5xx network requests
- [ ] Capture screenshots: desktop + mobile viewports
- [ ] Validate Core Web Vitals: LCP < 2.5s, CLS < 0.1, INP < 200ms

## Phase 2: Interaction Test
- [ ] Click all navigation links - verify no dead links
- [ ] Submit forms with valid data - verify success state
- [ ] Submit forms with invalid data - verify error state
- [ ] Test auth flow: login → protected page → logout
- [ ] Test key user journeys (checkout, onboarding, search)

## Phase 3: Visual Regression
- [ ] Capture screenshots at breakpoints: 375px, 768px, 1440px
- [ ] Compare with baseline screenshots (if available)
- [ ] Flag: layout shifts > 5px, missing elements, overflow
- [ ] Check dark mode (if applicable)

## Phase 4: Accessibility
- [ ] Run axe-core on each page
- [ ] Flag WCAG AA violations (contrast, labels, focus order)
- [ ] Verify keyboard navigation works end-to-end
- [ ] Check screen reader landmarks

## Output Format
```markdown
## QA Report — [URL] — [timestamp]

### Smoke Test
- [ ] Page loads
- [ ] Console errors: [details if any]
- [ ] Core Web Vitals: [LCP, CLS, INP values]
- [Screenshot]

### Interaction Test
- [ ] Navigation works
- [ ] Form validation
- [ ] Key journeys

### Visual Regression
- [ ] Desktop layout
- [ ] Mobile layout
- [ ] Dark mode (if applicable)

### Accessibility
- [ ] WCAG AA violations: [count]
- [ ] WCAG A violations: [count]
```