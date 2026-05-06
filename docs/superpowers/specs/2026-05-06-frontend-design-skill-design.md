# Frontend Design Skill Design

**Date:** 2026-05-06  
**Repo:** `companyhelm-skills`

## Goal
Add a new reusable skill named `frontend-design` that guides agents to build frontend UI with a strong aesthetic point of view, explicitly prefer shadcn/ui as the component framework, and prefer starting from existing templates or blocks when possible.

## Scope
Create a single new file:

- `skills/frontend-design/SKILL.md`

No supporting scripts, examples, or extra reference files will be added.

## Requirements

### Skill metadata
- Skill folder name: `frontend-design`
- Frontmatter name: `frontend-design`
- Description should trigger for generating or refining frontend UI across React, Tailwind, HTML, and CSS.

### Skill body
- Preserve the user-provided “Frontend Aesthetics” guidance essentially verbatim.
- Include the provided output expectations.
- Add a short section that states:
  - prefer `shadcn/ui`
  - prefer existing templates, blocks, or prebuilt starters when possible
  - use those starters as a base, then customize them so the result is distinctive rather than generic

### Usage scope
- The skill should apply to both product/application UI and marketing/landing page work.
- The skill should push agents away from generic “AI slop” aesthetics.

## Non-goals
- No scripts
- No starter catalog
- No example apps
- No repo-wide refactors

## Implementation notes
- Match the lightweight style already used in this repo’s existing skills.
- Keep the skill concise and directly actionable.
