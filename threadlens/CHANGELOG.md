# Changelog

## 0.2.0

- Expose ThreadLens Core dashboard through Home Assistant Ingress (`ingress_port: 8128`)
- Add sidebar panel metadata (`panel_icon`, `panel_title`)
- Update Core image pin to `ghcr.io/theaussiepom/threadlens:0.2.0` (dashboard UI + `/api/v1/dashboard`)
- Keep `host_network: true` for mDNS/TREL multicast observation
- Keep LAN API ports `8128`/`8129` for direct access and HACS integration compatibility
- Enhanced startup logs (dashboard/Ingress summary, no secrets)
- Ingress and dashboard validation checklist updates

**Requires Core `0.2.0` on GHCR** — see repository README and LIVE_HAOS_VALIDATION.md.

## 0.1.0

- First production HAOS add-on release
- Wraps `ghcr.io/theaussiepom/threadlens:0.1.2` (no duplicated collectors)
- Default mode `both` with host networking for mDNS/TREL
- Add-on options mapped to `/data/config.yaml` at startup with validation
- Startup summary logs without printing secrets
- MQTT Discovery defaults to `core-mosquitto`
- Documentation, CI, and live HAOS validation checklist
