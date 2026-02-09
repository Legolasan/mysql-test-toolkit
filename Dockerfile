# MySQL Testing Toolkit
# Image: arunsunderraj91/mysql-test-toolkit

FROM mysql:8.0

LABEL maintainer="arunsunderraj91"
LABEL description="MySQL Testing Toolkit for ETL/CDC testing"
LABEL version="1.0.0"

# Install Python
RUN microdnf install -y python3 python3-pip && \
    microdnf clean all

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
