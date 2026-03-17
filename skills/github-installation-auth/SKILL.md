---
name: github-installation-auth
description: Configure GitHub installation auth inside a CompanyHelm runtime by calling the agent REST API and setting up gh plus git HTTPS credentials.
---

# GitHub Installation Auth

Use the bundled script. It lists GitHub installations visible to the current thread and configures `gh` plus git HTTPS auth for a selected installation.

## Prerequisites

- The runtime already has an agent config file containing:
  - `agent_api_url`
  - `token`
- `gh` and `git` are available in `PATH`

## List Installations

```bash
python3 scripts/use_github_installation.py list
```

Use `--json` if structured output is easier for the current task:

```bash
python3 scripts/use_github_installation.py list --json
```

## Configure an Installation

```bash
python3 scripts/use_github_installation.py use <installation-id>
```

This configures:

- `gh auth login --with-token`
- `gh auth setup-git`
- git HTTPS credential helpers for `https://github.com` and `https://gist.github.com`

So `git push` works immediately after selection.

## Overrides

The script reads the default CompanyHelm agent config, but you can override it with env vars:

- `COMPANYHELM_AGENT_CONFIG_PATH`
- `COMPANYHELM_AGENT_API_URL`
- `COMPANYHELM_AGENT_TOKEN`

