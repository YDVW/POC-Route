"""
Vercel serverless entry point for Route Optimizer
"""
import os
import sys

# Add the parent directory to Python path so we can import our app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, request, jsonify, render_template
import pandas as pd
from werkzeug.utils import secure_filename
import logging
import time

# Import our route optimizer (without the database dependencies for now)
# We'll need to modify this for serverless deployment
try:
    from route_optimizer import RouteOptimizer
except ImportError:
    # Fallback for serverless environment
    RouteOptimizer = None

# Configure logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
           static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))

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
    """Main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Vercel"""
    return jsonify({
        'status': 'healthy',
        'message': 'Route Optimizer API is running on Vercel',
        'api_key_configured': bool(OPENROUTESERVICE_API_KEY),
        'route_optimizer_available': RouteOptimizer is not None
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
        
        # Read CSV directly from memory (no file saving in serverless)
        try:
            # Try different separators and encodings
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            try:
                file.seek(0)
                content = file.read().decode('latin-1')
            except:
                file.seek(0)
                content = file.read().decode('cp1252')
        
        # Create a StringIO object to simulate a file
        from io import StringIO
        csv_data = StringIO(content)
        
        # Try different separators
        separators_to_try = [',', ';', '\t']
        df = None
        
        for separator in separators_to_try:
            try:
                csv_data.seek(0)
                temp_df = pd.read_csv(csv_data, sep=separator)
                if len(temp_df.columns) > 1 and len(temp_df) > 0:
                    df = temp_df
                    logger.info(f"Successfully read CSV with separator='{separator}'")
                    break
            except Exception as e:
                continue
        
        if df is None:
            raise Exception("Could not parse CSV file")
        
        # Clean up the data
        df = df.dropna(how='all')
        
        # Basic validation (simplified for serverless)
        stats = {
            'file_info': {
                'filename': file.filename,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            },
            'validation': {
                'is_valid': True,
                'message': 'CSV loaded successfully. Full optimization requires local deployment with cache databases.'
            }
        }
        
        # For serverless, we'll return basic stats without optimization
        # Full optimization requires persistent storage for caching
        clean_df = df.fillna('')
        
        return jsonify({
            'success': True,
            'message': 'CSV file processed successfully (Vercel serverless mode)',
            'stats': stats,
            'data': clean_df.head(100).to_dict('records'),  # Limit to first 100 rows
            'note': 'Full route optimization with caching requires local deployment. This is a preview mode.'
        })
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/optimize', methods=['POST'])
def optimize_routes():
    """Simplified route optimization for serverless"""
    return jsonify({
        'error': 'Route optimization requires persistent storage and is not available in serverless mode.',
        'message': 'Please use local deployment or Replit for full functionality.',
        'suggestion': 'Clone from GitHub: https://github.com/YDVW/POC-Route.git'
    }), 501

# This is the entry point that Vercel will call
def handler(request):
    """Vercel serverless handler"""
    return app(request.environ, lambda *args: None)

# For local testing
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 