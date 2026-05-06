# Frontend Design Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single `frontend-design` skill that preserves the provided frontend-aesthetics guidance and adds concise shadcn-first starter guidance.

**Architecture:** This is a one-file skill addition. Validation uses a simple red-green repository check: first verify the skill file does not satisfy the required content checks, then create the file and rerun the same checks until they pass.

**Tech Stack:** Markdown, shell, git.

---

### Task 1: Add the frontend-design skill

**Files:**
- Create: `skills/frontend-design/SKILL.md`
- Create: `docs/superpowers/plans/2026-05-06-frontend-design-skill.md`

- [ ] **Step 1: Write the failing validation command**

```bash
test -f skills/frontend-design/SKILL.md \
  && grep -Fq 'name: frontend-design' skills/frontend-design/SKILL.md \
  && grep -Fq 'prefer shadcn/ui' skills/frontend-design/SKILL.md \
  && grep -Fq 'Prefer 1–2 “hero moments” of motion over lots of tiny animations' skills/frontend-design/SKILL.md
```

- [ ] **Step 2: Run validation to verify it fails**

Run:

```bash
test -f skills/frontend-design/SKILL.md \
  && grep -Fq 'name: frontend-design' skills/frontend-design/SKILL.md \
  && grep -Fq 'prefer shadcn/ui' skills/frontend-design/SKILL.md \
  && grep -Fq 'Prefer 1–2 “hero moments” of motion over lots of tiny animations' skills/frontend-design/SKILL.md
```

Expected: non-zero exit because the skill does not exist yet.

- [ ] **Step 3: Write the minimal skill file**

Create `skills/frontend-design/SKILL.md` with the requested frontmatter, the provided Frontend Aesthetics content, and a short shadcn-first section.

- [ ] **Step 4: Run validation to verify it passes**

Run the same command from Step 2.

Expected: zero exit status.

- [ ] **Step 5: Commit**

```bash
git add skills/frontend-design/SKILL.md docs/superpowers/plans/2026-05-06-frontend-design-skill.md
git commit -m "feat: add frontend design skill"
```
