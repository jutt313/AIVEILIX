#!/bin/zsh
set -euo pipefail

CLI_BIN=""
if command -v valkey-cli >/dev/null 2>&1; then
  CLI_BIN="valkey-cli"
elif command -v redis-cli >/dev/null 2>&1; then
  CLI_BIN="redis-cli"
else
  echo "No valkey-cli or redis-cli binary found." >&2
  exit 1
fi

$CLI_BIN -p 6380 ping
$CLI_BIN -p 6380 set aiveilix:health ok >/dev/null
VALUE="$($CLI_BIN -p 6380 get aiveilix:health)"
echo "health_key=$VALUE"
$CLI_BIN -p 6380 del aiveilix:health >/dev/null
