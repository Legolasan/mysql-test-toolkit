# MySQL Testing Toolkit

A Docker image for testing ETL/CDC replication scenarios with MySQL binlog.

## Quick Start

```bash
# Pull and run
docker run -d -p 3306:3306 --name mysql-toolkit arunsunderraj91/mysql-test-toolkit

# Check status
docker exec mysql-toolkit toolkit status

# Connect to MySQL
mysql -h 127.0.0.1 -P 3306 -uroot -prootpassword
```

## Commands

### Status
```bash
docker exec mysql-toolkit toolkit status
docker exec mysql-toolkit toolkit status --json
```

### Generate Data
```bash
# One-shot: insert 100 records
docker exec mysql-toolkit toolkit generate-data --count 100

# Continuous: insert 100 records every 60 seconds
docker exec mysql-toolkit toolkit generate-data --count 100 --interval 60
```

### Monitor Binlog
```bash
# Single check
docker exec mysql-toolkit toolkit monitor

# Continuous monitoring
docker exec mysql-toolkit toolkit monitor --watch

# JSON output
docker exec mysql-toolkit toolkit monitor --json
```

### Corrupt Binlog
```bash
# Truncate at 50%
docker exec mysql-toolkit toolkit corrupt --type truncate

# Inject random bytes
docker exec mysql-toolkit toolkit corrupt --type random-bytes

# Corrupt magic number
docker exec mysql-toolkit toolkit corrupt --type magic-number
```

### Simulate Replication Issues
```bash
# Simulate replica lag
docker exec mysql-toolkit toolkit replicate --scenario lag --duration 60

# Simulate connection disconnect
docker exec mysql-toolkit toolkit replicate --scenario disconnect

# Create GTID gap
docker exec mysql-toolkit toolkit replicate --scenario gtid-gap
```

### Schema Changes (DDL)
```bash
docker exec mysql-toolkit toolkit schema-change --type add-column
docker exec mysql-toolkit toolkit schema-change --type drop-column
docker exec mysql-toolkit toolkit schema-change --type create-table
docker exec mysql-toolkit toolkit schema-change --type drop-table
```

### Restore Binlog
```bash
# List backups
docker exec mysql-toolkit toolkit restore --list

# Restore specific backup
docker exec mysql-toolkit toolkit restore --file mysql-bin.000003.backup

# Restore all backups
docker exec mysql-toolkit toolkit restore --all
```

### Large Transactions
```bash
# Many rows in single transaction (10K rows)
docker exec mysql-toolkit toolkit transaction --type many-rows --rows 10000

# Large data per row (100 rows x 1MB each = 100MB transaction)
docker exec mysql-toolkit toolkit transaction --type large-data --rows 100 --size 1024

# Long-running transaction (held open for 5 minutes)
docker exec mysql-toolkit toolkit transaction --type long-running --duration 300

# Mixed: many rows + large data + held open
docker exec mysql-toolkit toolkit transaction --type mixed --rows 500 --size 100 --duration 120

# Large blob data instead of text
docker exec mysql-toolkit toolkit transaction --type large-data --rows 50 --size 512 --data-type blob
```

### Expose to Internet

#### Option 1: Cloudflare Tunnel (Persistent URL - Recommended)
```bash
# Requires: Cloudflare account + domain added to Cloudflare
# 1. Go to https://one.dash.cloudflare.com/
# 2. Navigate to Networks > Tunnels > Create tunnel
# 3. Configure tunnel to point to tcp://localhost:3306
# 4. Copy the tunnel token

docker exec mysql-toolkit toolkit tunnel --provider cloudflare --token YOUR_TUNNEL_TOKEN

# Your MySQL will be accessible at the hostname you configured
# mysql -h your-hostname.yourdomain.com -P 3306 -uroot -prootpassword
```

#### Option 2: ngrok (Random URL)
```bash
# Get token from: https://dashboard.ngrok.com/get-started/your-authtoken
docker exec mysql-toolkit toolkit tunnel --provider ngrok --authtoken YOUR_NGROK_TOKEN

# Or use legacy expose command
docker exec mysql-toolkit toolkit expose --authtoken YOUR_NGROK_TOKEN
```

#### Tunnel Management
```bash
# Check all tunnel status
docker exec mysql-toolkit toolkit tunnel --status

# Stop all tunnels
docker exec mysql-toolkit toolkit tunnel --stop
```

## Connection Details

| Field | Value |
|-------|-------|
| Host | localhost |
| Port | 3306 |
| User | root |
| Password | rootpassword |
| Database | testdb |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| MYSQL_ROOT_PASSWORD | rootpassword | MySQL root password |
| MYSQL_DATABASE | testdb | Default database |

## Build from Source

```bash
git clone <repo>
cd mysql_test_case
docker build -t arunsunderraj91/mysql-test-toolkit .
```

## License

MIT
