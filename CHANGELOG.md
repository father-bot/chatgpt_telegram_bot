# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
