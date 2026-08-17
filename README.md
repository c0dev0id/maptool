# MapTool

A mapping tool for Android with offline maps, routing, and track and
waypoint management.

## Planned scope

- Offline vector maps rendered with [Mapsforge](https://github.com/mapsforge/mapsforge)
- Offline routing with [BRouter](https://github.com/abrensch/brouter)
- Routes: plan, import, export, navigate
- Tracks: record, import, export
- Waypoints: create, edit, organise

## Status

Boilerplate only. The app currently builds and launches a placeholder
Compose screen; no map, routing, or data handling is implemented yet.

## Build

Builds run in CI, not locally:

| What | Trigger |
|---|---|
| Lint + debug APK | Push to `main`, PR labeled `run-build`, or manual run |
| Signed release APK + draft GitHub release | Manual run of the Release workflow |
