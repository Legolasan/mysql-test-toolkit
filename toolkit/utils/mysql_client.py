"""MySQL connection helper"""
import subprocess
import os

MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD', 'rootpassword')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'testdb')
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
BINLOG_DIR = '/var/lib/mysql'


def execute_sql(sql, database=None, raw=False):
    """Execute SQL and return output

    Uses stdin for large queries to avoid 'Argument list too long' errors.
    """
    db = database or MYSQL_DATABASE
    cmd = [
        'mysql',
        f'-u{MYSQL_USER}',
        f'-p{MYSQL_PASSWORD}',
        '-h', MYSQL_HOST,
        db,
    ]
    if raw:
        cmd.append('-N')  # No headers

    # Use stdin for SQL to handle large queries
    result = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"MySQL error: {result.stderr}")
    return result.stdout.strip()


def get_binlog_status():
    """Get current binlog file and position"""
    output = execute_sql("SHOW MASTER STATUS;", raw=True)
    if output:
        parts = output.split('\t')
        return {
            'file': parts[0],
            'position': int(parts[1]),
            'gtid': parts[4] if len(parts) > 4 else ''
        }
    return None


def get_binlog_files():
    """Get list of all binlog files"""
    output = execute_sql("SHOW BINARY LOGS;", raw=True)
    files = []
    for line in output.split('\n'):
        if line:
            parts = line.split('\t')
            files.append({
                'name': parts[0],
                'size': int(parts[1]),
                'encrypted': parts[2] if len(parts) > 2 else 'No'
            })
    return files


def get_record_count(table='users'):
    """Get record count from table"""
    output = execute_sql(f"SELECT COUNT(*) FROM {table};", raw=True)
    return int(output) if output else 0


def get_current_binlog_path():
    """Get full path to current binlog file"""
    status = get_binlog_status()
    if status:
        return f"{BINLOG_DIR}/{status['file']}"
    return None


def flush_binary_logs():
    """Force creation of new binlog file"""
    execute_sql("FLUSH BINARY LOGS;")
