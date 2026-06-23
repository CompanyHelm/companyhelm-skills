---
name: frontend-design
description: Use when generating or refining frontend UI in React, Tailwind, HTML, or CSS, including app UI, dashboards, landing pages, and design systems that should avoid generic AI-looking aesthetics.
---

# Frontend Design

Prefer `shadcn/ui` as the default component framework when working in React.

Prefer existing templates, blocks, and prebuilt starters when possible so there is a strong starting point. Start from them, then customize aggressively so the result feels genuinely designed for the context instead of generic.

If using shadcn, check for an existing shadcn-compatible template, block, or app shell first before composing everything from scratch.

# Frontend Aesthetics

Use this skill whenever you are:
- Designing a new UI, landing page, dashboard, marketing site, or component library
- “Polishing” an existing UI
- Choosing typography, color, motion, layout, or backgrounds

<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight.

Focus on:
- Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.
- Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.
- Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions.
- Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!
</frontend_aesthetics>

## Output expectations
- Produce real, runnable code (no pseudocode)
- Include font import/setup when you pick a font (e.g. Google Fonts / local)
- Use CSS variables for theme tokens
- Prefer 1–2 “hero moments” of motion over lots of tiny animations

## Information architecture and copy
- Breadcrumbs belong at the top of the content hierarchy. Put the breadcrumb trail in the app/page header or the first content row before page-specific actions, hero content, tabs, cards, or forms; do not bury breadcrumbs below CTAs or body copy.
- Avoid duplicating titles across adjacent hierarchy levels. If the app shell/header, sidebar item, route title, or breadcrumb already says the page name, do not immediately repeat the same word as the largest page heading unless the heading adds meaningful context.
- Avoid repeating the same noun or title across adjacent hierarchy levels. If a tab, sidebar item, breadcrumb, or page title already names the area,
  do not immediately follow it with another section heading or empty-state title that repeats the same name.
- Each hierarchy level should add new meaning: use the navigation label for orientation, the page or section heading for the specific job to be done,
  and helper copy for constraints, status, or next steps.
- Audit visible text for duplication before finalizing UI: active nav label, page heading, card heading, empty-state headline, CTA, and tooltip should not
  feel like repetitive copies of one another.
- When the obvious heading repeats the nav label, replace it with context-specific copy that describes the user goal, object state, or next action.
- Empty states should explain what is missing and what the user can do next instead of restating the container name.

## Menus, selects, and popovers
- Never ship browser-default, unstyled menus or selects in a polished app surface. Native controls are acceptable only when they are intentionally styled to match the design system and verified in the target browsers.
- Prefer the product’s design-system menu/select/popover components over raw `<select>`, `<details>`, or ad-hoc floating panels.
- Check menus and popovers in dark mode, at constrained/mobile widths, and near viewport edges. They must have deliberate background, border, radius, shadow/elevation, hover/focus states, selected states, keyboard behavior, and readable contrast.
- Do not let popovers clip, overflow off-screen, hide behind modal boundaries, or look detached from the app theme.

## User-facing data display
- Do not expose internal IDs, UUIDs, database keys, opaque organization IDs, task IDs, workflow IDs, session IDs, or similar implementation
  identifiers in primary user-facing UI unless the ID is directly actionable for the user.
- Prefer human-readable names, titles, labels, slugs, statuses, dates, owners, and short descriptions that help users recognize the object.
- When an internal ID is genuinely actionable, such as for support handoff, debugging, audit logs, API usage, or a copy/paste integration
  workflow, show it intentionally: label it clearly, keep it visually secondary, and make it easy to copy.
