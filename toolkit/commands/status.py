"""Status command"""
import argparse
import json
import os
from datetime import datetime

from utils.mysql_client import (
    get_binlog_status, get_binlog_files, get_record_count,
    execute_sql, BINLOG_DIR
)


def format_size(bytes_val):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


def get_mysql_status():
    """Get MySQL server status"""
    try:
        uptime = execute_sql("SHOW STATUS LIKE 'Uptime';", raw=True)
        uptime_val = int(uptime.split('\t')[1]) if uptime else 0

        threads = execute_sql("SHOW STATUS LIKE 'Threads_connected';", raw=True)
        threads_val = int(threads.split('\t')[1]) if threads else 0

        return {
            'running': True,
            'uptime_seconds': uptime_val,
            'uptime_human': f"{uptime_val // 3600}h {(uptime_val % 3600) // 60}m",
            'threads_connected': threads_val
        }
    except Exception as e:
        return {
            'running': False,
            'error': str(e)
        }


def get_disk_usage():
    """Get disk usage for MySQL data directory"""
    total_size = 0
    try:
        for f in os.listdir(BINLOG_DIR):
            path = os.path.join(BINLOG_DIR, f)
            if os.path.isfile(path):
                total_size += os.path.getsize(path)
    except:
        pass
    return total_size


def run(args):
    """Run status check"""
    parser = argparse.ArgumentParser(description='Show system status')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    opts = parser.parse_args(args)

    timestamp = datetime.now().isoformat()

    # Gather all status info
    mysql_status = get_mysql_status()
    binlog_status = get_binlog_status()
    binlog_files = get_binlog_files()
    binlog_total = sum(f['size'] for f in binlog_files)
    disk_usage = get_disk_usage()

    status = {
        'timestamp': timestamp,
        'mysql': mysql_status,
        'binlog': {
            'current_file': binlog_status['file'] if binlog_status else None,
            'position': binlog_status['position'] if binlog_status else None,
            'gtid': binlog_status['gtid'] if binlog_status else None,
            'files_count': len(binlog_files),
            'total_size': binlog_total,
        },
        'tables': {
            'users': get_record_count('users')
        },
        'disk': {
            'mysql_data': disk_usage
        }
    }

    if opts.json:
        print(json.dumps(status, indent=2))
        return

    # Human readable output
    print("=" * 55)
    print("  MySQL Testing Toolkit - Status")
    print("=" * 55)
    print(f"  Timestamp: {timestamp}")
    print("")

    print("  MySQL Server")
    print("  " + "-" * 50)
    if mysql_status['running']:
        print(f"    Status:     Running")
        print(f"    Uptime:     {mysql_status['uptime_human']}")
        print(f"    Threads:    {mysql_status['threads_connected']}")
    else:
        print(f"    Status:     NOT RUNNING")
        print(f"    Error:      {mysql_status.get('error', 'Unknown')}")
    print("")

    print("  Binary Logs")
    print("  " + "-" * 50)
    if binlog_status:
        print(f"    Current:    {binlog_status['file']}")
        print(f"    Position:   {binlog_status['position']}")
        print(f"    GTID:       {binlog_status['gtid']}")
        print(f"    Files:      {len(binlog_files)}")
        print(f"    Total Size: {format_size(binlog_total)}")
    else:
        print("    Status:     Not available")
    print("")

    print("  Data")
    print("  " + "-" * 50)
    print(f"    Users:      {status['tables']['users']} records")
    print(f"    Disk:       {format_size(disk_usage)}")
    print("")
    print("=" * 55)
