# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-09-28

### Added
- 🌐 **Web Interface**: Complete HTML interface with project dropdown and download functionality
- 🐳 **Docker Support**: Single container setup with proper naming and environment variable handling
- 📊 **Project Selection**: Dropdown populated from Notion database with all available projects
- 🔗 **URL Parsing**: Support for both Notion URLs and page IDs in the web interface
- 📥 **Download Management**: Proper file download functionality with correct path handling
- 🛠️ **Container Management**: `docker-manage.sh` script for easy container operations

### Changed
- 🔧 **API Endpoints**: Added new `/api/projects` and `/api/generate` endpoints for web interface
- 📁 **File Paths**: Improved path handling for Docker container environments
- 🎨 **User Experience**: Enhanced form validation to allow either dropdown or URL input
- 📝 **Documentation**: Updated README with Docker-first approach and comprehensive setup instructions

### Fixed
- 🐛 **Download Issues**: Fixed file download functionality in Docker containers
- 🔗 **URL Parsing**: Corrected Notion URL parsing to handle page IDs embedded in titles
- 📝 **Form Validation**: Fixed form validation to allow URL input without dropdown selection
- 🐳 **Docker Paths**: Resolved path construction issues for file downloads in containerized environment

### Technical Details
- Added `parse_notion_url()` function for robust URL/page ID parsing
- Enhanced JavaScript for proper download URL construction
- Improved Docker container naming and management
- Added support for `.env` file loading in Docker script

## [1.0.0] - 2025-09-28

### Added
- 📊 **Core Functionality**: Generate comprehensive project reports from Notion
- 🎯 **Rich Task Properties**: Extract status, priority, due dates, completion info, and custom formulas
- 📝 **Markdown Output**: Clean, structured reports with table of contents
- 🤖 **AI-Optimized**: Perfect structure for AI consumption and analysis
- 🔄 **Flexible Storage**: Support for both local file storage and Google Cloud Storage
- ⚡ **FastAPI Backend**: RESTful API with automatic documentation
- 🐳 **Docker Ready**: Easy deployment to Google Cloud Run
