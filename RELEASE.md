# Release checklist — ThreadLens HAOS Add-on

Version target: **add-on `0.2.0`** running **Core `0.2.0`** with **Ingress dashboard**

## Prerequisites (blocking)

- [x] Core `v0.2.0` (React dashboard) merged to Core `main` and published: `ghcr.io/theaussiepom/threadlens:0.2.0`
- [x] Core image available for `linux/amd64` and `linux/arm64` (verified via GHCR manifest)
- [ ] Core image pull succeeds on HAOS target architecture (amd64 / aarch64) — verify during live HAOS test
- [ ] [LIVE_HAOS_VALIDATION.md](LIVE_HAOS_VALIDATION.md) completed on a real HAOS host (Ingress + LAN API)

**Do not tag add-on `v0.2.0` until live HAOS Ingress validation passes.** Merging PR #2 without a release is acceptable if docs clearly mark validation as pending.

## Pre-release

- [x] Core image available: `ghcr.io/theaussiepom/threadlens:0.2.0`
- [x] `pytest tests/ -q` passes in this repo
- [x] `bash -n threadlens/run.sh` passes
- [x] Add-on `version` is `0.2.0` in `threadlens/config.yaml`
- [x] Dockerfile `BUILD_VERSION` is `0.2.0`
- [x] `ingress: true`, `ingress_port: 8128`, `panel_icon`, `panel_title` configured
- [x] `host_network: true` remains configured
- [x] LAN ports `8128`/`8129` remain mapped
- [x] Default `otbrs` and `matter_servers` are empty
- [x] Secret/public-safety audit passes (`tests/test_validate.py`)
- [ ] [LIVE_HAOS_VALIDATION.md](LIVE_HAOS_VALIDATION.md) completed on a real HAOS host (Ingress + LAN API)

## Publish add-on wrapper image (optional)

If publishing a pre-built wrapper image instead of local Supervisor build:

```bash
cd threadlens
docker build --build-arg BUILD_VERSION=0.2.0 -t ghcr.io/theaussiepom/threadlens-ha-addon:0.2.0 .
docker push ghcr.io/theaussiepom/threadlens-ha-addon:0.2.0
```

## HAOS install test

1. Add repository: `https://github.com/theaussiepom/threadlens-ha-addon`
2. Install ThreadLens add-on
3. Start with default safe config
4. Confirm logs show startup summary including `Ingress: enabled` (no secrets)
5. Click **Open Web UI** — dashboard loads through Ingress
6. `curl http://<ha-host>:8128/api/v1/health`
7. `curl http://<ha-host>:8128/api/v1/dashboard`
8. Configure OTBR/Matter/MQTT and restart
9. Re-open Ingress dashboard — collectors populate
10. (Optional) Connect HACS integration to `http://<ha-host>:8128`

## Related repositories

- Core: https://github.com/theaussiepom/threadlens
- HACS integration: https://github.com/theaussiepom/threadlens-ha-integration

## Security and networking reminders

- No API authentication in v1 on LAN — trusted LAN only
- Ingress Web UI uses Home Assistant session authentication
- Host networking is enabled by default for mDNS/TREL multicast visibility
- LAN ports 8128/8129 remain exposed for direct API access and HACS integration
- No SSH, Docker socket, log scraping, or mutating Thread/Matter operations
- Add-on wraps Core ThreadLens; it does not duplicate collector or dashboard logic

## Tagging

Do **not** tag `v0.2.0` until live HAOS Ingress validation passes. Core `0.2.0` is already published; the remaining gate is completing [LIVE_HAOS_VALIDATION.md](LIVE_HAOS_VALIDATION.md) on a real HAOS host.

## Branch protection

`main` should require PR + passing `test` CI job. See [CONTRIBUTING.md](CONTRIBUTING.md).
