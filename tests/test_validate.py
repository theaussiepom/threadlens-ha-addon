"""Static validation for the ThreadLens Home Assistant add-on repository."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import stat
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
ADDON_DIR = REPO_ROOT / "threadlens"
GENERATOR_PATH = ADDON_DIR / "config_generator.py"
CORE_IMAGE_TAG = "0.1.2"
ADDON_VERSION = "0.1.0"

REQUIRED_ADDON_FILES = [
    "config.yaml",
    "Dockerfile",
    "run.sh",
    "apparmor.txt",
    "README.md",
    "CHANGELOG.md",
    "DOCS.md",
    "icon.png",
    "logo.png",
    "config_generator.py",
]

REQUIRED_REPO_FILES = [
    "repository.yaml",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "LIVE_HAOS_VALIDATION.md",
]

SECRET_PATTERNS = [
    re.compile(r"192\.168\.100\."),
    re.compile(r"\bbennis\b", re.IGNORECASE),
    re.compile(r"\bpironman\b", re.IGNORECASE),
    re.compile(r"mqtt-threadlens", re.IGNORECASE),
    re.compile(r"-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----"),
]


def _load_generator_module():
    spec = importlib.util.spec_from_file_location("config_generator", GENERATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["config_generator"] = module
    spec.loader.exec_module(module)
    return module


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _core_root() -> Path | None:
    env_path = os.environ.get("THREADLENS_CORE_PATH")
    if env_path:
        candidate = Path(env_path)
        if (candidate / "threadlens" / "config.py").exists():
            return candidate
    for candidate in REPO_ROOT.parent.iterdir():
        if (candidate / "threadlens" / "config.py").exists():
            return candidate
    ci_core = REPO_ROOT / "threadlens-core"
    if (ci_core / "threadlens" / "config.py").exists():
        return ci_core
    return None


def test_repository_yaml_has_required_fields() -> None:
    repo = _load_yaml(REPO_ROOT / "repository.yaml")
    assert repo["name"]
    assert repo["url"] == "https://github.com/theaussiepom/threadlens-ha-addon"
    assert repo["maintainer"]


def test_required_repo_files_exist() -> None:
    for name in REQUIRED_REPO_FILES:
        assert (REPO_ROOT / name).exists(), name


def test_required_addon_files_exist() -> None:
    for name in REQUIRED_ADDON_FILES:
        assert (ADDON_DIR / name).exists(), name


def test_addon_config_has_required_metadata() -> None:
    config = _load_yaml(ADDON_DIR / "config.yaml")
    assert config["name"] == "ThreadLens"
    assert config["slug"] == "threadlens"
    assert config["version"] == ADDON_VERSION
    assert config["startup"] == "services"
    assert config["boot"] == "auto"
    assert config["init"] is False
    assert config["host_network"] is True
    assert set(config["arch"]) >= {"aarch64", "amd64", "armv7"}
    assert config["options"]["mode"] == "both"
    assert config["options"]["otbrs"] == []
    assert config["options"]["matter_servers"] == []
    assert "schema" in config
    assert config["ports"]["8128/tcp"] == 8128
    assert config["ports"]["8129/tcp"] == 8129


def test_addon_schema_includes_expected_keys() -> None:
    config = _load_yaml(ADDON_DIR / "config.yaml")
    schema = config["schema"]
    for key in (
        "site_name",
        "mode",
        "server",
        "agent",
        "storage",
        "mqtt",
        "mdns",
        "otbrs",
        "matter_servers",
        "reports",
        "homeassistant",
    ):
        assert key in schema


def test_run_sh_is_executable() -> None:
    mode = ADDON_DIR / "run.sh"
    assert mode.exists()
    assert os.access(mode, os.X_OK) or bool(mode.stat().st_mode & stat.S_IXUSR)


def test_dockerfile_wraps_core_image() -> None:
    content = (ADDON_DIR / "Dockerfile").read_text(encoding="utf-8")
    assert "ghcr.io/theaussiepom/threadlens" in content
    assert f"BUILD_VERSION={CORE_IMAGE_TAG}" in content
    assert "run.sh" in content
    assert "config_generator.py" in content


def test_generator_declares_core_image_tag() -> None:
    generator = _load_generator_module()
    assert generator.CORE_IMAGE_TAG == CORE_IMAGE_TAG


def test_config_generator_defaults_are_safe() -> None:
    generator = _load_generator_module()
    config = generator.build_threadlens_config(
        {
            "site_name": "Home",
            "mode": "both",
            "server": {"port": 8128},
            "agent": {"port": 8129},
            "storage": {"sqlite_path": "/data/threadlens.db", "event_retention_days": 30},
            "mqtt": {
                "enabled": True,
                "host": "core-mosquitto",
                "port": 1883,
                "username": "",
                "password": "",
                "discovery_prefix": "homeassistant",
                "topic_prefix": "threadlens",
                "retain_discovery": True,
                "retain_state": True,
                "per_trel_service_entities": False,
                "per_node_entities": True,
                "publish_interval_seconds": 30,
            },
            "mdns": {"enabled": True},
            "otbrs": [],
            "matter_servers": [],
            "reports": {"redact_secrets": True},
            "homeassistant": {"mqtt_discovery_enabled": True},
        }
    )
    assert config["mode"] == "both"
    assert config["otbrs"] == []
    assert config["matter_servers"] == []
    assert config["mqtt"]["password"] is None
    assert config["reports"]["redact_secrets"] is True
    assert config["storage"]["sqlite_path"] == "/data/threadlens.db"
    assert config["homeassistant"]["mqtt_discovery_enabled"] is True


def test_config_generator_maps_example_entries() -> None:
    generator = _load_generator_module()
    config = generator.build_threadlens_config(
        {
            "site_name": "Lab",
            "mode": "server",
            "server": {"port": 8128},
            "agent": {"port": 8129},
            "storage": {"event_retention_days": 14},
            "mqtt": {"enabled": False, "host": "mqtt", "port": 1883},
            "mdns": {"enabled": True},
            "otbrs": [
                {
                    "id": "study",
                    "name": "Study OTBR",
                    "rest_url": "http://192.168.1.10:8081",
                    "agent_url": "",
                }
            ],
            "matter_servers": [
                {
                    "id": "study_matter",
                    "name": "Study Matter Server",
                    "websocket_url": "ws://192.168.1.10:5580/ws",
                    "variant": "python",
                }
            ],
            "reports": {"redact_secrets": True},
            "homeassistant": {"mqtt_discovery_enabled": True},
        }
    )
    assert config["site"]["name"] == "Lab"
    assert config["otbrs"][0]["agent_url"] is None
    assert config["matter_servers"][0]["variant"] == "python"


def test_config_generator_rejects_invalid_mode() -> None:
    generator = _load_generator_module()
    try:
        generator.build_threadlens_config({"mode": "invalid"})
    except generator.ConfigGenerationError:
        return
    raise AssertionError("expected ConfigGenerationError")


def test_generated_config_validates_against_core_schema(tmp_path: Path) -> None:
    generator = _load_generator_module()
    options_path = tmp_path / "options.json"
    output_path = tmp_path / "config.yaml"
    options_path.write_text(
        json.dumps(
            {
                "site_name": "Home",
                "mode": "both",
                "server": {"port": 8128},
                "agent": {"port": 8129},
                "storage": {"sqlite_path": "/data/threadlens.db", "event_retention_days": 30},
                "mqtt": {
                    "enabled": True,
                    "host": "core-mosquitto",
                    "port": 1883,
                    "username": "",
                    "password": "secret-should-not-log",
                    "discovery_prefix": "homeassistant",
                    "topic_prefix": "threadlens",
                    "retain_discovery": True,
                    "retain_state": True,
                    "per_trel_service_entities": False,
                    "per_node_entities": True,
                    "publish_interval_seconds": 30,
                },
                "mdns": {"enabled": True},
                "otbrs": [],
                "matter_servers": [],
                "reports": {"redact_secrets": True},
                "homeassistant": {"mqtt_discovery_enabled": True},
            }
        ),
        encoding="utf-8",
    )
    generator.write_config(options_path, output_path)

    core_root = _core_root()
    if core_root is None:
        import pytest

        pytest.skip("ThreadLens core repository not available for schema validation")
    sys.path.insert(0, str(core_root))
    from threadlens.config import ThreadLensConfig

    loaded = ThreadLensConfig.model_validate(
        yaml.safe_load(output_path.read_text(encoding="utf-8"))
    )
    assert loaded.mode.value == "both"
    assert loaded.mqtt.host == "core-mosquitto"


def test_no_private_values_committed() -> None:
    skip_dirs = {".git", ".venv", ".pytest_cache", "threadlens-core", "tests"}
    hits: list[str] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix in {".png", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                hits.append(f"{path.relative_to(REPO_ROOT)}:{match.group(0)}")
    assert not hits, "private or sensitive values found:\n" + "\n".join(hits)
