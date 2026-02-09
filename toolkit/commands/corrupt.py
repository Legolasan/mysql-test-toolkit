"""Binlog corruption command"""
import argparse
import os
import random
import shutil
from datetime import datetime

from utils.mysql_client import get_binlog_status, get_current_binlog_path, BINLOG_DIR

BACKUP_DIR = '/opt/backups'


def ensure_backup_dir():
    """Ensure backup directory exists"""
    os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_binlog(binlog_path):
    """Create backup of binlog file"""
    ensure_backup_dir()
    filename = os.path.basename(binlog_path)
    backup_path = f"{BACKUP_DIR}/{filename}.backup"
    shutil.copy2(binlog_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path


def corrupt_truncate(binlog_path, percentage=50):
    """Truncate binlog file at given percentage"""
    file_size = os.path.getsize(binlog_path)
    truncate_size = int(file_size * percentage / 100)

    with open(binlog_path, 'r+b') as f:
        f.truncate(truncate_size)

    print(f"Truncated {binlog_path}")
    print(f"  Original size: {file_size} bytes")
    print(f"  New size: {truncate_size} bytes ({percentage}%)")


def corrupt_random_bytes(binlog_path, num_corruptions=10):
    """Inject random bytes at random positions"""
    file_size = os.path.getsize(binlog_path)

    # Skip first 100 bytes (header area)
    min_pos = 100
    if file_size <= min_pos:
        print("File too small to corrupt safely")
        return

    with open(binlog_path, 'r+b') as f:
        positions = []
        for _ in range(num_corruptions):
            pos = random.randint(min_pos, file_size - 1)
            f.seek(pos)
            original = f.read(1)
            f.seek(pos)
            # Write random byte (different from original)
            new_byte = bytes([random.randint(0, 255)])
            f.write(new_byte)
            positions.append(pos)

    print(f"Injected {num_corruptions} random bytes at positions:")
    for p in positions:
        print(f"  - {p}")


def corrupt_magic_number(binlog_path):
    """Corrupt the magic number (first 4 bytes)"""
    # MySQL binlog magic number is: 0xfe 0x62 0x69 0x6e (þbin)
    with open(binlog_path, 'r+b') as f:
        original = f.read(4)
        f.seek(0)
        # Write invalid magic number
        f.write(b'\x00\x00\x00\x00')

    print(f"Corrupted magic number in {binlog_path}")
    print(f"  Original: {original.hex()}")
    print(f"  New: 00000000")


def run(args):
    """Run corruption"""
    parser = argparse.ArgumentParser(description='Corrupt binlog for testing')
    parser.add_argument('--type', required=True,
                        choices=['truncate', 'random-bytes', 'magic-number'],
                        help='Type of corruption')
    parser.add_argument('--file', help='Specific binlog file (default: current)')
    parser.add_argument('--percentage', type=int, default=50,
                        help='Truncate percentage (for truncate type)')
    parser.add_argument('--count', type=int, default=10,
                        help='Number of corruptions (for random-bytes type)')
    parser.add_argument('--no-backup', action='store_true',
                        help='Skip creating backup')
    opts = parser.parse_args(args)

    # Get binlog path
    if opts.file:
        binlog_path = f"{BINLOG_DIR}/{opts.file}"
    else:
        binlog_path = get_current_binlog_path()

    if not binlog_path or not os.path.exists(binlog_path):
        print(f"Error: Binlog file not found: {binlog_path}")
        return

    print(f"Target: {binlog_path}")
    print(f"Corruption type: {opts.type}")
    print("-" * 40)

    # Create backup unless disabled
    if not opts.no_backup:
        backup_binlog(binlog_path)

    # Apply corruption
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Applying corruption...")

    if opts.type == 'truncate':
        corrupt_truncate(binlog_path, opts.percentage)
    elif opts.type == 'random-bytes':
        corrupt_random_bytes(binlog_path, opts.count)
    elif opts.type == 'magic-number':
        corrupt_magic_number(binlog_path)

    print("-" * 40)
    print("Corruption complete!")
    print("Test with: toolkit monitor")
    print("Restore with: toolkit restore")
