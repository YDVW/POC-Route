"""
Vercel serverless entry point for Route Optimizer - Full Functionality with Caching
"""
from flask import Flask, request, jsonify
import pandas as pd
import os
import logging
import sqlite3
from io import StringIO
import math
import requests
import time
import itertools

# Configure logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Get API key from environment
OPENROUTESERVICE_API_KEY = os.environ.get('OPENROUTESERVICE_API_KEY', None)
logger.info(f"Flask app startup: API key = '{OPENROUTESERVICE_API_KEY}'")
logger.info(f"API key length: {len(OPENROUTESERVICE_API_KEY) if OPENROUTESERVICE_API_KEY else 0} characters")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

# Embedded cache data for Vercel (since we can't use persistent SQLite)
GEOCODING_CACHE = {
    "Hauptstr. 40, 85643, Steinhöring, Germany": (48.0828668, 12.0630946),
    "Am Römerbrunnen 10, 85609, Aschheim, Germany": (48.1699178, 11.7097772),
    "Högerstr. 16, 85646, Anzing, Germany": (48.1527125, 11.8533032),
    "Hauptstr. 11, 85664, Hohenlinden, Germany": (48.1574977, 11.9964956),
    "Kastanienweg 4, 85652, Pliening, Germany": (48.1958199, 11.7999328),
    "Hauptstr. 14, 85669, Pastetten, Germany": (48.1986485, 11.9428809),
    "Erdinger Str. 6, 85570, Ottenhofen, Germany": (48.2145308, 11.8807559),
    "Klausnerring 12, 85551, Kirchheim, Germany": (48.1534232, 11.744214),
    "Fellnerstr. 2, 85656, Buch am Buchrain, Germany": (48.2115834, 11.9946216),
    "Markt Schwabener Str. 8, 85464, Finsing, Germany": (48.2157185, 11.8250747),
    "Morsestr. 1, 85716, Unterschleissheim, Germany": (48.2913849, 11.5712303),
    "Hauptstr. 32, 85778, Haimhausen, Germany": (48.3164316, 11.5536462),
    "Schlesierstr. 4, 85386, Eching, Germany": (48.3023776, 11.6203083),
    "Kirchgasse 4, 85435, Erding, Germany": (48.3062432, 11.9062046),
    "Am Stutenanger 2, 85764, Oberschleissheim, Germany": (48.2562362, 11.5560171),
    "Schleissheimer Str. 4, 85748, Garching, Germany": (48.2494586, 11.6513853)
}

# Sample routing cache for common routes (simplified for demo)
ROUTING_CACHE = {}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate haversine distance between two points"""
    R = 6371  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def geocode_address(street, postcode, city, country="Germany"):
    """Geocode address using cache first, then API if needed"""
    address_key = f"{street}, {postcode}, {city}, {country}"
    
    # Check cache first
    if address_key in GEOCODING_CACHE:
        logger.info(f"Cache hit: {address_key}... -> {GEOCODING_CACHE[address_key]}")
        return GEOCODING_CACHE[address_key]
    
    # If not in cache and we have API key, try to geocode
    if OPENROUTESERVICE_API_KEY:
        try:
            url = "https://api.openrouteservice.org/geocode/search"
            params = {
                'api_key': OPENROUTESERVICE_API_KEY,
                'text': f"{street}, {postcode} {city}, {country}",
                'boundary.country': 'DE' if country.lower() in ['germany', 'deutschland'] else None,
                'size': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['features']:
                    coords = data['features'][0]['geometry']['coordinates']
                    lat, lng = coords[1], coords[0]
                    logger.info(f"Geocoded: {address_key} -> ({lat}, {lng})")
                    return (lat, lng)
        except Exception as e:
            logger.warning(f"Geocoding failed for {address_key}: {str(e)}")
    
    # Return None if geocoding fails
    logger.warning(f"Could not geocode: {address_key}")
    return None

def optimize_route_2opt(stops_with_coords):
    """Optimize route using 2-opt algorithm"""
    n = len(stops_with_coords)
    if n < 3:
        return stops_with_coords, 0.0
    
    # Create distance matrix
    distances = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                lat1, lng1 = stops_with_coords[i]['coords']
                lat2, lng2 = stops_with_coords[j]['coords']
                distances[(i, j)] = haversine_distance(lat1, lng1, lat2, lng2)
    
    # Calculate initial route distance
    def calculate_route_distance(route_order):
        total_distance = 0
        for i in range(len(route_order)):
            current = route_order[i]
            next_stop = route_order[(i + 1) % len(route_order)]
            total_distance += distances[(current, next_stop)]
        return total_distance
    
    # Initial route (just the order we received)
    current_route = list(range(n))
    current_distance = calculate_route_distance(current_route)
    original_distance = current_distance
    
    improved = True
    iterations = 0
    max_iterations = 10  # Limit for serverless
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # Try reversing the segment between i and j
                new_route = current_route[:]
                new_route[i:j+1] = reversed(new_route[i:j+1])
                
                new_distance = calculate_route_distance(new_route)
                
                if new_distance < current_distance:
                    current_route = new_route
                    current_distance = new_distance
                    improved = True
    
    # Reorder stops according to optimized route
    optimized_stops = [stops_with_coords[i] for i in current_route]
    distance_saved = original_distance - current_distance
    
    logger.info(f"2-Opt completed after {iterations} iterations, improved: {distance_saved > 0}")
    logger.info(f"Route optimization: {n} stops, {distance_saved:.2f}km saved ({(distance_saved/original_distance)*100:.1f}%)")
    
    return optimized_stops, distance_saved

@app.route('/')
def index():
    """Main page - Upload form with route optimization"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Route Optimizer - Full Version</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { text-align: center; }
            .upload-form { margin: 30px 0; }
            .info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .success { background: #d4edda; color: #155724; }
            .warning { background: #fff3cd; color: #856404; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Route Optimizer - Full Version</h1>
            <p>Optimize delivery routes with cached geocoding data</p>
            
            <div class="info success">
                <h3>✅ Full Route Optimization Available</h3>
                <p>Upload your CSV file to get optimized routes with distance savings!</p>
                <p><strong>Features:</strong> Geocoding cache, 2-opt optimization, distance calculations</p>
            </div>
            
            <div class="upload-form">
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".csv" required>
                    <br><br>
                    <button type="submit">Upload & Optimize Routes</button>
                </form>
            </div>
            
            <div class="info warning">
                <p><strong>Note:</strong> This version uses embedded cache data. For full caching capabilities, use 
                <a href="https://github.com/YDVW/POC-Route.git" target="_blank">local deployment</a>.</p>
            </div>
            
            <p><a href="/health">Health Check</a> | <a href="https://github.com/YDVW/POC-Route.git">GitHub Repository</a></p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Route Optimizer API with full optimization capabilities',
        'api_key_configured': bool(OPENROUTESERVICE_API_KEY),
        'cached_addresses': len(GEOCODING_CACHE),
        'version': 'full-optimization',
        'platform': 'vercel'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and perform route optimization"""
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
        logger.info(f"Loaded CSV: {file.filename}")
        logger.info(f"Shape after cleaning: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Extract address information
        stops_with_coords = []
        geocoded_count = 0
        cache_hits = 0
        
        for index, row in df.iterrows():
            # Try to find address columns
            street = None
            postcode = None
            city = None
            name = None
            
            # Look for common column names
            for col in df.columns:
                col_lower = col.lower()
                if 'street' in col_lower or 'straße' in col_lower or col_lower == 'street':
                    street = str(row[col]) if pd.notna(row[col]) else None
                elif 'post' in col_lower or 'zip' in col_lower or 'plz' in col_lower:
                    postcode = str(row[col]) if pd.notna(row[col]) else None
                elif 'city' in col_lower or 'stadt' in col_lower or col_lower == 'city':
                    city = str(row[col]) if pd.notna(row[col]) else None
                elif 'name' in col_lower and not name:
                    name = str(row[col]) if pd.notna(row[col]) else None
            
            if street and postcode and city:
                coords = geocode_address(street, postcode, city)
                if coords:
                    stops_with_coords.append({
                        'index': index,
                        'name': name or f"Stop {index + 1}",
                        'address': f"{street}, {postcode} {city}",
                        'coords': coords,
                        'street': street,
                        'postcode': postcode,
                        'city': city
                    })
                    geocoded_count += 1
                    # Check if it was a cache hit
                    address_key = f"{street}, {postcode}, {city}, Germany"
                    if address_key in GEOCODING_CACHE:
                        cache_hits += 1
        
        logger.info(f"Geocoded {geocoded_count}/{len(df)} stops ({cache_hits} cache hits, {cache_hits/geocoded_count*100:.1f}% hit rate)")
        
        if len(stops_with_coords) < 2:
            return jsonify({
                'error': 'Not enough geocoded addresses for route optimization',
                'geocoded_count': geocoded_count,
                'total_addresses': len(df)
            }), 400
        
        # Perform route optimization
        start_time = time.time()
        optimized_stops, distance_saved = optimize_route_2opt(stops_with_coords)
        optimization_time = time.time() - start_time
        
        # Calculate total distance
        total_distance = 0
        for i in range(len(optimized_stops)):
            current = optimized_stops[i]
            next_stop = optimized_stops[(i + 1) % len(optimized_stops)]
            lat1, lng1 = current['coords']
            lat2, lng2 = next_stop['coords']
            total_distance += haversine_distance(lat1, lng1, lat2, lng2)
        
        # Prepare response
        result = {
            'success': True,
            'message': 'Route optimization completed successfully',
            'stats': {
                'file_info': {
                    'filename': file.filename,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'separator_used': separator_used
                },
                'geocoding': {
                    'total_addresses': len(df),
                    'geocoded_successfully': geocoded_count,
                    'cache_hits': cache_hits,
                    'cache_hit_rate': f"{cache_hits/geocoded_count*100:.1f}%" if geocoded_count > 0 else "0%"
                },
                'optimization': {
                    'stops_optimized': len(optimized_stops),
                    'total_distance_km': round(total_distance, 2),
                    'distance_saved_km': round(distance_saved, 2),
                    'improvement_percentage': f"{(distance_saved/(total_distance + distance_saved))*100:.1f}%",
                    'optimization_time_seconds': round(optimization_time, 2)
                }
            },
            'optimized_route': [
                {
                    'stop_number': i + 1,
                    'name': stop['name'],
                    'address': stop['address'],
                    'coordinates': {
                        'latitude': stop['coords'][0],
                        'longitude': stop['coords'][1]
                    }
                }
                for i, stop in enumerate(optimized_stops)
            ],
            'github_repo': 'https://github.com/YDVW/POC-Route.git'
        }
        
        logger.info(f"Optimization complete: {distance_saved:.2f}km saved ({(distance_saved/(total_distance + distance_saved))*100:.1f}% improvement)")
        logger.info(f"Route optimization completed in {optimization_time:.2f} seconds")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

# Vercel serverless handler
app = app 