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
