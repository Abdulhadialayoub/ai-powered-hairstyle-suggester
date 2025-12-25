# AI Hairstyle Suggester

An AI-powered web application that analyzes face shapes from uploaded photos and recommends suitable hairstyles.

## Tech Stack

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

## Features

- **Hybrid Face Analysis** - MediaPipe geometric analysis + CNN deep learning model
- **Smart Recommendations** - Personalized hairstyle suggestions based on face shape
- **AI Try-On** - Virtual hairstyle preview using PhotoMaker/Stable Diffusion
- **AI Evaluation** - Google Gemini provides styling feedback
- **User Authentication** - Register, login, session management
- **Favorites System** - Save and manage favorite hairstyles
- **Image Search** - Pexels integration for hairstyle images

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+

### 1. Clone & Setup Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment
Create `backend/.env`:
```env
REPLICATE_API_TOKEN=your_token
STABILITY_API_KEY=your_key
GEMINI_API_KEY=your_key
PEXELS_API_KEY=your_key
SECRET_KEY=your_secret
```

### 3. Setup Frontend
```bash
cd frontend
npm install
```

### 4. Run Application
```bash
# Terminal 1 - Backend
cd backend && python app.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

Access at: http://localhost:3000

## Project Structure

```
├── backend/
│   ├── app.py              # Flask entry point
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── ml/                 # ML models & training
│   ├── data/               # Database files
│   └── tests/              # Unit tests
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main component
│   │   └── components/     # React components
│   └── vite.config.js
└── docs/                   # Documentation
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register user |
| `/api/auth/login` | POST | Login |
| `/api/analysis/analyze` | POST | Analyze face shape |
| `/api/recommendations` | GET | Get hairstyle recommendations |
| `/api/favorites` | GET/POST | Manage favorites |
| `/api/try-on` | POST | AI hairstyle try-on |
| `/api/ai/comment` | POST | Generate AI comment |
| `/api/ml/analyze` | POST | CNN face analysis |
| `/api/health` | GET | Health check |

Full API docs: http://localhost:5000/api/docs

## External Services

| Service | Purpose | Link |
|---------|---------|------|
| ![Google](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat-square&logo=google&logoColor=white) | AI Comments | [makersuite.google.com](https://makersuite.google.com) |
| ![Replicate](https://img.shields.io/badge/Replicate-000000?style=flat-square&logo=replicate&logoColor=white) | AI Try-On | [replicate.com](https://replicate.com) |
| ![Stability](https://img.shields.io/badge/Stability_AI-5C3EE8?style=flat-square&logo=stability-ai&logoColor=white) | Image Generation | [stability.ai](https://stability.ai) |
| ![Pexels](https://img.shields.io/badge/Pexels-05A081?style=flat-square&logo=pexels&logoColor=white) | Hairstyle Images | [pexels.com](https://pexels.com) |

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System architecture diagram
- [Academic Report](docs/ACADEMIC_REPORT.md) - Detailed technical report (Turkish)
- [Project Summary](docs/PROJECT_SUMMARY.md) - Technical overview
- [Testing Guide](backend/TESTING.md) - Test documentation

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
