# Contributing

Thank you for contributing to the ThreadLens Home Assistant OS add-on.

## What belongs here

- Add-on packaging (`config.yaml`, `Dockerfile`, `run.sh`, AppArmor)
- Option → Core config translation
- Documentation for HAOS users
- CI and static validation

## What does not belong here

- ThreadLens collector logic — use [ThreadLens Core](https://github.com/theaussiepom/threadlens)
- HACS dashboard / entities — use [threadlens-ha-integration](https://github.com/theaussiepom/threadlens-ha-integration)

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest tests/ -q
bash -n threadlens/run.sh
```

Optional:

```bash
yamllint .
shellcheck threadlens/run.sh
```

## Pull requests

1. Branch from `main` (do not commit directly to `main`).
2. Keep changes focused on add-on packaging.
3. Do not commit secrets, private IPs, hostnames, or credentials.
4. Run `pytest tests/ -q` before opening a PR.
5. Update `threadlens/CHANGELOG.md` for user-visible add-on changes.

## Versioning

- **Add-on version** — `threadlens/config.yaml` `version` field (e.g. `0.1.0`)
- **Core image tag** — `threadlens/Dockerfile` `ARG BUILD_VERSION` (e.g. `0.1.2`)

These are intentionally independent. Document both in PRs and releases.

## Live HAOS validation

Packaging changes that affect install or startup should be validated on a real Home Assistant OS instance using [LIVE_HAOS_VALIDATION.md](LIVE_HAOS_VALIDATION.md) before tagging a release.
