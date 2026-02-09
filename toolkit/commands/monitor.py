"""Binlog monitoring command"""
import argparse
import time
import json
import os
from datetime import datetime

from utils.mysql_client import get_binlog_status, get_binlog_files, get_record_count


def format_size(bytes_val):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


def get_status_dict():
    """Get all status info as dictionary"""
    status = get_binlog_status()
    files = get_binlog_files()
    total_size = sum(f['size'] for f in files)

    return {
        'timestamp': datetime.now().isoformat(),
        'binlog': {
            'current_file': status['file'] if status else None,
            'position': status['position'] if status else None,
            'gtid': status['gtid'] if status else None,
        },
        'files': files,
        'total_size': total_size,
        'total_size_human': format_size(total_size),
        'records': {
            'users': get_record_count('users')
        }
    }


def print_status(data, clear=False):
    """Print status in human-readable format"""
    if clear:
        os.system('clear' if os.name == 'posix' else 'cls')

    print("=" * 50)
    print("MySQL Binlog Monitor")
    print("=" * 50)
    print(f"Timestamp:      {data['timestamp']}")
    print("-" * 50)
    print(f"Current File:   {data['binlog']['current_file']}")
    print(f"Position:       {data['binlog']['position']}")
    print(f"Total Size:     {data['total_size_human']}")
    print(f"GTID:           {data['binlog']['gtid']}")
    print("-" * 50)
    print(f"Table Records:  {data['records']['users']}")
    print("")
    print("Binlog Files:")
    for f in data['files']:
        print(f"  {f['name']:20s} {format_size(f['size']):>10s}")


def run(args):
    """Run monitoring"""
    parser = argparse.ArgumentParser(description='Monitor binlog status')
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring')
    parser.add_argument('--interval', type=int, default=2, help='Refresh interval (seconds)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    opts = parser.parse_args(args)

    try:
        while True:
            data = get_status_dict()

            if opts.json:
                print(json.dumps(data, indent=2))
            else:
                print_status(data, clear=opts.watch)

            if not opts.watch:
                break

            time.sleep(opts.interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
