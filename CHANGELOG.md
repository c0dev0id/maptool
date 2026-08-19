# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- `CLAUDE.md`: added concrete build/SDK-bootstrap commands, noted the absence
  of any test source set, documented the AGP 9 plugin setup, the centralised
  repository mode and the platform theme, and corrected the description of how
  the release workflow produces the version and the tag

## [0.0.1] - 2026-08-17

### Added
- Compose boilerplate app (`de.codevoid.maptool`) with a placeholder screen
- Release signing configuration driven by `SIGNING_*` environment variables
- `versionName` / `versionCode` overridable from the command line, derived
  from the release tag by CI
- Lint report uploaded as a CI artifact; `workflow_dispatch` trigger on the
  build workflow

### Changed
- Renamed the project from the `keytester` template to `maptool`: package,
  Gradle root project, app label, and app strings
- Source/target compatibility and Kotlin `jvmTarget` moved to 17
- Build workflow runs lint and the debug build in a single job

### Fixed
- Build failed with `Could not find androidx.activity:activity-compose:` —
  the Compose BOM does not manage that group, so the version is now explicit
- `assembleRelease` produced an unsigned APK because no signing config was
  wired up, which made the release workflow fail by design
- Resource linking failed on `android:Theme.Material.Light.NoTitleBar`, which
  does not exist; the Material family spells it `NoActionBar`

### Removed
- Template setup workflow, which had already done its one-time substitution
- Debug-APK signing job, which ran without a checkout and required release
  secrets in ordinary builds
- Key-tester template screen and its data model
