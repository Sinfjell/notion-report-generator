from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
from slugify import slugify

from app.settings import settings
from app.notion import notion_api
from app.blocks_to_text import blocks_to_text, get_page_title
from app.storage import upload_text_public_flexible
import re


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


app = FastAPI(title="Notion Report Generator", version="1.0.0")


class GenerateRequest(BaseModel):
    page_id: str


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
