#!/usr/bin/env python3
"""
Fix numpy/pandas compatibility issues on Replit
Run this script if you encounter numpy dtype errors
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error {description}: {e}")
        return False

def main():
    print("🔧 Fixing numpy/pandas compatibility issues...")
    
    # Uninstall conflicting packages
    print("📦 Uninstalling potentially conflicting packages...")
    packages_to_uninstall = ["numpy", "pandas", "scipy"]
    for package in packages_to_uninstall:
        run_command(f"pip uninstall -y {package}", f"Uninstalling {package}")
    
    # Clear pip cache
    print("🧹 Clearing pip cache...")
    run_command("pip cache purge", "Clearing pip cache")
    
    # Install packages in specific order
    print("📦 Installing packages in compatibility order...")
    install_order = [
        "numpy==1.24.3",
        "pandas==2.0.3",
        "Flask==2.3.3",
        "Werkzeug==2.3.7",
        "openrouteservice==2.3.3",
        "geopy==2.4.0",
        "requests==2.31.0"
    ]
    
    for package in install_order:
        if not run_command(f"pip install --no-cache-dir --force-reinstall {package}", 
                          f"Installing {package}"):
            print(f"⚠️  Warning: Failed to install {package}")
    
    print("\n✅ Compatibility fix completed!")
    print("🚀 Try running your app again with: python app.py")

if __name__ == "__main__":
    main() 