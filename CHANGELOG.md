# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] 2026-02-22

### Fixed

- Long responses were cut when the terminal width is exceeded, while the assistant is generating text. Fixed by implementing an auto-scroll mechanism in the response panel.

### Changed

- Spinner dots now have random behavior.

### Removed

- The use of environment variables, in favor of already implemented toml configuration files.

## [0.1.4] - 2026-02-21

### Added

- Implemented a function to preload models, making first response faster.
- The response panel now shows the role name.
