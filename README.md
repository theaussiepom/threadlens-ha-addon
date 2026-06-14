# ThreadLens Home Assistant Add-on

Home Assistant OS add-on packaging for [ThreadLens Core](https://github.com/theaussiepom/threadlens).

This repository does **not** duplicate ThreadLens collector logic. The add-on runs the published Core image `ghcr.io/theaussiepom/threadlens:0.2.0` with a thin wrapper that translates Supervisor options into ThreadLens `config.yaml`.

## Related projects

| Project | Purpose |
|---------|---------|
| [ThreadLens Core](https://github.com/theaussiepom/threadlens) | Collector application, REST API, and Core-served dashboard |
| [ThreadLens HACS integration](https://github.com/theaussiepom/threadlens-ha-integration) | Optional HA entities and sidebar dashboard (migration to launcher layer planned) |

## Target install path (HAOS users)

```text
Add ThreadLens add-on repository
Install ThreadLens add-on
Configure OTBR / Matter / MQTT options in the add-on UI
Start the add-on
Open ThreadLens dashboard from the add-on page (Ingress)
Optional: install ThreadLens HACS integration for entities / LAN API convenience
```

Container/power users can continue running ThreadLens Core directly with Docker/Compose from the Core repository.

## Add the repository

1. Open **Settings → Add-ons → Add-on store**.
2. Open the **⋮** menu → **Repositories**.
3. Add:

   ```text
   https://github.com/theaussiepom/threadlens-ha-addon
   ```

4. Refresh the add-on store.

## Install

1. Find **ThreadLens** in the add-on store.
2. Click **Install**.
3. Configure options (see `threadlens/DOCS.md`).
4. Start the add-on.
5. Click **Open Web UI** on the add-on page to open the Core-served ThreadLens dashboard through Home Assistant Ingress.

## Versions

| Component | Version |
|-----------|---------|
| Add-on | `0.2.0` |
| ThreadLens Core image | `ghcr.io/theaussiepom/threadlens:0.2.0` |

**Dependency:** Core `0.2.0` must be published on GHCR before this add-on can run in production. The add-on pins that image tag; it does not bundle dashboard assets.

## Default runtime

| Setting | Default |
|---------|---------|
| Mode | `both` (server API + agent API) |
| Host networking | `true` (recommended for mDNS/TREL multicast) |
| Ingress | `true` → Core dashboard on port `8128` |
| Server API | `http://<ha-host>:8128` (LAN) or Ingress Web UI |
| Agent API | `http://<ha-host>:8129` |
| Database | `/data/threadlens.db` (persistent add-on data) |

With host networking, the add-on shares the Home Assistant host network stack. LAN API URLs use your HA host IP or hostname directly. Port mappings remain exposed for direct LAN access alongside Ingress.

## Configuration

Configure OTBR REST URLs and Matter Server websocket URLs in the add-on **Configuration** tab. Defaults use empty `otbrs` and `matter_servers` arrays for a safe first install.

Example values (adjust for your LAN):

```yaml
otbrs:
  - id: study
    name: Study OTBR
    rest_url: http://192.168.1.10:8081
    agent_url: ""
matter_servers:
  - id: study_matter
    name: Study Matter Server
    websocket_url: ws://192.168.1.10:5580/ws
    variant: python
```

MQTT defaults to the Home Assistant Mosquitto broker hostname `core-mosquitto`. Enable the **MQTT** integration in Home Assistant.

Remote ThreadLens agents are configured per OTBR via optional `agent_url`.

## What this add-on does

- Runs ThreadLens Core read-only collectors
- Serves the **canonical ThreadLens dashboard** through Home Assistant Ingress
- Observes OTBR REST, Matter Server websocket inventory, mDNS/TREL (when host networking permits)
- Optionally publishes Home Assistant MQTT Discovery entities
- Exposes health, status, dashboard payload, and YAML/JSON diagnostic reports

## What this add-on does not do

- Does not mutate Thread datasets, OTBR state, Matter devices, commissioning, Home Assistant, or MQTT broker configuration
- Does not duplicate Core dashboard assets in the add-on image
- Does not use Docker socket, SSH, or host log scraping
- Does not provide API authentication in v1

## Logs

View add-on logs under **Settings → Add-ons → ThreadLens → Log**.

The wrapper prints startup summary lines and does **not** print MQTT passwords or broker secrets.

## API and dashboard access

| Access | URL / action |
|--------|----------------|
| **Ingress dashboard** | Add-on page → **Open Web UI** |
| `/api/v1/dashboard` | Dashboard JSON (relative from Ingress UI) |
| `/api/v1/health` | Structured health (LAN or via Ingress path) |
| `/api/v1/status` | Collector/runtime status |
| `/api/v1/report.yaml` | Diagnostic report (YAML) |
| `/api/v1/report.json` | Diagnostic report (JSON) |

LAN example:

```bash
curl http://homeassistant.local:8128/api/v1/health
curl http://homeassistant.local:8128/api/v1/dashboard
```

The HACS integration can still point at `http://<ha-host>:8128` for entities and its own sidebar panel during the migration period.

## Security

ThreadLens v1 has **no API authentication**. Use only on a trusted LAN. Do not expose ports 8128/8129 to the internet without a reverse proxy and authentication.

Reports redact secrets via Core `reports.redact_secrets` but still include operational metadata.

## Status

Early / pre-1.0. Validate on your HAOS instance using [LIVE_HAOS_VALIDATION.md](LIVE_HAOS_VALIDATION.md) before production use.

## Development / validation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest tests/ -q
bash -n threadlens/run.sh
```

Release checklist: [RELEASE.md](RELEASE.md)

## License

MIT — Copyright (c) 2026 Ben Dennis
