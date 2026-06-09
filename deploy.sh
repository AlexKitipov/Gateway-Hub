#!/bin/bash
# deploy.sh - Non-interactive, idempotent VPS deployment script for Gateway Hub.

set -euo pipefail

APP_USER="${APP_USER:-appuser}"
APP_DIR="${APP_DIR:-/home/${APP_USER}/backend}"
REPO_URL="${REPO_URL:-https://github.com/AlexKitipov/Gateway-Hub.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"
ENV_DIR="${ENV_DIR:-/etc/gateway-hub}"
ENV_FILE="${ENV_FILE:-${ENV_DIR}/gateway-hub.env}"
SERVICE_NAME="${SERVICE_NAME:-gateway-hub}"
RUN_APT_UPGRADE="${RUN_APT_UPGRADE:-false}"
ENABLE_SSL="${ENABLE_SSL:-false}"
DOMAIN="${DOMAIN:-}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"

log() {
    echo "[$(date --iso-8601=seconds)] $*"
}

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "This script must be run as root (for example: sudo $0)." >&2
        exit 1
    fi
}

validate_configuration() {
    if [[ ! "${APP_USER}" =~ ^[a-z_][a-z0-9_]*$ ]]; then
        echo "APP_USER must be a lowercase PostgreSQL-safe identifier: ${APP_USER}" >&2
        exit 1
    fi
}

install_packages() {
    log "Updating package metadata..."
    apt-get update

    if [ "${RUN_APT_UPGRADE}" = "true" ]; then
        log "Upgrading installed packages because RUN_APT_UPGRADE=true..."
        DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
    fi

    log "Installing required packages..."
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-contrib \
        nginx \
        git \
        redis-server \
        certbot \
        python3-certbot-nginx \
        openssl
}

ensure_app_user() {
    if id "${APP_USER}" >/dev/null 2>&1; then
        log "User ${APP_USER} already exists."
    else
        log "Creating user ${APP_USER}..."
        useradd -m -s /bin/bash "${APP_USER}"
    fi
}

sync_repository() {
    log "Synchronizing repository ${REPO_URL} (${REPO_BRANCH}) into ${APP_DIR}..."
    install -d -o "${APP_USER}" -g "${APP_USER}" "$(dirname "${APP_DIR}")"

    if [ -d "${APP_DIR}/.git" ]; then
        sudo -u "${APP_USER}" git -C "${APP_DIR}" fetch --prune origin "${REPO_BRANCH}"
        sudo -u "${APP_USER}" git -C "${APP_DIR}" checkout "${REPO_BRANCH}"
        sudo -u "${APP_USER}" git -C "${APP_DIR}" pull --ff-only origin "${REPO_BRANCH}"
    elif [ -e "${APP_DIR}" ]; then
        echo "${APP_DIR} exists but is not a git checkout; refusing to overwrite it." >&2
        exit 1
    else
        sudo -u "${APP_USER}" git clone --branch "${REPO_BRANCH}" "${REPO_URL}" "${APP_DIR}"
    fi
}

install_python_dependencies() {
    log "Creating/updating Python virtual environment..."
    sudo -u "${APP_USER}" python3 -m venv "${APP_DIR}/venv"
    sudo -u "${APP_USER}" "${APP_DIR}/venv/bin/pip" install --upgrade pip
    sudo -u "${APP_USER}" "${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt"
}

configure_database() {
    log "Ensuring PostgreSQL role and database exist..."
    sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${APP_USER}') THEN
        CREATE ROLE ${APP_USER} LOGIN;
    END IF;
END
\$\$;
SELECT 'CREATE DATABASE gateway_hub OWNER ${APP_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gateway_hub')\gexec
ALTER DATABASE gateway_hub OWNER TO ${APP_USER};
SQL
}

ensure_environment_file() {
    log "Ensuring ${ENV_FILE} exists and is protected..."
    install -d -m 0750 -o root -g "${APP_USER}" "${ENV_DIR}"

    if [ ! -f "${ENV_FILE}" ]; then
        local generated_secret
        generated_secret="$(openssl rand -hex 32)"
        cat >"${ENV_FILE}" <<ENVEOF
# Gateway Hub production environment.
# Keep this file root-owned and out of git. Update values for your domain and integrations.
DATABASE_URL=postgresql:///gateway_hub
SECRET_KEY=${generated_secret}
DEBUG=false
ENVIRONMENT=production
ALLOWED_ORIGINS=https://example.com
REDIS_URL=redis://localhost:6379
ENVEOF
        log "Created ${ENV_FILE} with a generated SECRET_KEY. Review ALLOWED_ORIGINS before exposing the service."
    else
        log "Using existing ${ENV_FILE}; no secrets were overwritten."
    fi

    chown root:"${APP_USER}" "${ENV_FILE}"
    chmod 0640 "${ENV_FILE}"
}

run_migrations() {
    log "Running database migrations after environment configuration..."
    sudo -u "${APP_USER}" ENV_FILE="${ENV_FILE}" APP_DIR="${APP_DIR}" bash -lc '
        set -euo pipefail
        set -a
        . "${ENV_FILE}"
        set +a
        cd "${APP_DIR}"
        ./scripts/migrate.sh
    '
}

install_systemd_service() {
    log "Installing systemd service..."
    sed \
        -e "s|User=appuser|User=${APP_USER}|" \
        -e "s|WorkingDirectory=/home/appuser/backend|WorkingDirectory=${APP_DIR}|" \
        -e "s|/home/appuser/backend/venv/bin|${APP_DIR}/venv/bin|g" \
        -e "s|EnvironmentFile=/etc/gateway-hub/gateway-hub.env|EnvironmentFile=${ENV_FILE}|" \
        "${APP_DIR}/gateway-hub.service" >"/etc/systemd/system/${SERVICE_NAME}.service"
    chmod 0644 "/etc/systemd/system/${SERVICE_NAME}.service"
    systemctl daemon-reload
    systemctl enable "${SERVICE_NAME}"
}

configure_nginx() {
    log "Configuring Nginx..."
    install -m 0644 "${APP_DIR}/nginx/gateway-hub.conf" /etc/nginx/sites-available/gateway-hub
    ln -sfn /etc/nginx/sites-available/gateway-hub /etc/nginx/sites-enabled/gateway-hub
    nginx -t
    systemctl restart nginx
}

configure_ssl() {
    if [ "${ENABLE_SSL}" != "true" ]; then
        log "Skipping SSL setup because ENABLE_SSL is not true."
        return
    fi

    if [ -z "${DOMAIN}" ]; then
        echo "ENABLE_SSL=true requires DOMAIN to be set." >&2
        exit 1
    fi

    log "Requesting/renewing Let's Encrypt certificate for ${DOMAIN}..."
    if [ -n "${CERTBOT_EMAIL}" ]; then
        certbot certonly --nginx --non-interactive --agree-tos --email "${CERTBOT_EMAIL}" -d "${DOMAIN}"
    else
        certbot certonly --nginx --non-interactive --agree-tos --register-unsafely-without-email -d "${DOMAIN}"
    fi
}

start_services() {
    log "Starting services..."
    systemctl enable redis-server
    systemctl restart redis-server
    systemctl restart "${SERVICE_NAME}"
}

verify_services() {
    log "Verifying service status..."
    systemctl --no-pager --full status "${SERVICE_NAME}"
    systemctl --no-pager --full status nginx
}

main() {
    require_root
    validate_configuration
    log "Starting Gateway Hub deployment."
    install_packages
    ensure_app_user
    sync_repository
    install_python_dependencies
    configure_database
    ensure_environment_file
    run_migrations
    install_systemd_service
    configure_nginx
    configure_ssl
    start_services
    verify_services
    log "Deployment complete. Environment file: ${ENV_FILE}"
    if [ -n "${DOMAIN}" ]; then
        log "API: https://${DOMAIN}/api/v1"
        log "Health: https://${DOMAIN}/health"
    fi
}

main "$@"
