# Replit Troubleshooting Guide

## 🚀 Quick Setup

1. **Set your API Key**: 
   - Go to the **Secrets** tab in Replit (🔒 icon in left sidebar)
   - Add a new secret:
     - Key: `OPENROUTESERVICE_API_KEY`
     - Value: Your OpenRouteService API key
   - Get a free API key at: https://openrouteservice.org/dev/#/signup

2. **Click the Run button** - The app should automatically set up and start

## ❌ Common Nix Errors and Solutions

### Error: "Package not found" or "Nix evaluation failed"
**Solution**: The Nix configuration has been updated to include all necessary packages. Try:
1. Clear Replit cache: Go to Shell tab and run `rm -rf ~/.cache/nix`
2. Click "Run" again to rebuild

### Error: "Python module not found" (e.g., pandas, flask)
**Solution**: Dependencies should auto-install. If not:
1. Go to Shell tab
2. Run: `pip install -r requirements.txt`
3. Then run: `python app.py`

### Error: "ImportError: No module named 'openrouteservice'"
**Solution**: 
1. In Shell tab: `pip install openrouteservice==2.3.3`
2. Or restart the Repl (click 3 dots → "Restart Repl")

### Error: "numpy.dtype size changed, may indicate binary incompatibility"
**Solution**: This is a numpy/pandas version compatibility issue. Try:
1. **Quick fix**: Run `python fix_numpy_replit.py` in the Shell tab
2. **Manual fix**: In Shell tab:
   ```bash
   pip uninstall -y numpy pandas
   pip install --no-cache-dir numpy==1.24.3
   pip install --no-cache-dir pandas==2.0.3
   pip install -r requirements.txt
   ```
3. **Alternative**: Restart the Repl completely

## 🔧 Manual Setup (if automatic setup fails)

If the automatic setup doesn't work, try these steps in the Shell tab:

```bash
# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads

# Run the app
python app.py
```

## 🐍 Python Version Issues

If you see Python version errors:
1. The configuration uses Python 3.11 (latest stable)
2. If you need a different version, update both:
   - `.replit` file: change `python-3.11` module
   - `replit.nix` file: change `pkgs.python311Full`

## 🌐 Network/API Issues

### "API key not found" warning
- Make sure you set `OPENROUTESERVICE_API_KEY` in the Secrets tab
- The key should be exactly as provided by OpenRouteService

### "Connection timeout" or "API limit exceeded"
- Free OpenRouteService accounts have limits (2000 requests/day)
- The app includes rate limiting (35 requests/minute)
- For high usage, consider upgrading your OpenRouteService plan

## 📁 File Upload Issues

### "No such file or directory: templates/index.html"
- This shouldn't happen as the template exists
- If it does, check that all files were uploaded to Replit correctly

### CSV processing errors
- Ensure your CSV has address columns (street, city, postal code)
- The app supports various delimiters (comma, semicolon, tab)
- Check encoding - the app handles UTF-8, Latin-1, CP1252, and ISO-8859-1

## 🔄 Alternative Run Commands

If the main setup fails, try these alternatives in the Shell:

**Option 1**: Direct Python run
```bash
python app.py
```

**Option 2**: Using the custom runner
```bash
python replit_run.py
```

**Option 3**: Manual setup script
```bash
chmod +x setup_replit.sh
./setup_replit.sh
python app.py
```

## 📊 Performance Tips

1. **Database files**: The app creates cache databases (`routing_cache.db`, `geocoding_cache.db`) - these are normal
2. **Memory usage**: Pandas can use significant memory with large CSV files
3. **API optimization**: The app caches geocoding and routing results to minimize API calls

## 🆘 If Nothing Works

1. **Check the Console tab** for detailed error messages
2. **Try the Shell tab** and run commands manually
3. **Restart the Repl**: Click 3 dots menu → "Restart Repl"
4. **Fork the Repl**: Create a fresh copy if issues persist

## 📝 Files Overview

- `replit.nix`: Nix package configuration (system dependencies)
- `.replit`: Replit run configuration
- `replit_run.py`: Custom Python setup script
- `setup_replit.sh`: Alternative shell setup script
- `requirements.txt`: Python dependencies
- `app.py`: Main Flask application
- `route_optimizer.py`: Core optimization logic 