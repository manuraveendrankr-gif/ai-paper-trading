#!/bin/bash

# TradeForge Start Script

echo "=================================="
echo "Starting TradeForge Platform"
echo "=================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start backend in background
echo "Starting backend server..."
python backend.py &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Start frontend server
echo "Starting frontend server..."
python -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "=================================="
echo "TradeForge is now running!"
echo "=================================="
echo ""
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080/trading-platform.html"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
