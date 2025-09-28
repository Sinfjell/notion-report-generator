from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime
from slugify import slugify
import re
import os
import urllib.parse

from app.settings import settings
from app.notion import notion_api
from app.blocks_to_text import blocks_to_text, get_page_title
from app.storage import upload_text_public_flexible


def extract_task_properties(task_page: Dict[str, Any]) -> Dict[str, str]:
    """Extract useful properties from a task page."""
    properties = task_page.get("properties", {})
    task_props = {}
    
    # Extract status (check both Status and Kanban properties)
    for status_prop_name in ["Status", "Kanban"]:
        status_prop = properties.get(status_prop_name, {})
        if status_prop.get("type") == "status":
            status_value = status_prop.get("status", {})
            if status_value and status_value.get("name"):
                task_props["status"] = status_value.get("name")
                break
    
    # Extract priority
    priority_prop = properties.get("Priority", {})
    if priority_prop.get("type") == "select":
        priority_value = priority_prop.get("select", {})
        if priority_value:
            task_props["priority"] = priority_value.get("name", "")
    
    # Extract due date
    due_prop = properties.get("Do date", {})
    if due_prop.get("type") == "date":
        due_value = due_prop.get("date", {})
        if due_value and due_value.get("start"):
            task_props["due_date"] = due_value.get("start", "")
    
    # Extract date done
    date_done_prop = properties.get("Date done", {})
    if date_done_prop.get("type") == "date":
        date_done_value = date_done_prop.get("date", {})
        if date_done_value and date_done_value.get("start"):
            task_props["date_done"] = date_done_value.get("start", "")
    
    # Extract info formula
    info_prop = properties.get("Info", {})
    if info_prop.get("type") == "formula":
        info_value = info_prop.get("formula", {})
        if info_value and info_value.get("string"):
            task_props["info"] = info_value.get("string", "")
    
    # Extract tags
    tags_prop = properties.get("Tags", {})
    if tags_prop.get("type") == "multi_select":
        tags = tags_prop.get("multi_select", [])
        if tags:
            task_props["tags"] = ", ".join([tag.get("name", "") for tag in tags])
    
    # Extract assignee
    assignee_prop = properties.get("Assignee", {})
    if assignee_prop.get("type") == "people":
        assignees = assignee_prop.get("people", [])
        if assignees:
            task_props["assignee"] = ", ".join([person.get("name", "") for person in assignees])
    
    return task_props


def generate_table_of_contents(content: str) -> str:
    """Generate a table of contents from Markdown headings."""
    toc_lines = []
    toc_lines.append("## Table of Contents\n")
    
    # Find all headings in the content
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    headings = re.findall(heading_pattern, content, re.MULTILINE)
    
    for level, title in headings:
        # Create anchor link (simple slug)
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor).strip('-')
        
        # Create indentation based on heading level
        indent = "  " * (len(level) - 1)
        
        # Create TOC entry
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    
    return "\n".join(toc_lines) + "\n\n---\n\n"


def parse_notion_url(url_or_id: str) -> str:
    """Parse Notion URL or return page ID directly."""
    if not url_or_id:
        raise ValueError("URL or page ID is required")
    
    # If it's already a page ID (32 characters with hyphens)
    if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', url_or_id):
        return url_or_id
    
    # If it's a Notion URL, extract the page ID
    if 'notion.so' in url_or_id:
        # First try to find a 32-character hex string anywhere in the URL
        page_id_match = re.search(r'([a-f0-9]{32})', url_or_id)
        if page_id_match:
            page_id_raw = page_id_match.group(1)
            # Convert 32-char format to UUID format
            page_id = f"{page_id_raw[:8]}-{page_id_raw[8:12]}-{page_id_raw[12:16]}-{page_id_raw[16:20]}-{page_id_raw[20:32]}"
            return page_id
        
        # Fallback to specific patterns
        patterns = [
            r'notion\.so/[^/]+/([a-f0-9]{32})',
            r'notion\.so/([a-f0-9]{32})',
            r'notion\.so/[^/]+/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
            r'notion\.so/[^/]+/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\?',  # With query params
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                page_id = match.group(1)
                # Convert 32-char format to UUID format if needed
                if len(page_id) == 32:
                    page_id = f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:32]}"
                return page_id
        
        raise ValueError("Could not extract page ID from Notion URL")
    
    raise ValueError("Invalid URL or page ID format")


app = FastAPI(title="Notion Report Generator", version="1.1.0")


class GenerateRequest(BaseModel):
    page_id: str


class ProjectOption(BaseModel):
    id: str
    title: str
    url: str


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Service is healthy"}


async def generate_report(page_id: str) -> dict:
    """Generate a plain text report for a Notion project."""
    try:
        # 1. Fetch Project page
        project_page = await notion_api.get_page(page_id)
        project_title = get_page_title(project_page)
        
        # 2. Extract relation IDs
        notes_ids = notion_api.extract_relation_ids(
            project_page, 
            settings.notion_rel_project_to_notes
        )
        tasks_ids = notion_api.extract_relation_ids(
            project_page, 
            settings.notion_rel_project_to_tasks
        )
        
        # 3. Fetch all pages and their blocks
        project_blocks = await notion_api.get_block_children(page_id)
        project_content = blocks_to_text(project_blocks)
        
        # Fetch notes
        notes_content = []
        for note_id in notes_ids:
            try:
                note_page = await notion_api.get_page(note_id)
                note_title = get_page_title(note_page)
                note_blocks = await notion_api.get_block_children(note_id)
                note_content = blocks_to_text(note_blocks, flatten_headings=True)
                notes_content.append(f"### {note_title}\n\n{note_content}\n")
            except Exception as e:
                notes_content.append(f"### [Error loading note: {str(e)}]\n\n")
        
        # Fetch tasks
        tasks_content = []
        for task_id in tasks_ids:
            try:
                task_page = await notion_api.get_page(task_id)
                task_title = get_page_title(task_page)
                
                # Extract task properties
                task_props = extract_task_properties(task_page)
                
                # Build property string with status first and highlighted
                prop_parts = []
                if task_props.get("status"):
                    prop_parts.append(f"**Status: {task_props['status']}**")
                if task_props.get("priority"):
                    prop_parts.append(f"Priority: {task_props['priority']}")
                if task_props.get("due_date"):
                    prop_parts.append(f"Due: {task_props['due_date']}")
                if task_props.get("date_done"):
                    prop_parts.append(f"Done: {task_props['date_done']}")
                if task_props.get("assignee"):
                    prop_parts.append(f"Assignee: {task_props['assignee']}")
                if task_props.get("tags"):
                    prop_parts.append(f"Tags: {task_props['tags']}")
                if task_props.get("info"):
                    prop_parts.append(f"Info: {task_props['info']}")
                
                properties_str = f" - {', '.join(prop_parts)}" if prop_parts else ""
                
                # Get task content with flattened headings
                task_blocks = await notion_api.get_block_children(task_id)
                task_content = blocks_to_text(task_blocks, flatten_headings=True)
                
                tasks_content.append(f"### {task_title}{properties_str}\n\n{task_content}\n")
            except Exception as e:
                tasks_content.append(f"### [Error loading task: {str(e)}]\n\n")
        
        # 4. Build final report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Build the main content first
        main_content = f"""# {project_title}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Project Overview

{project_content}

---

## Notes

{chr(10).join(notes_content) if notes_content else "*No notes found.*"}

---

## Tasks

{chr(10).join(tasks_content) if tasks_content else "*No tasks found.*"}

---

*Report generated by Notion Report Generator*
"""
        
        # Generate table of contents and insert it after the title
        toc = generate_table_of_contents(main_content)
        
        # Insert TOC after the title and generation info
        title_section = f"# {project_title}\n\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        rest_of_content = main_content[len(title_section):]
        
        report_content = title_section + toc + rest_of_content
        
        # 5. Upload to GCS
        project_slug = slugify(project_title)
        blob_path = f"reports/{page_id[:4]}/project-{project_slug}-{timestamp}.md"
        
        public_url = upload_text_public_flexible(
            blob_path,
            report_content
        )
        
        # 6. Update Project URL property
        await notion_api.update_page_url_property(
            page_id,
            settings.notion_project_pdf_url_prop,
            public_url
        )
        
        return {
            "status": "ok",
            "url": public_url,
            "project_title": project_title,
            "notes_count": len(notes_ids),
            "tasks_count": len(tasks_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate report: {str(e)}")


@app.get("/generate")
async def generate_get(page_id: str = Query(..., description="Notion page ID")):
    """Generate report via GET request."""
    return await generate_report(page_id)


@app.post("/generate")
async def generate_post(request: GenerateRequest):
    """Generate report via POST request."""
    return await generate_report(request.page_id)


@app.get("/", response_class=HTMLResponse)
async def web_interface():
    """Serve the web interface."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Notion Report Generator</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #555;
            }
            select, input {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            select:focus, input:focus {
                outline: none;
                border-color: #007bff;
            }
            button {
                background: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
                margin-top: 10px;
            }
            button:hover {
                background: #0056b3;
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 5px;
                display: none;
            }
            .status.loading {
                background: #e3f2fd;
                color: #1976d2;
                border: 1px solid #bbdefb;
            }
            .status.success {
                background: #e8f5e8;
                color: #2e7d32;
                border: 1px solid #c8e6c9;
            }
            .status.error {
                background: #ffebee;
                color: #c62828;
                border: 1px solid #ffcdd2;
            }
            .download-section {
                margin-top: 20px;
                text-align: center;
                display: none;
            }
            .download-btn {
                background: #28a745;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin: 10px;
            }
            .download-btn:hover {
                background: #218838;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #007bff;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Notion Report Generator</h1>
            
            <form id="reportForm">
                <div class="form-group">
                    <label for="projectSelect">Select Project:</label>
                    <select id="projectSelect" required>
                        <option value="">Loading projects...</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="customInput">Or paste Notion URL/Page ID:</label>
                    <input type="text" id="customInput" placeholder="https://notion.so/... or page-id">
                </div>
                
                <button type="submit" id="generateBtn">Generate Report</button>
            </form>
            
            <div id="status" class="status"></div>
            
            <div id="downloadSection" class="download-section">
                <h3>Report Generated Successfully!</h3>
                <a id="downloadBtn" class="download-btn" href="#" download>Download Report</a>
            </div>
        </div>

        <script>
            let projects = [];
            
            // Load projects on page load
            async function loadProjects() {
                try {
                    const response = await fetch('/api/projects');
                    projects = await response.json();
                    
                    const select = document.getElementById('projectSelect');
                    select.innerHTML = '<option value="">Select a project...</option>';
                    
                    projects.forEach(project => {
                        const option = document.createElement('option');
                        option.value = project.id;
                        option.textContent = project.title;
                        select.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error loading projects:', error);
                    document.getElementById('projectSelect').innerHTML = '<option value="">Error loading projects</option>';
                }
            }
            
            // Show status message
            function showStatus(message, type) {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = `status ${type}`;
                status.style.display = 'block';
            }
            
            // Hide status
            function hideStatus() {
                document.getElementById('status').style.display = 'none';
            }
            
            // Show download section
            function showDownload(url) {
                const downloadSection = document.getElementById('downloadSection');
                const downloadBtn = document.getElementById('downloadBtn');
                downloadBtn.href = url;
                downloadSection.style.display = 'block';
            }
            
            // Hide download section
            function hideDownload() {
                document.getElementById('downloadSection').style.display = 'none';
            }
            
            // Form submission
            document.getElementById('reportForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const projectSelect = document.getElementById('projectSelect');
                const customInput = document.getElementById('customInput');
                const generateBtn = document.getElementById('generateBtn');
                
                let pageId = projectSelect.value || customInput.value.trim();
                
                if (!pageId) {
                    showStatus('Please select a project or enter a URL/Page ID', 'error');
                    return;
                }
                
                // Clear dropdown validation if custom input is used
                if (customInput.value.trim()) {
                    projectSelect.setCustomValidity('');
                }
                
                // Disable button and show loading
                generateBtn.disabled = true;
                generateBtn.innerHTML = '<span class="spinner"></span>Generating Report...';
                hideStatus();
                hideDownload();
                
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ page_id: pageId })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showStatus('Report generated successfully!', 'success');
                        // Convert file:// URL to download endpoint
                        let downloadUrl = result.url;
                        if (downloadUrl.startsWith('file://')) {
                            // Extract the relative path from the file:// URL
                            let filePath = downloadUrl.replace('file://', '');
                            // Remove the absolute path prefix to get the relative path
                            if (filePath.includes('/local_reports/')) {
                                filePath = filePath.substring(filePath.indexOf('/local_reports/'));
                            }
                            // Handle Docker container paths
                            if (filePath.startsWith('/app/local_reports/')) {
                                filePath = filePath.replace('/app/local_reports/', 'local_reports/');
                            }
                            downloadUrl = '/download' + filePath;
                        }
                        showDownload(downloadUrl);
                    } else {
                        showStatus(`Error: ${result.detail || 'Unknown error'}`, 'error');
                    }
                } catch (error) {
                    showStatus(`Error: ${error.message}`, 'error');
                } finally {
                    // Re-enable button
                    generateBtn.disabled = false;
                    generateBtn.innerHTML = 'Generate Report';
                }
            });
            
            // Load projects when page loads
            loadProjects();
        </script>
    </body>
    </html>
    """


@app.get("/api/projects")
async def get_projects():
    """Get list of projects from Notion database."""
    try:
        # Use the database ID from your URL
        database_id = "a39c93bf51c64b2cb57ace514ff96817"
        pages = await notion_api.get_database_pages(database_id)
        
        projects = []
        for page in pages:
            title = get_page_title(page)
            page_id = page.get("id", "")
            projects.append(ProjectOption(
                id=page_id,
                title=title,
                url=f"https://notion.so/{page_id.replace('-', '')}"
            ))
        
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")


@app.post("/api/generate")
async def generate_report_api(request: GenerateRequest):
    """Generate report via API with URL parsing."""
    try:
        page_id = parse_notion_url(request.page_id)
        return await generate_report(page_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download generated report file."""
    # Convert file:// URL to actual file path
    if file_path.startswith("file://"):
        file_path = file_path[7:]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=os.path.basename(file_path)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
