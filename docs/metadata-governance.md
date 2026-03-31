# Metadata Governance Specification

## Purpose

This document defines the metadata governance rules for prompt assets in Prompt-Engineering-Kit (PEK). Its purpose is to keep prompt assets discoverable, comparable, reviewable, and maintainable as the repository grows.

This specification is intentionally lightweight. It is designed for a Markdown + YAML repository, not for a heavyweight content platform.

## 目标

本文档定义 Prompt-Engineering-Kit（PEK）中提示词资产的元数据治理规则，目标是确保仓库规模增长后，提示词资产仍然具备可检索、可比较、可审查、可维护的基本工程属性。

本规范刻意保持轻量，服务于 Markdown + YAML 仓库，而不是引入沉重的平台化治理流程。

## Scope

This specification applies to every prompt asset directory under `prompts/**/<slug>/`.

Each asset directory must contain:

- `prompt.zh-CN.md`
- `prompt.en.md`
- `meta.yml`

## Metadata Design Principles

1. **Asset-first, not language-first**: metadata describes one logical asset, not a single language file.
2. **Single source of truth**: one language must be marked as canonical.
3. **Human-readable, machine-usable**: fields must be easy to review in Git and stable enough for later tooling.
4. **Minimal but enforceable**: only fields that support retrieval, maintenance, or governance should be mandatory.
5. **No fake precision**: if the team does not really maintain a field, do not make it mandatory.

## Field Groups

### 1) Identity Fields

These fields define what the asset is.

| Field | Required | Description |
| --- | --- | --- |
| `id` | Yes | Stable asset identifier. Must match the slug directory name. |
| `name.zh-CN` | Yes | Chinese display name. |
| `name.en` | Yes | English display name. |
| `domain` | Yes | Top-level asset domain, such as `foundation` or `project-inception`. |
| `prompt_type` | Yes | Asset type, such as `playbook`, `workflow`, `template`, or `checklist`. |
| `summary` | Yes | One-paragraph summary of the asset’s purpose and scope. |

### 2) Governance Fields

These fields define how the asset is maintained.

| Field | Required | Description |
| --- | --- | --- |
| `status` | Yes | Lifecycle state. Allowed values: `draft`, `active`, `deprecated`, `archived`. |
| `version` | Yes | Semantic version of the asset definition, e.g. `1.0.0`. |
| `canonical_lang` | Yes | Source-of-truth language. Allowed values: one of `langs`. |
| `langs` | Yes | Supported language files, in priority order. |
| `translation_policy` | Yes | How non-canonical language files are maintained. Allowed values: `canonical-first`, `synchronized`, `independent`. |
| `last_reviewed` | Recommended | Last human review date in `YYYY-MM-DD`. |

### 3) Usage Fields

These fields define when and how to use the asset.

| Field | Required | Description |
| --- | --- | --- |
| `purpose` | Yes | The job this prompt is meant to accomplish. |
| `audience` | Recommended | Intended users, such as `full-stack developers`, `architects`, or `AI workflow designers`. |
| `inputs` | Recommended | Key input expectations for using the prompt. |
| `outputs` | Recommended | Primary output artifacts expected from the prompt. |
| `tags` | Yes | Stable classification tags for retrieval and grouping. |

### 4) Change Control Fields

These fields define how edits should be interpreted.

| Field | Required | Description |
| --- | --- | --- |
| `change_policy` | Recommended | How changes are versioned, e.g. `minor-for-copyedits-major-for-structure`. |
| `source_of_truth` | Recommended | Which file or locale should be trusted first when differences appear. |

## Required Field Baseline

At minimum, every `meta.yml` in PEK must contain the following fields:

```yaml
id:
name:
  zh-CN:
  en:
domain:
prompt_type:
summary:
status:
version:
canonical_lang:
langs:
translation_policy:
purpose:
tags:
```

## Lifecycle Rules

### Allowed `status` values

- `draft`: still being shaped; structure and wording may change frequently.
- `active`: approved for normal use and suitable as a maintained asset.
- `deprecated`: retained for reference, but new use should move elsewhere.
- `archived`: frozen historical asset; no longer maintained.

### Versioning Rules

- Increment **patch** for typo fixes, wording cleanup, and metadata-only adjustments that do not change prompt intent.
- Increment **minor** for stronger guidance, added sections, expanded constraints, or meaningful output-shape changes.
- Increment **major** when the prompt’s role, workflow contract, or usage model changes incompatibly.

## Bilingual Governance Rules

1. `canonical_lang` defines the source-of-truth language for semantic meaning.
2. `translation_policy: canonical-first` means the canonical version must be updated first, then translated.
3. If the canonical file changes structurally, the non-canonical file must be updated in the same change set whenever possible.
4. If semantic parity cannot be maintained immediately, the asset should not remain silently `active` without review.
5. Folder names stay language-neutral; language exists only at the file level.

## Authoring Rules

1. `id` must equal the slug directory name.
2. `domain` must match the directory segment directly under `prompts/`.
3. `summary` should explain scope, not marketing language.
4. `tags` should describe retrieval categories, not sentence fragments.
5. `purpose`, `inputs`, and `outputs` should describe actual usage contracts, not generic aspirations.

## Review Checklist

Before merging changes to a prompt asset, check:

1. Does `meta.yml` satisfy the required baseline?
2. Does `canonical_lang` match the real source-of-truth language?
3. Are `prompt.zh-CN.md` and `prompt.en.md` still structurally aligned?
4. Does `summary` describe the asset honestly?
5. Does the version change match the scale of the prompt change?

## Index Synchronization Rules

`meta.yml` and `prompts-index.md` do not own the same level of truth.

### Source of truth split

- `meta.yml` is the **detailed source of truth** for each asset.
- `prompts-index.md` is the **repository-level summary catalog**.

### Fields that must stay synchronized

For every asset row in `prompts-index.md`, the following values must match `meta.yml`:

| Index Column | Source Field in `meta.yml` |
| --- | --- |
| `Slug` | `id` |
| `Domain` | `domain` |
| `Type` | `prompt_type` |
| `中文标题` | `name.zh-CN` |
| `English Title` | `name.en` |
| `Canonical` | `canonical_lang` |
| `Locales` | `langs` |
| `Status` | `status` |
| `Version` | `version` |
| `Last Reviewed` | `last_reviewed` |

### Update rules

1. When creating a new asset, update `meta.yml` first, then add the matching row to `prompts-index.md` in the same change set.
2. When changing any mirrored metadata field, update `meta.yml` and `prompts-index.md` together.
3. When changing non-index fields such as `purpose`, `inputs`, `outputs`, `source_of_truth`, or `change_policy`, only `meta.yml` must change unless the asset summary should also change.
4. `prompts-index.md` must never contain fields that become a second semantic owner of asset meaning. It is a catalog, not a second metadata store.
5. If `meta.yml` and `prompts-index.md` conflict, reviewers must treat `meta.yml` as authoritative and require the index to be corrected before merge.

### Ordering rules

1. Keep index rows grouped by `Domain`.
2. Within each domain, sort rows by `Slug` in ascending ASCII order.
3. Do not reorder rows casually in unrelated changes.

### Minimal sync review checklist

Before merging a change that touches assets, check:

1. Does every asset directory have exactly one matching row in `prompts-index.md`?
2. Do `Slug`, `Domain`, names, `Status`, and `Version` match the asset `meta.yml`?
3. If a new locale was added or removed, was the `Locales` column updated?
4. If `last_reviewed` changed in `meta.yml`, was the index updated too?
5. If an asset is deprecated or archived, does the index reflect that lifecycle state?

## Recommended Minimal Template

```yaml
id: example-prompt
name:
  zh-CN: 示例提示词
  en: Example Prompt
domain: foundation
prompt_type: template
summary: Short summary of what the prompt does and where it should be used.
status: draft
version: 0.1.0
canonical_lang: zh-CN
langs:
  - zh-CN
  - en
translation_policy: canonical-first
purpose: Describe the practical job this prompt is intended to perform.
audience:
  - full-stack developers
inputs:
  - Project background
  - Constraints
outputs:
  - Structured markdown output
tags:
  - prompt-engineering
  - template
source_of_truth: prompt.zh-CN.md
change_policy: minor-for-structure-patch-for-copyedits
last_reviewed: 2026-03-31
```

## Non-Goals

- This specification does not require CI, databases, or external prompt hubs.
- This specification does not force every asset to have automated tests yet.
- This specification does not attempt to model every future governance need up front.

## Practical Reminder

If metadata becomes decorative, it becomes trash. A small set of maintained fields is better than a giant schema nobody updates.
