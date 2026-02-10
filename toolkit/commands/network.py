"""Network simulation for ETL resilience testing"""
import argparse
import subprocess
import time
import os
from datetime import datetime


# ============== MySQL Service Control ==============

def mysql_is_running():
    """Check if MySQL is running"""
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    return 'mysqld' in result.stdout


def mysql_stop():
    """Stop MySQL service"""
    if not mysql_is_running():
        print("MySQL is already stopped")
        return

    print("Stopping MySQL...")
    subprocess.run(['mysqladmin', '-uroot', '-prootpassword', 'shutdown'],
                   capture_output=True, stderr=subprocess.DEVNULL)
    time.sleep(2)

    if not mysql_is_running():
        print("MySQL stopped successfully")
    else:
        # Force kill if graceful shutdown failed
        subprocess.run(['pkill', '-9', 'mysqld'], capture_output=True)
        print("MySQL force stopped")


def mysql_start():
    """Start MySQL service"""
    if mysql_is_running():
        print("MySQL is already running")
        return

    print("Starting MySQL...")
    subprocess.Popen(
        ['mysqld', '--user=mysql'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for MySQL to be ready
    for _ in range(30):
        time.sleep(1)
        result = subprocess.run(
            ['mysqladmin', '-uroot', '-prootpassword', 'ping'],
            capture_output=True
        )
        if result.returncode == 0:
            print("MySQL started successfully")
            return

    print("Warning: MySQL may not be fully ready")


# ============== Firewall Control (iptables) ==============

def firewall_reject(port=3306):
    """Block port with connection refused (REJECT)"""
    subprocess.run([
        'iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', str(port),
        '-j', 'REJECT', '--reject-with', 'tcp-reset'
    ], capture_output=True)
    print(f"Firewall: Port {port} blocked (connection refused)")


def firewall_drop(port=3306):
    """Block port with silent drop (timeout)"""
    subprocess.run([
        'iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', str(port),
        '-j', 'DROP'
    ], capture_output=True)
    print(f"Firewall: Port {port} blocked (timeout/drop)")


def firewall_clear():
    """Clear all iptables rules"""
    subprocess.run(['iptables', '-F'], capture_output=True)
    subprocess.run(['iptables', '-X'], capture_output=True)
    print("Firewall: All rules cleared")


def firewall_status():
    """Get current iptables rules"""
    result = subprocess.run(['iptables', '-L', '-n'], capture_output=True, text=True)
    return result.stdout


# ============== Latency Control (tc) ==============

def get_default_interface():
    """Get the default network interface"""
    result = subprocess.run(
        ['ip', 'route', 'show', 'default'],
        capture_output=True, text=True
    )
    if result.stdout:
        parts = result.stdout.split()
        if 'dev' in parts:
            idx = parts.index('dev')
            return parts[idx + 1]
    return 'eth0'


def add_latency(latency_ms):
    """Add latency to network traffic"""
    interface = get_default_interface()

    # Remove existing qdisc first
    subprocess.run(
        ['tc', 'qdisc', 'del', 'dev', interface, 'root'],
        capture_output=True, stderr=subprocess.DEVNULL
    )

    # Add latency
    result = subprocess.run([
        'tc', 'qdisc', 'add', 'dev', interface, 'root', 'netem',
        'delay', f'{latency_ms}ms'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Latency: Added {latency_ms}ms delay on {interface}")
    else:
        print(f"Error adding latency: {result.stderr}")


def remove_latency():
    """Remove latency from network traffic"""
    interface = get_default_interface()
    subprocess.run(
        ['tc', 'qdisc', 'del', 'dev', interface, 'root'],
        capture_output=True, stderr=subprocess.DEVNULL
    )
    print(f"Latency: Removed delay on {interface}")


# ============== Flapping Mode ==============

def flap_connection(failure_type, interval, duration):
    """Toggle connection up/down at intervals"""
    print(f"Starting flapping mode: {failure_type} every {interval}s for {duration}s")
    print("Press Ctrl+C to stop")
    print("-" * 40)

    start_time = time.time()
    is_down = False

    try:
        while (time.time() - start_time) < duration:
            timestamp = datetime.now().strftime("%H:%M:%S")

            if is_down:
                # Bring up
                if failure_type == 'service':
                    mysql_start()
                else:
                    firewall_clear()
                print(f"[{timestamp}] Connection UP")
            else:
                # Bring down
                if failure_type == 'service':
                    mysql_stop()
                elif failure_type == 'reject':
                    firewall_reject()
                elif failure_type == 'timeout':
                    firewall_drop()
                print(f"[{timestamp}] Connection DOWN ({failure_type})")

            is_down = not is_down
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nFlapping stopped by user")

    finally:
        # Restore connectivity
        if failure_type == 'service':
            mysql_start()
        else:
            firewall_clear()
        print("Connection restored")


# ============== Status ==============

def show_status():
    """Show current network status"""
    print("=" * 50)
    print("Network Simulation Status")
    print("=" * 50)

    # MySQL status
    print("\nMySQL Service:")
    if mysql_is_running():
        print("  Status: Running")
    else:
        print("  Status: STOPPED")

    # Firewall status
    print("\nFirewall (iptables):")
    fw_status = firewall_status()
    if 'REJECT' in fw_status or 'DROP' in fw_status:
        print("  Status: BLOCKING")
        for line in fw_status.split('\n'):
            if 'REJECT' in line or 'DROP' in line:
                print(f"    {line.strip()}")
    else:
        print("  Status: Open (no blocks)")

    # Latency status
    print("\nLatency (tc):")
    interface = get_default_interface()
    result = subprocess.run(
        ['tc', 'qdisc', 'show', 'dev', interface],
        capture_output=True, text=True
    )
    if 'netem' in result.stdout and 'delay' in result.stdout:
        print(f"  Status: ACTIVE")
        print(f"    {result.stdout.strip()}")
    else:
        print("  Status: No latency added")

    print("=" * 50)


# ============== Main ==============

def run(args):
    """Run network simulation"""
    parser = argparse.ArgumentParser(description='Network simulation for ETL testing')
    parser.add_argument('--down', action='store_true', help='Bring connection down')
    parser.add_argument('--up', action='store_true', help='Bring connection up (restore)')
    parser.add_argument('--type', choices=['service', 'reject', 'timeout'],
                        default='reject', help='Type of failure (default: reject)')
    parser.add_argument('--duration', type=int, help='Auto-restore after N seconds')
    parser.add_argument('--flap', action='store_true', help='Flapping mode (toggle up/down)')
    parser.add_argument('--interval', type=int, default=30,
                        help='Flapping interval in seconds (default: 30)')
    parser.add_argument('--slow', action='store_true', help='Enable latency injection')
    parser.add_argument('--latency', type=int, default=2000,
                        help='Latency in milliseconds (default: 2000)')
    parser.add_argument('--off', action='store_true', help='Disable latency')
    parser.add_argument('--status', action='store_true', help='Show network status')
    opts = parser.parse_args(args)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Show status
    if opts.status:
        show_status()
        return

    # Restore connection
    if opts.up:
        print(f"[{timestamp}] Restoring connection...")
        mysql_start()
        firewall_clear()
        remove_latency()
        print("All connections restored")
        return

    # Latency control
    if opts.slow:
        if opts.off:
            remove_latency()
        else:
            add_latency(opts.latency)
        return

    # Flapping mode
    if opts.flap:
        duration = opts.duration or 300  # Default 5 minutes
        flap_connection(opts.type, opts.interval, duration)
        return

    # Bring down
    if opts.down:
        print(f"[{timestamp}] Bringing connection down ({opts.type})...")

        if opts.type == 'service':
            mysql_stop()
        elif opts.type == 'reject':
            firewall_reject()
        elif opts.type == 'timeout':
            firewall_drop()

        # Auto-restore if duration specified
        if opts.duration:
            print(f"Will auto-restore in {opts.duration} seconds...")
            time.sleep(opts.duration)
            print("Auto-restoring...")
            if opts.type == 'service':
                mysql_start()
            else:
                firewall_clear()
            print("Connection restored")

        return

    # No action specified
    print("Usage:")
    print("  toolkit network --down --type reject     # Block with connection refused")
    print("  toolkit network --down --type timeout    # Block with timeout")
    print("  toolkit network --down --type service    # Stop MySQL")
    print("  toolkit network --down --duration 60     # Auto-restore after 60s")
    print("  toolkit network --flap --interval 30     # Flapping mode")
    print("  toolkit network --slow --latency 2000    # Add 2s latency")
    print("  toolkit network --slow --off             # Remove latency")
    print("  toolkit network --up                     # Restore all")
    print("  toolkit network --status                 # Show status")
