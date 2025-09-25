---
name: Codex Fix Request
about: Request automated code fixes using the Codex agent
title: '[CODEX] '
labels: codex, automated-fix
assignees: ''
---

## 🤖 Codex Fix Request

Use this template to request automated code fixes using the HVDC Codex agent.

## 📋 Fix Description
<!-- Describe what needs to be fixed -->

**Task:** [e.g., fix mypy errors, refactor imports, apply ruff fixes]

## 🎯 Target Scope
<!-- Specify what should be fixed -->

**Target Path:** `[e.g., src/, tools/, specific file]`  
**File Pattern:** `[e.g., *.py, specific files]`  
**Max Diff Size:** `[e.g., 8000 characters]`

## 🔧 Specific Issues
<!-- List specific issues that need to be addressed -->

- [ ] Issue 1
- [ ] Issue 2
- [ ] Issue 3

## 📝 Example Command
<!-- Example of how to trigger the fix -->

```
/codex fix mypy path=src task="fix type annotations"
```

## ✅ Expected Outcome
<!-- What should the fix accomplish? -->

## 🚫 Constraints
<!-- Any constraints or limitations -->

- [ ] Must preserve existing business logic
- [ ] Must maintain MACHO-GPT integration
- [ ] Must follow HVDC project conventions
- [ ] Must pass all quality gates

## 📊 Priority
<!-- How urgent is this fix? -->

- [ ] 🔴 Critical (blocking development)
- [ ] 🟡 High (should be done soon)
- [ ] 🟢 Medium (can wait)
- [ ] 🔵 Low (nice to have)

## 🏷️ Labels
<!-- Add relevant labels -->
- codex
- automated-fix
- [component] (e.g. logistics, ocr, weather-tie)
- [priority] (e.g. critical, high, medium, low)
