#!/usr/bin/env python3
"""
Replit runner script for Route Optimizer
This script handles setup and then runs the main application
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error {description}: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def main():
    print("🚀 Starting Route Optimizer on Replit...")
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Install/upgrade pip
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Warning: Could not upgrade pip, continuing...")
    
    # Fix numpy/pandas compatibility issues by installing in specific order
    print("🔧 Installing numpy first to avoid compatibility issues...")
    if not run_command("pip install --no-cache-dir numpy==1.24.3", "Installing numpy"):
        print("⚠️  Warning: Could not install numpy specifically, continuing...")
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        if not run_command("pip install --no-cache-dir -r requirements.txt", "Installing Python packages"):
            print("❌ Failed to install requirements. Trying alternative approach...")
            # Try installing packages individually if batch install fails
            packages = [
                "Flask==2.3.3",
                "pandas==2.0.3", 
                "Werkzeug==2.3.7",
                "openrouteservice==2.3.3",
                "geopy==2.4.0",
                "requests==2.31.0"
            ]
            for package in packages:
                if not run_command(f"pip install --no-cache-dir {package}", f"Installing {package}"):
                    print(f"⚠️  Warning: Could not install {package}")
    else:
        print("⚠️  Warning: requirements.txt not found")
    
    # Check API key
    api_key = os.environ.get('OPENROUTESERVICE_API_KEY')
    if api_key:
        print("✅ OpenRouteService API key found")
        print(f"   Key length: {len(api_key)} characters")
    else:
        print("⚠️  WARNING: OPENROUTESERVICE_API_KEY not set!")
        print("   Set it in Replit's Secrets tab:")
        print("   Key: OPENROUTESERVICE_API_KEY")
        print("   Value: Your OpenRouteService API key")
        print("   Get a free key at: https://openrouteservice.org/dev/#/signup")
    
    # Create directories
    os.makedirs("uploads", exist_ok=True)
    print("✅ Created uploads directory")
    
    # Check templates
    if os.path.exists("templates/index.html"):
        print("✅ Template file found")
    else:
        print("⚠️  Warning: templates/index.html not found")
    
    print("\n🎯 Starting Flask application...")
    print("   The app should be available at the URL shown by Replit")
    print("   Look for 'Running on http://...' message below")
    print("-" * 50)
    
    # Import and run the main app
    try:
        import app
        # The app.py file should handle running the Flask app
    except ImportError as e:
        print(f"❌ Could not import app.py: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 