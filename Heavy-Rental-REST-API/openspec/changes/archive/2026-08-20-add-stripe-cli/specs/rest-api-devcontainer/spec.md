## ADDED Requirements

### Requirement: Stripe CLI in the app image

Both packs MUST install the official Stripe CLI in the `heavy-rental-rest-api` image so the `stripe` binary is on `PATH` for user `vscode`. Packs MUST NOT add a Stripe Compose service or bake Stripe API keys into Compose.

#### Scenario: CLI present

- **GIVEN** either pack is active and the app container is running
- **WHEN** an operator runs `stripe --version` in `heavy-rental-rest-api`
- **THEN** the command succeeds

### Requirement: Webhook listen helper (not Dashboard Run)

Both packs MUST ship `/usr/local/bin/start-stripe-listen.sh` and invoke it from Dev Container `postStartCommand`. Default forward URL MUST be `http://localhost:8080/api/payments/webhook` (overridable with `STRIPE_CLI_FORWARD_TO`). The helper MUST start `stripe listen` only when `STRIPE_API_KEY` or a Stripe CLI login config is present; otherwise it MUST print login instructions and MUST NOT fail container start. Spring Boot Dashboard Run is not required to start `stripe listen`.

#### Scenario: Listen starts when credentials exist

- **GIVEN** `STRIPE_API_KEY` or a Stripe login config file is present in the app container
- **WHEN** `postStartCommand` / `start-stripe-listen.sh` runs
- **THEN** `stripe listen` is running and forwards to the configured webhook URL

#### Scenario: Missing credentials do not fail start

- **GIVEN** no Stripe API key and no login config
- **WHEN** `postStartCommand` runs
- **THEN** the container still starts
- **AND** the operator is told to run `stripe login` then re-run the helper
