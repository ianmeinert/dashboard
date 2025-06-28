# Getting Started

Welcome to the Family Dashboard! This guide will help you get up and running in minutes.

## 🎯 What You'll Build

A modern, interactive dashboard that includes:

- 📅 **Family Calendar** - Google Calendar integration
- 🌤️ **Weather Widget** - Current conditions and forecasts
- 🛒 **Grocery List** - Smart shopping management
- 📊 **System Monitoring** - Health and performance tracking

## ⚡ Quick Start (5 minutes)

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd dashboard
```

### 2. Set Up Credentials

```bash
# Copy the template
cp templates/credentials_template.json backend/data/credentials.json

# Edit with your API keys
# You'll need Google Calendar and OpenWeatherMap credentials
```

### 3. Start the Backend

```bash
cd backend
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
uv pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the Frontend

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

### 5. Open Your Dashboard

Visit `http://localhost:5173` to see your dashboard!

## 🔑 Required Credentials

You'll need to set up two API services:

### Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth2 credentials (Desktop application)
5. Download the credentials file

### OpenWeatherMap API

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Add it to your credentials file

**Need help?** See the [Configuration Guide](configuration.md) for detailed setup instructions.

## 🏠 Dashboard Overview

Once running, you'll see a four-quadrant dashboard:

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

## 🚀 Next Steps

### For Users

- [Configure your preferred weather location](features/weather.md)
- [Set up your grocery list](features/grocery.md)
- [Customize the dashboard layout](development.md)

### For Developers

- [Understand the architecture](architecture.md)
- [Explore the API](api-reference.md)
- [Add new features](development.md)

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**

```bash
# Check Python version
python --version  # Should be 3.8+

# Verify credentials
ls backend/data/credentials.json

# Check dependencies
uv pip list
```

**Frontend can't connect:**

```bash
# Verify backend is running
curl http://localhost:8000/api/monitoring/health

# Check CORS settings
# Backend should be on port 8000, frontend on 5173
```

**Weather widget not working:**

- Verify OpenWeatherMap API key in credentials
- Check browser geolocation permissions
- Try searching by city/state or zip code

### Getting Help

- **Check the logs** in the terminal for error messages
- **Review the [Troubleshooting Guide](troubleshooting.md)**
- **Open an issue** with detailed error information

## 📱 Supported Devices

The dashboard works great on:

- 🖥️ **Desktop computers** - Full-featured experience
- 📱 **Tablets** - Touch-optimized interface
- 🖼️ **Wall-mounted displays** - Kiosk mode
- 📱 **Mobile phones** - Responsive design

## 🔒 Security Notes

- **Never commit credentials** to version control
- **Use environment variables** for production
- **Keep API keys secure** and rotate regularly
- **Enable HTTPS** for production deployments

---

**Ready to dive deeper?** Check out the [Installation Guide](installation.md) for detailed setup instructions.
