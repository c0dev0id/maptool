# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**MapTool** — an Android mapping tool. Planned around Mapsforge for
offline vector map rendering and BRouter for offline routing, with
support for routes, tracks, and waypoints.

**Status:** Boilerplate only. The template rename is done (package
`de.codevoid.maptool`); the app builds and shows a placeholder Compose
screen. Map, routing, and data features are not designed yet.

## Build & CI

Builds normally run in CI/CD. A local build is nevertheless possible and worth
doing before pushing: Gradle, Google Maven and `dl.google.com` are reachable —
only a preinstalled SDK is missing. Install `cmdline-tools` plus
`platforms;android-36` and `build-tools;36.0.0` into a scratch `ANDROID_HOME`,
then run `./gradlew lint assembleDebug`.

```sh
# one-time SDK bootstrap for a fresh container
export ANDROID_HOME=/tmp/android-sdk
mkdir -p "$ANDROID_HOME/cmdline-tools"
curl -o /tmp/cmdline-tools.zip \
  https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q /tmp/cmdline-tools.zip -d "$ANDROID_HOME/cmdline-tools"
mv "$ANDROID_HOME/cmdline-tools/cmdline-tools" "$ANDROID_HOME/cmdline-tools/latest"
yes | "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" --licenses
"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" \
  "platforms;android-36" "build-tools;36.0.0"
```

```sh
./gradlew lint assembleDebug   # what CI runs on every build
./gradlew assembleRelease      # unsigned unless the SIGNING_* vars are exported
```

Lint reports land in `app/build/reports/lint-results-debug.{html,xml}`.

**There is no test source set.** No `src/test`, no `src/androidTest`, no test
dependencies — `lint` is the only automated check. Adding tests means creating
the source set and its dependencies from scratch; do not assume a `./gradlew
test` invocation does anything today.

| CI task | Trigger |
|---|---|
| Lint + debug APK | Push to `main`, PR labeled `run-build`, or `workflow_dispatch` |
| Signed release APK + GitHub draft release | Manual `workflow_dispatch` |

PRs do **not** build by default — the build workflow's `pull_request` trigger is
`types: [labeled]` and gated on the label being `run-build`.

Signing secrets required: `SIGNING_KEYSTORE_BASE64`, `SIGNING_KEYSTORE_PASSWORD`, `SIGNING_KEY_ALIAS`, `SIGNING_KEY_PASSWORD`.

The release workflow owns the version: it takes a `version` input or
auto-increments the patch of the newest `v*` tag, derives `versionCode` as
`major * 10000 + minor * 100 + patch`, passes both to Gradle as
`-PversionName` / `-PversionCode`, and only then creates and pushes the tag.
The versions in `app/build.gradle.kts` are just the local/debug fallback.
The workflow decodes `SIGNING_KEYSTORE_BASE64` to a temp file and exports its
path as `SIGNING_KEYSTORE_PATH`, which is the variable `app/build.gradle.kts`
actually reads; when it is absent no signing config is created at all and the
release build stays unsigned.

## Architecture

- **Single Activity** (`MainActivity`) — no fragments, no navigation component.
- **Jetpack Compose** UI only — no XML layouts.
- **minSdk 26** (Android 8.0) — no need for pre-Oreo compatibility paths.
- The Compose BOM only manages the `androidx.compose.*` groups. Any other
  AndroidX dependency (e.g. `activity-compose`) needs an explicit version.
- **AGP 9 provides Kotlin support itself.** Only `com.android.application` and
  `org.jetbrains.kotlin.plugin.compose` are applied; do not add
  `org.jetbrains.kotlin.android`. Java and Kotlin both target 17.
- **Repositories are centralised** in `settings.gradle.kts` under
  `RepositoriesMode.FAIL_ON_PROJECT_REPOS`. A new repository (JitPack for
  BRouter, for instance) goes there, never into `app/build.gradle.kts`.
- The manifest theme is the **platform** `android:Theme.Material.Light.NoActionBar`,
  not an AppCompat or Material Components theme — there is no AppCompat
  dependency, and Compose supplies the real theming via `MaterialTheme`.

## Rules

- Always commit every logical step. Do not batch unrelated changes into one commit.
- Always rebase the working branch onto `main` at the end of a task.
- Maintain `CHANGELOG.md` (keep-a-changelog format) after each task.
- Maintain `.github/development-journal.md` with stack info, key decisions, and core features.

## Git

Configure before any git operation:
- `user.name = c0dev0id`
- `user.email = sh+git@codevoid.de`

No `Co-Authored-By` or other attribution lines in commits or PRs. Remove any lines containing "claude" from commit/PR messages. If `.gh_token` is present, use it for GitHub API access.
