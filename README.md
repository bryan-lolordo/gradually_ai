# Gradually AI

An AI-powered application that helps users optimize their daily schedules through intelligent task management and habit formation.

## Project Structure

```
gradually_ai/
├── backend/    # FastAPI Backend
├── frontend/   # React Frontend
└── mobile/     # Flutter Mobile App
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Flutter 3.0+
- PostgreSQL
- Redis

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Then edit .env with your settings
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env  # Then edit .env with your settings
npm run dev
```

### Mobile Setup

```bash
cd mobile
flutter pub get
cp .env.example .env  # Then edit .env with your settings
flutter run
```

## Development

### Architecture

- **Backend**: FastAPI with SQLAlchemy, Redis caching, and JWT authentication
- **Frontend**: React with Vite, TypeScript, and TailwindCSS
- **Mobile**: Flutter with Provider for state management

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Environment Variables

See `.env.example` for all required environment variables.

## Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

### Mobile
```bash
cd mobile
flutter test
```

## Deployment

### Backend
```bash
cd backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
```

### Mobile
```bash
cd mobile
flutter build apk  # Android
flutter build ios  # iOS
```

## Features

- User Authentication
- Schedule Management
- Task Tracking
- Habit Formation
- AI Recommendations
- Cross-platform Support

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 