# Local Testing Guide

This guide helps you test the Notion Report Generator locally before deploying to Google Cloud.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your Notion API token:**
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the "Internal Integration Token"
   - Share your Notion pages with this integration

3. **Set up environment:**
   ```bash
   export NOTION_API_TOKEN='your_token_here'
   ```

4. **Run tests:**
   ```bash
   python test_local.py
   ```

5. **Start development server:**
   ```bash
   python dev_server.py
   ```

## What's Different in Local Mode

- **Local Storage**: Reports are saved to `./local_reports/` instead of Google Cloud Storage
- **No GCS Required**: You don't need Google Cloud credentials for local testing
- **File URLs**: Reports get `file://` URLs instead of public HTTP URLs
- **Auto-reload**: Development server restarts when you change code

## Testing Workflow

### 1. Basic Connectivity Test
```bash
python test_local.py
```
This tests:
- Notion API token validity
- Local storage functionality
- Basic app configuration

### 2. Full Workflow Test
```bash
python test_local.py --page-id YOUR_PAGE_ID
```
This tests the complete report generation process with a real Notion page.

### 3. Manual API Testing
Start the server and test the API endpoints:

```bash
# Start server
python dev_server.py

# Test health check
curl http://localhost:8080/healthz

# Generate report (replace with real page ID)
curl "http://localhost:8080/generate?page_id=YOUR_PAGE_ID"
```

## Configuration

The app uses these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTION_API_TOKEN` | (required) | Your Notion integration token |
| `USE_LOCAL_STORAGE` | `true` | Use local file storage instead of GCS |
| `LOCAL_STORAGE_PATH` | `./local_reports` | Directory for local reports |
| `NOTION_REL_PROJECT_TO_NOTES` | `Notes` | Property name for notes relation |
| `NOTION_REL_PROJECT_TO_TASKS` | `Tasks` | Property name for tasks relation |
| `NOTION_PROJECT_PDF_URL_PROP` | `Latest PDF URL` | Property name for PDF URL |

## File Structure

```
notion-report-generator/
├── app/                    # Main application code
├── local_reports/          # Generated reports (created automatically)
│   └── reports/
│       └── [page_id]/
│           └── project-[name]-[timestamp].txt
├── test_local.py          # Local testing script
├── dev_server.py          # Development server
└── requirements.txt       # Dependencies
```

## Troubleshooting

### "Notion API token not set"
- Make sure you've set the `NOTION_API_TOKEN` environment variable
- Or create a `.env` file with: `NOTION_API_TOKEN=your_token_here`

### "Invalid Notion API token"
- Check that your token is correct
- Make sure you've shared your Notion pages with the integration

### "File not found" errors
- Check that the `local_reports` directory is writable
- The directory will be created automatically if it doesn't exist

### "Relation property not found"
- Check that your Notion pages have the correct relation properties
- Update the property names in your environment variables if needed

## Next Steps

Once local testing works:

1. **Test with real data**: Use actual project pages with notes and tasks
2. **Verify report format**: Check that the generated reports contain all expected content
3. **Test error handling**: Try with invalid page IDs or pages without relations
4. **Deploy to Google Cloud**: When ready, switch to GCS storage and deploy

## API Endpoints

- `GET /healthz` - Health check
- `GET /generate?page_id=...` - Generate report via GET
- `POST /generate` - Generate report via POST with JSON body
- `GET /docs` - Interactive API documentation (when server is running)
