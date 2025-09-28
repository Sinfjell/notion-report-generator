# Notion Report Generator

Generate comprehensive project reports from Notion with tasks, notes, and properties. Perfect for AI consumption and project overviews.

**Version:** 1.3.0

## Features

- 📊 **Comprehensive Reports**: Extract project content, related tasks, and notes
- 🎯 **Rich Task Properties**: Status, priority, due dates, completion info, and custom formulas
- 📝 **Markdown Output**: Clean, structured reports with table of contents
- 🤖 **AI-Optimized**: Perfect structure for AI consumption and analysis
- 🌐 **Web Interface**: Simple HTML interface with project dropdown and download functionality
- 🔄 **Flexible Storage**: Support for both local file storage and Google Cloud Storage
- ⚡ **FastAPI Backend**: RESTful API with automatic documentation
- 🐳 **Docker Ready**: Easy deployment with single container setup

## Quick Start

### Docker (Recommended)

1. **Clone and setup**:
   ```bash
   git clone https://github.com/Sinfjell/notion-report-generator.git
   cd notion-report-generator
   ```

2. **Set your Notion API token**:
   ```bash
   export NOTION_API_TOKEN='your_notion_api_token_here'
   ```

3. **Run with Docker**:
   ```bash
   ./docker-run.sh
   ```

4. **Access the web interface**:
   - Open http://localhost:8080 in your browser
   - Select a project from the dropdown or paste a Notion URL
   - Click "Generate Report" and download the result

### Local Development

1. **Clone and setup**:
   ```bash
   git clone https://github.com/Sinfjell/notion-report-generator.git
   cd notion-report-generator
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Notion API**:
   ```bash
   export NOTION_API_TOKEN='your_notion_api_token_here'
   ```

3. **Test locally**:
   ```bash
   python test_local.py --page-id YOUR_PAGE_ID
   ```

4. **Start development server**:
   ```bash
   python dev_server.py
   ```

### Google Cloud Deployment

1. **Setup Google Cloud**:
   ```bash
   make setup
   ```

2. **Deploy to Cloud Run**:
   ```bash
   export NOTION_API_TOKEN='your_notion_api_token_here'
   make deploy BUCKET=your-gcs-bucket-name
   ```

3. **Test deployment**:
   ```bash
   make test-generate PROJECT_PAGE_ID=your-page-id
   ```

## API Endpoints

- `GET /` - Web interface with project dropdown
- `GET /api/projects` - Get list of projects from Notion database
- `POST /api/generate` - Generate report via API with URL parsing
- `GET /download/{file_path}` - Download generated report file
- `GET /healthz` - Health check
- `GET /generate?page_id=...` - Generate report via GET (legacy)
- `POST /generate` - Generate report via POST with JSON body (legacy)
- `GET /docs` - Interactive API documentation

## Report Structure

Generated reports include:

```markdown
# Project Title
**Generated:** 2025-09-28 11:39:11

## Table of Contents
- [Project Overview](#project-overview)
- [Tasks](#tasks)
  - [Task 1 - **Status: Done**, Due: 2025-09-11, Done: 2025-09-12](#task-1)
  - [Task 2 - **Status: Next action**, Info: 🟢 Next action 5d](#task-2)

---

## Project Overview
[Main project content with proper headings]

---

## Tasks
### Task 1 - **Status: Done**, Due: 2025-09-11, Done: 2025-09-12, Info: ✅ Done 16d
**Content heading** (flattened to avoid hierarchy conflicts)
Task content...

### Task 2 - **Status: Next action**, Info: 🟢 Next action 5d
**Another content heading** (flattened)
More task content...
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTION_API_TOKEN` | (required) | Your Notion integration token |
| `USE_LOCAL_STORAGE` | `true` | Use local file storage instead of GCS |
| `LOCAL_STORAGE_PATH` | `./local_reports` | Directory for local reports |
| `GCS_BUCKET` | (required for production) | Google Cloud Storage bucket name |
| `NOTION_REL_PROJECT_TO_NOTES` | `Notes` | Property name for notes relation |
| `NOTION_REL_PROJECT_TO_TASKS` | `Tasks` | Property name for tasks relation |
| `NOTION_PROJECT_PDF_URL_PROP` | `Latest PDF URL` | Property name for PDF URL |

## Notion Setup

1. **Create Integration**:
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the "Internal Integration Token"

2. **Share Pages**:
   - Share your Notion pages with the integration
   - Ensure the integration has access to all related pages

3. **Configure Relations**:
   - Set up relation properties between projects and tasks/notes
   - Use the property names specified in your environment variables

## Development

### Project Structure

```
notion-report-generator/
├── app/                    # Main application code
│   ├── main.py            # FastAPI application
│   ├── notion.py          # Notion API client
│   ├── blocks_to_text.py  # Content conversion
│   ├── storage.py         # Storage abstraction
│   └── settings.py        # Configuration
├── local_reports/         # Generated reports (local mode)
├── test_local.py         # Local testing script
├── dev_server.py         # Development server
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
└── Makefile            # Deployment commands
```

### Testing

```bash
# Basic connectivity test
python test_local.py

# Full workflow test
python test_local.py --page-id YOUR_PAGE_ID

# Start development server
python dev_server.py
```

## Deployment

### Google Cloud Run

The project includes a complete Makefile for Google Cloud deployment:

```bash
# Setup Google Cloud project
make setup

# Deploy to Cloud Run
export NOTION_API_TOKEN='your_token'
make deploy BUCKET=your-bucket-name

# Test deployment
make test-generate PROJECT_PAGE_ID=your-page-id
```

### Docker

```bash
# Build image
docker build -t notion-report-generator .

# Run locally
docker run -p 8080:8080 \
  -e NOTION_API_TOKEN='your_token' \
  -e USE_LOCAL_STORAGE=true \
  notion-report-generator
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `LOCAL_TESTING.md`
- Review the API documentation at `/docs` when running locally