# ThreadLens add-on

Files in this directory package ThreadLens Core for Home Assistant OS.

## Layout

```text
threadlens/
  config.yaml          # Add-on metadata, options, schema
  Dockerfile           # Thin wrapper around ghcr.io/theaussiepom/threadlens:0.1.2
  run.sh               # Reads /data/options.json, starts ThreadLens
  config_generator.py  # Maps add-on options → core config.yaml
  apparmor.txt         # AppArmor profile
  DOCS.md              # User-facing add-on documentation (shown in HA UI)
  README.md            # Maintainer notes (this file)
  CHANGELOG.md
  icon.png / logo.png  # Add-on branding
```

## Wrapper behaviour

1. Supervisor writes user options to `/data/options.json`.
2. `run.sh` calls `config_generator.py` to write `/data/config.yaml`.
3. `threadlens --config /data/config.yaml --mode <configured>` runs the **Core** image.

No collector logic lives in this repository.

## Versioning

| Artifact | Value |
|----------|-------|
| Add-on version (`config.yaml`) | `0.1.0` |
| Core image (`Dockerfile` `BUILD_VERSION`) | `0.1.2` |

## Publishing

For local development, leave `image:` commented in `config.yaml` so Supervisor builds from `Dockerfile`.

To publish a pre-built wrapper image:

```text
ghcr.io/theaussiepom/threadlens-ha-addon:0.1.0
```

Uncomment `image:` in `config.yaml` after publishing.

## Manual test on HAOS

See [LIVE_HAOS_VALIDATION.md](../LIVE_HAOS_VALIDATION.md).

## Static validation

From repository root:

```bash
pytest tests/ -q
bash -n threadlens/run.sh
```
