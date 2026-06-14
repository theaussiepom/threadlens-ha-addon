#!/usr/bin/env bash
set -euo pipefail

readonly OPTIONS_PATH="/data/options.json"
readonly CONFIG_PATH="/data/config.yaml"

export THREADLENS_CONFIG_PATH="${CONFIG_PATH}"
export PYTHONUNBUFFERED=1

if [[ ! -f "${OPTIONS_PATH}" ]]; then
  echo "ThreadLens add-on error: ${OPTIONS_PATH} not found" >&2
  exit 1
fi

python3 /config_generator.py "${OPTIONS_PATH}" "${CONFIG_PATH}"

MODE="$(python3 -c 'import json; print(json.load(open("/data/options.json"))["mode"])')"

python3 - <<'PY'
import json
from pathlib import Path

options = json.loads(Path("/data/options.json").read_text(encoding="utf-8"))
mode = options.get("mode", "both")
server_port = options.get("server", {}).get("port", 8128)
agent_port = options.get("agent", {}).get("port", 8129)
otbrs = options.get("otbrs") or []
matter_servers = options.get("matter_servers") or []
mqtt = options.get("mqtt") or {}
mdns = options.get("mdns") or {}
ha = options.get("homeassistant") or {}

print("ThreadLens add-on starting")
print(f"Mode: {mode}")
print(f"Server port: {server_port}")
print(f"Agent port: {agent_port}")
print(f"Configured OTBRs: {len(otbrs)}")
print(f"Configured Matter servers: {len(matter_servers)}")
print(f"MQTT enabled: {bool(mqtt.get('enabled', True))}")
print(f"Home Assistant Discovery enabled: {bool(ha.get('mqtt_discovery_enabled', True))}")
print(f"mDNS enabled: {bool(mdns.get('enabled', True))}")
if not otbrs and not matter_servers:
    print("Note: no OTBR or Matter Server endpoints configured yet; add them in the add-on Configuration tab")
PY

exec threadlens --config "${CONFIG_PATH}" --mode "${MODE}"
