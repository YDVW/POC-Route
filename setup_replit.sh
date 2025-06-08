#!/bin/bash

echo "🚀 Setting up Route Optimizer for Replit..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if API key is set
if [ -z "$OPENROUTESERVICE_API_KEY" ]; then
    echo "⚠️  WARNING: OPENROUTESERVICE_API_KEY environment variable is not set!"
    echo "   Please set it in the Replit Secrets tab with your OpenRouteService API key"
    echo "   Key name: OPENROUTESERVICE_API_KEY"
    echo "   Get your free key at: https://openrouteservice.org/dev/#/signup"
else
    echo "✅ OpenRouteService API key found"
fi

# Create necessary directories
mkdir -p uploads
mkdir -p templates

# Check if templates exist
if [ ! -f "templates/index.html" ]; then
    echo "⚠️  WARNING: templates/index.html not found"
    echo "   The app may not work without the HTML template"
fi

echo "✅ Setup complete! Run 'python app.py' to start the application" 