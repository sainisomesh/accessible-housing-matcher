#!/bin/bash
# Start the HousingMatcher API server

cd /Users/somesh/Desktop

# Activate virtual environment
source housingmatcher/venv/bin/activate

# Start the server
echo "🚀 Starting HousingMatcher API server..."
echo "📚 API Docs will be available at: http://localhost:8000/docs"
echo "🌐 API will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn housingmatcher.main:app --reload --host 0.0.0.0 --port 8000

