# Release checklist — ThreadLens HAOS Add-on

Version target: **add-on `0.1.0`** running **Core `0.1.2`**

## Pre-release

- [ ] Core image available: `ghcr.io/theaussiepom/threadlens:0.1.2`
- [ ] `pytest tests/ -q` passes in this repo
- [ ] `bash -n threadlens/run.sh` passes
- [ ] Add-on `version` is `0.1.0` in `threadlens/config.yaml`
- [ ] Dockerfile `BUILD_VERSION` is `0.1.2`
- [ ] `host_network: true` remains configured
- [ ] Default `otbrs` and `matter_servers` are empty
- [ ] Secret/public-safety audit passes (`tests/test_validate.py`)
- [ ] [LIVE_HAOS_VALIDATION.md](LIVE_HAOS_VALIDATION.md) completed on a real HAOS host

## Publish add-on wrapper image (optional)

If publishing a pre-built wrapper image instead of local Supervisor build:

```bash
cd threadlens
docker build --build-arg BUILD_VERSION=0.1.2 -t ghcr.io/theaussiepom/threadlens-ha-addon:0.1.0 .
docker push ghcr.io/theaussiepom/threadlens-ha-addon:0.1.0
```

## HAOS install test

1. Add repository: `https://github.com/theaussiepom/threadlens-ha-addon`
2. Install ThreadLens add-on
3. Start with default safe config
4. Confirm logs show startup summary (no secrets)
5. `curl http://<ha-host>:8128/api/v1/health`
6. `curl http://<ha-host>:8128/api/v1/report.yaml`
7. Configure OTBR/Matter/MQTT and restart
8. Connect HACS integration to `http://<ha-host>:8128`

## Related repositories

- Core: https://github.com/theaussiepom/threadlens
- HACS integration: https://github.com/theaussiepom/threadlens-ha-integration

## Security and networking reminders

- No API authentication in v1 — trusted LAN only
- Host networking is enabled by default for mDNS/TREL multicast visibility
- Ingress is not wired in v1 — use direct API access
- No SSH, Docker socket, log scraping, or mutating Thread/Matter operations
- Add-on wraps Core ThreadLens; it does not duplicate collector logic

## Tagging

Do **not** tag `v0.1.0` until live HAOS validation passes.

## Branch protection

`main` should require PR + passing `test` CI job. See [CONTRIBUTING.md](CONTRIBUTING.md).
