FROM mcr.microsoft.com/devcontainers/java:3-21-trixie

ARG INSTALL_MAVEN="true"
ARG MAVEN_VERSION=""

ARG INSTALL_GRADLE="false"
ARG GRADLE_VERSION=""

RUN if [ "${INSTALL_MAVEN}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/sdkman/bin/sdkman-init.sh && sdk install maven \"${MAVEN_VERSION}\""; fi \
    && if [ "${INSTALL_GRADLE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/sdkman/bin/sdkman-init.sh && sdk install gradle \"${GRADLE_VERSION}\""; fi

# Stripe CLI (official Debian repo). Used for local webhook forwarding:
#   stripe listen --forward-to http://localhost:8080/api/payments/webhook
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends ca-certificates curl gnupg \
    && curl -fsSL https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public \
        | gpg --dearmor -o /usr/share/keyrings/stripe.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" \
        > /etc/apt/sources.list.d/stripe.list \
    && apt-get update \
    && apt-get -y install --no-install-recommends stripe \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && stripe --version

COPY scripts/start-stripe-listen.sh /usr/local/bin/start-stripe-listen.sh
RUN chmod 0755 /usr/local/bin/start-stripe-listen.sh

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1
