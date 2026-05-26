---
name: write-docs
description: Use when creating, rewriting, reviewing, or standardizing project documentation, especially README files, contributing guides, changelogs, issue/PR templates, codebase maps, TODOs, and docs that should be easy for new users and contributors to follow.
---

# Write Docs

Use this skill to produce documentation that people can actually understand, skim, and act on. It is adapted from the CC0-licensed patterns in [`race2infinity/The-Documentation-Compendium`](https://github.com/race2infinity/The-Documentation-Compendium).

## Documentation goals

Good docs should answer, in order:

1. **What is this?** One plain-language sentence and a short paragraph.
2. **Why should I care?** The problem solved, audience, and practical value.
3. **How do I start?** Copy-pasteable setup and first-success path.
4. **How do I use it?** Real examples, CLI/API/UI flows, common options.
5. **How do I verify it worked?** Expected output, screenshots, logs, or tests.
6. **How do I contribute or extend it?** Codebase map, contribution flow, standards.
7. **Where do I go next?** Links to deeper reference, troubleshooting, support.

Optimize for readers who are interested but unfamiliar. Do not assume prior project knowledge.

## Voice and writing rules

Do:

- Keep a friendly, light, direct tone.
- Keep sections brief and scannable.
- Use frequent descriptive headings.
- Put immediately relevant information inline; link away only for optional depth.
- Include concrete code snippets, CLI commands, payload examples, screenshots, or UI steps whenever possible.
- Gently introduce context before technical details.
- Describe the purpose of important files and directories.
- Use gender-neutral language.
- Prefer active voice and imperative steps: “Run”, “Open”, “Create”, “Set”.

Avoid:

- Assuming prior knowledge.
- Idioms, slang, or culture-specific phrases that make translation harder.
- Huge examples that obscure the core idea.
- Offensive, exclusionary, or unnecessarily gendered terms.
- Decorative badges, logos, emoji, or tables that distract from comprehension.
- Links that force readers to chase basic setup information across many pages.

## README structure

When asked for a README, choose the smallest structure that answers the project’s needs.

### Minimal README

Use for small utilities, internal repos, prototypes, and packages where speed matters.

````md
# Project Title

Short description of what this project does and who it is for.

## About

Explain the problem, what this project provides, and when someone should use it.

## Getting started

### Prerequisites

- Requirement 1
- Requirement 2

### Install

```bash
command to install
```

### Run

```bash
command to run
```

Expected result:

```text
example output
```

## Usage

Show the most common workflow first.

```bash
real command or example
```

## Contributing

Link to CONTRIBUTING.md or explain the basic contribution flow.
````

### Standard README

Use for public projects, libraries, services, developer tools, and anything needing onboarding.

````md
# Project Title

One-sentence value proposition.

Brief paragraph explaining what the project does, who it helps, and why it exists.

## Table of contents

- [About](#about)
- [Getting started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## About

Describe the purpose, target users, and main capabilities in 1–2 paragraphs.

## Getting started

Explain how to get a local copy running for development and testing.

### Prerequisites

List required runtimes, package managers, services, API keys, or permissions.

### Install

```bash
copy-pasteable install commands
```

### Run locally

```bash
copy-pasteable run commands
```

Show the expected URL, output, or success state.

## Usage

Start with the most common example. Add advanced examples only after the basics.

```bash
example command
```

## Configuration

Document environment variables, config files, flags, and defaults.

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `EXAMPLE_ENV` | Yes | — | What it controls. |

## Testing

```bash
command to run tests
```

Explain test categories if useful: unit, integration, end-to-end, lint, typecheck.

## Deployment

Document the normal deployment path and any required checks or rollback notes.

## Project structure

```text
path/          purpose
path/file.ext  purpose
```

## Contributing

Link to CONTRIBUTING.md and summarize the branch, commit, test, and PR flow.

## License

State the license and link to the license file.
````

## Specialized README additions

Add these sections only when relevant:

- **Demo / screenshots**: for UI, bots, CLIs, hardware, and hackathon projects.
- **How it works**: for bots, automation, AI systems, infrastructure, and complex flows.
- **API reference**: for libraries and services; include auth, endpoints, payloads, errors.
- **Architecture**: for systems with multiple services or non-obvious data flow.
- **Hardware requirements**: for IoT or physical projects; include parts, wiring, diagrams, safety.
- **Troubleshooting**: for projects with common setup failures.
- **Security**: for auth, tokens, webhooks, permissions, network exposure, or sensitive data.
- **Acknowledgements**: for copied ideas, templates, papers, assets, libraries, or sponsors.

## Contributing guide template

````md
# Contributing

Thanks for helping improve this project.

## Before you start

- Read the README and relevant docs.
- Check existing issues and pull requests.
- For large changes, open an issue or discussion first.

## Development flow

1. Fork or branch from the default branch.
2. Create a focused branch named for the change.
3. Make the smallest useful change.
4. Run formatting, linting, tests, and docs checks.
5. Commit with a clear message.
6. Open a pull request with context, screenshots or logs, and test results.

## Standards

- Keep changes focused.
- Include tests or explain why tests are not applicable.
- Update docs when behavior changes.
- Follow the existing style unless the project says otherwise.
````

## Changelog template

Use a changelog when releases or shipped behavior need to be tracked.

````md
# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning when applicable.

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

## [1.2.3] - YYYY-MM-DD

### Added

- User-facing change with issue or PR link when available.
````

## Codebase structure template

````md
# Codebase structure

Describe the directories and files that contributors need to understand first.

```text
src/              application source
src/api/          API routes and request handlers
src/lib/          shared utilities
src/components/   UI components
tests/            automated tests
docs/             project documentation
```

## Notes

- Explain dependency direction and ownership boundaries.
- Call out generated files, migrations, scripts, and deployment config.
- Link to deeper architecture docs if they exist.
````

## Issue template checklist

A useful bug report asks for:

- Summary
- Expected behavior
- Actual behavior
- Steps to reproduce
- Environment: version, OS/browser/runtime, relevant config
- Logs, screenshots, or minimal reproduction
- Regression info: when it last worked, if known

A useful feature request asks for:

- Problem or user need
- Proposed solution
- Alternatives considered
- Examples, mockups, or prior art
- Scope notes and non-goals

## Pull request template checklist

A useful PR description includes:

- What changed
- Why it changed
- How to test or verify
- Screenshots, recordings, or logs when UI/behavior changed
- Related issues or tasks
- Risk, rollout, and rollback notes when relevant
- Documentation updates or reason docs are not needed

## Review checklist

Before finishing docs, verify:

- A new reader can understand the project from the first screen.
- The first successful action is copy-pasteable.
- Commands are real and ordered correctly.
- Examples include expected output or result.
- Links are relevant and not required for basic comprehension.
- Headings form a sensible outline.
- The docs say where config, tests, deployment, and contribution rules live.
- Changed behavior is reflected in README, changelog, and related docs.
- Sensitive values, private URLs, and credentials are not included.
