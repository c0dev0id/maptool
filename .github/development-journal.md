# Development Journal

## Software Stack

- **Language:** Kotlin
- **UI:** Jetpack Compose (Material3), Compose BOM 2026.02.01
- **Min SDK:** 26 (Android 8.0)
- **Target/Compile SDK:** 36
- **Build:** CI-only via GitHub Actions (Gradle 9.4.0, AGP 9.1.0, Kotlin
  Compose plugin 2.3.10, JDK 17)
- **Planned:** Mapsforge (offline vector maps), BRouter (offline routing)

## Key Decisions

**AGP 9's built-in Kotlin support is used; no separate `kotlin-android` plugin.**
AGP 9.1 registers the `compileDebugKotlin` task and the `kotlin { }` extension
on its own, so only `com.android.application` and the Compose compiler plugin
are applied.

**Non-Compose AndroidX dependencies carry explicit versions.**
`androidx.compose:compose-bom` only constrains the `androidx.compose.*` groups.
`androidx.activity:activity-compose` was declared without a version and
resolution failed with `Could not find androidx.activity:activity-compose:`;
it is now pinned. Any future AndroidX dependency outside `androidx.compose.*`
needs the same treatment.

**Release signing comes from environment variables, not a properties file.**
`SIGNING_KEYSTORE_PATH`, `SIGNING_KEYSTORE_PASSWORD`, `SIGNING_KEY_ALIAS` and
`SIGNING_KEY_PASSWORD` are read in `app/build.gradle.kts`. The keystore never
enters the repository, and when the variables are absent the signing config is
simply not created, so debug builds and local release builds still work.

**Version metadata is a Gradle property, sourced from the release tag.**
The release workflow resolves the tag, derives `versionCode` as
`major * 10000 + minor * 100 + patch`, and passes both via `-P` flags.
Without this, every release APK would report the version checked into
`app/build.gradle.kts`.

**Lint and the debug build share one CI job.**
As separate jobs they duplicated the Gradle distribution download and raced
each other for identical cache keys (`ReserveCacheError` in the logs).

**Signing lives only in the release workflow.**
The build workflow previously had a job that signed the *debug* APK with the
release keystore, ran without `actions/checkout`, and failed whenever the
signing secrets were unset — which is every ordinary build.

## Core Features

None implemented yet. Planned:

- Offline vector map display (Mapsforge)
- Offline routing (BRouter)
- Route planning, import/export, navigation
- Track recording, import/export
- Waypoint creation, editing, organisation
