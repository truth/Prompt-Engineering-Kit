# Prompt-Engineering-Kit (PEK)

> Structured prompt engineering framework and asset kit for production use.

## Overview

**Prompt-Engineering-Kit (PEK)** is a production-oriented framework and asset management kit for structured prompt engineering. It turns scattered, ad hoc "AI spells" into standardized engineering assets that are reusable, testable, and version-controlled.

PEK covers the full software engineering lifecycle, including requirement clarification, architecture design, technology selection, and code generation. It is designed to help full-stack developers establish a rigorous interaction model for large language models, reduce communication and trial-and-error costs, and improve output quality, logical consistency, and system-level stability in complex business development.

## 项目简介

**Prompt-Engineering-Kit (PEK)** 是一个面向生产环境的结构化提示词工程框架与资产管理套件。它致力于将零散、随意的“AI 咒语”转化为可复用、可测试、可版本控制的标准化工程资产。

PEK 覆盖从需求拆解、架构设计、技术选型到代码生成的软件工程全生命周期场景，旨在为全栈开发者提供一套严谨的大模型交互范式，从而大幅降低沟通与试错成本，确保 AI 在复杂业务开发中的输出质量、逻辑连贯性与系统级稳定性。

## Repository Structure

```text
.
├─ README.md
├─ prompts-index.md
├─ docs/
│  └─ metadata-governance.md
└─ prompts/
   ├─ foundation/
   │  └─ ai-agent-prompt-engineering-playbook/
   │     ├─ meta.yml
   │     ├─ prompt.zh-CN.md
   │     └─ prompt.en.md
   └─ project-inception/
      └─ software-engineering-project-preparation/
         ├─ meta.yml
         ├─ prompt.zh-CN.md
         └─ prompt.en.md
```

## Conventions

- Organize prompts by **asset purpose**, not by language-first directory trees.
- Keep bilingual variants of the same asset side by side as `prompt.zh-CN.md` and `prompt.en.md`.
- Use stable ASCII slugs for folders.
- Store durable metadata in `meta.yml`.
- Register every prompt asset in `prompts-index.md`.
- Follow `docs/metadata-governance.md` for required metadata fields and lifecycle rules.

## How to Add a New Prompt Asset

1. Create a new slug directory under the correct domain in `prompts/`.
2. Add `prompt.zh-CN.md` and `prompt.en.md` with aligned structure.
3. Add a `meta.yml` file describing the asset.
4. Register the asset in `prompts-index.md`.
5. Review naming, section parity, and intended usage before commit.

## Current Assets

- Foundation / Methodology
  - `ai-agent-prompt-engineering-playbook`
- Project Inception / Pre-coding Preparation
  - `software-engineering-project-preparation`
