# Security Policy

## Supported versions

| Add-on version | Supported |
|----------------|-----------|
| 0.1.x          | Yes       |

## Reporting a vulnerability

Please report security issues privately:

1. Open a **private** security advisory on GitHub if you have access, or
2. Email the maintainer listed in `repository.yaml`.

Do not open public issues for undisclosed vulnerabilities.

## Scope

This repository covers the **Home Assistant OS add-on packaging** for ThreadLens Core.

- Collector behaviour, API semantics, and report redaction are owned by [ThreadLens Core](https://github.com/theaussiepom/threadlens).
- The HACS dashboard integration is owned by [threadlens-ha-integration](https://github.com/theaussiepom/threadlens-ha-integration).

## Security model (v1)

ThreadLens v1 is **read-only** and intended for trusted LAN use.

- No API authentication on ports `8128` / `8129`
- No Docker socket access
- No SSH access
- No host log scraping
- No mutating Thread, OTBR, Matter, commissioning, or Home Assistant operations

MQTT credentials are accepted through add-on options and passed to Core. They must not be committed to this repository.

Reports may include operational metadata even when `reports.redact_secrets` is enabled.

## Recommendations

- Do not expose ThreadLens API ports to the public internet without a reverse proxy and authentication.
- Keep OTBR and Matter Server endpoints on trusted networks.
- Use strong MQTT broker credentials and restrict broker access to your LAN.
