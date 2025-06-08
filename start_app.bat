@echo off
echo Starting Route Optimizer with OpenRouteService API key...
echo.

REM Set the API key for this session
set OPENROUTESERVICE_API_KEY=5b3ce3597851110001cf6248e8b27c27c8964dd1859f92ba3a1ebb63

REM Verify the API key is set
echo API Key: %OPENROUTESERVICE_API_KEY%
echo.

REM Start the Flask app
echo Starting Flask app...
python app.py

pause 