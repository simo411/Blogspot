#!/usr/bin/env bash
# End-to-end check of a running stack, through the web container like a browser would.
#   ./scripts/smoke-test.sh                         # compose  (http://localhost:8080)
#   ./scripts/smoke-test.sh http://localhost:30080  # kind
set -euo pipefail

BASE="${1:-http://localhost:8080}"
TIMEOUT="${SMOKE_TIMEOUT:-180}"
RUN="$(date +%s)$RANDOM"
JSON='Content-Type: application/json'

json() { python3 -c "import sys,json; print(json.load(sys.stdin)$1)"; }
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; exit 1; }
expect_code() { # expect_code <want> <description> <curl args...>
  local want=$1 desc=$2; shift 2
  local got; got=$(curl -s -o /dev/null -w '%{http_code}' "$@")
  [[ "$got" == "$want" ]] && pass "$desc ($got)" || fail "$desc: expected $want, got $got"
}

echo "Waiting for $BASE to be ready (max ${TIMEOUT}s)..."
deadline=$((SECONDS + TIMEOUT))
until curl -sf "$BASE/api/blogs" >/dev/null 2>&1; do
  (( SECONDS > deadline )) && fail "stack not ready after ${TIMEOUT}s"
  sleep 3
done

echo "Smoke testing $BASE"
expect_code 200 "web serves the React app"           "$BASE/"
expect_code 200 "SPA deep link falls back to index"   "$BASE/blogs/1"
expect_code 200 "API docs reachable through proxy"    "$BASE/api/docs"

A="alice$RUN"; B="bob$RUN"
for u in "$A" "$B"; do
  expect_code 201 "register $u" -X POST "$BASE/api/auth/register" -H "$JSON" \
    -d "{\"name\":\"$u\",\"username\":\"$u\",\"email\":\"$u@example.com\",\"password\":\"password123\"}"
done
expect_code 401 "wrong password rejected" -X POST "$BASE/api/auth/login" -H "$JSON" \
  -d "{\"username\":\"$A\",\"password\":\"wrong-password\"}"

login() { curl -sf -X POST "$BASE/api/auth/login" -H "$JSON" \
  -d "{\"username\":\"$1\",\"password\":\"password123\"}" | json "['access_token']"; }
TA=$(login "$A"); TB=$(login "$B"); pass "login returns JWTs"

expect_code 401 "create blog without token rejected" -X POST "$BASE/api/blogs" -H "$JSON" -d '{"title":"x","body":"y"}'
ID=$(curl -sf -X POST "$BASE/api/blogs" -H "$JSON" -H "Authorization: Bearer $TA" \
  -d "{\"title\":\"Smoke $RUN\",\"body\":\"hello\"}" | json "['id']")
pass "create blog (id $ID)"

AUTHOR=$(curl -sf "$BASE/api/blogs/$ID" | json "['author']['username']")
[[ "$AUTHOR" == "$A" ]] && pass "author taken from token" || fail "author was $AUTHOR"

expect_code 403 "other user cannot delete" -X DELETE "$BASE/api/blogs/$ID" -H "Authorization: Bearer $TB"
expect_code 204 "author can delete"        -X DELETE "$BASE/api/blogs/$ID" -H "Authorization: Bearer $TA"
expect_code 404 "deleted blog is gone"     "$BASE/api/blogs/$ID"

echo "All smoke tests passed."
