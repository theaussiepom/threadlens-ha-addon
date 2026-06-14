# Changelog

## 0.1.0

- First production HAOS add-on release
- Wraps `ghcr.io/theaussiepom/threadlens:0.1.2` (no duplicated collectors)
- Default mode `both` with host networking for mDNS/TREL
- Add-on options mapped to `/data/config.yaml` at startup with validation
- Startup summary logs without printing secrets
- MQTT Discovery defaults to `core-mosquitto`
- Documentation, CI, and live HAOS validation checklist
