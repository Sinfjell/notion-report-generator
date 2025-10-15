# Docker Usage Guide

## Easy Way: Using Docker Desktop (Recommended)

### First Time Setup
1. Open your terminal in this project folder
2. Run: `docker-compose up -d --build`
3. That's it! The app is now running at http://localhost:8080

### Daily Usage
Just open **Docker Desktop** and:
- ▶️ Click **Play** to start the app
- ⏸️ Click **Stop** to stop the app  
- 🔄 Click **Restart** to restart the app

You'll see it listed as `notion-report-generator` under Containers.

### After Code Changes
When you update the code:
1. In Docker Desktop, click the 🔄 button next to your container
2. Or run: `docker-compose up -d --build`

### Viewing Logs
In Docker Desktop:
1. Click on your container
2. Click the **Logs** tab

Or in terminal: `docker-compose logs -f`

### Stopping Everything
- Docker Desktop: Click the Stop button
- Terminal: `docker-compose down`

### Removing Everything (Fresh Start)
```bash
docker-compose down -v
docker-compose up -d --build
```

## Environment Variables
Make sure you have a `.env` file with:
```
NOTION_API_TOKEN=your_token_here
```

The app automatically:
- ✅ Loads your `.env` file
- ✅ Uses local storage for reports
- ✅ Restarts automatically if it crashes
- ✅ Has increased timeout for large Notion databases (30 seconds)

