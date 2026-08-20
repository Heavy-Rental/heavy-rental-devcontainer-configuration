#!/usr/bin/env bash
# Start `stripe listen` in the REST API app container when credentials exist.
#
# Spring Boot Dashboard has no hook to run extra processes when you click Run.
# This script is the pack substitute: Dev Container postStartCommand (and
# manual re-run after `stripe login`).
set -euo pipefail

FORWARD_TO="${STRIPE_CLI_FORWARD_TO:-http://localhost:8080/api/payments/webhook}"
LOG="${STRIPE_CLI_LISTEN_LOG:-/tmp/stripe-listen.log}"
PIDFILE="${STRIPE_CLI_LISTEN_PIDFILE:-/tmp/stripe-listen.pid}"

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "stripe listen already running (pid $(cat "$PIDFILE")) → ${FORWARD_TO}"
  exit 0
fi

has_creds=false
if [[ -n "${STRIPE_API_KEY:-}" ]]; then
  has_creds=true
fi
# Device login writes config under the vscode home directory.
if [[ -f "${HOME}/.config/stripe/config.toml" ]] || [[ -f "${HOME}/.stripe/config.toml" ]]; then
  has_creds=true
fi

if [[ "$has_creds" != true ]]; then
  echo "Stripe CLI is installed (stripe --version) but not logged in."
  echo "Spring Boot Dashboard Run does not start stripe listen."
  echo "Once per rebuild, in the app container terminal:"
  echo "  stripe login"
  echo "  /usr/local/bin/start-stripe-listen.sh"
  echo "Or set STRIPE_API_KEY (test key) in the environment and reopen the container."
  echo "Forward target: ${FORWARD_TO}"
  exit 0
fi

nohup stripe listen --forward-to "${FORWARD_TO}" >>"${LOG}" 2>&1 &
echo $! >"$PIDFILE"
echo "stripe listen started (pid $(cat "$PIDFILE")) → ${FORWARD_TO}"
echo "Log: ${LOG}"
