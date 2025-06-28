# Troubleshooting Guide

This guide helps you resolve common issues with the Family Dashboard. If you don't find your issue here, please open a GitHub issue with detailed information.

## 🚨 Quick Diagnosis

### Check System Status

```bash
# Test backend health
curl http://localhost:8000/api/monitoring/health

# Test frontend connectivity
curl http://localhost:5173

# Check if ports are in use
netstat -an | grep :8000
netstat -an | grep :5173
```

### Common Error Patterns

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| Backend won't start | Python version, missing dependencies | Check Python 3.8+, run `uv pip install -r requirements.txt` |
| Frontend can't connect | Backend not running, CORS issues | Start backend, check CORS settings |
| Weather not loading | API key issues, network problems | Verify OpenWeatherMap key, check network |
| Calendar not working | OAuth setup, credentials | Complete OAuth flow, verify credentials |
| Grocery items not saving | Database issues, permissions | Check database file, verify permissions |

## 🔧 Backend Issues

### Backend Won't Start

**Error**: `ModuleNotFoundError` or `ImportError`

**Solution**:

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
cd backend
uv pip install -r requirements.txt

# Check for missing packages
uv pip list
```

**Error**: `Port already in use`

**Solution**:

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Error**: `Permission denied` on database or credentials

**Solution**:

```bash
# Fix file permissions
chmod 644 backend/data/credentials.json
chmod 644 backend/data/dashboard.db

# Check file ownership
ls -la backend/data/
```

### API Endpoints Not Responding

**Error**: `Connection refused` or timeout

**Check**:

1. Backend server is running
2. Correct port (8000)
3. Firewall settings
4. Network connectivity

**Test**:

```bash
# Test basic connectivity
curl http://localhost:8000/

# Test health endpoint
curl http://localhost:8000/api/monitoring/health

# Test with verbose output
curl -v http://localhost:8000/api/monitoring/health
```

### Database Issues

**Error**: `database is locked` or SQLite errors

**Solution**:

```bash
# Check database file
ls -la backend/data/dashboard.db

# Backup and recreate if corrupted
cp backend/data/dashboard.db backend/data/dashboard.db.backup
rm backend/data/dashboard.db
# Restart backend to recreate database
```

**Error**: Migration failed

**Solution**:

```bash
# Check legacy file exists
ls -la backend/data/grocery_list.json

# Manual migration
python -c "
import json
from backend.models import init_db, get_session
from backend.schemas.grocery import GroceryItemCreate

# Initialize database
init_db()

# Load legacy data
with open('backend/data/grocery_list.json', 'r') as f:
    data = json.load(f)

# Migrate items
async def migrate():
    async with get_session() as session:
        for item in data:
            grocery_item = GroceryItemCreate(**item)
            # Add to database
            # ... implementation details
"
```

## 🎨 Frontend Issues

### Frontend Won't Start

**Error**: `ENOENT: no such file or directory`

**Solution**:

```bash
# Check Node.js version
node --version  # Should be 18+

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error**: `Port 5173 already in use`

**Solution**:

```bash
# Find process using port 5173
lsof -i :5173  # macOS/Linux
netstat -ano | findstr :5173  # Windows

# Use different port
npm run dev -- --port 5174
```

### Frontend Can't Connect to Backend

**Error**: CORS errors in browser console

**Solution**:

1. Check backend CORS settings in `.env`:

   ```env
   ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

2. Verify frontend environment variables:

   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. Restart both frontend and backend

**Error**: Network errors or timeouts

**Check**:

- Backend is running on port 8000
- No firewall blocking connections
- Network connectivity between frontend and backend

### UI Not Updating

**Symptom**: Changes not reflected in browser

**Solution**:

```bash
# Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
# Clear browser cache
# Check browser console for JavaScript errors
```

## 🌤️ Weather Widget Issues

### Weather Not Loading

**Error**: `401 Unauthorized` or `403 Forbidden`

**Solution**:

1. Verify OpenWeatherMap API key in `credentials.json`
2. Check API key is activated (may take hours for new keys)
3. Test API key directly:

   ```bash
   curl "http://api.openweathermap.org/data/2.5/weather?q=Austin,TX&appid=YOUR_API_KEY"
   ```

**Error**: `404 Not Found` for location

**Solution**:

- Check location format (city, state or zip code)
- Verify location exists in OpenWeatherMap database
- Try alternative location formats

**Error**: Geolocation not working

**Solution**:

1. Check browser permissions for location
2. Ensure HTTPS in production (geolocation requires secure context)
3. Test with manual location search

### Location Settings Not Saving

**Symptom**: Location reverts after page refresh

**Check**:

1. Backend database is writable
2. Weather settings API is responding
3. Frontend is sending correct data format

**Test**:

```bash
# Test weather settings API
curl -X GET http://localhost:8000/api/weather/settings
curl -X POST http://localhost:8000/api/weather/settings \
  -H "Content-Type: application/json" \
  -d '{"city": "Austin", "state": "TX"}'
```

## 📅 Calendar Issues

### Google Calendar Not Loading

**Error**: OAuth authentication failed

**Solution**:

1. Complete OAuth flow:
   - Visit `http://localhost:8000/docs`
   - Follow OAuth2 authorization
   - Grant calendar permissions

2. Check OAuth consent screen:
   - Verify test users are added
   - Check scopes include `calendar.readonly`

**Error**: `token.json` not found or invalid

**Solution**:

```bash
# Remove old token and re-authenticate
rm backend/data/token.json
# Restart backend and complete OAuth flow again
```

**Error**: Calendar events not showing

**Check**:

1. Calendar has events in the specified date range
2. Calendar ID is correct (default: `primary`)
3. Events are not private or restricted

### Calendar API Health Check

```bash
# Test calendar health
curl http://localhost:8000/api/calendar/health

# Test events endpoint
curl http://localhost:8000/api/calendar/events
```

## 🛒 Grocery List Issues

### Items Not Saving

**Error**: Database connection issues

**Solution**:

```bash
# Check database file
ls -la backend/data/dashboard.db

# Test database connectivity
python -c "
from backend.models import get_session
import asyncio

async def test_db():
    async with get_session() as session:
        result = await session.execute('SELECT 1')
        print('Database connection OK')

asyncio.run(test_db())
"
```

**Error**: Validation errors

**Check**:

- Item name is not empty
- Priority is one of: low, medium, high
- All required fields are provided

### Migration Issues

**Error**: Legacy data not migrated

**Solution**:

```bash
# Check for legacy file
ls -la backend/data/grocery_list.json

# Manual migration trigger
# Restart backend with DEBUG=true to see migration logs
```

## 🔒 Security Issues

### Credential Problems

**Error**: `credentials.json` not found

**Solution**:

```bash
# Copy template
cp templates/credentials_template.json backend/data/credentials.json

# Edit with your actual credentials
# Ensure file permissions are correct
chmod 600 backend/data/credentials.json
```

**Error**: API keys not working

**Check**:

1. Keys are correctly formatted
2. Keys are activated (especially OpenWeatherMap)
3. Keys have proper permissions
4. No extra spaces or characters

### CORS Issues

**Error**: Cross-origin request blocked

**Solution**:

1. Update backend CORS settings:

   ```env
   ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

2. Restart backend server

3. Check frontend URL matches allowed origins

## 📊 Performance Issues

### Slow Loading

**Symptom**: Dashboard takes long to load

**Check**:

1. Network connectivity to external APIs
2. Database performance
3. Browser developer tools for slow requests

**Optimization**:

```bash
# Enable caching in backend
# Reduce API call frequency
# Optimize database queries
```

### Memory Issues

**Symptom**: High memory usage

**Solution**:

1. Check for memory leaks in browser
2. Restart backend periodically
3. Monitor system resources

## 🐛 Debug Mode

### Enable Debug Logging

**Backend**:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

**Frontend**:

```env
VITE_DEV_MODE=true
```

### Check Logs

**Backend logs**: Check terminal output when running `uvicorn`

**Frontend logs**: Check browser developer console (F12)

**Database logs**: Check SQLite database directly:

```bash
sqlite3 backend/data/dashboard.db
.tables
SELECT * FROM grocery_items LIMIT 5;
```

## 📞 Getting Help

### Before Opening an Issue

1. **Check this guide** for your specific error
2. **Enable debug mode** and check logs
3. **Test with minimal setup** (fresh install)
4. **Gather error details**:
   - Error messages
   - Browser console logs
   - Backend terminal output
   - System information

### Issue Template

When opening a GitHub issue, include:

```
**Environment:**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Node.js: [e.g., 18.12.0]
- Browser: [e.g., Chrome 108]

**Error:**
[Paste the exact error message]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Logs:**
[Paste relevant logs from backend terminal and browser console]
```

### Community Support

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and help
- **Documentation**: Check the [main documentation](../README.md)

---

**Still stuck?** Open a GitHub issue with the information above, and we'll help you resolve it!
