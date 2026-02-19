# Abyss Alignment Notes

This repo adopts practical Docker hardening patterns inspired by `zhugez/Abyss`:

## Adopted
- Multi-stage Python image build with wheel prebuild (`pip wheel`) and runtime install from wheels.
- Non-root container user for app services.
- Strict runtime posture in compose: `read_only`, `tmpfs`, `cap_drop: [ALL]`, `no-new-privileges`.
- Healthchecks + startup dependency on healthy upstream.
- Pinned infra images where practical.
- CI vulnerability gate using Trivy for app images.

## Out of scope (for now)
- Firecracker/microVM worker isolation
- Full observability stack (Loki/Promtail/Grafana)
- Distroless runtime migration
