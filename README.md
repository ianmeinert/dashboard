# Family Dashboard Project

A modern, modular, and extensible dashboard for home, family, or shared spaces. This project combines a SvelteKit frontend and a FastAPI backend to provide a real-time, interactive dashboard experience for family organization, scheduling, and daily information.

## Purpose

The Family Dashboard is designed to serve as a central hub for:

- Family calendar and event management (Google Calendar integration)
- Weather and forecast information (OpenWeatherMap integration)
- Grocery list and family chores (extensible placeholders)
- System health and monitoring (for kiosk or smart home use)

It is optimized for touchscreen kiosks, wall-mounted tablets, or any shared display.

## Main Features

- **Modular Dashboard Layout**: Quadrants for calendar, weather, grocery list, and chores
- **Google Calendar Integration**: Real-time family events
- **Weather Widget**: Current and 5-day forecast by geolocation, city/state, or zip code
- **Responsive UI**: Works on tablets, desktops, and large displays
- **Card-Style Widgets**: Visually distinct, modern look
- **Robust Error Handling**: User-friendly messages and fallbacks
- **Extensible**: Add more widgets or integrations as needed

## Architecture

- **Frontend**: SvelteKit (TypeScript, Tailwind CSS)
  - Handles UI, user interaction, and API communication
  - Provides a responsive, interactive dashboard experience
  - See [frontend/README.md](./frontend/README.md) for details

- **Backend**: FastAPI (Python)
  - Provides RESTful APIs for calendar, weather, and monitoring
  - Integrates with Google Calendar and OpenWeatherMap
  - Handles authentication, data aggregation, and error handling
  - See [backend/README.md](./backend/README.md) for details

## Quick Start

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd dashboard
   ```

2. **Set up credentials:**
   - See [Credentials Setup](#credentials-setup) below for Google Calendar and OpenWeatherMap configuration

3. **Set up the backend:**
   - See [backend/README.md](./backend/README.md) for setup and running instructions

4. **Set up the frontend:**
   - See [frontend/README.md](./frontend/README.md) for setup and running instructions

5. **Open the dashboard:**
   - By default, the frontend runs at `http://localhost:5173` and the backend at `http://localhost:8000`

## Credentials Setup

### Google Calendar Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Calendar API

2. **Create OAuth2 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application" as the application type
   - Download the credentials file

3. **Get OpenWeatherMap API Key:**
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your free API key from your account dashboard

4. **Configure Credentials:**
   - Copy `templates/credentials_template.json` to `backend/data/credentials.json`
   - Replace the placeholder values with your actual credentials:
     - `client_id`: Your Google OAuth2 client ID
     - `client_secret`: Your Google OAuth2 client secret
     - `project_id`: Your Google Cloud project ID
     - `openweathermap_api_key`: Your OpenWeatherMap API key

   ```bash
   cp templates/credentials_template.json backend/data/credentials.json
   # Edit backend/data/credentials.json with your actual credentials
   ```

### Security Notes

- **Never commit `credentials.json` to version control**
- The file is already in `.gitignore` to prevent accidental commits
- Store credentials securely and restrict file permissions
- Use environment variables for production deployments

## Extending the Dashboard

- Add new widgets by creating Svelte components and updating the dashboard layout
- Add new backend APIs for additional data sources or integrations
- Customize styles and layout with Tailwind CSS and Svelte

## License

[Add your license information here]

## Support & Contributions

- For issues, questions, or contributions, please open an issue or pull request in the repository.
