"""Restore command"""
import argparse
import os
import shutil
import glob

from utils.mysql_client import BINLOG_DIR, flush_binary_logs

BACKUP_DIR = '/opt/backups'


def list_backups():
    """List available backups"""
    if not os.path.exists(BACKUP_DIR):
        return []

    backups = glob.glob(f"{BACKUP_DIR}/*.backup")
    return sorted(backups)


def restore_binlog(backup_path, target_path):
    """Restore a binlog from backup"""
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    shutil.copy2(backup_path, target_path)
    print(f"Restored: {backup_path} -> {target_path}")


def run(args):
    """Run restore"""
    parser = argparse.ArgumentParser(description='Restore binlog from backup')
    parser.add_argument('--file', help='Specific backup file to restore')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--all', action='store_true', help='Restore all backups')
    parser.add_argument('--flush', action='store_true',
                        help='Flush to new binlog after restore')
    opts = parser.parse_args(args)

    backups = list_backups()

    if opts.list or (not opts.file and not opts.all):
        print("Available backups:")
        print("-" * 40)
        if not backups:
            print("  No backups found")
            print("  Backups are created automatically when using 'toolkit corrupt'")
        else:
            for b in backups:
                size = os.path.getsize(b)
                print(f"  {os.path.basename(b):30s} {size:>10d} bytes")
        return

    if opts.all:
        if not backups:
            print("No backups to restore")
            return

        print(f"Restoring {len(backups)} backup(s)...")
        for backup in backups:
            filename = os.path.basename(backup).replace('.backup', '')
            target = f"{BINLOG_DIR}/{filename}"
            restore_binlog(backup, target)

    elif opts.file:
        # Find the backup
        backup_path = None
        for b in backups:
            if opts.file in b:
                backup_path = b
                break

        if not backup_path:
            # Try direct path
            if os.path.exists(opts.file):
                backup_path = opts.file
            else:
                backup_path = f"{BACKUP_DIR}/{opts.file}"

        if not os.path.exists(backup_path):
            print(f"Backup not found: {opts.file}")
            print("Use --list to see available backups")
            return

        filename = os.path.basename(backup_path).replace('.backup', '')
        target = f"{BINLOG_DIR}/{filename}"
        restore_binlog(backup_path, target)

    if opts.flush:
        print("Flushing binary logs...")
        flush_binary_logs()
        print("New binlog file created")

    print("-" * 40)
    print("Restore complete!")
