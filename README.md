# Family Dashboard

A modern, modular dashboard for home and family organization built with SvelteKit and FastAPI.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-2.0+-orange.svg)](https://kit.svelte.dev)

## 🚀 Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd dashboard

# Set up environment variables
cp templates/env_template.txt backend/.env
# Edit backend/.env with your API keys and settings

# Set up credentials (see Credentials section below)
cp templates/credentials_template.json backend/data/credentials.json
# Edit backend/data/credentials.json with your API keys

# Start the backend
cd backend
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
uv pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, start the frontend
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to see your dashboard!

**📚 Need detailed setup instructions?** Check out our [Getting Started Guide](docs/getting-started.md)

## 📋 Features

### 🗓️ Calendar Integration

- **Google Calendar Sync**: Real-time family events and appointments
- **OAuth2 Authentication**: Secure, token-based access
- **Event Display**: Clean, readable event cards with details

### 🌤️ Weather Widget

- **Current Conditions**: Real-time weather data
- **5-Day Forecast**: Extended weather predictions
- **Location Management**: Geolocation, city/state, or zip code lookup
- **Persistent Settings**: Remembers your preferred location

### 🛒 Grocery List

- **Smart Management**: Add, edit, delete, and check off items
- **Categories & Priorities**: Organize with categories and priority levels
- **Database Storage**: Robust SQLite backend with async SQLAlchemy
- **Auto-Migration**: Seamless upgrade from legacy JSON storage

### 📊 System Monitoring

- **Health Checks**: Real-time system status
- **Performance Metrics**: Dashboard and API monitoring
- **Error Tracking**: Comprehensive error handling and logging

## 🏗️ Architecture

```
dashboard/
├── frontend/          # SvelteKit application
│   ├── src/
│   │   ├── lib/components/  # Reusable UI components
│   │   ├── stores/          # State management
│   │   └── routes/          # Page routes
│   └── package.json
├── backend/           # FastAPI application
│   ├── api/           # API endpoints
│   ├── models.py      # Database models
│   ├── schemas/       # Pydantic schemas
│   └── requirements.txt
├── docs/              # 📚 Comprehensive documentation
│   ├── getting-started.md
│   ├── configuration.md
│   ├── troubleshooting.md
│   └── features/
└── data/              # Shared data storage
```

### Technology Stack

**Frontend:**

- [SvelteKit](https://kit.svelte.dev/) - Full-stack web framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first styling
- [Vite](https://vitejs.dev/) - Build tool and dev server

**Backend:**

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [SQLAlchemy](https://sqlalchemy.org/) - Async ORM
- [SQLite](https://sqlite.org/) - Lightweight database
- [Pydantic](https://pydantic.dev/) - Data validation

**Integrations:**

- [Google Calendar API](https://developers.google.com/calendar) - Event management
- [OpenWeatherMap API](https://openweathermap.org/api) - Weather data

## 🔧 Setup

### Prerequisites

- **Python 3.8+** with [uv](https://github.com/astral-sh/uv) (recommended) or pip
- **Node.js 18+** with npm, yarn, or pnpm
- **Google Cloud Platform** account for Calendar API
- **OpenWeatherMap** account for weather data

### Credentials Setup

1. **Google Calendar Setup:**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Calendar API
   - Create OAuth2 credentials (Desktop application)
   - Download credentials file

2. **OpenWeatherMap Setup:**
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your free API key

3. **Configure Credentials:**

   ```bash
   cp templates/credentials_template.json backend/data/credentials.json
   # Edit backend/data/credentials.json with your actual credentials
   ```

### Installation

Detailed setup instructions are available in our comprehensive documentation:

- **[Getting Started Guide](docs/getting-started.md)** - Quick setup and first steps
- **[Configuration Guide](docs/configuration.md)** - Detailed API and environment setup
- **[Backend Setup](backend/README.md)** - FastAPI server configuration
- **[Frontend Setup](frontend/README.md)** - SvelteKit application setup

## 🎯 Usage

### Dashboard Overview

The dashboard is organized into four main quadrants:

```
┌─────────────────┬─────────────────┐
│   📅 Calendar   │   🌤️ Weather    │
│                 │                 │
│ Family Events   │ Current Weather │
│ & Appointments  │ & Forecast      │
└─────────────────┴─────────────────┘
┌─────────────────┬─────────────────┐
│   🛒 Grocery    │   📊 Monitoring │
│                 │                 │
│ Shopping List   │ System Health   │
│ & Household     │ & Performance   │
└─────────────────┴─────────────────┘
```

### Key Interactions

- **Click any quadrant** to expand for detailed view
- **Weather widget** supports location search and geolocation
- **Grocery list** allows adding, editing, and organizing items
- **Calendar** shows upcoming events with details

### Mobile & Touch Support

The dashboard is optimized for:

- Touchscreen kiosks
- Wall-mounted tablets
- Desktop and mobile browsers
- Large displays and projectors

## 🔒 Security

- **OAuth2 Authentication** for Google Calendar
- **Environment Variables** for sensitive configuration
- **Input Validation** with Pydantic schemas
- **CORS Protection** for API endpoints
- **Secure Credential Storage** (never committed to git)

## 🚀 Deployment

### Development

```bash
# Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev
```

### Production

See deployment guides in the component READMEs:

- [Backend Deployment](backend/README.md#deployment)
- [Frontend Deployment](frontend/README.md#deployment)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages
- Write tests for new features
- Update documentation for API changes
- Follow the established code style and patterns

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SvelteKit](https://kit.svelte.dev/) for the amazing frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the modern Python backend
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first styling
- [Google Calendar API](https://developers.google.com/calendar) for calendar integration
- [OpenWeatherMap](https://openweathermap.org/) for weather data

---

**Made with ❤️ for families everywhere**

**📚 Ready to dive deeper?** Start with our [Getting Started Guide](docs/getting-started.md) or explore the [Documentation Hub](docs/README.md).
