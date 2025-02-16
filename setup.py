import subprocess
import sys
from pathlib import Path

def setup_environment():
    """Setup the environment including Playwright browsers."""
    try:
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install-deps", "chromium"], check=True)
        print("Playwright setup completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_environment() 