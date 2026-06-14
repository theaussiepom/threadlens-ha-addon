# Live Home Assistant OS Validation Checklist

This checklist is for **manual validation on a real Home Assistant OS instance**. Complete it before tagging add-on release `v0.1.0`.

## Versions under test

| Component | Expected |
|-----------|----------|
| Add-on version | `0.1.0` |
| Core image | `ghcr.io/theaussiepom/threadlens:0.1.2` |
| HACS integration | latest from `threadlens-ha-integration` |

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

### API smoke test

Replace `<ha-host>` with your Home Assistant hostname or IP.

```bash
curl http://<ha-host>:8128/api/v1/health
curl http://<ha-host>:8128/api/v1/status
curl http://<ha-host>:8128/api/v1/report.yaml
```

- [ ] `/api/v1/health` returns JSON
- [ ] `/api/v1/status` returns JSON
- [ ] `/api/v1/report.yaml` returns YAML

## 3. Configure your environment

Fill in your LAN values locally (do not commit these):

| Setting | Your value |
|---------|------------|
| Study OTBR REST URL | `http://____________:8081` |
| Lounge OTBR REST URL | `http://____________:8081` |
| Matter Server websocket | `ws://____________:5580/ws` |
| MQTT broker host | `core-mosquitto` or `____________` |
| MQTT username | `____________` |
| MQTT password | `____________` (keep private) |
| ThreadLens API URL for HACS | `http://<ha-host>:8128` |

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

## 4. Expected collector results

After one or two poll cycles:

- [ ] OTBRs appear in `/api/v1/status`
- [ ] Matter nodes populate when Matter Server is reachable
- [ ] mDNS/TREL counts populate if host networking permits multicast
- [ ] MQTT connects when broker credentials are correct
- [ ] MQTT Discovery entities appear (optional baseline path)

### Expected warnings (informational)

These may appear without indicating an add-on fault:

- `otbr_rest_endpoint_mismatch`
- `foreign_trel_services_observed`

- [ ] Warnings understood and documented if present

## 5. HACS integration follow-up

1. Install **ThreadLens** from HACS (`threadlens-ha-integration`)
2. Configure integration URL:

   ```text
   http://<ha-host>:8128
   ```

3. Restart Home Assistant if prompted
4. Hard-refresh the ThreadLens sidebar panel

- [ ] Integration connects
- [ ] Sidebar dashboard loads
- [ ] Matter node health section populates

## 6. Read-only safety check

Confirm the add-on does **not**:

- [ ] Require Docker socket access
- [ ] Require SSH access
- [ ] Mutate OTBR, Matter, Thread, or HA state

## 7. Sign-off

| Check | Pass |
|-------|------|
| Add-on install | ☐ |
| API health/status/report | ☐ |
| OTBR collection | ☐ |
| Matter collection | ☐ |
| mDNS/TREL (if expected) | ☐ |
| MQTT (if enabled) | ☐ |
| HACS dashboard | ☐ |
| No secrets in logs | ☐ |

**Validator:** ________________  
**Date:** ________________  
**HAOS version:** ________________  
**Add-on branch/commit:** ________________

When all checks pass, tag add-on release `v0.1.0`.
