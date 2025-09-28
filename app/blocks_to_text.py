from typing import List, Dict, Any


def extract_text_content(block: Dict[str, Any]) -> str:
    """Extract text content from a Notion block's rich text."""
    text_content = ""
    
    # Handle different block types
    block_type = block.get("type", "")
    block_data = block.get(block_type, {})
    
    # Extract rich text content
    rich_text = block_data.get("rich_text", [])
    for text_obj in rich_text:
        if text_obj.get("type") == "text":
            text_content += text_obj.get("text", {}).get("content", "")
    
    return text_content


def block_to_text(block: Dict[str, Any], flatten_headings: bool = False) -> str:
    """Convert a single Notion block to text."""
    block_type = block.get("type", "")
    text_content = extract_text_content(block)
    
    if block_type == "heading_1":
        if flatten_headings:
            return f"**{text_content}**\n\n"
        return f"# {text_content}\n"
    elif block_type == "heading_2":
        if flatten_headings:
            return f"**{text_content}**\n\n"
        return f"## {text_content}\n"
    elif block_type == "heading_3":
        if flatten_headings:
            return f"**{text_content}**\n\n"
        return f"### {text_content}\n"
    elif block_type == "paragraph":
        return f"{text_content}\n" if text_content else "\n"
    elif block_type == "to_do":
        checked = block.get("to_do", {}).get("checked", False)
        checkbox = "- [x]" if checked else "- [ ]"
        return f"{checkbox} {text_content}\n"
    elif block_type == "bulleted_list_item":
        return f"- {text_content}\n"
    elif block_type == "numbered_list_item":
        return f"1. {text_content}\n"
    elif block_type == "quote":
        return f"> {text_content}\n"
    elif block_type == "code":
        language = block.get("code", {}).get("language", "")
        return f"```{language}\n{text_content}\n```\n"
    elif block_type == "divider":
        return "---\n"
    elif block_type == "callout":
        icon = block.get("callout", {}).get("icon", {}).get("emoji", "")
        return f"{icon} {text_content}\n"
    elif block_type == "toggle":
        return f"<details>\n<summary>{text_content}</summary>\n"
    elif block_type == "table":
        return f"[Table: {text_content}]\n"
    elif block_type == "image":
        caption = block.get("image", {}).get("caption", [])
        caption_text = "".join([item.get("text", {}).get("content", "") for item in caption])
        return f"[Image: {caption_text}]\n"
    elif block_type == "file":
        return f"[File: {text_content}]\n"
    elif block_type == "video":
        return f"[Video: {text_content}]\n"
    elif block_type == "audio":
        return f"[Audio: {text_content}]\n"
    elif block_type == "embed":
        return f"[Embed: {text_content}]\n"
    elif block_type == "bookmark":
        return f"[Bookmark: {text_content}]\n"
    elif block_type == "link_preview":
        return f"[Link: {text_content}]\n"
    elif block_type == "equation":
        return f"$${text_content}$$\n"
    elif block_type == "table_of_contents":
        return f"[Table of Contents]\n"
    elif block_type == "breadcrumb":
        return f"[Breadcrumb]\n"
    elif block_type == "column_list":
        return f"[Column List]\n"
    elif block_type == "column":
        return f"[Column]\n"
    elif block_type == "link_to_page":
        return f"[Link to Page: {text_content}]\n"
    elif block_type == "synced_block":
        return f"[Synced Block]\n"
    elif block_type == "template":
        return f"[Template: {text_content}]\n"
    elif block_type == "child_page":
        return f"[Child Page: {text_content}]\n"
    elif block_type == "child_database":
        return f"[Child Database: {text_content}]\n"
    else:
        return f"[Unsupported block: {block_type}]\n"


def blocks_to_text(blocks: List[Dict[str, Any]], flatten_headings: bool = False) -> str:
    """Convert a list of Notion blocks to plain text."""
    result = []
    
    for block in blocks:
        text = block_to_text(block, flatten_headings)
        result.append(text)
    
    return "".join(result)


def get_page_title(page: Dict[str, Any]) -> str:
    """Extract the title from a Notion page."""
    properties = page.get("properties", {})
    
    # Look for common title property names
    for prop_name in ["Name", "Title", "Page"]:
        if prop_name in properties:
            prop = properties[prop_name]
            if prop.get("type") == "title":
                title_rich_text = prop.get("title", [])
                if title_rich_text:
                    return "".join([item.get("text", {}).get("content", "") for item in title_rich_text])
    
    # Fallback to first title property
    for prop_name, prop in properties.items():
        if prop.get("type") == "title":
            title_rich_text = prop.get("title", [])
            if title_rich_text:
                return "".join([item.get("text", {}).get("content", "") for item in title_rich_text])
    
    return "Untitled"
