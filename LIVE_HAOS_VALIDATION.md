# Live Home Assistant OS Validation Checklist

This checklist is for **manual validation on a real Home Assistant OS instance**. Complete it before tagging add-on release `v0.2.0`.

## Current status (Phase 7A — deferred)

| Check | Status |
|-------|--------|
| Core `0.2.0` published on GHCR | ✅ Done |
| Add-on PR #2 structurally aligned with Core `0.2.0` | ✅ Done (static/repo validation) |
| Core image pin verified (`linux/amd64`, `linux/arm64`) | ✅ Done |
| Add-on tests and CI green | ✅ Done |
| **Live HAOS Ingress validation** | ⏳ **Pending** — no HAOS test instance available yet |

**Do not tag or release add-on `v0.2.0` until this checklist is completed on a real HAOS host.**

Repository and CI validation do **not** prove Ingress dashboard behaviour. Treat Ingress as unvalidated until the checks below pass.

## Prerequisites

| Dependency | Status |
|------------|--------|
| Core `v0.2.0` (React dashboard) merged and published | ✅ |
| Core image `ghcr.io/theaussiepom/threadlens:0.2.0` on GHCR | ✅ |
| Add-on branch `feat/ingress-core-dashboard` (or merged main) | ☐ install from branch or merged main |
| Real Home Assistant OS test host | ☐ required before release |

## Versions under test

| Component | Expected |
|-----------|----------|
| Add-on version | `0.2.0` |
| Core image | `ghcr.io/theaussiepom/threadlens:0.2.0` |
| HACS integration (optional) | latest from `threadlens-ha-integration` |

## 1. Add the add-on repository

```text
Settings → Add-ons → Add-on Store → ⋮ → Repositories
```

Add:

```text
https://github.com/theaussiepom/threadlens-ha-addon
```

- [ ] Repository added without error
- [ ] Add-on store refreshed
- [ ] **ThreadLens** appears in the store

## 2. Install with safe defaults

1. Install **ThreadLens**
2. Leave `otbrs` and `matter_servers` empty for the first start
3. Keep defaults:
   - `mode: both`
   - `host_network: true`
   - `server.port: 8128`
   - `agent.port: 8129`
4. Start the add-on

### Expected startup log lines (no secrets)

```text
ThreadLens add-on starting
Mode: both
Dashboard: enabled on Core port 8128
Ingress: enabled
Server port: 8128
Agent port: 8129
Configured OTBRs: 0
Configured Matter servers: 0
MQTT enabled: true
Home Assistant Discovery enabled: true
mDNS enabled: true
```

- [ ] Add-on reaches **Running**
- [ ] No passwords or tokens in logs

## 3. Ingress dashboard

1. Open **Settings → Add-ons → ThreadLens**
2. Confirm **Open Web UI** (or equivalent Ingress launch) is available
3. Click to open the dashboard

- [ ] Dashboard opens through Ingress
- [ ] Page title shows ThreadLens Dashboard
- [ ] CSS/JS assets load (no blank page)
- [ ] Header shows API connected / version
- [ ] Incident summary and sections render (may be sparse with empty config)

### Dashboard API through Ingress

Open browser developer tools on the Ingress dashboard page:

- [ ] Network request to relative `api/v1/dashboard` succeeds (200 JSON)
- [ ] No `hass.callWS` or Home Assistant websocket errors in console
- [ ] Report YAML link opens in a new tab and returns YAML text

## 4. LAN API smoke test

Replace `<ha-host>` with your Home Assistant hostname or IP.

```bash
curl http://<ha-host>:8128/api/v1/health
curl http://<ha-host>:8128/api/v1/dashboard
curl http://<ha-host>:8128/api/v1/status
curl http://<ha-host>:8128/api/v1/report.yaml
```

- [ ] `/api/v1/health` returns JSON
- [ ] `/api/v1/dashboard` returns JSON with `threadlens` section
- [ ] `/api/v1/status` returns JSON
- [ ] `/api/v1/report.yaml` returns YAML
- [ ] `GET /` on LAN returns dashboard HTML (Core static UI)

## 5. Configure your environment

Fill in your LAN values locally (do not commit these):

| Setting | Your value |
|---------|------------|
| Study OTBR REST URL | `http://____________:8081` |
| Lounge OTBR REST URL | `http://____________:8081` |
| Matter Server websocket | `ws://____________:5580/ws` |
| MQTT broker host | `core-mosquitto` or `____________` |
| MQTT username | `____________` |
| MQTT password | `____________` (keep private) |
| ThreadLens LAN API URL | `http://<ha-host>:8128` |

Example configuration shape:

```yaml
site_name: Home
mode: both
otbrs:
  - id: study
    name: Study OTBR
    rest_url: http://<study-otbr-host>:8081
  - id: lounge
    name: Lounge OTBR
    rest_url: http://<lounge-otbr-host>:8081
matter_servers:
  - id: study_matter
    name: Study Matter Server
    websocket_url: ws://<matter-host>:5580/ws
    variant: python
mqtt:
  enabled: true
  host: core-mosquitto
  port: 1883
  username: "<your-mqtt-user>"
  password: "<your-mqtt-password>"
homeassistant:
  mqtt_discovery_enabled: true
```

- [ ] Configuration saved
- [ ] Add-on restarted cleanly

## 6. Expected collector results

After one or two poll cycles, re-open the Ingress dashboard:

- [ ] OTBRs appear in dashboard and `/api/v1/status`
- [ ] Matter nodes populate when Matter Server is reachable
- [ ] mDNS/TREL counts populate with host networking enabled
- [ ] MQTT connects when broker credentials are correct
- [ ] MQTT Discovery entities appear (optional baseline path)
- [ ] Matter node health section shows grouped nodes when data exists

### Expected warnings (informational)

These may appear without indicating an add-on fault:

- `otbr_rest_endpoint_mismatch` (reconciled mismatch should not look scary in dashboard)
- `foreign_trel_services_observed` (informational in dashboard)

- [ ] Warnings understood and documented if present

## 7. HACS integration (optional)

The HACS integration is **not required** for the Ingress dashboard. Optional follow-up:

1. Install **ThreadLens** from HACS (`threadlens-ha-integration`)
2. Configure integration URL:

   ```text
   http://<ha-host>:8128
   ```

3. Restart Home Assistant if prompted

- [ ] Integration connects to LAN API
- [ ] HACS sidebar dashboard still works (parallel path during migration)
- [ ] Ingress dashboard remains the canonical Core UI

## 8. Read-only safety check

Confirm the add-on does **not**:

- [ ] Require Docker socket access
- [ ] Require SSH access
- [ ] Mutate OTBR, Matter, Thread, or HA state
- [ ] Duplicate Core dashboard assets in the add-on image

## 9. Sign-off

| Check | Pass |
|-------|------|
| Add-on install | ☐ |
| Ingress dashboard opens | ☐ |
| Dashboard API via Ingress | ☐ |
| Report YAML via Ingress | ☐ |
| LAN API health/dashboard/report | ☐ |
| OTBR collection | ☐ |
| Matter collection | ☐ |
| mDNS/TREL (host networking) | ☐ |
| MQTT (if enabled) | ☐ |
| HACS integration (optional) | ☐ |
| No secrets in logs | ☐ |

**Validator:** ________________  
**Date:** ________________  
**HAOS version:** ________________  
**Add-on branch/commit:** ________________

When all checks pass on a real HAOS host, tag add-on release `v0.2.0`. Core `0.2.0` is already published; live HAOS Ingress validation is the remaining gate.
