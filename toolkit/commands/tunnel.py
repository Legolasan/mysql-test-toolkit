"""Unified tunnel command for exposing MySQL to internet"""
import argparse
import subprocess
import time
import json
import os
import urllib.request
from datetime import datetime


# Configuration directories
NGROK_CONFIG_DIR = '/root/.config/ngrok'
CLOUDFLARE_CONFIG_DIR = '/root/.cloudflared'


def is_installed(binary):
    """Check if a binary is installed"""
    result = subprocess.run(['which', binary], capture_output=True)
    return result.returncode == 0


# ============== NGROK ==============

def ngrok_is_configured():
    """Check if ngrok authtoken is configured"""
    return os.path.exists(f'{NGROK_CONFIG_DIR}/ngrok.yml')


def ngrok_configure(authtoken):
    """Configure ngrok with authtoken"""
    os.makedirs(NGROK_CONFIG_DIR, exist_ok=True)
    result = subprocess.run(
        ['ngrok', 'config', 'add-authtoken', authtoken],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Failed to configure ngrok: {result.stderr}")
    print("Ngrok configured successfully")


def ngrok_get_tunnel_url():
    """Get the public URL from ngrok API"""
    try:
        with urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels', timeout=5) as response:
            data = json.loads(response.read().decode())
            if data['tunnels']:
                return data['tunnels'][0]['public_url']
    except Exception:
        pass
    return None


def ngrok_start(port):
    """Start ngrok tunnel"""
    existing_url = ngrok_get_tunnel_url()
    if existing_url:
        return existing_url

    subprocess.Popen(
        ['ngrok', 'tcp', str(port), '--log=stdout'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("Starting ngrok tunnel...")
    for _ in range(30):
        time.sleep(1)
        url = ngrok_get_tunnel_url()
        if url:
            return url

    raise Exception("Timeout waiting for ngrok tunnel")


def ngrok_stop():
    """Stop ngrok tunnel"""
    subprocess.run(['pkill', '-f', 'ngrok'], capture_output=True)


# ============== CLOUDFLARE ==============

def cloudflare_is_running():
    """Check if cloudflared is running"""
    result = subprocess.run(['pgrep', '-f', 'cloudflared'], capture_output=True)
    return result.returncode == 0


def cloudflare_start_named_tunnel(token):
    """Start cloudflared with a named tunnel token"""
    # The token contains all tunnel configuration
    subprocess.Popen(
        ['cloudflared', 'tunnel', '--no-autoupdate', 'run', '--token', token],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("Starting Cloudflare Tunnel...")
    time.sleep(5)

    if cloudflare_is_running():
        return True
    raise Exception("Failed to start Cloudflare Tunnel")


def cloudflare_start_quick_tunnel(port):
    """Start cloudflared quick tunnel (HTTP only)"""
    # Quick tunnels only work for HTTP, not TCP
    # This is here for completeness but won't work for MySQL
    print("Warning: Quick tunnels only support HTTP/HTTPS, not TCP (MySQL)")
    print("For MySQL, use a named tunnel with --token")
    return None


def cloudflare_stop():
    """Stop cloudflared tunnel"""
    subprocess.run(['pkill', '-f', 'cloudflared'], capture_output=True)


# ============== MAIN ==============

def show_status():
    """Show status of all tunnels"""
    print("=" * 50)
    print("Tunnel Status")
    print("=" * 50)

    # Ngrok status
    print("\nNgrok:")
    if is_installed('ngrok'):
        url = ngrok_get_tunnel_url()
        if url:
            print(f"  Status: Running")
            print(f"  URL: {url}")
            if url.startswith('tcp://'):
                parts = url[6:].split(':')
                print(f"  Connect: mysql -h {parts[0]} -P {parts[1]} -uroot -prootpassword")
        else:
            print(f"  Status: Not running")
        print(f"  Configured: {'Yes' if ngrok_is_configured() else 'No'}")
    else:
        print("  Status: Not installed")

    # Cloudflare status
    print("\nCloudflare Tunnel:")
    if is_installed('cloudflared'):
        if cloudflare_is_running():
            print(f"  Status: Running")
            print(f"  Note: URL is configured in Cloudflare dashboard")
        else:
            print(f"  Status: Not running")
    else:
        print("  Status: Not installed")

    print("=" * 50)


def run(args):
    """Run tunnel command"""
    parser = argparse.ArgumentParser(description='Expose MySQL to internet via tunnel')
    parser.add_argument('--provider', choices=['ngrok', 'cloudflare'],
                        help='Tunnel provider')
    parser.add_argument('--port', type=int, default=3306,
                        help='Port to expose (default: 3306)')
    parser.add_argument('--authtoken', help='Ngrok authtoken')
    parser.add_argument('--token', help='Cloudflare tunnel token')
    parser.add_argument('--status', action='store_true',
                        help='Show tunnel status')
    parser.add_argument('--stop', action='store_true',
                        help='Stop all tunnels')
    opts = parser.parse_args(args)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Show status
    if opts.status:
        show_status()
        return

    # Stop tunnels
    if opts.stop:
        print("Stopping all tunnels...")
        ngrok_stop()
        cloudflare_stop()
        print("All tunnels stopped")
        return

    # Require provider for starting
    if not opts.provider:
        print("Error: --provider is required (ngrok or cloudflare)")
        print("\nUsage:")
        print("  toolkit tunnel --provider ngrok --authtoken YOUR_TOKEN")
        print("  toolkit tunnel --provider cloudflare --token YOUR_TUNNEL_TOKEN")
        print("  toolkit tunnel --status")
        print("  toolkit tunnel --stop")
        return

    print(f"[{timestamp}] Starting {opts.provider} tunnel...")
    print("-" * 50)

    # NGROK
    if opts.provider == 'ngrok':
        if not is_installed('ngrok'):
            print("Error: ngrok is not installed")
            return

        if opts.authtoken:
            ngrok_configure(opts.authtoken)
        elif not ngrok_is_configured():
            print("Error: Ngrok authtoken not configured")
            print("Get token from: https://dashboard.ngrok.com/get-started/your-authtoken")
            print("Run: toolkit tunnel --provider ngrok --authtoken YOUR_TOKEN")
            return

        url = ngrok_start(opts.port)
        print(f"Ngrok tunnel active!")
        print(f"Public URL: {url}")

        if url.startswith('tcp://'):
            parts = url[6:].split(':')
            print(f"\nMySQL Connection:")
            print(f"  Host:     {parts[0]}")
            print(f"  Port:     {parts[1]}")
            print(f"  User:     root")
            print(f"  Password: rootpassword")
            print(f"\nConnect command:")
            print(f"  mysql -h {parts[0]} -P {parts[1]} -uroot -prootpassword")

    # CLOUDFLARE
    elif opts.provider == 'cloudflare':
        if not is_installed('cloudflared'):
            print("Error: cloudflared is not installed")
            return

        if not opts.token:
            print("Error: Cloudflare tunnel token required")
            print("\nTo get a tunnel token:")
            print("1. Go to: https://one.dash.cloudflare.com/")
            print("2. Navigate to: Networks > Tunnels")
            print("3. Create a tunnel")
            print("4. Copy the tunnel token")
            print("5. Run: toolkit tunnel --provider cloudflare --token YOUR_TOKEN")
            print("\nNote: You need a domain added to Cloudflare for TCP tunnels")
            return

        cloudflare_start_named_tunnel(opts.token)
        print("Cloudflare Tunnel active!")
        print("\nYour MySQL is accessible at the hostname configured in Cloudflare dashboard")
        print("(The hostname you set when creating the tunnel)")
        print("\nConnect using:")
        print("  mysql -h YOUR_HOSTNAME -P 3306 -uroot -prootpassword")

    print("-" * 50)
    print("Use 'toolkit tunnel --status' to check tunnel status")
    print("Use 'toolkit tunnel --stop' to stop tunnels")
