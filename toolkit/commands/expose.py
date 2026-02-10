"""Expose MySQL to internet via ngrok"""
import argparse
import subprocess
import time
import json
import os
import urllib.request
from datetime import datetime


NGROK_CONFIG_DIR = '/root/.config/ngrok'
NGROK_CONFIG_FILE = f'{NGROK_CONFIG_DIR}/ngrok.yml'


def is_ngrok_installed():
    """Check if ngrok is installed"""
    result = subprocess.run(['which', 'ngrok'], capture_output=True)
    return result.returncode == 0


def is_ngrok_configured():
    """Check if ngrok authtoken is configured"""
    return os.path.exists(NGROK_CONFIG_FILE)


def configure_ngrok(authtoken):
    """Configure ngrok with authtoken"""
    os.makedirs(NGROK_CONFIG_DIR, exist_ok=True)
    result = subprocess.run(
        ['ngrok', 'config', 'add-authtoken', authtoken],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Failed to configure ngrok: {result.stderr}")
    print("Ngrok configured successfully")


def get_tunnel_url():
    """Get the public URL from ngrok API"""
    try:
        with urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels', timeout=5) as response:
            data = json.loads(response.read().decode())
            if data['tunnels']:
                return data['tunnels'][0]['public_url']
    except Exception:
        pass
    return None


def start_ngrok(port):
    """Start ngrok tunnel"""
    # Check if already running
    existing_url = get_tunnel_url()
    if existing_url:
        return existing_url

    # Start ngrok in background
    subprocess.Popen(
        ['ngrok', 'tcp', str(port), '--log=stdout'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for tunnel to be ready
    print("Starting ngrok tunnel...")
    for _ in range(30):
        time.sleep(1)
        url = get_tunnel_url()
        if url:
            return url

    raise Exception("Timeout waiting for ngrok tunnel")


def stop_ngrok():
    """Stop ngrok tunnel"""
    subprocess.run(['pkill', '-f', 'ngrok'], capture_output=True)
    print("Ngrok stopped")


def run(args):
    """Run expose command"""
    parser = argparse.ArgumentParser(description='Expose MySQL to internet via ngrok')
    parser.add_argument('--port', type=int, default=3306, help='Port to expose (default: 3306)')
    parser.add_argument('--authtoken', help='Ngrok authtoken (required on first use)')
    parser.add_argument('--stop', action='store_true', help='Stop the ngrok tunnel')
    parser.add_argument('--status', action='store_true', help='Show current tunnel status')
    opts = parser.parse_args(args)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if ngrok is installed
    if not is_ngrok_installed():
        print("Error: ngrok is not installed in this container")
        print("Please use a container with ngrok support or run ngrok on your host")
        return

    # Stop tunnel
    if opts.stop:
        stop_ngrok()
        return

    # Show status
    if opts.status:
        url = get_tunnel_url()
        if url:
            print(f"Ngrok tunnel is active")
            print(f"Public URL: {url}")
            # Parse host and port from tcp://host:port
            if url.startswith('tcp://'):
                parts = url[6:].split(':')
                print(f"\nConnect with:")
                print(f"  mysql -h {parts[0]} -P {parts[1]} -uroot -prootpassword")
        else:
            print("No active ngrok tunnel")
        return

    # Configure authtoken if provided
    if opts.authtoken:
        configure_ngrok(opts.authtoken)
    elif not is_ngrok_configured():
        print("Error: Ngrok authtoken not configured")
        print("Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("Then run: toolkit expose --authtoken YOUR_TOKEN")
        return

    # Start tunnel
    print(f"[{timestamp}] Exposing port {opts.port} to internet...")
    print("-" * 50)

    try:
        url = start_ngrok(opts.port)
        print(f"Ngrok tunnel active!")
        print(f"Public URL: {url}")
        print("-" * 50)

        # Parse host and port
        if url.startswith('tcp://'):
            parts = url[6:].split(':')
            host = parts[0]
            port = parts[1]

            print(f"\nMySQL Connection:")
            print(f"  Host:     {host}")
            print(f"  Port:     {port}")
            print(f"  User:     root")
            print(f"  Password: rootpassword")
            print(f"\nConnect command:")
            print(f"  mysql -h {host} -P {port} -uroot -prootpassword")
            print(f"\nConnection string:")
            print(f"  mysql://root:rootpassword@{host}:{port}/testdb")

        print("-" * 50)
        print("Tunnel running in background. Use 'toolkit expose --stop' to stop.")
        print("Use 'toolkit expose --status' to check tunnel status.")

    except Exception as e:
        print(f"Error: {e}")
