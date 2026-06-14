# ThreadLens

Read-only observability for Thread, OpenThread Border Routers, TREL/mDNS, Matter Server, and Matter-over-Thread node health.

## What this add-on does

- Runs [ThreadLens Core](https://github.com/theaussiepom/threadlens) `0.1.2` on Home Assistant OS
- Polls OTBR REST APIs you configure
- Observes Matter Server websocket inventory (read-only)
- Observes mDNS/TREL service types when host networking allows multicast visibility
- Optionally publishes Home Assistant MQTT Discovery entities
- Exposes health, status, and YAML/JSON diagnostic reports

Pair with the [ThreadLens HACS integration](https://github.com/theaussiepom/threadlens-ha-integration) for the sidebar dashboard.

## What this add-on does not do

- Does not commission or mutate Thread networks
- Does not issue Matter commands or change node state
- Does not use SSH, Docker socket access, or host log scraping
- Does not provide API authentication in v1

## Requirements

- Home Assistant OS with Supervisor
- **MQTT integration** enabled if you want MQTT Discovery entities (recommended)
- Mosquitto broker add-on or equivalent (default MQTT host: `core-mosquitto`)

## Network mode and mDNS/TREL

This add-on enables **host networking** by default (`host_network: true`).

Host networking is recommended so ThreadLens can observe:

- `_trel._udp`
- `_meshcop._udp`
- `_matter._tcp`
- `_matterc._udp`

Without multicast visibility, mDNS/TREL lists may be empty while OTBR REST, Matter websocket, MQTT, and reports still work. That usually indicates a **network visibility** limitation — ThreadLens does **not** infer device parentage or topology from missing mDNS data.

If you disable host networking, expect degraded or no mDNS/TREL observation. Explicit mDNS interface allowlists are not exposed by Core `0.1.2`; the add-on enables or disables mDNS collection only.

## Configuration

### Site and mode

| Option | Default | Description |
|--------|---------|-------------|
| `site_name` | `Home` | Site label in reports and MQTT |
| `mode` | `both` | `server`, `agent`, or `both` |

| Mode | Server API `:8128` | Local agent API `:8129` |
|------|--------------------|-------------------------|
| `server` | Yes | No |
| `agent` | No | Yes |
| `both` | Yes | Yes |

### OTBR REST URLs

Add one entry per OpenThread Border Router:

| Field | Description |
|-------|-------------|
| `id` | Unique ID (e.g. `study`) |
| `name` | Display name |
| `rest_url` | OTBR REST base URL (e.g. `http://192.168.1.10:8081`) |
| `agent_url` | Optional co-located ThreadLens agent URL; leave empty if unused |

**Single OTBR example:**

```yaml
otbrs:
  - id: study
    name: Study OTBR
    rest_url: http://192.168.1.10:8081
    agent_url: ""
```

**Multi-OTBR example:**

```yaml
otbrs:
  - id: study
    name: Study OTBR
    rest_url: http://192.168.1.10:8081
  - id: lounge
    name: Lounge OTBR
    rest_url: http://192.168.1.20:8081
```

Remote ThreadLens agents are configured through per-OTBR `agent_url` in Core `0.1.2`. There is no separate global agents list in the add-on schema.

### Matter Server websocket

| Field | Description |
|-------|-------------|
| `id` | Unique ID |
| `name` | Display name |
| `websocket_url` | e.g. `ws://192.168.1.10:5580/ws` |
| `variant` | `python` for python-matter-server |

### MQTT Discovery

| Option | Default | Notes |
|--------|---------|-------|
| `enabled` | `true` | Requires HA MQTT integration |
| `host` | `core-mosquitto` | Mosquitto add-on hostname on HAOS |
| `discovery_prefix` | `homeassistant` | HA MQTT discovery root |
| `topic_prefix` | `threadlens` | State topic prefix |
| `per_node_entities` | `true` | Per Matter node sensors |
| `per_trel_service_entities` | `false` | Disabled to avoid entity sprawl |

ThreadLens does not publish passwords, tokens, or network keys to MQTT topics.

### Storage

| Option | Default | Notes |
|--------|---------|-------|
| `sqlite_path` | `/data/threadlens.db` | Persistent add-on data directory |
| `event_retention_days` | `30` | Event retention window |

### Reports

`reports.redact_secrets` defaults to `true`. Core ThreadLens performs redaction. Reports may still include operational metadata (network names, node IDs, health reasons).

### Logging

Core `0.1.2` uses a fixed application log level (`info`). The add-on does not expose a separate logging option until Core supports it.

## API URLs

Replace `<ha-host>` with your Home Assistant hostname or IP.

| URL | Description |
|-----|-------------|
| `http://<ha-host>:8128/api/v1/health` | Structured health |
| `http://<ha-host>:8128/api/v1/status` | Collector status |
| `http://<ha-host>:8128/api/v1/report.yaml` | Diagnostic report (YAML) |
| `http://<ha-host>:8128/api/v1/report.json` | Diagnostic report (JSON) |
| `http://<ha-host>:8129/api/v1/agent/health` | Agent health (when mode is `agent` or `both`) |

Report examples:

```bash
curl http://homeassistant.local:8128/api/v1/report.yaml
curl -H "Accept: application/json" http://homeassistant.local:8128/api/v1/report
curl "http://homeassistant.local:8128/api/v1/report.yaml?window=7d&focus_node=24"
```

Supported windows: `24h`, `7d`. Optional `focus_node` and `focus_device` query parameters prioritise related events.

## Expected warnings

These informational warnings can appear on healthy networks:

- `otbr_rest_endpoint_mismatch` — OTBR REST and agent endpoints disagree; verify URLs
- `foreign_trel_services_observed` — TREL services from outside your configured site scope

## Security

- **No authentication in v1** — trusted LAN only
- Do not expose ports 8128/8129 publicly without a reverse proxy and auth
- MQTT credentials are used only for broker connection and are not written to logs or reports
- No SSH, Docker socket, or mutating Thread/Matter operations

## Troubleshooting

### No mDNS/TREL services

- Confirm `mdns.enabled` is true
- Confirm host networking is enabled (default)
- If OTBR/Matter work but mDNS is empty, suspect multicast visibility — not absent TREL on the LAN

### OTBR unreachable

- Verify `rest_url` from the HA host: `curl http://<otbr-ip>:8081/api/node`
- Check firewall and VLAN routing

### Matter Server disconnected

- Verify websocket URL and that python-matter-server is running
- Check `collectors.matter` in `/api/v1/status`

### MQTT entities not appearing

- Enable MQTT integration in Home Assistant
- Confirm Mosquitto is running and `mqtt.host` is correct
- Check add-on logs and `/api/v1/status` → `collectors.mqtt`

### HACS dashboard empty

- Confirm the HACS integration points at `http://<ha-host>:8128`
- Restart Home Assistant after changing the integration URL
- Hard-refresh the ThreadLens sidebar panel

## Core project

https://github.com/theaussiepom/threadlens

## Support

Open issues in the add-on repository for packaging problems. Collector behaviour is owned by the core ThreadLens project.
