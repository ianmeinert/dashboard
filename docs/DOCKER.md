# Docker Setup for Family Dashboard

This document provides instructions for running the Family Dashboard application using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- OpenWeatherMap API key (optional, for weather features)
- Google Calendar credentials (optional, for calendar features)

## Quick Start

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
# Required for weather features
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here

# Optional: Override default settings
DEBUG=false
LOG_LEVEL=INFO
```

### 2. Google Calendar Setup (Optional)

If you want to use Google Calendar features:

1. Place your `credentials.json` file in the `backend/` directory
2. The first time you run the application, it will prompt for OAuth authentication
3. The `token.json` file will be created automatically

### 3. Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 4. Access the Application

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>
- **Health Check**: <http://localhost:8000/health>
- **Metrics**: <http://localhost:8000/metrics>

## Service Architecture

### Backend API (`backend` service)

- **Port**: 8000
- **Technology**: FastAPI + Python 3.11
- **Features**:
  - REST API endpoints
  - Database operations
  - External API integrations
  - Prometheus metrics
  - Health monitoring

### Frontend (`frontend` service)

- **Port**: 3000
- **Technology**: Svelte + Nginx
- **Features**:
  - Modern web interface
  - Static file serving
  - API proxy configuration
  - Security headers

### Nginx Reverse Proxy (Production)

- **Ports**: 80, 443
- **Profile**: production
- **Features**:
  - SSL termination
  - Load balancing
  - Rate limiting

## Docker Commands

### Development

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build
```

### Production

```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d

# Scale backend instances
docker-compose up -d --scale backend=3
```

### Maintenance

```bash
# Update images
docker-compose pull

# Remove all containers and volumes
docker-compose down -v

# Clean up unused images
docker image prune

# View resource usage
docker stats
```

## Individual Service Commands

### Backend Only

```bash
# Build backend image
docker build -t dashboard-backend ./backend

# Run backend container
docker run -d \
  --name dashboard-backend \
  -p 8000:8000 \
  -e OPENWEATHERMAP_API_KEY=your_key \
  -v $(pwd)/backend/data:/app/data \
  dashboard-backend
```

### Frontend Only

```bash
# Build frontend image
docker build -t dashboard-frontend ./frontend

# Run frontend container
docker run -d \
  --name dashboard-frontend \
  -p 3000:3000 \
  dashboard-frontend
```

## Environment Variables

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DATABASE_URL` | `sqlite:///app/data/dashboard.db` | Database connection string |
| `OPENWEATHERMAP_API_KEY` | - | OpenWeatherMap API key |
| `OPENWEATHERMAP_BASE_URL` | `https://api.openweathermap.org` | OpenWeatherMap base URL |
| `OPENWEATHERMAP_TIMEOUT` | `10` | API timeout in seconds |
| `RATE_LIMIT_REQUESTS` | `100` | Rate limit requests per window |
| `RATE_LIMIT_WINDOW` | `60` | Rate limit window in seconds |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS allowed origins |
| `PROMETHEUS_MULTIPROC_DIR` | `/tmp/prometheus_multiproc` | Prometheus multiprocess directory |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Node.js environment |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

## Volumes and Data Persistence

The following directories are mounted as volumes:

- `./backend/data` → `/app/data` (Backend data directory)
- `./backend/logs` → `/app/logs` (Backend logs)
- `./backend/credentials.json` → `/app/data/credentials.json` (Google Calendar credentials)
- `./backend/token.json` → `/app/data/token.json` (Google Calendar token)

## Security Considerations

1. **Non-root users**: Both containers run as non-root users
2. **Security headers**: Nginx includes security headers
3. **CORS configuration**: Backend has CORS protection
4. **Rate limiting**: API endpoints have rate limiting
5. **Health checks**: All services have health check endpoints

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Permission errors**: Check file permissions for mounted volumes
3. **API key missing**: Set the `OPENWEATHERMAP_API_KEY` environment variable
4. **Build failures**: Check Docker build logs for dependency issues

### Debug Commands

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs [service_name]

# Execute commands in running container
docker-compose exec backend python -c "print('Backend is working')"
docker-compose exec frontend nginx -t

# Check container resources
docker stats

# Inspect container configuration
docker inspect dashboard-backend
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000/health

# Metrics endpoint
curl http://localhost:8000/metrics
```

## Production Deployment

For production deployment, consider:

1. **SSL/TLS**: Use the nginx reverse proxy with SSL certificates
2. **Load balancing**: Scale backend instances
3. **Monitoring**: Set up Prometheus and Grafana
4. **Backup**: Regular database backups
5. **Updates**: Automated container updates

```bash
# Production deployment
docker-compose --profile production up -d

# With SSL certificates
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
