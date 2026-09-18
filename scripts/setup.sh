#!/bin/bash

# Exit on error
set -e

echo "Setting up Gradually AI development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv backend/venv
fi

# Activate virtual environment
source backend/venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Install mobile dependencies
echo "Installing mobile dependencies..."
cd mobile
flutter pub get
cd ..

# Initialize database and run migrations
echo "Setting up database..."
cd backend
alembic upgrade head
cd ..

# Create necessary directories if they don't exist
mkdir -p backend/logs
mkdir -p backend/tests/unit
mkdir -p backend/tests/integration

# Copy example environment files if they don't exist
if [ ! -f "backend/.env" ]; then
    cp .env.example backend/.env
    echo "Created backend/.env from template. Please update with your settings."
fi

if [ ! -f "frontend/.env" ]; then
    cp .env.example frontend/.env
    echo "Created frontend/.env from template. Please update with your settings."
fi

if [ ! -f "mobile/.env" ]; then
    cp .env.example mobile/.env
    echo "Created mobile/.env from template. Please update with your settings."
fi

echo "Setup complete! Please update the .env files with your settings." 