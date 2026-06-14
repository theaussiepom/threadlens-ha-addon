"""Translate Home Assistant add-on options into ThreadLens Core config."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

CORE_IMAGE_TAG = "0.2.0"

DEFAULT_MDNS_SERVICES = [
    "_trel._udp.local.",
    "_meshcop._udp.local.",
    "_matter._tcp.local.",
    "_matterc._udp.local.",
]


class ConfigGenerationError(ValueError):
    """Raised when add-on options cannot be mapped to a valid Core config."""


def _null_if_empty(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _validate_mode(mode: Any) -> str:
    if mode not in {"server", "agent", "both"}:
        raise ConfigGenerationError(f"Invalid mode: {mode!r} (expected server, agent, or both)")
    return mode


def _validate_otbr(entry: dict[str, Any], index: int) -> dict[str, Any]:
    for field in ("id", "name", "rest_url"):
        if not str(entry.get(field, "")).strip():
            raise ConfigGenerationError(f"otbrs[{index}] requires non-empty {field}")
    return {
        "id": str(entry["id"]).strip(),
        "name": str(entry["name"]).strip(),
        "rest_url": str(entry["rest_url"]).strip(),
        "agent_url": _null_if_empty(entry.get("agent_url")),
    }


def _validate_matter_server(entry: dict[str, Any], index: int) -> dict[str, Any]:
    for field in ("id", "name", "websocket_url"):
        if not str(entry.get(field, "")).strip():
            raise ConfigGenerationError(
                f"matter_servers[{index}] requires non-empty {field}"
            )
    variant = entry.get("variant", "python")
    if variant not in {"python", "unknown"}:
        raise ConfigGenerationError(
            f"matter_servers[{index}] variant must be python or unknown"
        )
    return {
        "id": str(entry["id"]).strip(),
        "name": str(entry["name"]).strip(),
        "websocket_url": str(entry["websocket_url"]).strip(),
        "variant": variant,
    }


def build_threadlens_config(options: dict[str, Any]) -> dict[str, Any]:
    """Map HA add-on options to the ThreadLens Core config schema."""
    mode = _validate_mode(options.get("mode", "both"))
    mqtt = options.get("mqtt", {})
    storage = options.get("storage", {})
    server = options.get("server", {})
    agent = options.get("agent", {})
    mdns = options.get("mdns", {})
    reports = options.get("reports", {})
    homeassistant = options.get("homeassistant", {})

    otbrs = [_validate_otbr(entry, index) for index, entry in enumerate(options.get("otbrs", []))]
    matter_servers = [
        _validate_matter_server(entry, index)
        for index, entry in enumerate(options.get("matter_servers", []))
    ]

    sqlite_path = storage.get("sqlite_path") or "/data/threadlens.db"

    return {
        "site": {"name": options.get("site_name", "Home")},
        "mode": mode,
        "server": {
            "host": "0.0.0.0",
            "port": server.get("port", 8128),
        },
        "agent": {
            "host": "0.0.0.0",
            "port": agent.get("port", 8129),
        },
        "storage": {
            "sqlite_path": sqlite_path,
            "event_retention_days": storage.get("event_retention_days", 30),
        },
        "flapping": {
            "debounce_seconds": 30,
            "matter_node_availability_warning_24h": 3,
            "matter_node_availability_degraded_24h": 6,
            "matter_node_unavailable_critical_minutes": 30,
            "otbr_role_changes_warning_1h": 2,
            "otbr_role_changes_degraded_1h": 5,
            "mdns_service_flaps_warning_1h": 5,
            "mdns_service_flaps_degraded_1h": 15,
        },
        "otbr": {
            "poll_interval_seconds": 60,
            "request_timeout_seconds": 5,
            "allow_read_only_actions": False,
        },
        "mqtt": {
            "enabled": bool(mqtt.get("enabled", True)),
            "host": mqtt.get("host", "core-mosquitto"),
            "port": mqtt.get("port", 1883),
            "username": _null_if_empty(mqtt.get("username")),
            "password": _null_if_empty(mqtt.get("password")),
            "discovery_prefix": mqtt.get("discovery_prefix", "homeassistant"),
            "topic_prefix": mqtt.get("topic_prefix", "threadlens"),
            "retain_discovery": bool(mqtt.get("retain_discovery", True)),
            "retain_state": bool(mqtt.get("retain_state", True)),
            "publish_interval_seconds": mqtt.get("publish_interval_seconds", 30),
            "per_trel_service_entities": bool(mqtt.get("per_trel_service_entities", False)),
            "per_node_entities": bool(mqtt.get("per_node_entities", True)),
        },
        "mdns": {
            "enabled": bool(mdns.get("enabled", True)),
            "services": DEFAULT_MDNS_SERVICES,
        },
        "matter": {
            "reconnect_initial_seconds": 5,
            "reconnect_max_seconds": 60,
            "request_timeout_seconds": 10,
        },
        "otbrs": otbrs,
        "matter_servers": matter_servers,
        "reports": {
            "redact_secrets": bool(reports.get("redact_secrets", True)),
        },
        "homeassistant": {
            "mqtt_discovery_enabled": bool(
                homeassistant.get("mqtt_discovery_enabled", True)
            ),
        },
    }


def write_config(options_path: Path, output_path: Path) -> dict[str, Any]:
    try:
        options = json.loads(options_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigGenerationError(f"Invalid options JSON: {options_path}") from exc
    if not isinstance(options, dict):
        raise ConfigGenerationError("Add-on options must be a JSON object")
    config = build_threadlens_config(options)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(config, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return config


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: config_generator.py <options.json> <config.yaml>")
    try:
        write_config(Path(sys.argv[1]), Path(sys.argv[2]))
    except ConfigGenerationError as exc:
        print(f"ThreadLens add-on config error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
