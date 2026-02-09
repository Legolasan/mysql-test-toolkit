#!/bin/bash
set -e

# Create backup directory (outside MySQL data dir)
mkdir -p /opt/backups

# Start MySQL in background using the original entrypoint
docker-entrypoint.sh mysqld &

# Wait for MySQL to be ready
echo "Waiting for MySQL to start..."
until mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} --silent 2>/dev/null; do
    sleep 1
done
echo "MySQL is ready!"

# Keep container running
wait
