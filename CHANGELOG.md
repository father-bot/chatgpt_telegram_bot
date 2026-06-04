# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0]

### Removed
- Legacy `gpt-3.5-turbo` and `gpt-4` models from the menu and config — the
  lineup is now gpt-4o-mini (default), gpt-5.5, gpt-4o and the Claude models.

### Changed
- Simplified the token-count overhead table (all current chat models share
  the same overhead).
- Refreshed the README (title and feature list) to drop legacy GPT-4 mentions.

### Fixed
- `/balance` no longer raises a `KeyError` for users with historical usage of
  models that have since been removed from the config.

## [1.2.0]

### Added
- Minimal GitHub Actions CI: installs requirements on Python 3.12 and
  byte-compiles the bot on every push and pull request.

### Changed
- Image generation now uses OpenAI **gpt-image-1** (default size 1024×1024);
  images are returned as bytes and `/balance` / pricing updated accordingly.
- Updated `gpt-4o` pricing to current rates (0.0025 / 0.01 per 1k tokens).

### Removed
- Deprecated models `gpt-3.5-turbo-16k`, `gpt-4-1106-preview` and
  `gpt-4-vision-preview` from the model menu (gpt-4o / gpt-4o-mini cover them).

## [1.1.0]

### Added
- **OpenRouter provider support**: models can declare `provider: openrouter`
  in `models.yml` and are routed through an OpenAI-compatible OpenRouter
  client. New `openrouter_api_key` / `openrouter_api_base` config options.
- **Anthropic Claude models** via OpenRouter: Claude Opus 4.8, Claude Sonnet
  and Claude Haiku.
- OpenAI `gpt-5.5` (via OpenRouter).

### Changed
- Chat models are now dispatched by their `type` in `models.yml` instead of
  hardcoded model-name lists, so adding a model is a config-only change.
- Token counting falls back to the `o200k_base` encoding for models unknown
  to `tiktoken` (e.g. Claude).
- The `/settings` model picker lays buttons out in rows of two to stay within
  Telegram's per-row inline-button limit.
- Image understanding is now driven by a `vision: true` flag in `models.yml`,
  so any vision-capable model (GPT-4o, GPT-4o mini, GPT-5.5, Claude) can read
  images — no longer limited to GPT-4o / GPT-4 Vision.

## [1.0.0]

### Added
- `gpt-4o` and `gpt-4o-mini` models, with `gpt-4o-mini` as the new default.
- `VERSION` file and this changelog.

### Changed
- Migrated from the deprecated `openai==0.28` API to the `openai>=1.x` SDK
  (`AsyncOpenAI` client, new chat/image/audio/moderation methods, updated
  error classes).
- Default model is now `gpt-4o-mini` instead of the outdated `gpt-3.5-turbo`
  (new users, `/new`, and the `ChatGPT` fallback).
- Upgraded the Docker base image to Python 3.12 (3.8 is end-of-life).
- Bumped dependencies: `python-telegram-bot` 20.8, `pymongo` 4.6.3,
  `PyYAML` 6.0.2, `python-dotenv` 1.0.1, `tiktoken` >= 0.7.0.
- Docker: smaller image (`pip --no-cache-dir`), unbuffered logs
  (`PYTHONUNBUFFERED`), live-mounted config, expanded `.dockerignore`,
  removed the obsolete Compose `version` key.

### Removed
- `text-davinci-003` and its legacy completion code paths (the model was
  shut down by OpenAI).

### Fixed
- Corrected `gpt-4o` pricing and scores in `models.yml`.
- `tiktoken` now recognizes the `o200k_base` encoding used by `gpt-4o`.
- Removed debug logging that fired on every incoming message.
- Narrowed bare `except:` clauses so shutdown/cancellation propagates.
- Stopped tracking `.DS_Store`; various typo and docs fixes.
