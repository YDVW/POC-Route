"""
Vercel serverless entry point for Route Optimizer - Simplified Version
"""
from flask import Flask, request, jsonify
import pandas as pd
import os
import logging
from io import StringIO

# Configure logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Get API key from environment
OPENROUTESERVICE_API_KEY = os.environ.get('OPENROUTESERVICE_API_KEY', None)
logger.info(f"Vercel deployment: API key configured = {bool(OPENROUTESERVICE_API_KEY)}")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page - Simple HTML response"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Route Optimizer - Vercel Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { text-align: center; }
            .upload-form { margin: 30px 0; }
            .info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Route Optimizer</h1>
            <p>Vercel Serverless Demo Version</p>
            
            <div class="info">
                <h3>📊 CSV Data Validation & Preview</h3>
                <p>Upload your CSV file to validate data structure and preview content.</p>
                <p><strong>Note:</strong> Full route optimization with caching is available on 
                <a href="https://github.com/YDVW/POC-Route.git" target="_blank">Replit</a> or local deployment.</p>
            </div>
            
            <div class="upload-form">
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".csv" required>
                    <br><br>
                    <button type="submit">Upload & Validate CSV</button>
                </form>
            </div>
            
            <div class="info">
                <h3>🔗 Full Functionality</h3>
                <p>For complete route optimization with caching:</p>
                <ul>
                    <li><strong>Replit:</strong> Import from <a href="https://github.com/YDVW/POC-Route.git">GitHub</a></li>
                    <li><strong>Local:</strong> <code>git clone https://github.com/YDVW/POC-Route.git</code></li>
                </ul>
            </div>
            
            <p><a href="/health">Health Check</a> | <a href="https://github.com/YDVW/POC-Route.git">GitHub Repository</a></p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint for Vercel"""
    return jsonify({
        'status': 'healthy',
        'message': 'Route Optimizer API is running on Vercel',
        'api_key_configured': bool(OPENROUTESERVICE_API_KEY),
        'version': 'serverless-demo',
        'platform': 'vercel'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload - simplified for serverless"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Check if file is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Read CSV directly from memory
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            try:
                file.seek(0)
                content = file.read().decode('latin-1')
            except:
                file.seek(0)
                content = file.read().decode('cp1252')
        
        # Create a StringIO object to simulate a file
        csv_data = StringIO(content)
        
        # Try different separators
        separators_to_try = [',', ';', '\t']
        df = None
        separator_used = None
        
        for separator in separators_to_try:
            try:
                csv_data.seek(0)
                temp_df = pd.read_csv(csv_data, sep=separator)
                if len(temp_df.columns) > 1 and len(temp_df) > 0:
                    df = temp_df
                    separator_used = separator
                    logger.info(f"Successfully read CSV with separator='{separator}'")
                    break
            except Exception as e:
                continue
        
        if df is None:
            raise Exception("Could not parse CSV file")
        
        # Clean up the data
        df = df.dropna(how='all')
        
        # Basic validation
        stats = {
            'file_info': {
                'filename': file.filename,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'separator_used': separator_used
            },
            'validation': {
                'is_valid': True,
                'message': 'CSV loaded successfully. This is a demo version - full optimization available on Replit/local deployment.'
            },
            'sample_data': df.head(5).fillna('').to_dict('records')
        }
        
        return jsonify({
            'success': True,
            'message': 'CSV file processed successfully (Vercel serverless mode)',
            'stats': stats,
            'note': 'This is a demo version. For full route optimization with caching, use Replit or local deployment.',
            'github_repo': 'https://github.com/YDVW/POC-Route.git'
        })
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/optimize', methods=['POST'])
def optimize_routes():
    """Simplified route optimization info for serverless"""
    return jsonify({
        'message': 'Route optimization is not available in serverless mode.',
        'reason': 'Requires persistent storage and long-running calculations.',
        'alternatives': {
            'replit': 'Import from https://github.com/YDVW/POC-Route.git to Replit',
            'local': 'git clone https://github.com/YDVW/POC-Route.git && pip install -r requirements.txt && python app.py'
        },
        'features_available_locally': [
            'Full route optimization with 2-opt algorithm',
            'Geocoding cache (83 pre-cached addresses)',
            'Routing cache (272+ cached route segments)', 
            'Real-time optimization results',
            'Performance improvements up to 61.5% distance savings'
        ]
    }), 200

# Vercel serverless handler
app = app 