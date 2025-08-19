#!/usr/bin/env python3
"""
Setup script for IT Dashboard Generator
Creates virtual environment and installs dependencies
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    print("IT Dashboard Generator - Setup Script")
    print("=" * 50)
    project_root = Path(__file__).parent
    os.chdir(project_root)
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    if os.name == 'nt':
        activate_cmd = "venv\\Scripts\\activate && "
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate && "
        pip_cmd = "venv/bin/pip"
    if not run_command(f"{activate_cmd} {pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    if not run_command(f"{activate_cmd} {pip_cmd} install -r requirements.txt", "Installing requirements"):
        return False
    directories = ["reports", "logs", "reports/charts"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit config/settings.json to configure your GitHub repositories")
    print("2. Run the dashboard generator:")
    if os.name == 'nt':
        print("   - Windows: scripts\\run_dashboard_windows.bat")
    else:
        print("   - Unix/Linux: ./scripts/run_dashboard_unix.sh")
    print("3. Schedule the script to run daily using:")
    print("   - Windows: Task Scheduler")
    print("   - Unix/Linux: crontab")

if __name__ == "__main__":
    main()
