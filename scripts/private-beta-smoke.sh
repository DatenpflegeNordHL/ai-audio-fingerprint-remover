#!/usr/bin/env sh
set -eu

BASE_URL="${AQH_BASE_URL:-http://127.0.0.1:8017}"
TOKEN="${AQH_WEB_TOKEN:-}"
BETA_PASSWORD="${AQH_BETA_SMOKE_PASSWORD:-}"

if [ -z "$TOKEN" ]; then
  printf '%s\n' "AQH_WEB_TOKEN is required for API smoke checks." >&2
  exit 2
fi

if [ -z "$BETA_PASSWORD" ]; then
  printf '%s\n' "AQH_BETA_SMOKE_PASSWORD is required for dashboard smoke checks." >&2
  exit 2
fi

expect_status() {
  label="$1"
  expected="$2"
  method="$3"
  url="$4"
  shift 4
  status="$(curl -sS -o /dev/null -w '%{http_code}' -X "$method" "$@" "$url")"
  if [ "$status" != "$expected" ]; then
    printf '%s\n' "FAIL $label: expected $expected, got $status" >&2
    exit 1
  fi
  printf '%s\n' "OK $label: $status"
}

expect_status "health" "200" "GET" "$BASE_URL/health"
expect_status "dashboard gate" "401" "GET" "$BASE_URL/"
expect_status "dashboard password" "200" "GET" "$BASE_URL/" -u "beta:$BETA_PASSWORD"
expect_status "api config without token" "401" "GET" "$BASE_URL/api/config"
expect_status "api config with token" "200" "GET" "$BASE_URL/api/config" -H "Authorization: Bearer $TOKEN"
expect_status "cleanup with token" "200" "POST" "$BASE_URL/api/maintenance/cleanup" -H "Authorization: Bearer $TOKEN"

printf '%s\n' "Private beta smoke checks passed."
