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

**Local verification is possible after installing the SDK by hand.**
Gradle, Google Maven and `dl.google.com/android/repository` are all reachable
from the dev container; only a preinstalled SDK is missing. Installing
`cmdline-tools` plus `platforms;android-36` and `build-tools;36.0.0` into a
scratch `ANDROID_HOME` makes `./gradlew lint assembleDebug` work locally, which
caught the theme resource error before it reached CI.

**Signing lives only in the release workflow.**
The build workflow previously had a job that signed the *debug* APK with the
release keystore, ran without `actions/checkout`, and failed whenever the
signing secrets were unset — which is every ordinary build.

## Planned Architecture (milestone 1)

**Renderer: VTM (OpenGL), not the classic Mapsforge canvas renderer.**
Rotation, tilt and smooth zoom matter for a navigation-style app. Same `.map`
file format either way. VTM 0.25.0 ships its native libraries as per-ABI
classifier JARs (`vtm-android-0.25.0-natives-arm64-v8a.jar` and friends), so
each ABI has to be declared explicitly in the build.

**Routing: intent calls to the separately installed BRouter app.**
Far less code than embedding `brouter-core`, and BRouter manages its own
segment data. The cost is a hard dependency on the user installing BRouter.
Routing results enter the app as an overlay layer, so an embedded engine can
replace the intent call later without touching the layer model.

**Map storage: app-private external storage (`getExternalFilesDir("maps")`).**
No runtime permissions and no SAF plumbing, and VTM can open the file by
path. Maps are lost on uninstall and cannot be shared with other map apps;
a SAF-based import path can be added later for existing on-device maps.

**Map catalog: generated and bundled, not scraped at runtime.**
`download.mapsforge.org` serves a plain Apache directory index with no
manifest, so the catalog is crawled by `tools/generate-map-catalog.py` and
checked in as an asset. The picker then works offline and on first launch.
Regenerate when the upstream list changes. Sizes in the catalog are
approximate (the index shows `3.0G`); the exact length comes from
`Content-Length` at download time.

**Multiple `.map` files render at once via `MultiMapFileTileSource`.**
Country files are huge — `europe/germany.map` is 3.0 GB against 545 MB for
`bayern.map` — so the expected usage is downloading several sub-regions.
Stacking them into one tile source means no manual map switching at regional
borders.

## Core Features

None implemented yet. Planned:

- Offline vector map display (Mapsforge)
- Offline routing (BRouter)
- Route planning, import/export, navigation
- Track recording, import/export
- Waypoint creation, editing, organisation
