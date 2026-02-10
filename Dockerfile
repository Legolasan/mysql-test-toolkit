# MySQL Testing Toolkit
# Image: arunsunderraj91/mysql-test-toolkit

FROM mysql:8.0

LABEL maintainer="arunsunderraj91"
LABEL description="MySQL Testing Toolkit for ETL/CDC testing"
LABEL version="1.0.0"

# Install Python and dependencies
RUN microdnf install -y python3 python3-pip curl unzip && \
    microdnf clean all

# Install network tools for simulation (iptables, tc, procps)
RUN microdnf install -y iptables iproute-tc procps-ng && \
    microdnf clean all

# Install ngrok (auto-detect architecture)
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then NGROK_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then NGROK_ARCH="arm64"; \
    else NGROK_ARCH="amd64"; fi && \
    curl -sLo /tmp/ngrok.tgz "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-${NGROK_ARCH}.tgz" && \
    tar -xzf /tmp/ngrok.tgz -C /usr/local/bin && \
    rm /tmp/ngrok.tgz && \
    chmod +x /usr/local/bin/ngrok

# Install cloudflared (auto-detect architecture)
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then CF_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then CF_ARCH="arm64"; \
    else CF_ARCH="amd64"; fi && \
    curl -sLo /usr/local/bin/cloudflared "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${CF_ARCH}" && \
    chmod +x /usr/local/bin/cloudflared

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=testdb
ENV PYTHONUNBUFFERED=1

# Copy MySQL configuration
COPY config/my.cnf /etc/mysql/conf.d/toolkit.cnf

# Copy initialization SQL
COPY init/init.sql /docker-entrypoint-initdb.d/

# Copy toolkit
COPY toolkit/ /opt/toolkit/
RUN chmod +x /opt/toolkit/toolkit.py

# Create symlink for easy access
RUN ln -s /opt/toolkit/toolkit.py /usr/local/bin/toolkit

# Copy custom entrypoint
COPY docker-entrypoint.sh /opt/docker-entrypoint.sh
RUN chmod +x /opt/docker-entrypoint.sh

# Expose MySQL port
EXPOSE 3306

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} --silent || exit 1

# Use custom entrypoint
ENTRYPOINT ["/opt/docker-entrypoint.sh"]
