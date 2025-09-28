# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2025-09-28

### Fixed
- 🐛 **Notes Fetching**: Fixed critical bug where notes were not being fetched from Notion
- 🔐 **Database Access**: Resolved issue where Notion integration lacked access to notes database
- 📊 **Report Completeness**: Reports now properly include all related notes and tasks
- 📈 **Content Volume**: Reports now contain significantly more content (2x+ increase in size)

### Technical Details
- Root cause was missing database permissions for notes database
- Integration now has proper access to both tasks and notes databases
- All 4 notes are now properly fetched and included in generated reports
- Enhanced debugging revealed the access permission issue

## [1.3.0] - 2025-09-28

### Added
- 📄 **PDF Export**: Complete PDF generation with professional styling and table of contents
- 🎨 **PDF Styling**: Custom CSS with page breaks, headers, footers, and responsive design
- 📊 **Enhanced Content**: Comprehensive Notion block processing including toggles and nested content
- 🔄 **Fallback System**: Robust PDF generation with simplified HTML fallback for complex content
- 📱 **UI Integration**: PDF download button with loading states and progress indicators
- ⚡ **Performance**: Memory-optimized Docker container with proper resource limits

### Changed
- 🧹 **Production Ready**: Removed all debug code and console logging for clean production deployment
- 📝 **Content Processing**: Enhanced block-to-text conversion with recursive child block fetching
- 🎯 **Error Handling**: Improved error handling with proper timeout mechanisms and user feedback
- 🔧 **Code Quality**: Clean, maintainable codebase with comprehensive error logging for production debugging

### Fixed
- 🐛 **PDF Download**: Fixed PDF download button getting stuck in loading state
- 📄 **Content Capture**: Resolved missing content from Notion toggles and nested blocks
- 🔄 **UI Reliability**: Enhanced frontend error handling and timeout protection
- 📊 **Report Completeness**: Ensured all Notion content is properly captured in both MD and PDF formats

### Technical Details
- Added WeasyPrint integration for high-quality PDF generation
- Implemented recursive block processing for complete content capture
- Enhanced JavaScript with proper error handling and timeout management
- Added HEAD method support for file existence checking
- Improved Docker memory limits for PDF generation stability
- Comprehensive debug code cleanup while preserving essential error logging

## [1.2.0] - 2025-09-28

### Added
- 🔄 **Auto-Selection**: Projects dropdown now auto-selects first project when loaded
- 📊 **Status Grouping**: Projects grouped by status with visual icons in dropdown
- 🎨 **Enhanced UI**: Loading indicators and improved user feedback
- 🔧 **Flexible Input**: URL input works without requiring dropdown selection
- 📈 **Status Extraction**: Automatic status property extraction from Notion projects

### Changed
- 🎯 **Form Validation**: Dynamic validation based on input method (dropdown vs URL)
- 🎨 **Dropdown Styling**: Enhanced with optgroups, status icons, and loading states
- 📱 **User Experience**: Better visual feedback during project loading and selection

### Fixed
- 🐛 **Form Validation**: Fixed "Please select a project" warning when using URL input
- 🔄 **Loading States**: Added proper loading indicators and disabled states
- 📊 **Status Display**: Projects now show status information with appropriate icons

### Technical Details
- Added status property extraction from multiple Notion property types
- Implemented project grouping by status with smart ordering
- Enhanced JavaScript for better form handling and user feedback
- Added CSS styling for loading states and status indicators

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
