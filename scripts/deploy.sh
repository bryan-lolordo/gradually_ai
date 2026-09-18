#!/bin/bash

# Exit on error
set -e

# Function to display usage
usage() {
    echo "Usage: $0 [-b|--backend] [-f|--frontend] [-m|--mobile] [-a|--all]"
    echo "Options:"
    echo "  -b, --backend   Deploy backend only"
    echo "  -f, --frontend  Deploy frontend only"
    echo "  -m, --mobile    Deploy mobile only"
    echo "  -a, --all       Deploy all components"
    exit 1
}

# Parse command line arguments
DEPLOY_BACKEND=0
DEPLOY_FRONTEND=0
DEPLOY_MOBILE=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--backend)
            DEPLOY_BACKEND=1
            shift
            ;;
        -f|--frontend)
            DEPLOY_FRONTEND=1
            shift
            ;;
        -m|--mobile)
            DEPLOY_MOBILE=1
            shift
            ;;
        -a|--all)
            DEPLOY_BACKEND=1
            DEPLOY_FRONTEND=1
            DEPLOY_MOBILE=1
            shift
            ;;
        *)
            usage
            ;;
    esac
done

# If no options specified, show usage
if [[ $DEPLOY_BACKEND -eq 0 && $DEPLOY_FRONTEND -eq 0 && $DEPLOY_MOBILE -eq 0 ]]; then
    usage
fi

# Deploy backend
if [[ $DEPLOY_BACKEND -eq 1 ]]; then
    echo "Deploying backend..."
    cd backend
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run tests
    python -m pytest tests/
    
    # Run database migrations
    alembic upgrade head
    
    # Restart backend service (assuming systemd)
    sudo systemctl restart gradually-backend
    
    cd ..
    echo "Backend deployment complete!"
fi

# Deploy frontend
if [[ $DEPLOY_FRONTEND -eq 1 ]]; then
    echo "Deploying frontend..."
    cd frontend
    
    # Install dependencies
    npm install
    
    # Build production bundle
    npm run build
    
    # Deploy to web server (assuming nginx)
    sudo cp -r build/* /var/www/gradually/
    
    # Restart nginx
    sudo systemctl restart nginx
    
    cd ..
    echo "Frontend deployment complete!"
fi

# Deploy mobile
if [[ $DEPLOY_MOBILE -eq 1 ]]; then
    echo "Deploying mobile..."
    cd mobile
    
    # Get dependencies
    flutter pub get
    
    # Build release APK
    flutter build apk --release
    
    # Build iOS release (if on macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        flutter build ios --release
    fi
    
    cd ..
    echo "Mobile deployment complete!"
fi

echo "Deployment completed successfully!" 